import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User

def fix_passwords():
    """Resetea las contraseñas de los usuarios por defecto"""
    
    print("🔧 Reparando contraseñas de usuarios...")
    
    try:
        with app.app_context():
            users_data = [
                {'username': 'superadmin', 'password': 'admin123'},
                {'username': 'tienda_ropa', 'password': 'ropa123'},
                {'username': 'tienda_muebles', 'password': 'muebles123'},
                {'username': 'agencia_cerveza', 'password': 'cerveza123'}
            ]
            
            for user_data in users_data:
                user = User.query.filter_by(username=user_data['username']).first()
                if user:
                    user.set_password(user_data['password'])
                    user.is_blocked = False  # Desbloquear si estaba bloqueado
                    print(f"✅ Contraseña actualizada para: {user_data['username']}")
                else:
                    print(f"❌ Usuario no encontrado: {user_data['username']}")
            
            try:
                db.session.commit()
                print("\n✅ Todas las contraseñas han sido reparadas exitosamente")
                print("\n📋 Credenciales actualizadas:")
                print("- superadmin / admin123")
                print("- tienda_ropa / ropa123")
                print("- tienda_muebles / muebles123")
                print("- agencia_cerveza / cerveza123")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error guardando cambios: {e}")
                
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")

if __name__ == '__main__':
    fix_passwords()
