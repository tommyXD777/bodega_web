from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from functools import wraps
import csv
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'

# Configuración mejorada de base de datos
DATABASE_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # Cambia por tu usuario de MySQL
    'password': '',  # Cambia por tu contraseña de MySQL
    'database': 'tienda_contabilidad'
}

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}/{DATABASE_CONFIG['database']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

db = SQLAlchemy(app)

# Modelos de la base de datos
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum('superadmin', 'admin', 'empleado'), nullable=False)
    store_type = db.Column(db.Enum('ropa', 'muebles', 'cerveza'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_blocked = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_expired(self):
        if self.role == 'superadmin':
            return False
        return datetime.utcnow() - self.created_at > timedelta(days=30)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price_provider = db.Column(db.Float, nullable=False)
    price_client = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    store_type = db.Column(db.Enum('ropa', 'muebles', 'cerveza'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    store_type = db.Column(db.Enum('ropa', 'muebles', 'cerveza'), nullable=False)
    payment_type = db.Column(db.Enum('cash', 'credit'), default='cash')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CreditPayment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    credit_id = db.Column(db.Integer, db.ForeignKey('credit.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.String(200))
    
    credit = db.relationship('Credit', backref='payments')

# Decoradores para autenticación
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            user = User.query.get(session['user_id'])
            if not user or user.role not in roles:
                return jsonify({'error': 'Acceso denegado'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Rutas principales
@app.route('/')
def index():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user.role == 'superadmin':
            return redirect(url_for('superadmin'))
        elif user.role == 'admin':
            return redirect(url_for('dashboard', store_type=user.store_type))
        else:
            return redirect(url_for('empleado', store_type=user.store_type))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                print("No se recibieron datos JSON")
                return jsonify({'error': 'No se recibieron datos'}), 400
            
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                print("Usuario o contraseña vacíos")
                return jsonify({'error': 'Usuario y contraseña son requeridos'}), 400
            
            print(f"Intento de login - Usuario: {username}")
            
            user = User.query.filter_by(username=username).first()
            
            if not user:
                print(f"Usuario no encontrado: {username}")
                return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401
            
            print(f"Usuario encontrado: {user.username}, Role: {user.role}")
            
            if not user.check_password(password):
                print(f"Contraseña incorrecta para usuario: {username}")
                return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401
            
            # Verificar si la cuenta está expirada
            if user.is_expired():
                user.is_blocked = True
                db.session.commit()
                print(f"Cuenta expirada para usuario: {username}")
            
            if user.is_blocked:
                print(f"Cuenta bloqueada para usuario: {username}")
                return jsonify({'error': 'Tu cuenta ha sido bloqueada. Contacta al administrador.'}), 401
            
            session['user_id'] = user.id
            session['user_role'] = user.role
            session['store_type'] = user.store_type
            
            print(f"Login exitoso para usuario: {username}")
            
            return jsonify({
                'success': True,
                'redirect': get_redirect_url(user)
            })
            
        except Exception as e:
            print(f"Error en login: {str(e)}")
            return jsonify({'error': 'Error interno del servidor'}), 500
    
    return render_template('login.html')

def get_redirect_url(user):
    if user.role == 'superadmin':
        return url_for('superadmin')
    elif user.role == 'admin':
        return url_for('dashboard', store_type=user.store_type)
    else:
        return url_for('empleado', store_type=user.store_type)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Rutas del Super Admin
@app.route('/superadmin')
@role_required(['superadmin'])
def superadmin():
    return render_template('superadmin.html')

@app.route('/api/users')
@role_required(['superadmin'])
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
@role_required(['superadmin'])
def create_user():
    data = request.get_json()
    
    # Verificar si el usuario ya existe
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

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@role_required(['superadmin'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    user.username = data['username']
    user.name = data['name']
    user.role = data['role']
    user.store_type = data['store_type']
    
    if data.get('password'):
        user.set_password(data['password'])
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Usuario actualizado exitosamente'})

@app.route('/api/users/<int:user_id>/toggle-block', methods=['POST'])
@role_required(['superadmin'])
def toggle_user_block(user_id):
    user = User.query.get_or_404(user_id)
    user.is_blocked = not user.is_blocked
    db.session.commit()
    
    status = 'bloqueado' if user.is_blocked else 'desbloqueado'
    return jsonify({'success': True, 'message': f'Usuario {status} exitosamente'})

# Rutas del Dashboard Admin
@app.route('/dashboard/<store_type>')
@role_required(['admin'])
def dashboard(store_type):
    user = User.query.get(session['user_id'])
    if user.store_type != store_type:
        return redirect(url_for('index'))
    return render_template('dashboard.html', store_type=store_type)

@app.route('/api/products/<store_type>')
@login_required
def get_products(store_type):
    products = Product.query.filter_by(store_type=store_type).all()
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

@app.route('/api/products', methods=['POST'])
@role_required(['admin'])
def create_product():
    data = request.get_json()
    user = User.query.get(session['user_id'])
    
    product = Product(
        name=data['name'],
        price_provider=data['price_provider'],
        price_client=data['price_client'],
        stock=data['stock'],
        category=data['category'],
        store_type=user.store_type
    )
    
    db.session.add(product)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Producto creado exitosamente'})

@app.route('/api/sales/<store_type>')
@login_required
def get_sales(store_type):
    user = User.query.get(session['user_id'])
    
    if user.role == 'admin':
        sales = Sale.query.filter_by(store_type=store_type).all()
    else:  # empleado
        sales = Sale.query.filter_by(store_type=store_type, employee_id=user.id).all()
    
    sales_data = []
    for sale in sales:
        sales_data.append({
            'id': sale.id,
            'product_name': sale.product_name,
            'quantity': sale.quantity,
            'unit_price': sale.unit_price,
            'total': sale.total,
            'customer_name': sale.customer_name,
            'customer_phone': sale.customer_phone,
            'payment_type': sale.payment_type,
            'created_at': sale.created_at.isoformat(),
            'employee_name': sale.employee.name
        })
    return jsonify(sales_data)

@app.route('/api/sales', methods=['POST'])
@login_required
def create_sale():
    data = request.get_json()
    user = User.query.get(session['user_id'])
    
    product = Product.query.get(data['product_id'])
    if not product or product.stock < data['quantity']:
        return jsonify({'error': 'Producto no disponible o stock insuficiente'}), 400
    
    total = product.price_client * data['quantity']
    
    sale = Sale(
        product_id=product.id,
        product_name=product.name,
        quantity=data['quantity'],
        unit_price=product.price_client,
        total=total,
        customer_name=data['customer_name'],
        customer_phone=data['customer_phone'],
        employee_id=user.id,
        store_type=user.store_type,
        payment_type=data.get('payment_type', 'cash')
    )
    
    # Actualizar stock
    product.stock -= data['quantity']
    
    db.session.add(sale)
    
    # Si es venta a crédito en tienda de muebles, crear registro de crédito
    if data.get('payment_type') == 'credit' and user.store_type == 'muebles':
        installments = data.get('installments', 6)  # Por defecto 6 meses
        
        # Validar que esté entre 2 y 6 meses
        if installments < 2:
            installments = 2
        elif installments > 6:
            installments = 6
        
        installment_amount = total / installments
        
        credit = Credit(
            customer_name=data['customer_name'],
            customer_phone=data['customer_phone'],
            customer_address=data.get('customer_address', ''),
            product_name=product.name,
            total_amount=total,
            remaining_amount=total,
            installments=installments,
            installment_amount=installment_amount,
            next_payment_date=datetime.utcnow() + timedelta(days=30),
            store_type='muebles'
        )
        db.session.add(credit)
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Venta registrada exitosamente', 'sale_id': sale.id})

@app.route('/api/credits/<store_type>')
@role_required(['admin'])
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
@role_required(['admin'])
def register_credit_payment(credit_id):
    data = request.get_json()
    credit = Credit.query.get_or_404(credit_id)
    
    payment_amount = data['amount']
    
    # Crear registro de pago
    payment = CreditPayment(
        credit_id=credit.id,
        amount=payment_amount,
        notes=data.get('notes', '')
    )
    
    # Actualizar crédito
    credit.paid_amount += payment_amount
    credit.remaining_amount -= payment_amount
    
    if credit.remaining_amount <= 0:
        credit.status = 'completed'
    else:
        # Calcular próxima fecha de pago
        credit.next_payment_date = datetime.utcnow() + timedelta(days=30)
    
    db.session.add(payment)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Pago registrado exitosamente'})

# Rutas del Empleado
@app.route('/empleado/<store_type>')
@role_required(['empleado'])
def empleado(store_type):
    user = User.query.get(session['user_id'])
    if user.store_type != store_type:
        return redirect(url_for('index'))
    return render_template('empleado.html', store_type=store_type)

# Rutas de reportes y tickets
@app.route('/api/ticket/<int:sale_id>')
@login_required
def generate_ticket(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    
    # Crear ticket en memoria
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Contenido del ticket
    p.drawString(100, 750, "TICKET DE VENTA")
    p.drawString(100, 730, "=" * 30)
    p.drawString(100, 710, f"Tienda: {sale.store_type.upper()}")
    p.drawString(100, 690, f"Fecha: {sale.created_at.strftime('%d/%m/%Y %H:%M')}")
    p.drawString(100, 670, f"Empleado: {sale.employee.name}")
    p.drawString(100, 650, "")
    p.drawString(100, 630, f"PRODUCTO: {sale.product_name}")
    p.drawString(100, 610, f"Cantidad: {sale.quantity}")
    p.drawString(100, 590, f"Precio Unit: ${sale.unit_price}")
    p.drawString(100, 570, f"TOTAL: ${sale.total}")
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
@role_required(['admin'])
def export_sales(store_type):
    sales = Sale.query.filter_by(store_type=store_type).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Escribir encabezados
    writer.writerow(['Fecha', 'Producto', 'Cantidad', 'Precio Unit.', 'Total', 'Cliente', 'Empleado', 'Tipo Pago'])
    
    # Escribir datos
    for sale in sales:
        writer.writerow([
            sale.created_at.strftime('%d/%m/%Y'),
            sale.product_name,
            sale.quantity,
            sale.unit_price,
            sale.total,
            sale.customer_name,
            sale.employee.name,
            'Contado' if sale.payment_type == 'cash' else 'Crédito'
        ])
    
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        as_attachment=True,
        download_name=f'ventas-{store_type}-{datetime.now().strftime("%Y%m%d")}.csv',
        mimetype='text/csv'
    )

# Inicialización de la base de datos
# Reemplazar @app.before_first_request por @app.before_request
@app.before_request
def create_tables():
    # Solo crear tablas una vez
    if not hasattr(create_tables, 'tables_created'):
        try:
            db.create_all()
            print("Tablas de base de datos creadas/verificadas exitosamente")
            
            # Crear usuario super admin por defecto
            if not User.query.filter_by(username='superadmin').first():
                admin = User(
                    username='superadmin',
                    name='Super Administrador',
                    role='superadmin'
                )
                admin.set_password('admin123')
                db.session.add(admin)
                
                # Crear usuarios de ejemplo
                users_data = [
                    {'username': 'tienda_ropa', 'password': 'ropa123', 'name': 'Admin Tienda Ropa', 'role': 'admin', 'store_type': 'ropa'},
                    {'username': 'tienda_muebles', 'password': 'muebles123', 'name': 'Admin Tienda Muebles', 'role': 'admin', 'store_type': 'muebles'},
                    {'username': 'agencia_cerveza', 'password': 'cerveza123', 'name': 'Admin Agencia Cerveza', 'role': 'admin', 'store_type': 'cerveza'}
                ]
                
                for user_data in users_data:
                    user = User(
                        username=user_data['username'],
                        name=user_data['name'],
                        role=user_data['role'],
                        store_type=user_data['store_type']
                    )
                    user.set_password(user_data['password'])
                    db.session.add(user)
                
                try:
                    db.session.commit()
                    print("Usuarios creados exitosamente")
                except Exception as e:
                    db.session.rollback()
                    print(f"Error creando usuarios: {e}")
            
            create_tables.tables_created = True
            
        except Exception as e:
            print(f"Error conectando a la base de datos: {e}")
            print("Asegúrate de que MySQL esté ejecutándose y la base de datos exista")

if __name__ == '__main__':
    app.run(debug=True)
