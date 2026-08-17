import os
import pandas as pd
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Tablero_pemex.settings')
django.setup()

from proyectos.models import Proyecto

# Buscar el archivo Excel en la carpeta actual
excel_file = 'Tablero_pemex.xlsx'
if not os.path.exists(excel_file):
    archivos = [f for f in os.listdir('.') if f.endswith('.xlsx')]
    if archivos:
        excel_file = archivos[0]

print(f"Leyendo datos desde: {excel_file}")

xls = pd.ExcelFile(excel_file)
Proyecto.objects.all().delete()

proyectos_a_crear = []
contador_global = 1

for sheet_name in xls.sheet_names:
    df = pd.read_excel(xls, sheet_name=sheet_name)
    df.columns = df.columns.astype(str).str.strip().str.upper()
    sheet_upper = sheet_name.upper()

    for _, row in df.iterrows():
        def obtener_val(*cols):
            for c in cols:
                for col_df in df.columns:
                    if c in col_df:
                        val = row.get(col_df)
                        if pd.notnull(val) and str(val).strip() not in ['', 'nan', 'None', 'NaN']:
                            return str(val).strip()
            return None

        def obtener_fecha(*cols):
            for c in cols:
                for col_df in df.columns:
                    if c in col_df:
                        val = row.get(col_df)
                        if pd.notnull(val):
                            try:
                                return pd.to_datetime(val).date()
                            except Exception:
                                pass
            return None

        # 1. Extracción e Identificación de RCN y SR
        rcn_val = obtener_val('RCN', 'FOLIO RCN', 'FOLIO_RCN', 'FOLIO')
        sr_val = obtener_val('SR', 'FOLIO SR', 'FOLIO_SR', 'SOLICITUD')

        # Generar Folios automáticos si la pestaña lo indica y la columna venía vacía
        if 'RCN' in sheet_upper and not rcn_val:
            rcn_val = f"RCN-{contador_global:03d}"
        if 'SR' in sheet_upper and not sr_val:
            sr_val = f"SR-{contador_global:03d}"

        # 2. Extracción de Nombre del Proyecto / Descripción
        proyecto_val = obtener_val(
            'PROYECTO', 'DESCRIPCION', 'REQUERIMIENTO', 
            'DESCRIPCION DE REQUERIMIENTO', 'NOMBRE', 'TITULO', 'ASUNTO'
        )
        if not proyecto_val:
            proyecto_val = f"Requerimiento #{contador_global}"

        # 3. Responsables y Estados
        responsable_val = obtener_val('RESPONSABLE', 'ASIGNADO', 'SOLICITANTE', 'USUARIO') or 'Sin Asignar'
        estado_val = obtener_val('ESTADO', 'ESTATUS', 'SITUACION') or 'En Proceso'
        prioridad_val = obtener_val('PRIORIDAD') or '-'

        proyecto_obj = Proyecto(
            rcn=rcn_val,
            sr=sr_val,
            proyecto=proyecto_val,
            responsable=responsable_val,
            estado=estado_val,
            prioridad=prioridad_val,
            fecha_inicio=obtener_fecha('INICIO', 'FECHA_INICIO', 'CREACION'),
            fecha_fin=obtener_fecha('FIN', 'TERMINO', 'FECHA_FIN'),
            fase=sheet_name
        )
        proyectos_a_crear.append(proyecto_obj)
        contador_global += 1

Proyecto.objects.bulk_create(proyectos_a_crear)
print(f"✅ ¡Éxito! Se guardaron {len(proyectos_a_crear)} registros procesando las pestañas {xls.sheet_names}.")