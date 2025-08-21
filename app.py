from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
import os
from functools import wraps
import csv
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from config import Config
import pymysql
from dotenv import load_dotenv
app = Flask(__name__)
app.secret_key = Config.SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Config.SQLALCHEMY_TRACK_MODIFICATIONS
load_dotenv()
db = SQLAlchemy(app)

# Crear tablas al iniciar la aplicación
with app.app_context():
    try:
        db.create_all()
        print("Tablas de base de datos creadas/verificadas exitosamente")
    except Exception as e:
        print(f"Error al crear tablas: {e}")

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum('superadmin', 'admin', 'empleado'), nullable=False)
    store_type = db.Column(db.Enum('ropa', 'muebles', 'cerveza'), nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_blocked = db.Column(db.Boolean, default=False)
    
    employees = db.relationship('User', backref=db.backref('parent', remote_side=[id]))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_expired(self):
        if self.role == 'superadmin':
            return False
        
        current_time = datetime.now(timezone.utc)
        created_time = self.created_at
        
        # If created_at is naive (no timezone info), assume it's UTC
        if created_time.tzinfo is None:
            created_time = created_time.replace(tzinfo=timezone.utc)
        
        return current_time - created_time > timedelta(days=30)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price_provider = db.Column(db.Float, nullable=False)
    price_client = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    store_type = db.Column(db.Enum('ropa', 'muebles', 'cerveza'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    owner = db.relationship('User', backref='products')

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    customer_name = db.Column(db.String(100), default='Cliente')
    customer_phone = db.Column(db.String(20), default='')
    payment_type = db.Column(db.String(20), default='cash')
    employee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    product = db.relationship('Product', backref='sales')
    employee = db.relationship('User', backref='sales')

class Credit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    customer_address = db.Column(db.String(200), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    paid_amount = db.Column(db.Float, default=0)
    remaining_amount = db.Column(db.Float, nullable=False)
    installments = db.Column(db.Integer, nullable=False)
    installment_amount = db.Column(db.Float, nullable=False)
    next_payment_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum('active', 'completed', 'overdue'), default='active')
    store_type = db.Column(db.Enum('muebles'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class CreditPayment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    credit_id = db.Column(db.Integer, db.ForeignKey('credit.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    notes = db.Column(db.String(200))
    
    credit = db.relationship('Credit', backref='payments')

def get_redirect_url(user):
    """Determina la URL de redirección basada en el rol del usuario"""
    if user.role == 'superadmin':
        return url_for('superadmin')
    elif user.role == 'admin':
        return url_for('dashboard', store_type=user.store_type)
    elif user.role == 'empleado':
        return url_for('empleado', store_type=user.store_type)
    else:
        return url_for('index')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('index'))
        user = db.session.get(User, session['user_id'])
        if not user:
            session.clear()
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('index'))
            user = db.session.get(User, session['user_id'])
            if not user or user.role not in roles:
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            if request.is_json:
                data = request.get_json()
            else:
                data = {
                    'username': request.form.get('username'),
                    'password': request.form.get('password')
                }
            
            if not data:
                print("No se recibieron datos")
                return jsonify({'error': 'No se recibieron datos'}), 400
            
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                print("Usuario o contraseña vacíos")
                return jsonify({'error': 'Usuario y contraseña son requeridos'}), 400
            
            print(f"Intento de login - Usuario: {username}")
            
            try:
                user = User.query.filter_by(username=username).first()
            except Exception as db_error:
                print(f"Error de base de datos: {str(db_error)}")
                return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
            if not user:
                print(f"Usuario no encontrado: {username}")
                return jsonify({'error': 'Usuario no encontrado'}), 401
            
            print(f"Usuario encontrado: {user.username}, Role: {user.role}")
            
            try:
                password_valid = user.check_password(password)
            except Exception as pwd_error:
                print(f"Error al verificar contraseña: {str(pwd_error)}")
                return jsonify({'error': 'Error al verificar credenciales'}), 500
            
            if not password_valid:
                print(f"Contraseña incorrecta para usuario: {username}")
                return jsonify({'error': 'Contraseña incorrecta'}), 401
            
            try:
                if user.is_expired():
                    user.is_blocked = True
                    db.session.commit()
                    print(f"Cuenta expirada para usuario: {username}")
            except Exception as exp_error:
                print(f"Error al verificar expiración: {str(exp_error)}")
                # Continue with login process even if expiration check fails
            
            if user.is_blocked:
                print(f"Cuenta bloqueada para usuario: {username}")
                return jsonify({'error': 'Usuario bloqueado. Comunícate con el distribuidor para renovar suscripción'}), 401
            
            try:
                session['user_id'] = user.id
                session['user_role'] = user.role
                session['store_type'] = user.store_type
            except Exception as session_error:
                print(f"Error al crear sesión: {str(session_error)}")
                return jsonify({'error': 'Error al iniciar sesión'}), 500
            
            print(f"Login exitoso para usuario: {username}")
            
            return jsonify({
                'success': True,
                'redirect': get_redirect_url(user)
            })
            
        except Exception as e:
            print(f"Error general en login: {str(e)}")
            print(f"Tipo de error: {type(e).__name__}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return jsonify({'error': f'Error específico: {str(e)}'}), 500
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/superadmin')
@role_required('superadmin')
def superadmin():
    return render_template('superadmin.html')

@app.route('/api/users')
@role_required('superadmin')
def get_users():
    users = User.query.filter(User.role != 'superadmin').all()
    users_data = []
    for user in users:
        users_data.append({
            'id': user.id,
            'username': user.username,
            'name': user.name,
            'role': user.role,
            'store_type': user.store_type,
            'created_at': user.created_at.isoformat(),
            'is_blocked': user.is_blocked,
            'is_expired': user.is_expired()
        })
    return jsonify(users_data)

@app.route('/api/users', methods=['POST'])
@role_required('superadmin')
def create_user():
    try:
        data = request.get_json()
        
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'El usuario ya existe'}), 400
        
        user = User(
            username=data['username'],
            name=data['name'],
            role=data['role'],
            store_type=data['store_type']
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Usuario creado exitosamente'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al crear usuario: {str(e)}'}), 500

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@role_required('superadmin')
def update_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        existing_user = User.query.filter(User.username == data['username'], User.id != user_id).first()
        if existing_user:
            return jsonify({'error': 'El nombre de usuario ya existe'}), 400
        
        user.username = data['username']
        user.name = data['name']
        user.role = data['role']
        user.store_type = data['store_type']
        
        if data.get('password'):
            user.set_password(data['password'])
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Usuario actualizado exitosamente'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al actualizar usuario: {str(e)}'}), 500

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@role_required('superadmin')
def delete_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        
        # Verificar que no sea un superadmin
        if user.role == 'superadmin':
            return jsonify({'error': 'No se puede eliminar un superadministrador'}), 400
        
        # Verificar si tiene productos asociados
        if user.products:
            return jsonify({'error': 'No se puede eliminar el usuario porque tiene productos asociados'}), 400
        
        # Verificar si tiene ventas asociadas
        if user.sales:
            return jsonify({'error': 'No se puede eliminar el usuario porque tiene ventas asociadas'}), 400
        
        # Verificar si tiene empleados a cargo
        if user.employees:
            return jsonify({'error': 'No se puede eliminar el usuario porque tiene empleados a cargo'}), 400
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Usuario eliminado exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al eliminar usuario: {str(e)}'}), 500

@app.route('/api/users/<int:user_id>/toggle-block', methods=['POST'])
@role_required('superadmin')
def toggle_user_block(user_id):
    try:
        user = User.query.get_or_404(user_id)
        
        if user.role == 'superadmin':
            return jsonify({'error': 'No se puede bloquear un superadministrador'}), 400
        
        user.is_blocked = not user.is_blocked
        db.session.commit()
        
        status = 'bloqueado' if user.is_blocked else 'desbloqueado'
        return jsonify({
            'success': True, 
            'message': f'Usuario {status} exitosamente',
            'is_blocked': user.is_blocked
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al cambiar estado del usuario: {str(e)}'}), 500

@app.route('/api/employees')
@role_required('admin')
def get_employees():
    try:
        admin_user = User.query.get(session['user_id'])
        employees = User.query.filter_by(role='empleado', parent_id=admin_user.id, store_type=admin_user.store_type).all()
        
        employees_data = []
        for employee in employees:
            employees_data.append({
                'id': employee.id,
                'username': employee.username,
                'name': employee.name,
                'store_type': employee.store_type,
                'created_at': employee.created_at.isoformat(),
                'is_blocked': employee.is_blocked,
                'is_expired': employee.is_expired()
            })
        return jsonify(employees_data)
    
    except Exception as e:
        return jsonify({'error': f'Error al obtener empleados: {str(e)}'}), 500

@app.route('/api/employees', methods=['POST'])
@role_required('admin')
def create_employee():
    try:
        data = request.get_json()
        admin_user = User.query.get(session['user_id'])
        
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'El usuario ya existe'}), 400
        
        employee = User(
            username=data['username'],
            name=data['name'],
            role='empleado',
            store_type=admin_user.store_type,
            parent_id=admin_user.id
        )
        employee.set_password(data['password'])
        
        db.session.add(employee)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Empleado creado exitosamente'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al crear empleado: {str(e)}'}), 500

