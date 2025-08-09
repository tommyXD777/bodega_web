from app import app, db, User

def reset_passwords():
    with app.app_context():
        # Resetear contraseñas de usuarios existentes
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
                print(f"Contraseña actualizada para: {user_data['username']}")
            else:
                print(f"Usuario no encontrado: {user_data['username']}")
        
        try:
            db.session.commit()
            print("Todas las contraseñas han sido actualizadas exitosamente")
        except Exception as e:
            db.session.rollback()
            print(f"Error actualizando contraseñas: {e}")

if __name__ == '__main__':
    reset_passwords()
