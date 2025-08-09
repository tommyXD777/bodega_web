import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User
from sqlalchemy import text

def test_database_connection():
    """Prueba la conexión a la base de datos y verifica los usuarios"""
    
    print("🔍 Probando conexión a la base de datos...")
    
    try:
        with app.app_context():
            # Probar conexión básica
            result = db.session.execute(text('SELECT 1'))
            print("✅ Conexión a la base de datos exitosa")
            
            # Verificar si las tablas existen
            try:
                user_count = User.query.count()
                print(f"✅ Tabla 'user' encontrada con {user_count} registros")
            except Exception as e:
                print(f"❌ Error accediendo a la tabla 'user': {e}")
                return False
            
            # Verificar usuarios específicos
            test_users = ['superadmin', 'tienda_ropa', 'tienda_muebles', 'agencia_cerveza']
            
            print("\n📋 Verificando usuarios:")
            print("-" * 50)
            
            for username in test_users:
                user = User.query.filter_by(username=username).first()
                if user:
                    print(f"✅ {username}: Encontrado (ID: {user.id}, Role: {user.role})")
                    
                    # Probar contraseñas
                    test_passwords = {
                        'superadmin': 'admin123',
                        'tienda_ropa': 'ropa123',
                        'tienda_muebles': 'muebles123',
                        'agencia_cerveza': 'cerveza123'
                    }
                    
                    if username in test_passwords:
                        password_ok = user.check_password(test_passwords[username])
                        status = "✅ Correcta" if password_ok else "❌ Incorrecta"
                        print(f"   Contraseña: {status}")
                else:
                    print(f"❌ {username}: No encontrado")
            
            print("\n🔧 Información de configuración:")
            print(f"DATABASE_URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'No configurada')}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        print("\n🔧 Posibles soluciones:")
        print("1. Verifica que MySQL esté ejecutándose")
        print("2. Verifica que la base de datos 'tienda_contabilidad' exista")
        print("3. Verifica las credenciales en la configuración")
        print("4. Ejecuta: mysql -u root -p < database.sql")
        return False

if __name__ == '__main__':
    test_database_connection()
