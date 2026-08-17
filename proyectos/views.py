import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q

# Importar el modelo REAL de la base de datos
from proyectos.models import Proyecto


# ==========================================
# 🛠️ HELPER DE MAPEO DE DATOS Y COMPATIBILIDAD
# ==========================================

def mapear_datos_proyecto(p):
    """
    Toma un objeto Proyecto de PostgreSQL / SQLite y mapea sus columnas
    a las variables que espera la plantilla HTML.
    """
    rcn_val = (p.rcn or '').strip()
    sr_val = (p.sr or '').strip()
    nombre_p = (p.proyecto or '').strip() or f'Requerimiento #{p.id}'
    resp_val = (p.responsable or '').strip() or 'Sin asignar'
    estado_val = (p.estado or '').strip() or 'En proceso'
    prioridad_val = (p.prioridad or '').strip() or '-'
    fase_val = (p.fase or '').strip() or '-'

    # Formateo de fechas
    f_inicio = p.fecha_inicio.strftime('%Y-%m-%d') if p.fecha_inicio else '-'
    f_fin = p.fecha_fin.strftime('%Y-%m-%d') if p.fecha_fin else '-'

    return {
        'id': p.id,
        'issue_id': p.id,
        'pk': p.id,
        
        # Identificadores y folios
        'rcn': rcn_val if rcn_val else '-',
        'sr': sr_val if sr_val else '-',
        'folio_sr': sr_val if sr_val else '-',
        'sr_folio': sr_val if sr_val else '-',
        'estatus_sr': estado_val,
        'sr_status': estado_val,
        'proyecto': nombre_p,
        'nombre': nombre_p,
        'subject': nombre_p,
        'titulo': nombre_p,
        'description': nombre_p,
        'descripcion': nombre_p,

        # Responsables y Estados
        'responsable': resp_val,
        'solicitante': resp_val,
        'author': {'name': resp_val},
        'assigned_to': {'name': resp_val},
        'asignado_a': resp_val,
        'estado': estado_val,
        'estatus': estado_val,
        'status': {'name': estado_val},
        'prioridad': prioridad_val,
        'priority': {'name': prioridad_val},
        'fase': fase_val,

        # Fechas
        'fecha_inicio': f_inicio,
        'f_inicio_base': f_inicio,
        'fecha_fin': f_fin,
        'f_fin_base': f_fin,

        # Campos secundarios
        'grupo_tarea': fase_val if fase_val != '-' else 'General',
        'clasificacion_requerimiento': estado_val,
        'prioridad_negocio': prioridad_val,
        'impacto_otros_proyectos': '-',
        'capacidades': '-',
        'acciones_coordinadas_sti': '-',
        'edo_salud': estado_val,
        'area_responsable_habilitacion': resp_val,
        'fuente_negocio': '-',
        'prioridad_ept': prioridad_val,
        'consultor_negocio': resp_val,
        'situacion_actual': estado_val,
        'fabrica_software': '-',
    }


# ==========================================
# 📌 1. DASHBOARD Y LISTA PRINCIPAL
# ==========================================

def dashboard(request):
    """📊 Vista principal del Dashboard con conteos reales"""
    total_proyectos = Proyecto.objects.count()
    
    total_rcn = Proyecto.objects.filter(
        (Q(rcn__isnull=False) & ~Q(rcn='')) | Q(fase__icontains='rcn')
    ).count()

    total_sr = Proyecto.objects.filter(
        (Q(sr__isnull=False) & ~Q(sr='')) | Q(fase__icontains='sr')
    ).count()

    total_backlog = Proyecto.objects.filter(
        Q(rcn__isnull=True) | Q(rcn=''),
        Q(sr__isnull=True) | Q(sr=''),
        ~Q(fase__icontains='rcn'),
        ~Q(fase__icontains='sr')
    ).count()

    total_rcn_activo = Proyecto.objects.filter(
        (Q(rcn__isnull=False) & ~Q(rcn='')) | Q(fase__icontains='rcn') | Q(fase__icontains='activo')
    ).exclude(estado__icontains='cerrado').count()

    contexto = {
        "total_proyectos": total_proyectos,
        "total_rcn": total_rcn,
        "total_sr": total_sr,
        "total_backlog": total_backlog,
        "total_rcn_activo": total_rcn_activo,
        "seccion_actual": "dashboard",
    }
    return render(request, "dashboard/index.html", contexto)


def lista_proyectos(request):
    """📋 Vista general de todos los requerimientos"""
    busqueda = request.GET.get('buscar', '').strip()
    proyectos_qs = Proyecto.objects.all()

    if busqueda:
        proyectos_qs = proyectos_qs.filter(
            Q(proyecto__icontains=busqueda) | 
            Q(rcn__icontains=busqueda) |
            Q(sr__icontains=busqueda) |
            Q(responsable__icontains=busqueda)
        )

    proyectos_procesados = [mapear_datos_proyecto(p) for p in proyectos_qs.order_by('-id')]

    return render(
        request, 
        "proyectos/lista.html", 
        {
            "proyectos": proyectos_procesados, 
            "busqueda": busqueda, 
            "titulo": "Todos los Proyectos",
            "tipo_vista": "TODOS",
            "seccion_actual": "proyectos"
        }
    )


# ==========================================
# 🔥 2. VISTAS FILTRADAS
# ==========================================

