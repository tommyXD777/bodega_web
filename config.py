import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'tienda-contabilidad-2024-super-secret-key-change-in-production'
    
    DB_USER = os.environ.get('DB_USER') or 'nelson'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or '3011551141.Arias'
    DB_HOST = os.environ.get('DB_HOST') or 'admin.isladigital.xyz'
    DB_PORT = os.environ.get('DB_PORT') or '3311'
    DB_NAME = os.environ.get('DB_NAME') or 'bd_nelson'
    
    
    SQLALCHEMY_DATABASE_URI = (
        f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    )
    print(SQLALCHEMY_DATABASE_URI, flush=True)
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    ITEMS_PER_PAGE = 20
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
