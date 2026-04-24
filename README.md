# Modelo de Datos - Dronify

## Diagrama ER

```mermaid
erDiagram
    PILOTO }o--o{ DRON : "piloto_autorizado_ids / dron_autorizado_ids"
    
    CLIENTE ||--o{ PAQUETE : "cliente_id"
    PAQUETE }o--|| VUELO : "vuelo_id"
    
    DRON ||--o{ VUELO : "dron_id"
    PILOTO ||--o{ VUELO : "piloto_id"
    
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
    
    PILOTO {
        int id PK
        string name
        boolean es_cliente
        boolean es_vip
        boolean es_piloto "True"
        string licencia "obligatorio"
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