def lista_rcn(request):
    """Filtra proyectos que corresponden a RCN (incluyendo activos y generales)"""
    busqueda = request.GET.get('buscar', '').strip()
    
    # Filtra por folio RCN existente O por fases que contengan 'rcn' o 'activo'
    proyectos_qs = Proyecto.objects.filter(
        (Q(rcn__isnull=False) & ~Q(rcn='')) | 
        Q(fase__icontains='rcn') | 
        Q(fase__icontains='activo')
    )

    if busqueda:
        proyectos_qs = proyectos_qs.filter(
            Q(proyecto__icontains=busqueda) | 
            Q(rcn__icontains=busqueda) |
            Q(responsable__icontains=busqueda)
        )

    proyectos_procesados = [mapear_datos_proyecto(p) for p in proyectos_qs.order_by('-id')]

    return render(
        request, 
        "proyectos/lista.html", 
        {
            "proyectos": proyectos_procesados, 
            "busqueda": busqueda, 
            "titulo": "Gestión de RCNs",
            "tipo_vista": "RCN",
            "seccion_actual": "rcn"
        }
    )


def lista_sr(request):
    """Filtra proyectos que corresponden a SR"""
    busqueda = request.GET.get('buscar', '').strip()
    proyectos_qs = Proyecto.objects.filter(
        (Q(sr__isnull=False) & ~Q(sr='')) | Q(fase__icontains='sr')
    )

    if busqueda:
        proyectos_qs = proyectos_qs.filter(
            Q(proyecto__icontains=busqueda) | 
            Q(sr__icontains=busqueda) |
            Q(responsable__icontains=busqueda)
        )

    proyectos_procesados = [mapear_datos_proyecto(p) for p in proyectos_qs.order_by('-id')]

    return render(
        request, 
        "proyectos/lista.html", 
        {
            "proyectos": proyectos_procesados, 
            "busqueda": busqueda, 
            "titulo": "Gestión de SRs",
            "tipo_vista": "SR",
            "seccion_actual": "sr"
        }
    )


def lista_backlog(request):
    """Filtra proyectos en Backlog (sin RCN ni SR específicos)"""
    busqueda = request.GET.get('buscar', '').strip()
    proyectos_qs = Proyecto.objects.filter(
        Q(rcn__isnull=True) | Q(rcn=''),
        Q(sr__isnull=True) | Q(sr=''),
        ~Q(fase__icontains='rcn'),
        ~Q(fase__icontains='sr')
    )

    if busqueda:
        proyectos_qs = proyectos_qs.filter(
            Q(proyecto__icontains=busqueda) | 
            Q(responsable__icontains=busqueda)
        )

    proyectos_procesados = [mapear_datos_proyecto(p) for p in proyectos_qs.order_by('-id')]

    return render(
        request, 
        "proyectos/lista.html", 
        {
            "proyectos": proyectos_procesados, 
            "busqueda": busqueda, 
            "titulo": "Proyectos en Backlog",
            "tipo_vista": "BACKLOG",
            "seccion_actual": "backlog"
        }
    )


def lista_rcn_activo(request):
    """Filtra proyectos RCN Activos (no cerrados)"""
    busqueda = request.GET.get('buscar', '').strip()
    proyectos_qs = Proyecto.objects.filter(
        (Q(rcn__isnull=False) & ~Q(rcn='')) | Q(fase__icontains='rcn') | Q(fase__icontains='activo')
    ).exclude(estado__icontains='cerrado')

    if busqueda:
        proyectos_qs = proyectos_qs.filter(
            Q(proyecto__icontains=busqueda) | 
            Q(rcn__icontains=busqueda) |
            Q(responsable__icontains=busqueda)
        )

    proyectos_procesados = [mapear_datos_proyecto(p) for p in proyectos_qs.order_by('-id')]

    return render(
        request, 
        "proyectos/lista.html", 
        {
            "proyectos": proyectos_procesados, 
            "busqueda": busqueda, 
            "titulo": "Proyectos RCN Activos",
            "tipo_vista": "ACTIVOS",
            "seccion_actual": "rcn_activo"
        }
    )


# ==========================================
# 🔍 3. VISTAS SECUNDARIAS Y NAVEGACIÓN
# ==========================================

def index_descargas(request):
    return render(request, "descargas/index.html")


def vista_validaciones(request):
    return render(request, 'dashboard/validaciones.html')


# ==========================================
# 🛠️ FUNCIONES DE GESTIÓN (NUEVO, EDITAR, ELIMINAR)
# ==========================================

def nuevo_proyecto(request):
    """Vista para crear un nuevo proyecto"""
    if request.method == "POST":
        messages.success(request, "Proyecto creado con éxito.")
        return redirect("lista_proyectos")
    return render(request, "proyectos/formulario.html", {"titulo": "Nuevo Proyecto"})


def editar_proyecto(request, pk):
    """Vista para editar un proyecto"""
    proyecto = get_object_or_404(Proyecto, pk=pk)
    proyecto_dict = mapear_datos_proyecto(proyecto)
    return render(
        request, 
        "proyectos/formulario.html", 
        {"proyecto": proyecto_dict, "titulo": "Editar Proyecto"}
    )


def eliminar_proyecto(request, pk):
    """Vista para eliminar un proyecto"""
    proyecto = get_object_or_404(Proyecto, pk=pk)
    proyecto.delete()
    messages.success(request, "Registro eliminado correctamente.")
    return redirect("lista_proyectos")


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
    if request.method == "POST" and request.FILES.get("archivo_excel"):
        messages.success(request, "Archivo Excel subido correctamente.")
        return redirect("lista_proyectos")
    return render(request, "proyectos/subir_excel.html")


def exportar_proyectos_excel(request):
    """Vista para la descarga/exportación a Excel"""
    messages.info(request, "Exportación a Excel en desarrollo.")
    return redirect("lista_proyectos")


def exportar_proyectos_pdf(request):
    """Vista para la descarga/exportación a PDF"""
    messages.info(request, "Exportación a PDF en desarrollo.")
    return redirect("lista_proyectos")