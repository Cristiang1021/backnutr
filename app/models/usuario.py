from flask_bcrypt import Bcrypt
from ..factory import db

bcrypt = Bcrypt()

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(20), nullable=False, default='usuario')
    reset_token = db.Column(db.String(255), nullable=True)
    token_expiration = db.Column(db.DateTime, nullable=True)

