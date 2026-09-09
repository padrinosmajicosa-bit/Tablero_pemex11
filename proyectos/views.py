import json

from io import BytesIO

import pandas as pd

from django.shortcuts import render, redirect, get_object_or_404

from django.contrib import messages

from django.db.models import Q

from django.http import HttpResponse



from proyectos.models import Proyecto





# ==========================================

# 🛠️ HELPER DE MAPEO DE DATOS Y COMPATIBILIDAD

# ==========================================



def mapear_datos_proyecto(p):

    """

    Extrae todos los campos posibles de cada instancia del modelo Proyecto.

    """

    def val(attr_name, default='-'):

        v = getattr(p, attr_name, None)

        if v is not None and str(v).strip() != '':

            return str(v).strip()

        return default



    def fmt_date(d):

        return d.strftime('%Y-%m-%d') if d else '-'



    return {

        'id': p.id,

        'pk': p.id,

        'issue_id': p.id,

        'rcn': val('rcn'),

        'sr': val('sr'),

        'proyecto': val('proyecto') if val('proyecto') != '-' else val('nombre', default=f'Requerimiento #{p.id}'),

        'asunto': val('asunto') if val('asunto') != '-' else (val('proyecto') if val('proyecto') != '-' else val('nombre', default=f'Requerimiento #{p.id}')),

        'clasificacion_requerimiento': val('clasificacion_requerimiento'),

        'grupo_tarea': val('grupo_tarea'),

        'solicitante': val('subdireccion_solicitante') if val('subdireccion_solicitante') != '-' else val('responsable'),

        'prioridad_negocio': val('prioridad_negocio') if val('prioridad_negocio') != '-' else val('prioridad'),

        'prioridad': val('prioridad', default='Normal'),

        'resumen_acciones': val('resumen_acciones'),

        'impacto_otros_proyectos': val('impacto_otros_proyectos'),

        'capacidades_acciones_sti': val('capacidades_acciones_sti'),

        'edo_salud': val('edo_salud') if val('edo_salud') != '-' else val('estado'),

        'estado_salud': val('edo_salud') if val('edo_salud') != '-' else val('estado'),

        'area_responsable_habilitacion': val('area_responsable_habilitacion'),

        'area_apoyo_habilitacion': val('area_apoyo_habilitacion'),

        'fuente_negocio': val('fuente_negocio'),

        'prioridad_ept': val('prioridad_ept'),

        'consultor_negocio': val('consultor_negocio'),

        'consultor': val('consultor_negocio') if val('consultor_negocio') != '-' else val('responsable'),

        'do_campo': val('do_campo'),

        'situacion_actual': val('situacion_actual') if val('situacion_actual') != '-' else val('fase'),

        'fase': val('fase') if val('fase') != '-' else val('situacion_actual'),

        'fabrica_software': val('fabrica_software'),

        'tipo_proyecto': val('tipo_proyecto'),

        'categoria_proyecto': val('categoria_proyecto'),

        'pct_planeado': val('pct_planeado'),

        'pct_ponderado': val('pct_ponderado'),

        'fecha_inicio': fmt_date(getattr(p, 'fecha_inicio', None)),

        'fecha_fin': fmt_date(getattr(p, 'fecha_fin', None)),

        'estado': val('estado', default='En proceso'),

    }



def _obtener_proyectos_filtrados(request, queryset, titulo, tipo_vista, seccion_actual):

    """

    Función helper para procesar listas filtradas de proyectos.

    """

    proyectos_mapeados = [mapear_datos_proyecto(p) for p in queryset]

    contexto = {

        'proyectos': proyectos_mapeados,

        'titulo': titulo,

        'tipo_vista': tipo_vista,

        'seccion_actual': seccion_actual,

    }

    return render(request, 'proyectos/lista.html', contexto)





# ==========================================

# 📌 1. DASHBOARD Y LISTA PRINCIPAL

# ==========================================

