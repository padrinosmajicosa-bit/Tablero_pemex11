import os
import pandas as pd
from redminelib import Redmine

# 1. Configuración de conexión a Redmine
REDMINE_URL = 'http://localhost:3000'
API_KEY = '8ba838b9c71502b0cfb481d2cda04a026e600106' # Pega aquí tu clave de Redmine ('Mi cuenta')
PROJECT_ID = ' admin' # El ID corto (slug) de tu proyecto en Redmine

redmine = Redmine(REDMINE_URL, key=API_KEY)

# 2. Localizar y leer el archivo Excel
excel_file = 'REPORTE MENSUAL REQUERIMIENTOS.xlsx'
if not os.path.exists(excel_file):
    archivos = [f for f in os.listdir('.') if f.endswith('.xlsx')]
    if archivos:
        excel_file = archivos[0]

print(f"Leyendo requerimientos desde: {excel_file}")
xls = pd.ExcelFile(excel_file)

# 3. Recorrer las hojas y poblar Redmine
total_creados = 0

for sheet_name in xls.sheet_names:
    df = pd.read_excel(xls, sheet_name=sheet_name)
    df.columns = df.columns.astype(str).str.strip().str.upper()
    
    print(f"Procesando hoja: {sheet_name} ({len(df)} registros)...")
    
    for _, row in df.iterrows():
        # Extraer el asunto o descripción del requerimiento usando las mismas columnas flexibles
        asunto = None
        for col in ['ASUNTO', 'PROYECTO', 'DESCRIPCION', 'REQUERIMIENTO', 'NOMBRE', 'TITULO']:
            if col in df.columns:
                val = row.get(col)
                if pd.notnull(val) and str(val).strip() not in ['', 'nan', 'None']:
                    asunto = str(val).strip()
                    break
        
        if not asunto:
            asunto = f"Requerimiento de hoja {sheet_name}"

        # Extraer descripción o situación actual si existe
        descripcion = f"Fase / Pestaña: {sheet_name}"
        for col_desc in ['SITUACIÓN ACTUAL', 'SITUACION ACTUAL', 'RESUMEN ACCIONES']:
            if col_desc in df.columns:
                val_desc = row.get(col_desc)
                if pd.notnull(val_desc) and str(val_desc).strip() not in ['', 'nan']:
                    descripcion += f" - {str(val_desc).strip()}"
                    break

        # Crear la petición en Redmine vía API
        try:
            issue = redmine.issue.create(
                project_id=PROJECT_ID,
                subject=asunto[:255], # Redmine limita el tamaño del asunto
                description=descripcion,
                status_id=1,   # 1: Nueva (puedes ajustarlo según tus estados en Redmine)
                tracker_id=1   # 1: Error o Tarea (ajustar según tu configuración)
            )
            total_creados += 1
            print(f"  [✔] Creado en Redmine - ID: {issue.id} | {asunto[:40]}...")
        except Exception as e:
            print(f"  [✘] Error al crear '{asunto[:30]}': {e}")

print(f"\n🚀 ¡Proceso finalizado! Se subieron {total_creados} peticiones a Redmine.")