@app.route('/api/employees/<int:employee_id>', methods=['PUT'])
@role_required('admin')
def update_employee(employee_id):
    try:
        admin_user = User.query.get(session['user_id'])
        employee = User.query.filter_by(id=employee_id, parent_id=admin_user.id).first()
        
        if not employee:
            return jsonify({'error': 'Empleado no encontrado o no tienes permisos'}), 404
        
        data = request.get_json()
        
        # Verificar si el nuevo username ya existe (excluyendo el empleado actual)
        existing_user = User.query.filter(User.username == data['username'], User.id != employee_id).first()
        if existing_user:
            return jsonify({'error': 'El nombre de usuario ya existe'}), 400
        
        employee.username = data['username']
        employee.name = data['name']
        
        if data.get('password'):
            employee.set_password(data['password'])
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Empleado actualizado exitosamente'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al actualizar empleado: {str(e)}'}), 500

@app.route('/api/employees/<int:employee_id>', methods=['DELETE'])
@role_required('admin')
def delete_employee(employee_id):
    try:
        admin_user = User.query.get(session['user_id'])
        employee = User.query.filter_by(id=employee_id, parent_id=admin_user.id).first()
        
        if not employee:
            return jsonify({'error': 'Empleado no encontrado o no tienes permisos'}), 404
        
        # Verificar si tiene ventas asociadas
        if employee.sales:
            return jsonify({'error': 'No se puede eliminar el empleado porque tiene ventas asociadas'}), 400
        
        db.session.delete(employee)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Empleado eliminado exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al eliminar empleado: {str(e)}'}), 500

