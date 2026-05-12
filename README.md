# Modelo de Datos - Dronify

## Diagrama ER

```mermaid
erDiagram
    CLIENTE }o--o{ DRON : "piloto_autorizado_ids / dron_autorizado_ids"
    
    CLIENTE ||--o{ PAQUETE : "cliente_id"
    PAQUETE }o--|| VUELO : "vuelo_id"
    
    DRON ||--o{ VUELO : "dron_id"
    CLIENTE ||--o{ VUELO : "piloto_id"
    
    ZONA ||--o{ VUELO : "zona_id"
    
    VUELO ||--o{ PAQUETE : "paquetes_ids"

    CLIENTE {
        int id PK
        string name
        boolean es_cliente "True"
        boolean es_vip
        boolean es_piloto
        string licencia "obligatorio si es_piloto=True"
    }
    
    DRON {
        int id PK
        string name
        float capacidad_max "obligatorio"
        int bateria "default: 100, 0-100%"
        string estado "disponible/vuelo/taller"
    }
    
    PAQUETE {
        int id PK
        string codigo "autogenerado, readonly"
        string name "obligatorio"
        float peso "obligatorio"
        int cliente_id FK "obligatorio, es_cliente=True"
        int vuelo_id FK "readonly"
        string dron_relacionado "related, readonly"
    }
    
    VUELO {
        int id PK
        string codigo "autogenerado, readonly"
        string name "default: YYYYMMDD_Vuelo, obligatorio"
        int dron_id FK "obligatorio"
        int piloto_id FK "obligatorio, solo pilotos"
        int zona_id FK "obligatorio"
        boolean preparado
        boolean realizado
        float peso_total "computado"
        float consumo_estimado "computado"
    }
    
    ZONA {
        int id PK
        string name "obligatorio"
        float distancia_km "default: 1.0"
        int nivel_riesgo "1-5, obligatorio"
        float tarifa_base
    }
```

## Viernes 08/05 - Clase

+ Modificado el manifest para incluir información relevante, y application=True
+ Añadidos los modelos básicos + relaciones entre tablas. Faltarían comprobaciones y campos calculados.

### Viernes 08/05 - Casa

+ Modelos listos, con relaciones y constrains implementadas.

## Sábado 09/05

+ Vistas básicas (Cliente, piloto, zona) + Campos calculados y métodos para hacer comprobaciones (números válidos en pesos, km, etc)

## Domingo 10/05

+ Vistas básicas al 60%. Dron, Vuelos (sólo la lista, action y botón en menú)
+ Compila y se puede visualizar.

+ Faltan: actions para los botones del header de Vuelo, crear formulario para Vuelo

+ Faltan: perfeccionar las vistas para que muestren datos o los oculten según las condiciones.

## Martes 12/05

+ Dominios actualizados
+ Creación de códigos + nombre compute hechos
+ Datos de prueba creados (IA)