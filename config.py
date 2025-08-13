import os
from dotenv import load_dotenv

# Ruta del .env (ajusta si está en otro directorio)
env_path = os.path.join(os.path.dirname(__file__), '.env')

if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"[INFO] Archivo .env cargado desde: {env_path}")
else:
    print(f"[ADVERTENCIA] No se encontró .env en: {env_path}")

class Config:
    SECRET_KEY = os.environ.get(
        'SECRET_KEY',
        'tienda-contabilidad-2024-super-secret-key-change-in-production'
    )

    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_NAME = os.environ.get('DB_NAME', 'test')
    DB_PORT = os.environ.get('DB_PORT', '3306')

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # Mostrar la URI sin la contraseña real
    print("[INFO] URI de conexión:", SQLALCHEMY_DATABASE_URI.replace(DB_PASSWORD, "******"), flush=True)

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ITEMS_PER_PAGE = 20
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
