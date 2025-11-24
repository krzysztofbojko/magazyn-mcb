from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


product_owners = db.Table('product_owners',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default='user')  # 'admin' or 'user'

class Unit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False) # Unique enforced
    quantity = db.Column(db.Float, default=0.0)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'), nullable=False)
    min_level = db.Column(db.Integer, default=5)
    
    owners_all = db.Column(db.Boolean, default=False)
    owners = db.relationship('User', secondary=product_owners, backref=db.backref('products_owned', lazy='dynamic'))

    unit = db.relationship('Unit', backref='products')

    def __repr__(self):
        return f'<Product {self.name}>'

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, nullable=True) # Keep ID for reference, but no FK constraint
    product_name = db.Column(db.String(150), nullable=False) # Store name permanently
    change_amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20), default='restock') # 'restock', 'take', 'delete'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('transactions', lazy=True))
