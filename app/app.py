from flask import Flask, Blueprint, request, jsonify
from flask_cors import CORS
from flask_session import Session
from .factory import create_app, db
from .routes.recommendations import recommendations_bp
from .routes.auth import auth_bp
from .routes.archivos import archivos_bp
from .routes.recetas import recetas_bp
import os
from app.models.usuario import Usuario
from app.factory import bcrypt

# Crear la aplicación usando el factory pattern
app = create_app()

# Configurar CORS
frontend_url = os.getenv('FRONTEND_URL', 'https://frontnutr.vercel.app/')
CORS(app, resources={r"/*": {"origins": frontend_url}})  # Permitir todas las rutas desde el frontend
CORS(app, resources={r"/archivos/*": {"origins": frontend_url, "methods": ["GET", "POST", "OPTIONS"]}})

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(recommendations_bp, url_prefix='/recommendations')
app.register_blueprint(archivos_bp, url_prefix='/archivos')
app.register_blueprint(recetas_bp, url_prefix='/recetas')

Session(app)

# Crear tablas si no existen y crear usuario admin por defecto
with app.app_context():
    db.create_all()
    # Crear usuario admin por defecto si no existe
    admin_email = 'admin@admin.com'
    admin = Usuario.query.filter_by(email=admin_email).first()
    if not admin:
        admin = Usuario(
            nombre='Administrador',
            email=admin_email,
            password=bcrypt.generate_password_hash('admin123').decode('utf-8'),
            tipo='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print('Usuario administrador creado: admin@admin.com / admin123')

@app.after_request
def add_cors_headers(response):
    if 'Origin' in request.headers:
        response.headers['Access-Control-Allow-Origin'] = request.headers['Origin']
        response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS,PUT,DELETE'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

@app.route('/auth/api/users/<int:user_id>', methods=['OPTIONS'])
def handle_options(user_id):
    response = jsonify({'status': 'ok'})
    response.headers['Access-Control-Allow-Origin'] = frontend_url
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS,PUT,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Recurso no encontrado',
        'status': 404
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Error interno del servidor',
        'status': 500
    }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
