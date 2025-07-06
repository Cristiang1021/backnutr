from flask import Blueprint, request, jsonify, send_file
from ..factory import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime


from ..models.archivo import Archivo  # Asegúrate de que el modelo Archivo esté definido
from io import BytesIO

archivos_bp = Blueprint('archivos', __name__)

@archivos_bp.route('/archivos', methods=['POST'])
@jwt_required()
def upload_file():
    current_user_id = get_jwt_identity()
    
    if 'file' not in request.files:
        return jsonify({'error': 'No se encontró ningún archivo'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
    
    # Leer contenido del archivo
    file_content = file.read()
    
    # Crear nuevo registro de archivo
    new_file = Archivo(
        usuario_id=current_user_id,
        nombre=file.filename,
        contenido=file_content
    )
    
    db.session.add(new_file)
    db.session.commit()
    
    return jsonify({
        'mensaje': 'Archivo subido exitosamente',
        'fecha_creacion': new_file.fecha_creacion.isoformat()
    }), 200

@archivos_bp.route('/archivos/<int:id>', methods=['GET'])
def obtener_archivo(id):
    archivo = Archivo.query.get(id)
    if archivo:
        return jsonify({
            'id': archivo.id,
            'nombre': archivo.nombre,
            'usuario_id': archivo.usuario_id,
            'fecha_creacion': archivo.fecha_creacion
        }), 200
    return jsonify({'mensaje': 'Archivo no encontrado'}), 404

@archivos_bp.route('/archivos/download/<int:id>', methods=['GET'])
def descargar_archivo(id):
    # Obtener el archivo de la base de datos
    archivo = Archivo.query.get(id)
    
    if archivo:
        # Crear un objeto BytesIO con el contenido binario del archivo
        archivo_bytes = BytesIO(archivo.contenido)
        
        # Enviar el archivo como respuesta
        return send_file(
            archivo_bytes,
            mimetype='application/pdf',  # Tipo MIME para archivos PDF
            as_attachment=True,  # Forzar la descarga
            download_name=archivo.nombre  # Nombre del archivo al descargar
        )
    
    # Si el archivo no existe, devolver un error 404
    return jsonify({'mensaje': 'Archivo no encontrado'}), 404

@archivos_bp.route('/archivos/usuario/<int:usuario_id>', methods=['GET'])
def obtener_archivos_por_usuario(usuario_id):
    archivos = Archivo.query.filter_by(usuario_id=usuario_id).all()  # Obtener todos los archivos del usuario
    if archivos:
        return jsonify([{
            'id': archivo.id,
            'nombre': archivo.nombre,
            'usuario_id': archivo.usuario_id,
            'fecha_creacion': archivo.fecha_creacion
        } for archivo in archivos]), 200  # Devolver la lista de archivos
    return jsonify({'mensaje': 'No se encontraron archivos para este usuario'}), 404