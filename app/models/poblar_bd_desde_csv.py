import pandas as pd
from sqlalchemy import create_engine, text
import sys

def poblar_base_de_datos(csv_path, db_connection_str):
    """
    Crea el esquema de la base de datos y la puebla desde un archivo CSV.
    Este script está diseñado para ejecutarse una sola vez.

    Args:
        csv_path (str): Ruta al archivo CSV con los datos de las recetas.
        db_connection_str (str): Cadena de conexión para la base de datos PostgreSQL.
    """
    try:
        engine = create_engine(db_connection_str)
        print("Conexión a la base de datos establecida.")
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")
        return

    # --- 1. Leer y limpiar el archivo CSV ---
    try:
        # Se especifica la codificación 'latin1' que suele funcionar con caracteres problemáticos como 'Ã©'
        df = pd.read_csv(csv_path, encoding='utf-8')
        print(f"Archivo CSV '{csv_path}' leído exitosamente. Se encontraron {len(df)} filas.")
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo en la ruta especificada: {csv_path}")
        return
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
        return

    # Renombrar columnas para que coincidan con la base de datos y sean más fáciles de usar
    column_mapping = {
        'Dish_Title': 'titulo_platillo',
        'Recipe_category': 'categoria_receta',
        'Recipe_subcategory': 'subcategoria_receta',
        'Recipe_ingredients': 'ingredientes',
        'Recipe': 'preparacion',
        'Restricciones Dietéticas': 'nombre_restriccion',
        'Preferencia': 'nombre_preferencia',
        'Requerimientos Nutricionales (Calorías)': 'calorias',
        'Tiempo de Preparación': 'tiempo_preparacion',
        'Altura (cm)': 'altura',
        'Peso (kg)': 'peso',
        'Edad': 'edad',
        'Etiqueta de Recomendación': 'etiqueta',
        'Tipo de Comida': 'nombre_tipo_comida'
    }

    df.rename(columns=column_mapping, inplace=True)
    
    # Asegurarse de que las columnas necesarias existen
    required_cols = list(column_mapping.values())
    if not all(col in df.columns for col in required_cols):
        print("Error: El archivo CSV no contiene todas las columnas requeridas.")
        print(f"Columnas requeridas: {required_cols}")
        print(f"Columnas encontradas: {list(df.columns)}")
        return

    # --- 2. Crear la estructura de tablas ---
    sql_crear_tablas = """
    DROP TABLE IF EXISTS recomendaciones, recetas, restricciones_dieteticas, preferencias, tipos_comida CASCADE;

    CREATE TABLE restricciones_dieteticas (
        id_restriccion SERIAL PRIMARY KEY,
        nombre_restriccion VARCHAR(50) UNIQUE NOT NULL
    );
    CREATE TABLE preferencias (
        id_preferencia SERIAL PRIMARY KEY,
        nombre_preferencia VARCHAR(50) UNIQUE NOT NULL
    );
    CREATE TABLE tipos_comida (
        id_tipo_comida SERIAL PRIMARY KEY,
        nombre_tipo_comida VARCHAR(50) UNIQUE NOT NULL
    );
    CREATE TABLE recetas (
        id_receta SERIAL PRIMARY KEY,
        titulo_platillo VARCHAR(255) NOT NULL,
        categoria_receta VARCHAR(100),
        subcategoria_receta VARCHAR(100),
        ingredientes TEXT,
        preparacion TEXT,
        calorias INTEGER,
        tiempo_preparacion VARCHAR(50),
        id_restriccion INTEGER REFERENCES restricciones_dieteticas(id_restriccion),
        id_preferencia INTEGER REFERENCES preferencias(id_preferencia),
        id_tipo_comida INTEGER REFERENCES tipos_comida(id_tipo_comida)
    );
    CREATE TABLE recomendaciones (
        id_recomendacion SERIAL PRIMARY KEY,
        id_receta INTEGER REFERENCES recetas(id_receta),
        altura FLOAT NOT NULL,
        peso FLOAT NOT NULL,
        edad INTEGER NOT NULL,
        etiqueta INTEGER NOT NULL
    );
    """
    try:
        with engine.connect() as connection:
            # Envolvemos el string SQL con la función text() para que SQLAlchemy lo ejecute
            connection.execute(text(sql_crear_tablas))
            # SQLAlchemy 2.0 requiere que las transacciones se confirmen explícitamente
            connection.commit()
        print("Tablas creadas exitosamente en la base de datos.")
    except Exception as e:
        print(f"Error al crear las tablas: {e}")
        return

    # --- 3. Poblar las tablas de búsqueda (look-up) ---
    try:
        # Extraer valores únicos y guardarlos en las tablas
        df[['nombre_restriccion']].dropna().drop_duplicates().to_sql('restricciones_dieteticas', engine, if_exists='append', index=False)
        df[['nombre_preferencia']].dropna().drop_duplicates().to_sql('preferencias', engine, if_exists='append', index=False)
        df[['nombre_tipo_comida']].dropna().drop_duplicates().to_sql('tipos_comida', engine, if_exists='append', index=False)
        print("Tablas de búsqueda (restricciones, preferencias, tipos de comida) pobladas.")
    except Exception as e:
        print(f"Error al poblar las tablas de búsqueda: {e}")
        return

    # --- 4. Preparar y poblar la tabla de recetas ---
    try:
        # Cargar las tablas de búsqueda para mapear nombres a IDs
        restricciones = pd.read_sql('SELECT * FROM restricciones_dieteticas', engine)
        preferencias = pd.read_sql('SELECT * FROM preferencias', engine)
        tipos_comida = pd.read_sql('SELECT * FROM tipos_comida', engine)

        # Unir (merge) para obtener los IDs correspondientes
        df_merged = df.merge(restricciones, on='nombre_restriccion', how='left')
        df_merged = df_merged.merge(preferencias, on='nombre_preferencia', how='left')
        df_merged = df_merged.merge(tipos_comida, on='nombre_tipo_comida', how='left')
        
        # Seleccionar y renombrar las columnas finales para la tabla 'recetas'
        df_recetas = df_merged[[
            'titulo_platillo', 'categoria_receta', 'subcategoria_receta', 
            'ingredientes', 'preparacion', 'calorias', 'tiempo_preparacion',
            'id_restriccion', 'id_preferencia', 'id_tipo_comida'
        ]].copy()

        # Limpiar filas donde alguna de las claves foráneas sea Nula
        df_recetas.dropna(subset=['id_restriccion', 'id_preferencia', 'id_tipo_comida'], inplace=True)
        
        # Convertir IDs a enteros
        for col in ['id_restriccion', 'id_preferencia', 'id_tipo_comida']:
            df_recetas[col] = df_recetas[col].astype(int)

        # Insertar los datos en la tabla 'recetas'
        df_recetas.to_sql('recetas', engine, if_exists='append', index=False)
        print(f"Tabla 'recetas' poblada con {len(df_recetas)} registros.")
        print("\n¡Proceso de población de la base de datos completado exitosamente!")

    except Exception as e:
        print(f"Error al preparar y poblar la tabla de recetas: {e}")
        return

    # --- 5. Poblar la tabla recomendaciones ---
    try:
        # Recuperar los IDs de las recetas para emparejar con la data original
        recetas_en_db = pd.read_sql('SELECT id_receta, titulo_platillo FROM recetas', engine)

        # Hacer merge para obtener los id_receta
        df_merged_recomendaciones = df_merged.merge(recetas_en_db, on='titulo_platillo', how='inner')

        # Preparar el DataFrame final
        df_recomendaciones = df_merged_recomendaciones[[
            'id_receta', 'altura', 'peso', 'edad', 'etiqueta'
        ]].copy()

        # Renombrar columnas
        df_recomendaciones.columns = ['id_receta', 'altura', 'peso', 'edad', 'etiqueta']

        # Convertir tipos
        df_recomendaciones = df_recomendaciones.dropna()
        df_recomendaciones['altura'] = df_recomendaciones['altura'].astype(float)
        df_recomendaciones['peso'] = df_recomendaciones['peso'].astype(float)
        df_recomendaciones['edad'] = df_recomendaciones['edad'].astype(int)
        df_recomendaciones['etiqueta'] = df_recomendaciones['etiqueta'].astype(int)

        # Insertar en la tabla
        df_recomendaciones.to_sql('recomendaciones', engine, if_exists='append', index=False)
        print(f"Tabla 'recomendaciones' poblada con {len(df_recomendaciones)} registros.")

    except Exception as e:
        print(f"Error al poblar la tabla de recomendaciones: {e}")


# --- Bloque principal para ejecutar el script ---
if __name__ == '__main__':
    # ¡IMPORTANTE! Reemplaza esta ruta con la ubicación real de tu archivo CSV.
    # Usa una ruta absoluta para evitar problemas.
    CSV_FILE_PATH = r'C:\Users\crist\OneDrive\Desktop\nutricion\nutritechv2\project-root\backend\app\models\final_recipes_utf8.csv'
    
    # Cadena de conexión a tu base de datos PostgreSQL
    DB_CONNECTION_STRING = "postgresql://recetas_normalized_user:LGs0KhjIVSgGTYvx3aez1I37YjT9LkNa@dpg-d1ldpd15pdvs73bsasqg-a.ohio-postgres.render.com/recetas_normalized"

    poblar_base_de_datos(CSV_FILE_PATH, DB_CONNECTION_STRING)