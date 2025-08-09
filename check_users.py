from app import app, db, User

def check_users():
    with app.app_context():
        users = User.query.all()
        print("Usuarios en la base de datos:")
        print("-" * 50)
        
        for user in users:
            print(f"ID: {user.id}")
            print(f"Username: {user.username}")
            print(f"Name: {user.name}")
            print(f"Role: {user.role}")
            print(f"Store Type: {user.store_type}")
            print(f"Is Blocked: {user.is_blocked}")
            print(f"Password Hash: {user.password_hash[:50]}...")
            
            # Verificar contraseña
            test_passwords = {
                'superadmin': 'admin123',
                'tienda_ropa': 'ropa123',
                'tienda_muebles': 'muebles123',
                'agencia_cerveza': 'cerveza123'
            }
            
            if user.username in test_passwords:
                password_correct = user.check_password(test_passwords[user.username])
                print(f"Password Check: {'✓ CORRECTO' if password_correct else '✗ INCORRECTO'}")
            
            print("-" * 50)

if __name__ == '__main__':
    check_users()
