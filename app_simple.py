from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'

# Datos en memoria (simulando base de datos)
users_data = [
    {
        'id': 1,
        'username': 'superadmin',
        'password': 'admin123',
        'name': 'Super Administrador',
        'role': 'superadmin',
        'store_type': None,
        'created_at': datetime.now().isoformat(),
        'is_blocked': False
    },
    {
        'id': 2,
        'username': 'tienda_ropa',
        'password': 'ropa123',
        'name': 'Admin Tienda Ropa',
        'role': 'admin',
        'store_type': 'ropa',
        'created_at': datetime.now().isoformat(),
        'is_blocked': False
    },
    {
        'id': 3,
        'username': 'tienda_muebles',
        'password': 'muebles123',
        'name': 'Admin Tienda Muebles',
        'role': 'admin',
        'store_type': 'muebles',
        'created_at': datetime.now().isoformat(),
        'is_blocked': False
    },
    {
        'id': 4,
        'username': 'agencia_cerveza',
        'password': 'cerveza123',
        'name': 'Admin Agencia Cerveza',
        'role': 'admin',
        'store_type': 'cerveza',
        'created_at': datetime.now().isoformat(),
        'is_blocked': False
    }
]

@app.route('/')
def index():
    if 'user_id' in session:
        user = next((u for u in users_data if u['id'] == session['user_id']), None)
        if user:
            if user['role'] == 'superadmin':
                return redirect(url_for('superadmin'))
            elif user['role'] == 'admin':
                return redirect(url_for('dashboard', store_type=user['store_type']))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No se recibieron datos'}), 400
            
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                return jsonify({'error': 'Usuario y contraseña son requeridos'}), 400
            
            # Buscar usuario
            user = next((u for u in users_data if u['username'] == username), None)
            
            if not user:
                return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401
            
            if user['password'] != password:
                return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401
            
            if user['is_blocked']:
                return jsonify({'error': 'Tu cuenta ha sido bloqueada. Contacta al administrador.'}), 401
            
            session['user_id'] = user['id']
            session['user_role'] = user['role']
            session['store_type'] = user['store_type']
            
            return jsonify({
                'success': True,
                'redirect': get_redirect_url(user)
            })
            
        except Exception as e:
            print(f"Error en login: {str(e)}")
            return jsonify({'error': 'Error interno del servidor'}), 500
    
    return render_template('login.html')

def get_redirect_url(user):
    if user['role'] == 'superadmin':
        return url_for('superadmin')
    elif user['role'] == 'admin':
        return url_for('dashboard', store_type=user['store_type'])
    else:
        return url_for('empleado', store_type=user['store_type'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/superadmin')
def superadmin():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = next((u for u in users_data if u['id'] == session['user_id']), None)
    if not user or user['role'] != 'superadmin':
        return redirect(url_for('login'))
    
    return render_template('superadmin.html')

@app.route('/dashboard/<store_type>')
def dashboard(store_type):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = next((u for u in users_data if u['id'] == session['user_id']), None)
    if not user or user['role'] != 'admin' or user['store_type'] != store_type:
        return redirect(url_for('login'))
    
    return render_template('dashboard-simple.html', store_type=store_type)

@app.route('/api/users')
def get_users():
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    user = next((u for u in users_data if u['id'] == session['user_id']), None)
    if not user or user['role'] != 'superadmin':
        return jsonify({'error': 'No autorizado'}), 401
    
    # Filtrar usuarios (no mostrar superadmin)
    filtered_users = [u for u in users_data if u['role'] != 'superadmin']
    return jsonify(filtered_users)

@app.route('/api/users', methods=['POST'])
def create_user():
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    user = next((u for u in users_data if u['id'] == session['user_id']), None)
    if not user or user['role'] != 'superadmin':
        return jsonify({'error': 'No autorizado'}), 401
    
    data = request.get_json()
    
    # Verificar si el usuario ya existe
    if any(u['username'] == data['username'] for u in users_data):
        return jsonify({'error': 'El usuario ya existe'}), 400
    
    new_user = {
        'id': max(u['id'] for u in users_data) + 1,
        'username': data['username'],
        'password': data['password'],
        'name': data['name'],
        'role': data['role'],
        'store_type': data['store_type'],
        'created_at': datetime.now().isoformat(),
        'is_blocked': False
    }
    
    users_data.append(new_user)
    return jsonify({'success': True, 'message': 'Usuario creado exitosamente'})

@app.route('/api/users/<int:user_id>/toggle-block', methods=['POST'])
def toggle_user_block(user_id):
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    current_user = next((u for u in users_data if u['id'] == session['user_id']), None)
    if not current_user or current_user['role'] != 'superadmin':
        return jsonify({'error': 'No autorizado'}), 401
    
    user = next((u for u in users_data if u['id'] == user_id), None)
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    user['is_blocked'] = not user['is_blocked']
    status = 'bloqueado' if user['is_blocked'] else 'desbloqueado'
    return jsonify({'success': True, 'message': f'Usuario {status} exitosamente'})

if __name__ == '__main__':
    print("🚀 Iniciando servidor de prueba...")
    print("📋 Usuarios disponibles:")
    print("- superadmin / admin123")
    print("- tienda_ropa / ropa123")
    print("- tienda_muebles / muebles123")
    print("- agencia_cerveza / cerveza123")
    print("\n🌐 Servidor ejecutándose en: http://localhost:5000")
    app.run(debug=True)
