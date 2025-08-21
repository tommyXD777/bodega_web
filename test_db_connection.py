import pymysql
import os
from dotenv import load_dotenv

# Cargar .env desde la raíz del proyecto
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

# Leer variables del .env
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = int(os.getenv("DB_PORT", 3306))

try:
    print(f"[INFO] Intentando conectar a MySQL en {DB_HOST}:{DB_PORT} con usuario {DB_USER}...")
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    print("✅ Conexión exitosa a la base de datos")
    conn.close()
except Exception as e:
    print("❌ Error al conectar:", e)
