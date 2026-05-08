from odoo import models, fields, api
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
    
class Dron(models.Model):
    _name = "dronify.dron"
    _description = "Modelo para gestionar los drones de Dronify"
    
    name = fields.Char(string="Nombre")
    capacidad_max = fields.Float(string="Capacidad de Carga máxima(kg)", required=True)
    bateria = fields.Integer(string="Batería disponible (%)", default=100)
    estado = fields.Selection([('disponible', 'Disponible'), ('taller', 'En Mantenimiento'), ('en_vuelo', 'En Vuelo')], string="Estado", default='disponible')
    piloto_autorizado_ids = fields.Many2many('res.partner', 'rel_partner_dron', 'dron_id', 'partner_id', string="Pilotos autorizados")
    vuelo_ids = fields.One2many('dronify.vuelo', 'dron_id', string='Vuelos')
    
class Vuelo(models.Model):
    _name = "dronify.vuelo"
    _description = "Modelo para gestionar vuelos"
    
    codigo = fields.Char(string="Código", readonly=True)
    name = fields.Char(string="Nombre", required=True) #tiene default
    preparado = fields.Boolean(string="Preparado")
    realizado = fields.Boolean(string="Realizado")
    peso_total = fields.Float(string="Peso total") #computado
    consumo_estimado = fields.Float(string="Consumo estimado") #computado
    dron_id = fields.Many2one('dronify.dron',string= "Dron asignado", required=True)
    piloto_id= fields.Many2one('res.partner', string="Piloto responsable", required=True) #required solo pilotos
    paquetes_ids = fields.One2many('dronify.paquete', 'vuelo_id', string="Paquetes")
    zona_id = fields.Many2one('dronify.zona', string="Zona asignada", required=True)
    
class Paquete(models.Model):
    _name = "dronify.paquete"
    _description = "Modelo para gestionar paquetes"
    
    codigo = fields.Char(string="Código", readonly=True) #autogenerado
    name = fields.Char(string="Nombre", required=True)
    peso = fields.Float(string="Peso", required=True)
    cliente_id = fields.Many2one('res.partner', string="Cliente", required=True)
    vuelo_id = fields.Many2one('dronify.vuelo', string="Vuelo", readonly=True)
    dron_relacionado = fields.Char(string="Nombre del dron relacionado", related='vuelo_id.dron_id.name', readonly=True) #computado
    
class Zona(models.Model):
    _name = "dronify.zona"
    _description = "Modelo para gestionar zonas"
    
    name = fields.Char(string="Nombre", required=True)
    distancia_km = fields.Float(string="Distancia(km)", default=1.0)
    nivel_riesgo = fields.Selection([('1', 'Muy bajo'), ('2', 'Bajo'), ('3', 'Medio'), ('4', 'Alto'), ('5', 'Muy alto')], required=True)
    tarifa_base = fields.Float(string="Tarifa base")
    vuelo_ids = fields.One2many('dronify.vuelo', 'zona_id', string='Vuelos')