@app.route('/api/employees/<int:employee_id>/toggle-block', methods=['POST'])
@role_required('admin')
def toggle_employee_block(employee_id):
    try:
        admin_user = User.query.get(session['user_id'])
        employee = User.query.filter_by(id=employee_id, parent_id=admin_user.id).first()
        
        if not employee:
            return jsonify({'error': 'Empleado no encontrado o no tienes permisos'}), 404
        
        employee.is_blocked = not employee.is_blocked
        db.session.commit()
        
        status = 'bloqueado' if employee.is_blocked else 'desbloqueado'
        return jsonify({
            'success': True, 
            'message': f'Empleado {status} exitosamente',
            'is_blocked': employee.is_blocked
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al cambiar estado del empleado: {str(e)}'}), 500

@app.route('/dashboard/<store_type>')
@role_required('admin')
def dashboard(store_type):
    user = User.query.get(session['user_id'])
    if user.store_type != store_type:
        return redirect(url_for('index'))
    return render_template('dashboard.html', store_type=store_type)

@app.route('/api/products/<store_type>')
@login_required
def get_products(store_type):
    try:
        user = User.query.get(session['user_id'])
        
        if user.role == 'empleado' and user.parent_id:
            # Los empleados ven los productos de su administrador
            admin_user = User.query.get(user.parent_id)
            products = Product.query.filter_by(store_type=store_type, user_id=admin_user.id).all()
        else:
            # Los administradores ven sus propios productos
            products = Product.query.filter_by(store_type=store_type, user_id=user.id).all()
        
        products_data = []
        for product in products:
            products_data.append({
                'id': product.id,
                'name': product.name,
                'price_provider': product.price_provider,
                'price_client': product.price_client,
                'stock': product.stock,
                'category': product.category
            })
        return jsonify(products_data)
    
    except Exception as e:
        return jsonify({'error': f'Error al obtener productos: {str(e)}'}), 500

@app.route('/api/products', methods=['POST'])
@role_required('admin')
def create_product():
    try:
        data = request.get_json()
        user = User.query.get(session['user_id'])
        
        if not all(key in data for key in ['name', 'price_provider', 'price_client', 'stock', 'category']):
            return jsonify({'error': 'Faltan campos requeridos'}), 400
        
        product = Product(
            name=data['name'],
            price_provider=float(data['price_provider']),
            price_client=float(data['price_client']),
            stock=int(data['stock']),
            category=data['category'],
            store_type=user.store_type,
            user_id=user.id
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Producto creado exitosamente'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al crear producto: {str(e)}'}), 500

@app.route('/api/sales/<store_type>')
@login_required
def get_sales(store_type):
    try:
        user = User.query.get(session['user_id'])
        
        if user.role == 'admin':
            user_products = Product.query.filter_by(user_id=user.id).all()
            product_ids = [p.id for p in user_products]
            sales = Sale.query.filter(Sale.product_id.in_(product_ids)).all()
        else:
            sales = Sale.query.filter_by(employee_id=user.id).all()
        
        sales_data = []
        for sale in sales:
            sales_data.append({
                'id': sale.id,
                'product_name': sale.product.name,
                'quantity': sale.quantity,
                'total_price': sale.total_price,
                'customer_name': sale.customer_name,
                'employee_name': sale.employee.name,
                'payment_type': sale.payment_type,
                'created_at': sale.created_at.isoformat()
            })
        return jsonify(sales_data)
    
    except Exception as e:
        return jsonify({'error': f'Error al obtener ventas: {str(e)}'}), 500

@app.route('/api/sales', methods=['POST'])
@login_required
def create_sale():
    try:
        data = request.get_json()
        user = db.session.get(User, session['user_id'])
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 400
        
        if user.role == 'empleado' and user.parent_id:
            admin_user = User.query.get(user.parent_id)
            product = Product.query.filter_by(id=data['product_id'], user_id=admin_user.id).first()
        else:
            product = Product.query.filter_by(id=data['product_id'], user_id=user.id).first()
        
        if not product:
            return jsonify({'error': 'Producto no encontrado o no tienes permisos para venderlo'}), 400
        
        if product.stock < data['quantity']:
            return jsonify({'error': 'Stock insuficiente'}), 400
        
        total_price = product.price_client * data['quantity']
        customer_name = data.get('customer_name', 'Cliente')
        customer_phone = data.get('customer_phone', '')
        payment_type = data.get('payment_type', 'cash')
        
        sale = Sale(
            product_id=product.id,
            product_name=product.name,
            quantity=data['quantity'],
            total_price=total_price,
            customer_name=customer_name,
            customer_phone=customer_phone,
            payment_type=payment_type,
            employee_id=user.id
        )
        
        product.stock -= data['quantity']
        
        db.session.add(sale)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Venta registrada exitosamente', 'sale_id': sale.id})
    
    except Exception as e:
        db.session.rollback()
        print(f"Error en create_sale: {str(e)}")
        return jsonify({'error': f'Error: {str(e)}'}), 500

@app.route('/api/credits/<store_type>')
@role_required('admin')
def get_credits(store_type):
    if store_type != 'muebles':
        return jsonify([])
    
    credits = Credit.query.filter_by(store_type=store_type).all()
    credits_data = []
    for credit in credits:
        credits_data.append({
            'id': credit.id,
            'customer_name': credit.customer_name,
            'customer_phone': credit.customer_phone,
            'customer_address': credit.customer_address,
            'product_name': credit.product_name,
            'total_amount': credit.total_amount,
            'paid_amount': credit.paid_amount,
            'remaining_amount': credit.remaining_amount,
            'installment_amount': credit.installment_amount,
            'next_payment_date': credit.next_payment_date.isoformat(),
            'status': credit.status,
            'created_at': credit.created_at.isoformat()
        })
    return jsonify(credits_data)

@app.route('/api/credits/<int:credit_id>/payment', methods=['POST'])
@role_required('admin')
def register_credit_payment(credit_id):
    try:
        data = request.get_json()
        credit = Credit.query.get_or_404(credit_id)
        
        payment_amount = data['amount']
        
        payment = CreditPayment(
            credit_id=credit.id,
            amount=payment_amount,
            notes=data.get('notes', '')
        )
        
        credit.paid_amount += payment_amount
        credit.remaining_amount -= payment_amount
        
        if credit.remaining_amount <= 0:
            credit.status = 'completed'
        else:
            credit.next_payment_date = datetime.now(timezone.utc) + timedelta(days=30)
        
        db.session.add(payment)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Pago registrado exitosamente'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al registrar pago: {str(e)}'}), 500

