import os
from dotenv import load_dotenv

# Ruta al .env dentro de la carpeta gigitnore
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = r"C:\Users\CGAO\Desktop\Nelson\bodega_web\gigitnore\.env"


if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"[INFO] Archivo .env cargado desde: {env_path}")
else:
    print(f"[ADVERTENCIA] No se encontró .env en: {env_path}")

class Config:
    # Clave secreta para Flask
    SECRET_KEY = os.getenv(
        'SECRET_KEY',
        'tienda-contabilidad-2024-super-secret-key-change-in-production'
    )

    # Variables de conexión a la base de datos
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_NAME = os.getenv('DB_NAME', 'test')
    DB_PORT = os.getenv('DB_PORT', '3306')

    # Cadena de conexión SQLAlchemy
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # Mostrar la URI sin la contraseña real
    print(
        "[INFO] URI de conexión:",
        SQLALCHEMY_DATABASE_URI.replace(DB_PASSWORD, "******"),
        flush=True
    )

    # Configuraciones adicionales
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ITEMS_PER_PAGE = 20
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
