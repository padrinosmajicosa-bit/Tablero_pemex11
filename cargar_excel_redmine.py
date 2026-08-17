import pandas as pd
import psycopg2

# 1. Configuración de conexión
DB_CONFIG = {
    "dbname": "redmine",
    "user": "redmine",
    "password": "redmine_password",
    "host": "localhost",
    "port": "5434"
}

# 2. Ruta del archivo Excel
EXCEL_FILE = 'REPORTE MENSUAL REQUERIMIENTOS.xlsx'

def cargar_datos():
    try:
        df = pd.read_excel(EXCEL_FILE)
        print(f"📊 Se leyeron {len(df)} filas del archivo Excel.")

        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # A. Crear proyecto base
        cursor.execute("""
            INSERT INTO projects (name, description, identifier, is_public, created_on, updated_on)
            VALUES ('Proyectos PEMEX', 'Proyecto principal', 'pemex-main', true, NOW(), NOW())
            ON CONFLICT (identifier) DO NOTHING;
        """)
        cursor.execute("SELECT id FROM projects WHERE identifier = 'pemex-main';")
        project_id = cursor.fetchone()[0]

        # B. Crear Tracker simplificado (sin campos de versión específicos)
        cursor.execute("""
            INSERT INTO trackers (id, name, position)
            VALUES (1, 'Requerimiento', 1)
            ON CONFLICT (id) DO NOTHING;
        """)

        # C. Crear Estado inicial
        cursor.execute("""
            INSERT INTO issue_statuses (id, name, is_closed, position)
            VALUES (1, 'Nuevo', false, 1)
            ON CONFLICT (id) DO NOTHING;
        """)

        # D. Asignar Tracker al proyecto
        cursor.execute("""
            INSERT INTO projects_trackers (project_id, tracker_id)
            VALUES (%s, 1)
            ON CONFLICT DO NOTHING;
        """, (project_id,))

        # E. Insertar peticiones desde Excel
        count = 0
        for _, row in df.iterrows():
            asunto = str(row.get('Asunto', row.get('Nombre', 'Petición sin título')))
            descripcion = str(row.get('Descripción', 'Importado desde Excel'))

            cursor.execute("""
                INSERT INTO issues (
                    project_id, tracker_id, subject, description, 
                    status_id, priority_id, author_id, lock_version,
                    created_on, updated_on
                )
                VALUES (%s, 1, %s, %s, 1, 2, 1, 0, NOW(), NOW());
            """, (project_id, asunto, descripcion))
            count += 1

        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ ¡Éxito! Se insertaron {count} peticiones correctamente en la base de datos de Redmine.")

    except Exception as e:
        print(f"❌ Error al cargar los datos: {e}")

if __name__ == "__main__":
    cargar_datos()