@app.route('/empleado/<store_type>')
@role_required('empleado')
def empleado(store_type):
    user = User.query.get(session['user_id'])
    if user.store_type != store_type:
        return redirect(url_for('index'))
    return render_template('empleado.html', store_type=store_type)

@app.route('/api/ticket/<int:sale_id>')
@login_required
def generate_ticket(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    p.drawString(100, 750, "TICKET DE VENTA")
    p.drawString(100, 730, "=" * 30)
    p.drawString(100, 710, f"Tienda: {sale.product.owner.store_type.upper()}")
    p.drawString(100, 690, f"Fecha: {sale.created_at.strftime('%d/%m/%Y %H:%M')} UTC")
    p.drawString(100, 670, f"Empleado: {sale.employee.name}")
    p.drawString(100, 650, "")
    p.drawString(100, 630, f"PRODUCTO: {sale.product.name}")
    p.drawString(100, 610, f"Cantidad: {sale.quantity}")
    p.drawString(100, 590, f"Precio Unit: ${sale.product.price_client}")
    p.drawString(100, 570, f"TOTAL: ${sale.total_price}")
    p.drawString(100, 550, "")
    p.drawString(100, 530, f"Cliente: {sale.customer_name}")
    p.drawString(100, 510, f"Teléfono: {sale.customer_phone}")
    p.drawString(100, 490, "")
    p.drawString(100, 470, "¡Gracias por su compra!")
    p.drawString(100, 450, "=" * 30)
    
    p.save()
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'ticket-{sale_id}.pdf',
        mimetype='application/pdf'
    )

