from odoo import models, fields, api
from . import logica_dronify
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)

class Cliente(models.Model):
    _inherit = "res.partner"
    _description = "Modelo para gestionar los clientes de Dronify"
    
    name = fields.Char(string="Nombre del cliente")
    es_cliente = fields.Boolean(string="Cliente", default=True)
    es_vip = fields.Boolean(string="VIP")
    es_piloto = fields.Boolean(string="Piloto")
    licencia = fields.Char(string="Licencia de Piloto") #obligatorio para pilotos
    dron_autorizado_ids = fields.Many2many('dronify.dron', 'rel_partner_dron', 'partner_id', 'dron_id', string ='Drones autorizados')
    
    #constraint para obligar a los pilotos a tener licencia
    @api.constrains('es_piloto', 'licencia')
    def _validar_licencia_piloto(self):
        for cliente in self:
            if cliente.es_piloto and not cliente.licencia:
                raise ValidationError(
                    f"Error: El piloto {cliente.name} debe tener una licencia asignada."
                )
                
class Dron(models.Model):
    _name = "dronify.dron"
    _description = "Modelo para gestionar los drones de Dronify"
    
    name = fields.Char(string="Nombre")
    capacidad_max = fields.Float(string="Capacidad de Carga máxima(kg)", required=True)
    bateria = fields.Integer(string="Batería disponible (%)", default=100)
    estado = fields.Selection([('disponible', 'Disponible'), ('taller', 'En Mantenimiento'), ('en_vuelo', 'En Vuelo')], string="Estado", default='disponible')
    piloto_autorizado_ids = fields.Many2many('res.partner', 'rel_partner_dron', 'dron_id', 'partner_id', string="Pilotos autorizados")
    vuelo_ids = fields.One2many('dronify.vuelo', 'dron_id', string='Vuelos')
    
    #constraint para controlar que el valor de la batería sea positivo
    @api.constrains('bateria')
    def _validar_bateria(self):
        for dron in self:
            if dron.bateria < 0 or dron.bateria > 100:
                raise ValidationError("Error: La batería debe estar entre 0% y 100%")
    
            
class Vuelo(models.Model):
    _name = "dronify.vuelo"
    _description = "Modelo para gestionar vuelos"
    
    codigo = fields.Char(string="Código", readonly=True)
    name = fields.Char(string="Nombre", required=True) #tiene default
    preparado = fields.Boolean(string="Preparado")
    realizado = fields.Boolean(string="Realizado")
    peso_total = fields.Float(string="Peso total", compute="_compute_peso_total", store=True) #computado
    consumo_estimado = fields.Float(string="Consumo estimado", compute="_compute_consumo_estimado", store=True) #computado
    dron_id = fields.Many2one('dronify.dron',string= "Dron asignado", required=True)
    piloto_id= fields.Many2one('res.partner', string="Piloto responsable", required=True) #required solo pilotos
    paquetes_ids = fields.One2many('dronify.paquete', 'vuelo_id', string="Paquetes")
    zona_id = fields.Many2one('dronify.zona', string="Zona asignada", required=True)
    
    #constraint para controlar que el piloto está asignado al dron
    @api.constrains('piloto_id', 'dron_id')
    def _validar_asignacion_piloto(self):
        for vuelo in self:
            if vuelo.preparado:
                autorizado = False
                for dron in vuelo.piloto_id.dron_autorizado_ids:
                    if dron.id == vuelo.dron_id.id:
                        autorizado = True
                        break
                if not autorizado:
                    raise ValidationError(f"Error: El piloto {vuelo.piloto_id.name} no está asignado para este dron.")
    
    #constraint para controlar que el dron esté disponible
    @api.constrains('dron_id', 'preparado')
    def _validar_disponibilidad(self):
        for vuelo in self:
            if vuelo.preparado:
                if vuelo.dron_id.estado != 'disponible':
                    raise ValidationError(f"Error: El dron {vuelo.dron_id.name} no está disponible para este vuelo. Estado actual: {vuelo.dron_id.estado}")
    
    #contraint para controlar que solo los clientes piloto puedan ser pilotos responsables
    @api.constrains('preparado','piloto_id')
    def _validar_piloto_id(self):
        for vuelo in self:
            if vuelo.preparado and not vuelo.piloto_id.es_piloto:
                raise ValidationError("El piloto a cargo debe estar asignado como piloto.")
            
    #constraint para comprobar que el vuelo preparado tiene paquetes
    @api.constrains('preparado', 'paquetes_ids')
    def _validar_paquetes(self):
        for vuelo in self:
            if vuelo.preparado and not vuelo.paquetes_ids:
                raise ValidationError("El vuelo debe contener al menos 1 paquete.")
    
    #constraint para comprobar que se puede hacer el vuelo
    @api.constrains('preparado', 'consumo_estimado')
    def _validar_capacidad_dron(self):
        for vuelo in self:
            if vuelo.preparado and vuelo.peso_total > vuelo.dron_id.capacidad_max:
                raise ValidationError("Error: El peso de la mercancía supera la capacidad máxima del dron.")   
     
    #constraint para comprobar que la bateria es suficiente segun lo estimado   
    @api.constrains('preparado', 'consumo_estimado', 'dron_id')
    def _validar_bateria_suficiente(self):
        for vuelo in self:
            if vuelo.preparado:
                bateria_ok = logica_dronify.validar_estado_bateria(bateria_actual=vuelo.dron_id.bateria, consumo_estimado=vuelo.consumo_estimado)
                if not bateria_ok:
                    raise ValidationError("La batería actual del dron no es suficiente para llevar a cabo el vuelo.")
    
    #funcion para calcular el peso total
    @api.depends('paquetes_ids', 'paquetes_ids.peso')
    def _compute_peso_total(self):
        for vuelo in self:
            peso_total = 0.0
            for paquete in vuelo.paquetes_ids:
                peso_total = peso_total + paquete.peso
                
            vuelo.peso_total = peso_total
    
    #funcion para calcular el consumo estimado
    @api.depends('paquetes_ids', 'paquetes_ids.peso', 'paquetes_ids.cliente_id.es_vip', 'zona_id.distancia_km', 'zona_id.nivel_riesgo')
    def _compute_consumo_estimado(self):
        for vuelo in self:
            #peso total
            peso_total = 0.0
            for paquete in vuelo.paquetes_ids:
                peso_total = peso_total + paquete.peso
            #vip o no vip
            es_vip = False
            for paquete in vuelo.paquetes_ids:
                if paquete.cliente_id.es_vip:
                    es_vip = True
                    break
            #datos de zona
            distancia = vuelo.zona_id.distancia_km
            riesgo = int(vuelo.zona_id.nivel_riesgo)
            #usar funcion
            consumo = logica_dronify.calcular_consumo_vuelo(peso_total=peso_total, distancia_total=distancia, riesgo_valor=riesgo, es_vip=es_vip)
            vuelo.consumo_estimado = consumo
    
    