def dashboard(request):

    # Traemos absolutamente todos los proyectos ordenados del más nuevo al más viejo

    proyectos = Proyecto.objects.all().order_by('-id')

   

    # Contadores estrictos por fase (Asegúrate de que tus IDs 149 y 150 tengan exactamente 'SR' en su campo fase)

    total_rcn_totales = proyectos.filter(fase='CONCLUIDOS').count()

    total_sr = proyectos.filter(fase='SR').count()

    total_backlog = proyectos.filter(fase='BACKLOG').count()

    total_rcn_activo = proyectos.filter(fase='ACTIVOS').count()

   

    # Mapeo para la tabla de movimientos recientes en el dashboard

    proyectos_mapeados = [mapear_datos_proyecto(p) for p in proyectos]

    total_alertas = sum(1 for p in proyectos_mapeados if 'rojo' in p['estado_salud'].lower() or 'urgente' in p['prioridad'].lower() or 'alta' in p['prioridad'].lower())



    contexto = {

        "seccion_actual": "dashboard",

        "total_rcn": total_rcn_totales,

        "total_sr": total_sr,

        "total_backlog": total_backlog,

        "total_rcn_activo": total_rcn_activo,

        "total_alertas": total_alertas,

        "rcn": total_rcn_totales,

        "sr": total_sr,  # <---- Esta variable es la que lee tu tarjeta de SR en el HTML del dashboard

        "backlog": total_backlog,

        "rcn_activo": total_rcn_activo,

        "alertas": total_alertas,

        "peticiones": proyectos_mapeados[:15], # Aquí ahora mostrará los 15 más recientes incluyendo tus pruebas

    }

   

    return render(request, "dashboard/index.html", contexto)

def lista_proyectos(request):

    """📋 Vista general de todos los requerimientos"""

    return _obtener_proyectos_filtrados(

        request,

        Proyecto.objects.all(),

        "Todos los Proyectos",

        "TODOS",

        "proyectos"

    )





# ==========================================

# 🔥 2. VISTAS FILTRADAS POR PESTAÑA EXACTA

# ==========================================



def lista_rcn(request):

    """RCN Totales ↔ Pestaña CONCLUIDOS del Excel"""

    queryset = Proyecto.objects.filter(fase='CONCLUIDOS')

    return _obtener_proyectos_filtrados(request, queryset, "Gestión de RCNs Totales", "RCN", "rcn")





def lista_sr(request):

    """SR ↔ Pestaña SR del Excel"""

    queryset = Proyecto.objects.filter(fase='SR')

    return _obtener_proyectos_filtrados(request, queryset, "Gestión de SRs", "SR", "sr")





def lista_backlog(request):

    """Backlog ↔ Pestaña BACKLOG del Excel"""

    queryset = Proyecto.objects.filter(fase='BACKLOG')

    return _obtener_proyectos_filtrados(request, queryset, "Proyectos en Backlog", "BACKLOG", "backlog")





def lista_rcn_activo(request):

    """RCN Activo ↔ Pestaña ACTIVOS del Excel"""

    queryset = Proyecto.objects.filter(fase='ACTIVOS')

    return _obtener_proyectos_filtrados(request, queryset, "Proyectos RCN Activos", "ACTIVOS", "rcn_activo")





# ==========================================

# 🔍 3. VISTAS SECUNDARIAS Y NAVEGACIÓN

# ==========================================



def index_descargas(request):

    return render(request, "descargas/index.html")




def vista_validaciones(request):
    """🔍 Auditor de integridad de datos para la base de datos de proyectos"""
    proyectos = Proyecto.objects.all()
    
    anomalias = []
    total_registros = proyectos.count()

    for p in proyectos:
        # Usamos tu helper para asegurar que tenga todos los campos mapeados de forma segura
        p_dict = mapear_datos_proyecto(p)

        # 1. Revisar fechas ilógicas (Fecha fin anterior a fecha inicio)
        if p.fecha_inicio and p.fecha_fin:
            if p.fecha_fin < p.fecha_inicio:
                anomalias.append({
                    'proyecto': p_dict,  # Pasamos el diccionario en lugar del objeto crudo
                    'tipo': 'Fechas Inconsistentes',
                    'descripcion': f"La fecha de fin ({p.fecha_fin}) es anterior a la de inicio ({p.fecha_inicio}).",
                    'severidad': 'danger'
                })

        # 2. Revisar registros activos sin responsable o consultor
        responsable = getattr(p, 'responsable', None) or getattr(p, 'consultor_negocio', None)
        if not responsable or str(responsable).strip() in ['', '-']:
            anomalias.append({
                'proyecto': p_dict,
                'tipo': 'Responsable Faltante',
                'descripcion': "El requerimiento no cuenta con un responsable o consultor asignado.",
                'severidad': 'warning'
            })
