# 🐶 WhatsApp Bot - Sistema de Ventas (ArgosMarket)

Bot automatizado de e-commerce para WhatsApp Web desarrollado en Python. Permite gestionar pedidos completos, validación de pagos, carrito de compras y exportación de reportes a Excel.

## 🚀 Características Principales

- **🤖 Automatización Inteligente:** Uso de `Playwright` para interactuar con WhatsApp Web en tiempo real.
- **🛒 Carrito de Compras:** Soporte para múltiples productos y cantidades en un solo pedido.
- **🧠 Detección con Regex:** Extracción inteligente de cantidades y pesos (Ej: "quiero 2 sacos" -> detecta `2`).
- **🛡️ Validaciones:**
  - Control de stock y marcas desde JSON.
  - Validación estricta de métodos de pago (Yape/Transferencia).
  - Flujo de salida prioritario ("Salir").
- **📊 Reportes:** Exportación de ventas a Excel con formato automático.
- **💾 Persistencia:** Base de datos SQLite local.

## 🛠️ Tecnologías Usadas

- **Python 3.10+**
- **Playwright** (Automatización de navegador)
- **Pandas** & **Openpyxl** (Reportes de datos)
- **SQLite** (Base de datos)

## 📂 Estructura del Proyecto

```text
├── src/
│   ├── pages/            # Page Object Model (POM)
│   ├── bot_logic.py      # Cerebro del bot (Lógica de ventas)
│   ├── config.py         # Configuraciones generales
│   ├── database.py       # Conexión y consultas SQL
│   ├── logger_config.py  # Configuración de logs
│   └── productos.json    # Catálogo de precios y stock
├── exportar_excel.py     # Script para generar reportes Excel
├── main.py               # Punto de entrada (Ejecutable)
├── ventas_argos.db       # Base de datos (Se crea automáticamente)
├── requirements.txt      # Lista de dependencias
└── Dockerfile            # Configuración para Docker
## 🔄 Flujo de Funcionamiento

El bot sigue una máquina de estados finitos para guiar al usuario a través del proceso de compra:

```mermaid
sequenceDiagram
    participant U as Usuario (WhatsApp)
    participant B as Bot (Python + Playwright)
    participant D as Base de Datos (SQLite)

    U->>B: "Hola" / "Menu"
    B-->>U: Muestra Catálogo (Productos.json)
    
    U->>B: Elige Marca (ej: Ricocan)
    B-->>U: Pregunta Tipo (Adulto/Cachorro)
    
    U->>B: Define Tipo
    B-->>U: Muestra Precios y pide Peso
    
    U->>B: Ingresa Peso (ej: 15kg)
    Note over B: Regex valida el número
    B-->>U: Pide Cantidad
    
    U->>B: Ingresa Cantidad (ej: 2)
    B->>B: Calcula Subtotal
    B-->>U: Confirma Carrito y pide Pago
    
    U->>B: "Yape" o "Transferencia"
    B->>D: Registra Venta (SQL INSERT)
    B-->>U: ¡Pedido Confirmado! (Ticket)