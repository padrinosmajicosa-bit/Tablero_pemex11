import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q

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
    proyectos = Proyecto.objects.all()

    # Mapeamos todos los proyectos primero para asegurar compatibilidad total
    proyectos_mapeados = [mapear_datos_proyecto(p) for p in proyectos]

    # Conteos seguros basados en los datos ya procesados por el helper
    total_rcn = sum(1 for p in proyectos_mapeados if p['rcn'] != '-')
    total_sr = sum(1 for p in proyectos_mapeados if p['sr'] != '-')
    total_backlog = sum(1 for p in proyectos_mapeados if p['rcn'] == '-' and p['sr'] == '-')
    total_rcn_activo = sum(1 for p in proyectos_mapeados if p['rcn'] != '-' and 'cerrado' not in p['estado'].lower() and 'concluido' not in p['estado'].lower())
    total_alertas = sum(1 for p in proyectos_mapeados if 'rojo' in p['estado_salud'].lower() or 'urgente' in p['prioridad'].lower() or 'alta' in p['prioridad'].lower())

    # 2. Contexto hacia la plantilla (limitamos la tabla a los primeros 15)
    contexto = {
        "seccion_actual": "dashboard",
        "total_rcn": total_rcn,
        "total_sr": total_sr,
        "total_backlog": total_backlog,
        "total_rcn_activo": total_rcn_activo,
        "total_alertas": total_alertas,
        "rcn": total_rcn,
        "sr": total_sr,
        "backlog": total_backlog,
        "rcn_activo": total_rcn_activo,
        "alertas": total_alertas,
        "peticiones": proyectos_mapeados[:15],
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
# 🔥 2. VISTAS FILTRADAS
# ==========================================

def lista_rcn(request):
    """Filtra proyectos correspondientes a RCN"""
    queryset = Proyecto.objects.filter(
        (Q(rcn__isnull=False) & ~Q(rcn='')) | 
        Q(fase__icontains='rcn') | 
        Q(fase__icontains='activo')
    )
    return _obtener_proyectos_filtrados(request, queryset, "Gestión de RCNs", "RCN", "rcn")


def lista_sr(request):
    """Filtra proyectos correspondientes a SR"""
    queryset = Proyecto.objects.filter(
        (Q(sr__isnull=False) & ~Q(sr='')) | Q(fase__icontains='sr')
    )
    return _obtener_proyectos_filtrados(request, queryset, "Gestión de SRs", "SR", "sr")


def lista_backlog(request):
    """Filtra proyectos en Backlog (sin RCN ni SR específicos)"""
    queryset = Proyecto.objects.filter(
        Q(rcn__isnull=True) | Q(rcn=''),
        Q(sr__isnull=True) | Q(sr=''),
        ~Q(fase__icontains='rcn'),
        ~Q(fase__icontains='sr')
    )
    return _obtener_proyectos_filtrados(request, queryset, "Proyectos en Backlog", "BACKLOG", "backlog")


def lista_rcn_activo(request):
    """Filtra proyectos RCN Activos (no cerrados)"""
    queryset = Proyecto.objects.filter(
        (Q(rcn__isnull=False) & ~Q(rcn='')) | Q(fase__icontains='rcn') | Q(fase__icontains='activo')
    ).exclude(estado__icontains='cerrado')
    return _obtener_proyectos_filtrados(request, queryset, "Proyectos RCN Activos", "ACTIVOS", "rcn_activo")


# ==========================================
# 🔍 3. VISTAS SECUNDARIAS Y NAVEGACIÓN
# ==========================================

def index_descargas(request):
    return render(request, "descargas/index.html")


def vista_validaciones(request):
    return render(request, 'dashboard/validaciones.html')


# ==========================================
# 🛠️ FUNCIONES DE GESTIÓN (CRUD REAL)
# ==========================================

def nuevo_proyecto(request):
    """Vista para crear un nuevo proyecto"""
    if request.method == "POST":
        Proyecto.objects.create(
            proyecto=request.POST.get('proyecto', '').strip(),
            rcn=request.POST.get('rcn', '').strip(),
            sr=request.POST.get('sr', '').strip(),
            responsable=request.POST.get('responsable', '').strip(),
            estado=request.POST.get('estado', 'En proceso').strip(),
            prioridad=request.POST.get('prioridad', '-').strip(),
            fase=request.POST.get('fase', '-').strip(),
            fecha_inicio=request.POST.get('fecha_inicio') or None,
            fecha_fin=request.POST.get('fecha_fin') or None,
        )
        messages.success(request, "Proyecto creado con éxito.")
        return redirect("lista_proyectos")
    return render(request, "proyectos/formulario.html", {"titulo": "Nuevo Proyecto"})


def editar_proyecto(request, pk):
    """Vista para editar un proyecto existente"""
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
    """Vista para eliminar un proyecto"""
    proyecto = get_object_or_404(Proyecto, pk=pk)
    if request.method == "POST":
        proyecto.delete()
        messages.success(request, "Registro eliminado correctamente.")
        return redirect("lista_proyectos")
    return render(request, "proyectos/confirmar_eliminacion.html", {"proyecto": proyecto})


def detalle_proyecto(request, pk):
    """🔍 Vista para consultar el detalle de un proyecto"""
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
    """Vista para la carga de archivos Excel"""
    if request.method == "POST":
        archivo = request.FILES.get("archivo_excel")
        if archivo and (archivo.name.endswith('.xlsx') or archivo.name.endswith('.xls')):
            messages.success(request, f"Archivo '{archivo.name}' procesado correctamente.")
            return redirect("lista_proyectos")
        else:
            messages.error(request, "Formato de archivo inválido. Por favor sube un archivo Excel (.xlsx o .xls).")
    
    return render(request, "proyectos/subir_excel.html")


def exportar_proyectos_excel(request):
    """Vista para la descarga/exportación a Excel"""
    messages.info(request, "La función de exportación a Excel estará disponible próximamente.")
    return redirect("lista_proyectos")


def exportar_proyectos_pdf(request):
    """Vista para la descarga/exportación a PDF"""
    messages.info(request, "La función de exportación a PDF estará disponible próximamente.")
    return redirect("lista_proyectos")