# Aseguramos que el diccionario tenga la clave 'nombre' para evitar cualquier error en el HTML
        p_dict['nombre'] = p_dict['proyecto']
        # 3. Revisar si falta folio en activos o RCN
        fase_str = str(p.fase).upper()
        if 'ACTIVO' in fase_str and not p.rcn and not p.sr:
            
            anomalias.append({
                'proyecto': p_dict,
                'tipo': 'Sin Folios de Referencia',
                'descripcion': "El proyecto está marcado como activo pero no tiene ni folio RCN ni SR.",
                'severidad': 'warning'
            })

    total_anomalias = len(anomalias)
    sistema_saludable = total_anomalias == 0

    contexto = {
        "titulo": "Validaciones y Auditoría del Sistema",
        "seccion_actual": "validaciones",
        "total_registros": total_registros,
        "total_anomalias": total_anomalias,
        "anomalias": anomalias,
        "sistema_saludable": sistema_saludable,
    }
    
    return render(request, 'dashboard/validaciones.html', contexto)
# ==========================================

# 🛠️ FUNCIONES DE GESTIÓN (CRUD REAL)

# ==========================================

from .forms import ProyectoForm # Asegúrate de tener importado tu formulario



def nuevo_proyecto(request):

    # Capturamos la fase que viene por la URL (ej: ?fase=SR)

    fase_predefinida = request.GET.get('fase', 'ACTIVOS').strip().upper()

   

    if request.method == "POST":

        form = ProyectoForm(request.POST)

        if form.is_valid():

            # Guardamos usando la lógica limpia de tu forms.py

            proyecto_guardado = form.save(commit=False)

            # Aseguramos que la fase tome la predefinida si viene vacía

            if not proyecto_guardado.fase:

                proyecto_guardado.fase = fase_predefinida

            proyecto_guardado.save()

           

            messages.success(request, "¡Requerimiento agregado con éxito!")

           

            # Redireccionamos según la fase guardada

            fase_guardada = str(proyecto_guardado.fase).upper()

            if 'SR' in fase_guardada:

                return redirect("lista_sr")

            elif 'BACKLOG' in fase_guardada:

                return redirect("lista_backlog")

            elif 'CONCLUIDOS' in fase_guardada or 'RCN' in fase_guardada:

                return redirect("lista_rcn")

            else:

                return redirect("lista_activos")

        else:

            # Imprime errores en la terminal si algo falla

            print("ERRORES DE VALIDACIÓN:", form.errors)

    else:

        # Si es GET, inicializamos el formulario vacío (aquí es donde viaja la variable "formulario")

        form = ProyectoForm(initial={'fase': fase_predefinida})



    return render(request, "proyectos/formulario.html", {

        "formulario": form, # <--- ¡Esta era la variable que faltaba en tu render!

        "titulo": f"Nuevo Registro ({fase_predefinida})",

        "fase_predefinida": fase_predefinida

    })



def editar_proyecto(request, pk):

    proyecto = get_object_or_404(Proyecto, pk=pk)

   

    if request.method == "POST":

        proyecto.proyecto = request.POST.get('proyecto', proyecto.proyecto).strip()

        proyecto.rcn = request.POST.get('rcn', proyecto.rcn).strip()

        proyecto.sr = request.POST.get('sr', proyecto.sr).strip()

        proyecto.responsable = request.POST.get('responsable', proyecto.responsable).strip()

        proyecto.estado = request.POST.get('estado', proyecto.estado).strip()

        proyecto.prioridad = request.POST.get('prioridad', proyecto.prioridad).strip()

        proyecto.fase = request.POST.get('fase', proyecto.fase).strip()

       

        f_inicio = request.POST.get('fecha_inicio')

        f_fin = request.POST.get('fecha_fin')

        proyecto.fecha_inicio = f_inicio if f_inicio else None

        proyecto.fecha_fin = f_fin if f_fin else None

       

        proyecto.save()

        messages.success(request, "Proyecto actualizado correctamente.")

        return redirect("detalle_proyecto", pk=proyecto.pk)



    proyecto_dict = mapear_datos_proyecto(proyecto)

    return render(

        request,

        "proyectos/formulario.html",

        {"proyecto": proyecto_dict, "titulo": "Editar Proyecto"}

    )