@app.route('/api/export-sales/<store_type>')
@role_required('admin')
def export_sales(store_type):
    user = User.query.get(session['user_id'])
    user_products = Product.query.filter_by(user_id=user.id).all()
    product_ids = [p.id for p in user_products]
    sales = Sale.query.filter(Sale.product_id.in_(product_ids)).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Fecha', 'Producto', 'Cantidad', 'Precio Unit.', 'Total', 'Cliente', 'Empleado'])
    
    for sale in sales:
        writer.writerow([
            sale.created_at.strftime('%d/%m/%Y %H:%M UTC'),
            sale.product.name,
            sale.quantity,
            sale.product.price_client,
            sale.total_price,
            sale.customer_name,
            sale.employee.name
        ])
    
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        as_attachment=True,
        download_name=f'ventas-{store_type}-{datetime.now(timezone.utc).strftime("%Y%m%d")}.csv',
        mimetype='text/csv'
    )

@app.route('/add_sale', methods=['POST'])
@login_required
def add_sale():
    try:
        data = request.get_json()
        
        product_id = data['product_id']
        quantity = data['quantity']
        customer_name = data['customer_name']
        customer_phone = data.get('customer_phone', '')
        payment_type = data.get('payment_type', 'cash')
        customer_address = data.get('customer_address', '')
        
        product = Product.query.get(product_id)
        if not product or product.stock < quantity:
            return jsonify({'error': 'Producto no disponible o stock insuficiente'}), 400
        
        total = product.price_client * quantity
        
        sale = Sale(
            product_id=product.id,
            product_name=product.name,
            quantity=quantity,
            total_price=total,
            customer_name=customer_name,
            customer_phone=customer_phone,
            payment_type=payment_type,
            employee_id=session['user_id']
        )
        
        product.stock -= quantity
        
        db.session.add(sale)
        
        if payment_type == 'credit' and session['store_type'] == 'muebles':
            installments = data.get('installments', 6)
            
            if installments < 2:
                installments = 2
            elif installments > 6:
                installments = 6
            
            installment_amount = total / installments
            
            credit = Credit(
                customer_name=customer_name,
                customer_phone=customer_phone,
                customer_address=customer_address,
                product_name=product.name,
                total_amount=total,
                remaining_amount=total,
                installments=installments,
                installment_amount=installment_amount,
                next_payment_date=datetime.now(timezone.utc) + timedelta(days=30),
                store_type='muebles'
            )
            db.session.add(credit)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Venta registrada exitosamente', 'sale_id': sale.id})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/add_credit_payment', methods=['POST'])
@login_required
def add_credit_payment():
    try:
        data = request.get_json()
        
        credit_id = data['credit_id']
        amount = data['amount']
        notes = data.get('notes', '')
        
        credit = Credit.query.get_or_404(credit_id)
        
        payment = CreditPayment(
            credit_id=credit.id,
            amount=amount,
            notes=notes
        )
        
        credit.paid_amount += amount
        credit.remaining_amount -= amount
        
        if credit.remaining_amount <= 0:
            credit.status = 'completed'
        else:
            credit.next_payment_date = datetime.now(timezone.utc) + timedelta(days=30)
        
        db.session.add(payment)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Pago registrado exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
