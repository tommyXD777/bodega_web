import os

def create_env_file():
    """Crea un archivo .env con la configuración correcta"""
    
    print("=== CONFIGURADOR DE BASE DE DATOS ===")
    print()
    
    # Solicitar datos al usuario
    print("Ingresa los datos de tu base de datos:")
    db_host = input("Host (ej: isladigital.xyz): ").strip()
    db_port = input("Puerto (ej: 3311): ").strip()
    db_user = input("Usuario (ej: nelson): ").strip()
    db_password = input("Contraseña: ").strip()
    db_name = input("Nombre de la base de datos (ej: bd_nelson): ").strip()
    
    # Crear contenido del archivo .env
    env_content = f"""# Configuración de Base de Datos
DB_HOST={db_host}
DB_PORT={db_port}
DB_USER={db_user}
DB_PASSWORD={db_password}
DB_NAME={db_name}

# URL completa de la base de datos
DATABASE_URL=mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}

# Clave secreta de la aplicación
SECRET_KEY=tienda-contabilidad-2024-super-secret-key-change-in-production
"""
    
    # Escribir archivo .env
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print()
    print("✅ Archivo .env creado exitosamente!")
    print("📁 Ubicación: .env")
    print()
    print("🔄 Reinicia tu aplicación para que los cambios tomen efecto.")

if __name__ == "__main__":
    create_env_file()