def eliminar_proyecto(request, pk):

    proyecto = get_object_or_404(Proyecto, pk=pk)

    if request.method == "POST":

        proyecto.delete()

        messages.success(request, "Registro eliminado correctamente.")

        return redirect("lista_proyectos")

    return render(request, "proyectos/confirmar_eliminacion.html", {"proyecto": proyecto})





def detalle_proyecto(request, pk):

    proyecto = get_object_or_404(Proyecto, pk=pk)

    proyecto_dict = mapear_datos_proyecto(proyecto)

    return render(

        request,

        "proyectos/detalle.html",

        {"proyecto": proyecto_dict, "titulo": "Detalle del Proyecto"}

    )





# ==========================================

# 🛠️ VISTAS ADICIONALES (EXCEL Y EXPORTAR)

# ==========================================



def subir_excel(request):

    if request.method == "POST":

        archivo = request.FILES.get("archivo_excel")

        if archivo and (archivo.name.endswith('.xlsx') or archivo.name.endswith('.xls')):

            messages.success(request, f"Archivo '{archivo.name}' procesado correctamente.")

            return redirect("lista_proyectos")

        else:

            messages.error(request, "Formato de archivo inválido. Por favor sube un archivo Excel.")

    return render(request, "proyectos/subir_excel.html")





def exportar_proyectos_excel(request):

    proyectos = Proyecto.objects.all()

    proyectos_mapeados = [mapear_datos_proyecto(p) for p in proyectos]

    df = pd.DataFrame(proyectos_mapeados)

   

    for col in df.columns:

        df[col] = df[col].astype(str).fillna('-')



    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:

        df.to_excel(writer, sheet_name='Reporte General', index=False)

   

    buffer.seek(0)

    response = HttpResponse(

        buffer.getvalue(),

        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    )

    response['Content-Disposition'] = 'attachment; filename="reporte_pemex.xlsx"'

    return response





from reportlab.lib.pagesizes import letter, landscape

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from reportlab.lib import colors



def exportar_proyectos_pdf(request):

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)

    elementos = []

   

    styles = getSampleStyleSheet()

    estilo_titulo = ParagraphStyle(

        'TituloReporte',

        parent=styles['Heading1'],

        fontSize=18,

        textColor=colors.HexColor('#1b4d3e'),

        spaceAfter=15,

        alignment=1

    )

   

    elementos.append(Paragraph("Reporte General - Tablero PEMEX", estilo_titulo))

    elementos.append(Spacer(1, 10))

   

    proyectos = Proyecto.objects.all()[:50]

    data = [["ID", "Proyecto / Asunto", "Estado", "Responsable", "Prioridad", "Fase"]]

   

    for p in proyectos:

        p_dict = mapear_datos_proyecto(p)

        data.append([

            str(p_dict['id']),

            str(p_dict['proyecto'])[:35],

            str(p_dict['estado']),

            str(p_dict['consultor'])[:20],

            str(p_dict['prioridad']),

            str(p_dict['fase'])

        ])

   

    t = Table(data, colWidths=[40, 250, 80, 110, 80, 100])

    t.setStyle(TableStyle([

        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1b4d3e')),

        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),

        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),

        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

        ('FONTSIZE', (0, 0), (-1, 0), 10),

        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),

        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9f9f9')),

        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d3d3d3')),

        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),

        ('FONTSIZE', (0, 1), (-1, -1), 9),

    ]))

   

    elementos.append(t)

    doc.build(elementos)

   

    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')

    response['Content-Disposition'] = 'attachment; filename="reporte_pemex.pdf"'

    return response





descargar_excel = exportar_proyectos_excel

descargar_pdf = exportar_proyectos_pdf 

