import os
import pandas as pd
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Tablero_pemex.settings')
django.setup()

from proyectos.models import Proyecto

# Buscar el archivo Excel en la carpeta actual
excel_file = 'REPORTE MENSUAL REQUERIMIENTOS.xlsx'
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
                c_upper = c.strip().upper()
                for col_df in df.columns:
                    if c_upper == col_df or c_upper in col_df:
                        val = row.get(col_df)
                        if pd.notnull(val) and str(val).strip() not in ['', 'nan', 'None', 'NaN']:
                            return str(val).strip()
            return None

        def obtener_fecha(*cols):
            for c in cols:
                c_upper = c.strip().upper()
                for col_df in df.columns:
                    if c_upper == col_df or c_upper in col_df:
                        val = row.get(col_df)
                        if pd.notnull(val):
                            try:
                                return pd.to_datetime(val).date()
                            except Exception:
                                pass
            return None

        # 1. Extracción e Identificación de Folios
        rcn_val = obtener_val('RCN', 'FOLIO RCN', 'FOLIO_RCN', 'FOLIO', 'NO.')
        sr_val = obtener_val('SR', 'FOLIO SR', 'FOLIO_SR', 'SOLICITUD')

        # Si el folio es numérico (ej. 1090), conservamos la referencia original o el correlativo
        folio_num = obtener_val('#', 'NO', 'NO.', 'ID')

        if 'RCN' in sheet_upper and not rcn_val:
            rcn_val = f"RCN-{folio_num if folio_num else contador_global}"
        if 'SR' in sheet_upper and not sr_val:
            sr_val = f"SR-{folio_num if folio_num else contador_global}"

        # 2. Nombre / Asunto
        proyecto_val = obtener_val(
            'ASUNTO', 'PROYECTO', 'DESCRIPCION', 'REQUERIMIENTO', 
            'DESCRIPCION DE REQUERIMIENTO', 'NOMBRE', 'TITULO'
        ) or f"Requerimiento #{contador_global}"

        proyecto_obj = Proyecto(
            rcn=rcn_val,
            sr=sr_val,
            proyecto=proyecto_val,
            responsable=obtener_val('ASIGNADO A', 'RESPONSABLE', 'CONSULTOR DE NEGOCIO', 'SOLICITANTE', 'USUARIO') or 'Sin Asignar',
            estado=obtener_val('ESTADO', 'ESTATUS', 'SITUACIÓN') or 'En Proceso',
            prioridad=obtener_val('PRIORIDAD NEGOCIO', 'PRIORIDAD EPT', 'PRIORIDAD ORIGEN', 'PRIORIDAD') or '-',
            fase=sheet_name,
            clasificacion_requerimiento=obtener_val('CLASIFICACIÓN REQUERIMIENTO', 'CLASIFICACION REQUERIMIENTO'),
            grupo_tarea=obtener_val('GRUPO DE TAREA'),
            prioridad_negocio=obtener_val('PRIORIDAD NEGOCIO'),
            impacto_otros_proyectos=obtener_val('IMPACTO DE OTROS PROYECTOS', 'IMPACTO OTROS PROYECTOS'),
            capacidades_acciones_sti=obtener_val('CAPACIDADES ACCIONES COORDINADAS STI', 'CAPACIDADES', 'ACCIONES COORDINADAS STI'),
            edo_salud=obtener_val('EDO. SALUD', 'EDO SALUD', 'ESTADO SALUD'),
            area_responsable_habilitacion=obtener_val('ÁREA RESPONSABLE HABILITACIÓN', 'AREA RESPONSABLE HABILITACION'),
            area_apoyo_habilitacion=obtener_val('AREA APOYO HABILITACIÓN', 'AREA APOYO HABILITACION'),
            fuente_negocio=obtener_val('FUENTE NEGOCIO'),
            prioridad_ept=obtener_val('PRIORIDAD EPT'),
            consultor_negocio=obtener_val('CONSULTOR DE NEGOCIO'),
            do_campo=obtener_val('DO'),
            situacion_actual=obtener_val('SITUACIÓN ACTUAL', 'SITUACION ACTUAL'),
            resumen_acciones=obtener_val('RESUMEN ACCIONES'),
            fabrica_software=obtener_val('FÁBRICA SOFTWARE', 'FABRICA SOFTWARE'),
            tipo_proyecto=obtener_val('TIPO DE PROYECTO'),
            categoria_proyecto=obtener_val('CATEGORÍA DEL PROYECTO', 'CATEGORIA DEL PROYECTO'),
            pct_planeado=obtener_val('% PLANEADO'),
            pct_ponderado=obtener_val('% PONDERADO'),
            subdireccion_solicitante=obtener_val('SUBDIRECCIÓN SOLICITANTE', 'SUBDIRECCION SOLICITANTE'),
            prioridad_origen=obtener_val('PRIORIDAD ORIGEN'),
            tiempo_dedicado=obtener_val('TIEMPO DEDICADO'),
            tiempo_total_dedicado=obtener_val('TIEMPO TOTAL DEDICADO'),
            fecha_inicio=obtener_fecha('FECHA DE INICIO', 'INICIO'),
            fecha_fin=obtener_fecha('FECHA FIN', 'TERMINO', 'FIN'),
            f_inicio_base=obtener_fecha('F.INICIO BASE', 'F. INICIO BASE'),
            f_fin_base=obtener_fecha('F. FIN BASE', 'F.FIN BASE'),
            f_inicio_entendimiento=obtener_fecha('F INICIO ENTENDIMIENTO', 'F. INICIO ENTENDIMIENTO'),
            f_fin_entendimiento=obtener_fecha('F FIN ENTENDIMIENTO', 'F. FIN ENTENDIMIENTO'),
            f_inicio_habilitacion=obtener_fecha('F INICIO HABILITACIÓN', 'F INICIO HABILITACION'),
            f_fin_habilitacion=obtener_fecha('F FIN HABILITACIÓN', 'F FIN HABILITACION'),
        )
        proyectos_a_crear.append(proyecto_obj)
        contador_global += 1

Proyecto.objects.bulk_create(proyectos_a_crear)
print(f"✅ ¡Éxito! Se procesaron {len(proyectos_a_crear)} requerimientos con todos sus campos desde {xls.sheet_names}.")
