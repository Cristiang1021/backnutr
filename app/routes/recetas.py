from flask import Blueprint, request, jsonify
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

recetas_bp = Blueprint('recetas', __name__)

# Configuración de la conexión a PostgreSQL
DATABASE_URL = 'postgresql://recetas_normalized_user:LGs0KhjIVSgGTYvx3aez1I37YjT9LkNa@dpg-d1ldpd15pdvs73bsasqg-a.ohio-postgres.render.com/recetas_normalized'
engine = create_engine(DATABASE_URL)

# --- CRUD para restricciones_dieteticas ---
@recetas_bp.route('/restricciones', methods=['GET'])
def get_restricciones():
    try:
        with engine.connect() as conn:
            result = conn.execute(text('SELECT * FROM restricciones_dieteticas'))
            restricciones = [dict(row) for row in result.mappings()]
        return jsonify(restricciones), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@recetas_bp.route('/restricciones', methods=['POST'])
def create_restriccion():
    data = request.json
    nombre = data.get('nombre_restriccion')
    try:
        with engine.connect() as conn:
            conn.execute(text('INSERT INTO restricciones_dieteticas (nombre_restriccion) VALUES (:nombre)'), {'nombre': nombre})
        return jsonify({'message': 'Restricción creada'}), 201
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@recetas_bp.route('/restricciones/<int:id>', methods=['PUT'])
def update_restriccion(id):
    data = request.json
    nombre = data.get('nombre_restriccion')
    try:
        with engine.connect() as conn:
            conn.execute(text('UPDATE restricciones_dieteticas SET nombre_restriccion = :nombre WHERE id_restriccion = :id'), {'nombre': nombre, 'id': id})
        return jsonify({'message': 'Restricción actualizada'}), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@recetas_bp.route('/restricciones/<int:id>', methods=['DELETE'])
def delete_restriccion(id):
    try:
        with engine.connect() as conn:
            conn.execute(text('DELETE FROM restricciones_dieteticas WHERE id_restriccion = :id'), {'id': id})
        return jsonify({'message': 'Restricción eliminada'}), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

# --- CRUD para preferencias ---
@recetas_bp.route('/preferencias', methods=['GET'])
def get_preferencias():
    try:
        with engine.connect() as conn:
            result = conn.execute(text('SELECT * FROM preferencias'))
            preferencias = [dict(row) for row in result.mappings()]
        return jsonify(preferencias), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@recetas_bp.route('/preferencias', methods=['POST'])
def create_preferencia():
    data = request.json
    nombre = data.get('nombre_preferencia')
    try:
        with engine.connect() as conn:
            conn.execute(text('INSERT INTO preferencias (nombre_preferencia) VALUES (:nombre)'), {'nombre': nombre})
        return jsonify({'message': 'Preferencia creada'}), 201
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@recetas_bp.route('/preferencias/<int:id>', methods=['PUT'])
def update_preferencia(id):
    data = request.json
    nombre = data.get('nombre_preferencia')
    try:
        with engine.connect() as conn:
            conn.execute(text('UPDATE preferencias SET nombre_preferencia = :nombre WHERE id_preferencia = :id'), {'nombre': nombre, 'id': id})
        return jsonify({'message': 'Preferencia actualizada'}), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@recetas_bp.route('/preferencias/<int:id>', methods=['DELETE'])
def delete_preferencia(id):
    try:
        with engine.connect() as conn:
            conn.execute(text('DELETE FROM preferencias WHERE id_preferencia = :id'), {'id': id})
        return jsonify({'message': 'Preferencia eliminada'}), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

# --- CRUD para tipos_comida ---
@recetas_bp.route('/tipos_comida', methods=['GET'])
def get_tipos_comida():
    try:
        with engine.connect() as conn:
            result = conn.execute(text('SELECT * FROM tipos_comida'))
            tipos = [dict(row) for row in result.mappings()]
        return jsonify(tipos), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@recetas_bp.route('/tipos_comida', methods=['POST'])
def create_tipo_comida():
    data = request.json
    nombre = data.get('nombre_tipo_comida')
    try:
        with engine.connect() as conn:
            conn.execute(text('INSERT INTO tipos_comida (nombre_tipo_comida) VALUES (:nombre)'), {'nombre': nombre})
        return jsonify({'message': 'Tipo de comida creado'}), 201
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@recetas_bp.route('/tipos_comida/<int:id>', methods=['PUT'])
def update_tipo_comida(id):
    data = request.json
    nombre = data.get('nombre_tipo_comida')
    try:
        with engine.connect() as conn:
            conn.execute(text('UPDATE tipos_comida SET nombre_tipo_comida = :nombre WHERE id_tipo_comida = :id'), {'nombre': nombre, 'id': id})
        return jsonify({'message': 'Tipo de comida actualizado'}), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@recetas_bp.route('/tipos_comida/<int:id>', methods=['DELETE'])
def delete_tipo_comida(id):
    try:
        with engine.connect() as conn:
            conn.execute(text('DELETE FROM tipos_comida WHERE id_tipo_comida = :id'), {'id': id})
        return jsonify({'message': 'Tipo de comida eliminado'}), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

