from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_session import Session
from flask_cors import CORS
from datetime import timedelta
from flask_jwt_extended import JWTManager
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager() 

def create_app():
    app = Flask(__name__)

    # Configuración de base de datos
    #database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:12345@localhost:5432/recetas_normalized')
    database_url = os.getenv('DATABASE_URL', 'postgresql://recetas_normalized_user:LGs0KhjIVSgGTYvx3aez1I37YjT9LkNa@dpg-d1ldpd15pdvs73bsasqg-a.ohio-postgres.render.com/recetas_normalized')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
    app.config['SESSION_PERMANENT'] = True
    app.secret_key = os.getenv('SECRET_KEY', 'super_secret_key')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'tu_clave_secreta_muy_segura')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    app.config['JWT_ERROR_MESSAGE_KEY'] = 'message'
    app.config['PROPAGATE_EXCEPTIONS'] = True

    # Configurar CORS para producción
    frontend_url = os.getenv('FRONTEND_URL', 'https://frontnutr.vercel.app')
    CORS(app, resources={
        r"/auth/*": {
            "origins": [frontend_url],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "expose_headers": ["Content-Type", "Authorization"]
        }
    })

    db.init_app(app)
    bcrypt.init_app(app)
    Session(app)
    jwt.init_app(app)

    return app