class Paquete(models.Model):
    _name = "dronify.paquete"
    _description = "Modelo para gestionar paquetes"
    
    codigo = fields.Char(string="Código", readonly=True) #autogenerado
    name = fields.Char(string="Nombre", required=True)
    peso = fields.Float(string="Peso", required=True)
    cliente_id = fields.Many2one('res.partner', string="Cliente", required=True)
    vuelo_id = fields.Many2one('dronify.vuelo', string="Vuelo", readonly=True)
    dron_relacionado = fields.Char(string="Nombre del dron relacionado", related='vuelo_id.dron_id.name', readonly=True) #computado
    
    #constraint para comprobar que el contacto es cliente -- preguntar si SOLO tiene que ser cliente o pilotos tambien pueden
    @api.constrains('cliente_id', 'cliente_id.es_cliente')
    def _validar_cliente_id(self):
        for paquete in self:
            if paquete.cliente_id and not paquete.cliente_id.es_cliente:
                raise ValidationError(
                    f"Error: El cliente {paquete.cliente_id.name} debe tener un registro como cliente."
                )
    #constraint para controlar que el peso del paquete sea un numero positivo
    @api.constrains('peso')
    def _validar_peso(self):
        for paquete in self:
            if paquete.peso <= 0:
                raise ValidationError(
                    f"Error: El paquete con código {paquete.codigo} no tiene un peso válido."
                )
                
class Zona(models.Model):
    _name = "dronify.zona"
    _description = "Modelo para gestionar zonas"
    
    name = fields.Char(string="Nombre", required=True)
    distancia_km = fields.Float(string="Distancia(km)", default=1.0)
    nivel_riesgo = fields.Selection([('1', 'Muy bajo'), ('2', 'Bajo'), ('3', 'Medio'), ('4', 'Alto'), ('5', 'Muy alto')], required=True)
    tarifa_base = fields.Float(string="Tarifa base")
    vuelo_ids = fields.One2many('dronify.vuelo', 'zona_id', string='Vuelos')
    
    #constraint para comprobar que la distancia es un numero valido
    @api.constrains('distancia_km')
    def _validar_distancia_positiva(self):
        for zona in self:
            if zona.distancia_km <= 0:
                 raise ValidationError(
                    f"Error: La distancia debe ser un número positivo."
                )