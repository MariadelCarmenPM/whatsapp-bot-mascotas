import sqlite3
from datetime import datetime
from src.logger_config import get_logger

logger = get_logger(__name__)

DB_NAME = "ventas_argos.db"

def init_db():
    """Crea la tabla de ventas si no existe."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                cliente TEXT,
                producto TEXT,
                peso TEXT,
                precio REAL,
                metodo_pago TEXT,
                direccion TEXT
            )
        ''')
        conn.commit()
        conn.close()
        logger.info("💾 Base de datos lista.")
    except Exception as e:
        logger.error(f"Error DB: {e}")

def registrar_venta(datos):
    """Guarda la venta en la base de datos."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute('''
            INSERT INTO ventas (fecha, cliente, producto, peso, precio, metodo_pago, direccion)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            fecha_actual,
            datos.get('nombre', 'Anónimo'),
            f"{datos.get('marca', '')} {datos.get('tipo', '')}",
            datos.get('peso', ''),
            datos.get('precio', 0.0),
            datos.get('metodo_pago', ''),
            datos.get('direccion', '')
        ))
        
        conn.commit()
        conn.close()
        logger.info(f"💰 ¡Venta guardada en SQL!: S/ {datos.get('precio')}")
        return True
    except Exception as e:
        logger.error(f"Error al guardar venta: {e}")
        return False