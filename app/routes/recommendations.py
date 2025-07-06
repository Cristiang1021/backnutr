from flask import Blueprint, request, jsonify
from sqlalchemy import create_engine, text
import pandas as pd
import joblib
import numpy as np

# Crear el blueprint
recommendations_bp = Blueprint('recommendations', __name__)

MODEL_PATH = r'C:\Users\Jhon\Documents\8vo\Aplicaciones\proyecto\programa\project-root\backend\app\models\svm_recipes_optimized_fast.joblib'
DB_URL = 'postgresql://recetas_normalized_user:LGs0KhjIVSgGTYvx3aez1I37YjT9LkNa@dpg-d1ldpd15pdvs73bsasqg-a.ohio-postgres.render.com/recetas_normalized'

try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    print(f"Error al cargar el modelo: {e}")
    model = None

# Crear el engine solo una vez
global_engine = create_engine(DB_URL)

# Función utilitaria para convertir todo a tipos nativos de Python
def to_native(obj):
    if isinstance(obj, dict):
        return {k: to_native(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_native(v) for v in obj]
    elif isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    else:
        return obj

@recommendations_bp.route('/recommendations', methods=['POST'])
def get_recommendations():
    try:
        data = request.get_json()

        # Validar datos de entrada
        required_fields = ['edad', 'peso', 'altura', 'restricciones', 'preferencia', 'dias']
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        if missing_fields:
            return jsonify({"error": f"Faltan campos obligatorios: {', '.join(missing_fields)}."}), 400

        edad = data['edad']
        peso = data['peso']
        altura = data['altura']
        restricciones = data['restricciones']
        preferencia = data['preferencia']
        dias = data['dias']

        # Validaciones
        if not (isinstance(edad, int) and 0 < edad < 120):
            return jsonify({"error": "La edad debe ser un número entero entre 1 y 120."}), 400
        if not (isinstance(peso, (int, float)) and 0 < peso < 300):
            return jsonify({"error": "El peso debe ser un número entre 1 y 300."}), 400
        if not (isinstance(altura, (int, float)) and 0 < altura < 250):
            return jsonify({"error": "La altura debe ser un número entre 1 y 250."}), 400
        if not (isinstance(restricciones, list) and all(isinstance(r, str) for r in restricciones)):
            return jsonify({"error": "Las restricciones deben ser una lista de cadenas de texto."}), 400
        # Permitir 'salado', 'dulce', 'ambas' o lista con ambos
        preferencia_valida = False
        if isinstance(preferencia, str):
            if preferencia.lower() in ['salado', 'dulce', 'ambas']:
                preferencia_valida = True
        elif isinstance(preferencia, list):
            lower_prefs = [p.lower() for p in preferencia]
            if all(p in ['salado', 'dulce'] for p in lower_prefs):
                preferencia_valida = True
        if not preferencia_valida:
            return jsonify({"error": "La preferencia debe ser 'salado', 'dulce', 'ambas' o una lista con ambos."}), 400
        if not (isinstance(dias, int) and 1 <= dias <= 30):
            return jsonify({"error": "Los días deben ser un número entero entre 1 y 30."}), 400

        if model is None:
            return jsonify({"error": "El modelo de recomendación no está disponible."}), 500

        # Preparar restricción para consulta
        restric = 'ninguna' if 'ninguna' in [r.lower() for r in restricciones] else ','.join(restricciones)
        # Determinar flags de preferencia
        if isinstance(preferencia, str):
            if preferencia.lower() == 'ambas':
                pref_dulce = 1
                pref_salado = 1
                pref = None  # No filtrar por preferencia en SQL
            elif preferencia.lower() == 'dulce':
                pref_dulce = 1
                pref_salado = 0
                pref = 'dulce'
            else:
                pref_dulce = 0
                pref_salado = 1
                pref = 'salado'
        elif isinstance(preferencia, list):
            lower_prefs = [p.lower() for p in preferencia]
            pref_dulce = 1 if 'dulce' in lower_prefs else 0
            pref_salado = 1 if 'salado' in lower_prefs else 0
            if pref_dulce and pref_salado:
                pref = None  # No filtrar por preferencia en SQL
            elif pref_dulce:
                pref = 'dulce'
            else:
                pref = 'salado'

        # Construir el filtro de restricciones para SQL
        if restric == 'ninguna' or (isinstance(restricciones, list) and len(restricciones) == 1):
            restric_sql = f"rd.nombre_restriccion ILIKE '%{restric}%'"
        else:
            restric_sql = ' OR '.join([f"rd.nombre_restriccion ILIKE '%{r.lower()}%'" for r in restricciones])

        days_recommendations = {}
        meals = ["Desayuno", "Almuerzo", "Merienda"]
        used_recipes = {meal: set() for meal in meals}
        total_calories = 0

        try:
            for day in range(1, dias + 1):
                daily_plan = {}
                for meal in meals:
                    # Calcular IMC
                    imc = peso / ((altura / 100) ** 2)
                    restricciones_lower = [r.lower() for r in restricciones]
                    # Preparar entrada para el modelo SOLO con las columnas que espera el pipeline
                    sample_input = {
                        "Edad": edad,
                        "IMC": imc,
                        "Tiempo_Preparacion_Num": 30,  # Valor por defecto o puedes ajustar
                        "Preferencia_Dulce": pref_dulce,
                        "Preferencia_Salado": pref_salado,
                        "Restriccion_Keto": 1 if 'keto' in restricciones_lower else 0,
                        "Restriccion_Vegetariano": 1 if 'vegetariano' in restricciones_lower else 0,
                        "Tipo de Comida": meal
                    }
                    sample_df = pd.DataFrame([sample_input])
                    predicted_label = model.predict(sample_df)[0]

                    # Consulta SQL para obtener recetas con la etiqueta predicha
                    query = (
                        "SELECT r.titulo_platillo AS dish_title, "
                        "r.ingredientes AS recipe_ingredients, "
                        "r.preparacion AS recipe, "
                        "r.calorias AS calories, "
                        "r.tiempo_preparacion AS prep_time, "
                        "rd.nombre_restriccion AS diet_restriction, "
                        "p.nombre_preferencia AS preference, "
                        "tc.nombre_tipo_comida AS meal_type, "
                        "rec.etiqueta AS etiqueta "
                        "FROM recetas r "
                        "JOIN recomendaciones rec ON rec.id_receta = r.id_receta "
                        "JOIN restricciones_dieteticas rd ON r.id_restriccion = rd.id_restriccion "
                        "JOIN preferencias p ON r.id_preferencia = p.id_preferencia "
                        "JOIN tipos_comida tc ON r.id_tipo_comida = tc.id_tipo_comida "
                        f"WHERE ({restric_sql}) "
                        f"AND tc.nombre_tipo_comida = '{meal}' "
                        f"AND rec.etiqueta = '{predicted_label}'"
                    )
                    
                    # Agregar filtro de preferencia si es necesario
                    if pref is not None:
                        query += f" AND p.nombre_preferencia ILIKE '%{pref}%'"
                    
                    with global_engine.connect() as connection:
                        result = connection.execute(text(query))
                        recetas_df = pd.DataFrame(result.fetchall(), columns=result.keys())
                    
                    # Log para depuración
                    print(f"Día {day}, {meal}: {len(recetas_df)} recetas encontradas, etiqueta: {predicted_label}")
                    
                    # Si no hay recetas en absoluto para ese meal, retorna error claro
                    if recetas_df.empty:
                        return jsonify({"error": f"No hay recetas disponibles para {meal} con los filtros seleccionados."}), 404
                    recetas_filtradas = recetas_df[~recetas_df['dish_title'].isin(used_recipes[meal])]
                    if recetas_filtradas.empty:
                        # Si ya se usaron todas las recetas únicas para ese meal en el día, permite repetir solo dentro del mismo día
                        selected = recetas_df.sample(1).iloc[0]
                    else:
                        selected = recetas_filtradas.sample(1).iloc[0]
                    used_recipes[meal].add(selected['dish_title'])
                    total_calories += selected['calories'] if not pd.isnull(selected['calories']) else 0
                    # Convertir todos los valores numpy a tipos nativos de Python
                    selected = {k: (v.item() if isinstance(v, (np.integer, np.floating)) else v) for k, v in selected.items()}
                    daily_plan[meal] = {
                        "Nombre del Plato": selected['dish_title'],
                        "Ingredientes": selected['recipe_ingredients'],
                        "Restricciones": selected['diet_restriction'],
                        "Calorías": selected['calories'],
                        "Tiempo de Preparación": selected['prep_time'],
                        "Procedimiento": selected['recipe']
                    }
                days_recommendations[f"Día {day}"] = daily_plan
        except Exception as e:
            return jsonify({"error": f"Error al obtener recetas de la base de datos: {e}"}), 500

        avg_calories_per_day = total_calories / dias if dias else 0
        response = {
            "plan": days_recommendations,
            "resumen_nutricional": {
                "total_calorias": total_calories,
                "promedio_diario": round(avg_calories_per_day, 2)
            }
        }
        response = to_native(response)
        
        # Log para depuración
        print(f"Respuesta generada: {len(days_recommendations)} días, {total_calories} calorías totales")
        
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