# --- CRUD para recetas ---
@recetas_bp.route('/recetas', methods=['GET'])
def get_recetas():
    try:
        with engine.connect() as conn:
            result = conn.execute(text('SELECT * FROM recetas'))
            recetas = [dict(row) for row in result.mappings()]
        return jsonify(recetas), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@recetas_bp.route('/recetas', methods=['POST'])
def create_receta():
    data = request.json
    # Validar tiempo_preparacion
    tiempo_valido = data.get('tiempo_preparacion') in ['>60 minutos', '15-30 minutos', '30-60 minutos']
    if not tiempo_valido:
        return jsonify({'error': "El campo 'tiempo_preparacion' debe ser uno de: '>60 minutos', '15-30 minutos', '30-60 minutos'."}), 400
    print('Datos recibidos para insertar:', data)
    try:
        with engine.begin() as conn:
            conn.execute(text('''INSERT INTO recetas (titulo_platillo, categoria_receta, subcategoria_receta, ingredientes, preparacion, calorias, tiempo_preparacion, id_restriccion, id_preferencia, id_tipo_comida) VALUES (:titulo, :categoria, :subcategoria, :ingredientes, :preparacion, :calorias, :tiempo, :id_restriccion, :id_preferencia, :id_tipo_comida)'''), {
                'titulo': data.get('titulo_platillo'),
                'categoria': data.get('categoria_receta'),
                'subcategoria': data.get('subcategoria_receta'),
                'ingredientes': data.get('ingredientes'),
                'preparacion': data.get('preparacion'),
                'calorias': data.get('calorias'),
                'tiempo': data.get('tiempo_preparacion'),
                'id_restriccion': data.get('id_restriccion'),
                'id_preferencia': data.get('id_preferencia'),
                'id_tipo_comida': data.get('id_tipo_comida')
            })
        return jsonify({'message': 'Receta creada'}), 201
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@recetas_bp.route('/recetas/<int:id>', methods=['PUT'])
def update_receta(id):
    data = request.json
    try:
        with engine.begin() as conn:
            conn.execute(text('''UPDATE recetas SET titulo_platillo=:titulo, categoria_receta=:categoria, subcategoria_receta=:subcategoria, ingredientes=:ingredientes, preparacion=:preparacion, calorias=:calorias, tiempo_preparacion=:tiempo, id_restriccion=:id_restriccion, id_preferencia=:id_preferencia, id_tipo_comida=:id_tipo_comida WHERE id_receta=:id'''), {
                'titulo': data.get('titulo_platillo'),
                'categoria': data.get('categoria_receta'),
                'subcategoria': data.get('subcategoria_receta'),
                'ingredientes': data.get('ingredientes'),
                'preparacion': data.get('preparacion'),
                'calorias': data.get('calorias'),
                'tiempo': data.get('tiempo_preparacion'),
                'id_restriccion': data.get('id_restriccion'),
                'id_preferencia': data.get('id_preferencia'),
                'id_tipo_comida': data.get('id_tipo_comida'),
                'id': id
            })
        return jsonify({'message': 'Receta actualizada'}), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@recetas_bp.route('/recetas/<int:id>', methods=['DELETE'])
def delete_receta(id):
    try:
        with engine.begin() as conn:
            conn.execute(text('DELETE FROM recetas WHERE id_receta = :id'), {'id': id})
        return jsonify({'message': 'Receta eliminada'}), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

# --- CRUD para recomendaciones ---
@recetas_bp.route('/recomendaciones', methods=['GET'])
def get_recomendaciones():
    try:
        with engine.connect() as conn:
            result = conn.execute(text('SELECT * FROM recomendaciones'))
            recomendaciones = [dict(row) for row in result.mappings()]
        return jsonify(recomendaciones), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@recetas_bp.route('/recomendaciones', methods=['POST'])
def create_recomendacion():
    data = request.json
    try:
        with engine.connect() as conn:
            conn.execute(text('''INSERT INTO recomendaciones (id_receta, altura, peso, edad, etiqueta) VALUES (:id_receta, :altura, :peso, :edad, :etiqueta)'''), {
                'id_receta': data.get('id_receta'),
                'altura': data.get('altura'),
                'peso': data.get('peso'),
                'edad': data.get('edad'),
                'etiqueta': data.get('etiqueta')
            })
        return jsonify({'message': 'Recomendación creada'}), 201
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@recetas_bp.route('/recomendaciones/<int:id>', methods=['PUT'])
def update_recomendacion(id):
    data = request.json
    try:
        with engine.connect() as conn:
            conn.execute(text('''UPDATE recomendaciones SET id_receta=:id_receta, altura=:altura, peso=:peso, edad=:edad, etiqueta=:etiqueta WHERE id_recomendacion=:id'''), {
                'id_receta': data.get('id_receta'),
                'altura': data.get('altura'),
                'peso': data.get('peso'),
                'edad': data.get('edad'),
                'etiqueta': data.get('etiqueta'),
                'id': id
            })
        return jsonify({'message': 'Recomendación actualizada'}), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@recetas_bp.route('/recomendaciones/<int:id>', methods=['DELETE'])
def delete_recomendacion(id):
    try:
        with engine.connect() as conn:
            conn.execute(text('DELETE FROM recomendaciones WHERE id_recomendacion = :id'), {'id': id})
        return jsonify({'message': 'Recomendación eliminada'}), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500 