from flask import Flask, render_template, redirect, url_for, request, flash
from models import db, User, Product, Transaction, Unit
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tajny-klucz-do-zmiany-w-produkcji'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///magazyn.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Nieprawidłowa nazwa użytkownika lub hasło.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    products = Product.query.all()
    units = Unit.query.all()
    return render_template('dashboard.html', products=products, units=units)

@app.route('/add_unit', methods=['POST'])
@login_required
def add_unit():
    # Allow all logged in users to add units
    name = request.form.get('name')
    if name:
        if Unit.query.filter_by(name=name).first():
            flash('Taka jednostka już istnieje.', 'warning')
        else:
            db.session.add(Unit(name=name))
            db.session.commit()
            flash('Dodano jednostkę.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/add_product', methods=['POST'])
@login_required
def add_product():
    # Allow all logged in users to add products
    name = request.form.get('name').strip().upper() # FORCE UPPERCASE
    unit_id = request.form.get('unit_id')
    min_level = request.form.get('min_level', 5)
    
    if Product.query.filter_by(name=name).first():
        flash(f'Produkt "{name}" już istnieje!', 'danger')
        return redirect(url_for('dashboard'))

    new_product = Product(name=name, unit_id=unit_id, min_level=min_level)
    db.session.add(new_product)
    db.session.commit()
    flash(f'Dodano nowy produkt: {name}', 'success')
    return redirect(url_for('dashboard'))

@app.route('/transaction', methods=['POST'])
@login_required
def transaction():
    product_id = request.form.get('product_id')
    amount = int(request.form.get('amount'))
    action = request.form.get('action') # 'take' or 'restock'
    
    product = Product.query.get(product_id)
    if not product:
        flash('Produkt nie istnieje.', 'danger')
        return redirect(url_for('dashboard'))
    
    final_amount = 0
    if action == 'take':
        if product.quantity < amount:
            flash('Niewystarczająca ilość na stanie!', 'danger')
            return redirect(url_for('dashboard'))
        final_amount = -amount
        product.quantity -= amount
    elif action == 'restock':
        # Allow all users to restock
        final_amount = amount
        product.quantity += amount
        
    new_trans = Transaction(
        user_id=current_user.id, 
        product_id=product.id, 
        product_name=product.name, 
        change_amount=final_amount,
        type=action # 'take' or 'restock'
    )
    db.session.add(new_trans)
    db.session.commit()
    
    flash('Transakcja zakończona pomyślnie.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/history')
@login_required
def history():
    transactions = Transaction.query.order_by(Transaction.timestamp.desc()).all()
    return render_template('history.html', transactions=transactions)

# --- USER MANAGEMENT (ADMIN ONLY) ---

@app.route('/users')
@login_required
def users():
    if current_user.role != 'admin':
        flash('Brak uprawnień.', 'danger')
        return redirect(url_for('dashboard'))
    all_users = User.query.all()
    return render_template('users.html', users=all_users)

@app.route('/add_user', methods=['POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        flash('Brak uprawnień.', 'danger')
        return redirect(url_for('dashboard'))
    
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')
    
    if User.query.filter_by(username=username).first():
        flash('Użytkownik już istnieje.', 'danger')
        return redirect(url_for('users'))
        
    new_user = User(username=username, password_hash=generate_password_hash(password), role=role)
    db.session.add(new_user)
    db.session.commit()
    flash(f'Dodano użytkownika {username}.', 'success')
    return redirect(url_for('users'))

@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    if current_user.role != 'admin':
        flash('Brak uprawnień.', 'danger')
        return redirect(url_for('dashboard'))
    
    user_id = request.form.get('user_id')
    new_password = request.form.get('new_password')
    
    user = User.query.get(int(user_id))
    if user:
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        flash(f'Hasło dla użytkownika {user.username} zostało zmienione.', 'success')
    else:
        flash('Nie znaleziono użytkownika.', 'danger')
        
    return redirect(url_for('users'))

@app.route('/delete_product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Log deletion transaction
    new_trans = Transaction(
        user_id=current_user.id,
        product_id=product.id,
        product_name=product.name,
        change_amount=-product.quantity,
        type='delete'
    )
    db.session.add(new_trans)
    
    db.session.delete(product)
    db.session.commit()
    
    flash(f'Produkt {product.name} został usunięty (wraz z historią).', 'success')
    return redirect(url_for('dashboard'))

def init_db():
    with app.app_context():
        db.create_all()
        
        # Create default units
        if not Unit.query.first():
            db.session.add(Unit(name='szt'))
            db.session.add(Unit(name='kg'))
            db.session.add(Unit(name='litr'))
            db.session.add(Unit(name='m'))
            db.session.add(Unit(name='opak'))
            db.session.commit()
            print("Utworzono domyślne jednostki.")

        # Create default admin if not exists
        if not User.query.filter_by(username='admin').first():
            from werkzeug.security import generate_password_hash
            admin = User(username='admin', password_hash=generate_password_hash('admin123'), role='admin')
            db.session.add(admin)
            db.session.commit()
            print("Utworzono domyślnego użytkownika: admin / admin123")
            
            # Create demo user
            user = User(username='pracownik', password_hash=generate_password_hash('user123'), role='user')
            db.session.add(user)
            db.session.commit()
            print("Utworzono domyślnego pracownika: pracownik / user123")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0')
