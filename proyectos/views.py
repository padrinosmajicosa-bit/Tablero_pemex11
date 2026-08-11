import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q

from .models import Proyecto
from descargas.models import RegistroCarga
from .forms import ProyectoForm

# ReportLab para PDF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


# ==========================================
# 📌 1. DASHBOARD Y LISTA PRINCIPAL
# ==========================================

def dashboard(request):
    """
    📊 Vista principal del Dashboard
    """
    total_proyectos = Proyecto.objects.count()
    total_rcn = Proyecto.objects.filter(rcn__isnull=False).exclude(rcn="").count()
    total_sr = Proyecto.objects.filter(sr__isnull=False).exclude(sr="").filter(Q(rcn="") | Q(rcn__isnull=True)).count()
    total_backlog = Proyecto.objects.filter(estado__iexact='inicial').filter(
        (Q(rcn="") | Q(rcn__isnull=True)) & (Q(sr="") | Q(sr__isnull=True))
    ).count()
    total_rcn_activo = Proyecto.objects.filter(estado__iexact='en_proceso').filter(
        (Q(rcn="") | Q(rcn__isnull=True)) & (Q(sr="") | Q(sr__isnull=True))
    ).count()

    contexto = {
        "total_proyectos": total_proyectos,
        "total_rcn": total_rcn,
        "total_sr": total_sr,
        "total_backlog": total_backlog,
        "total_rcn_activo": total_rcn_activo,
        "seccion_actual": "dashboard",
    }
    return redirect('/')


def lista_proyectos(request):
    """
    📋 Vista con la tabla general de Todos los Proyectos
    """
    busqueda = request.GET.get('buscar', '').strip()
    proyectos = Proyecto.objects.all()

    if busqueda:
        proyectos = proyectos.filter(
            Q(rcn__icontains=busqueda) | 
            Q(sr__icontains=busqueda) |
            Q(proyecto__icontains=busqueda) | 
            Q(responsable__icontains=busqueda)
        )

    return render(
        request, 
        "proyectos/lista.html", 
        {
            "proyectos": proyectos.order_by('-id'), 
            "busqueda": busqueda, 
            "titulo_seccion": "Todos los Proyectos",
            "seccion_actual": "proyectos"
        }
    )


# ==========================================
# ✏️ 2. OPERACIONES CRUD (CREAR, EDITAR, ELIMINAR)
# ==========================================

def nuevo_proyecto(request):
    if request.method == "POST":
        formulario = ProyectoForm(request.POST)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "¡Proyecto creado correctamente!")
            return redirect("lista_proyectos")
    else:
        formulario = ProyectoForm()

    return render(
        request,
        "proyectos/formulario.html",
        {"formulario": formulario}
    )


def editar_proyecto(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)

    if request.method == "POST":
        formulario = ProyectoForm(request.POST, instance=proyecto)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "¡Proyecto actualizado correctamente!")
            return redirect("lista_proyectos")
    else:
        formulario = ProyectoForm(instance=proyecto)

    return render(
        request,
        "proyectos/formulario.html",
        {
            "formulario": formulario,
            "proyecto": proyecto
        }
    )


def eliminar_proyecto(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)

    if request.method == "POST":
        proyecto.delete()
        messages.success(request, "El proyecto fue eliminado con éxito.")
        return redirect("lista_proyectos")

    return render(
        request, 
        "proyectos/confirmar_eliminar.html", 
        {"proyecto": proyecto}
    )


# ==========================================
# 🔥 3. VISTAS FILTRADAS
# ==========================================

def lista_rcn(request):
    busqueda = request.GET.get('buscar', '').strip()
    proyectos = Proyecto.objects.filter(rcn__isnull=False).exclude(rcn="")

    if busqueda:
        proyectos = proyectos.filter(
            Q(rcn__icontains=busqueda) | 
            Q(proyecto__icontains=busqueda) | 
            Q(responsable__icontains=busqueda)
        )

    return render(
        request, 
        "proyectos/lista.html", 
        {
            "proyectos": proyectos.order_by('-id'), 
            "busqueda": busqueda, 
            "titulo_seccion": "Gestión de RCNs",
            "seccion_actual": "rcn"
        }
    )


def lista_sr(request):
    busqueda = request.GET.get('buscar', '').strip()
    proyectos = Proyecto.objects.filter(
        sr__isnull=False
    ).exclude(
        sr=""
    ).filter(
        Q(rcn="") | Q(rcn__isnull=True)
    )

    if busqueda:
        proyectos = proyectos.filter(
            Q(sr__icontains=busqueda) | 
            Q(proyecto__icontains=busqueda) | 
            Q(responsable__icontains=busqueda)
        )

    return render(
        request, 
        "proyectos/lista.html", 
        {
            "proyectos": proyectos.order_by('-id'), 
            "busqueda": busqueda, 
            "titulo_seccion": "Gestión de SRs",
            "seccion_actual": "sr"
        }
    )


def lista_backlog(request):
    busqueda = request.GET.get('buscar', '').strip()
    proyectos = Proyecto.objects.filter(
        estado__iexact='inicial'
    ).filter(
        (Q(rcn="") | Q(rcn__isnull=True)) & (Q(sr="") | Q(sr__isnull=True))
    )

    if busqueda:
        proyectos = proyectos.filter(
            Q(proyecto__icontains=busqueda) | 
            Q(responsable__icontains=busqueda)
        )

    return render(
        request, 
        "proyectos/lista.html", 
        {
            "proyectos": proyectos.order_by('-id'), 
            "busqueda": busqueda, 
            "titulo_seccion": "Proyectos en Backlog (Inicial)",
            "seccion_actual": "backlog"
        }
    )


def lista_rcn_activo(request):
    busqueda = request.GET.get('buscar', '').strip()
    proyectos = Proyecto.objects.filter(
        estado__iexact='en_proceso'
    ).filter(
        (Q(rcn="") | Q(rcn__isnull=True)) & (Q(sr="") | Q(sr__isnull=True))
    )

    if busqueda:
        proyectos = proyectos.filter(
            Q(proyecto__icontains=busqueda) | 
            Q(responsable__icontains=busqueda)
        )

    return render(
        request, 
        "proyectos/lista.html", 
        {
            "proyectos": proyectos.order_by('-id'), 
            "busqueda": busqueda, 
            "titulo_seccion": "Proyectos RCN Activos (En Proceso)",
            "seccion_actual": "rcn_activo"
        }
    )


def vista_validaciones(request):
    proyectos = Proyecto.objects.filter(
        Q(responsable__isnull=True) | Q(responsable='Sin asignar') | Q(responsable='') |
        Q(proyecto__isnull=True) | Q(proyecto='')
    ).order_by('-id')

    return render(
        request, 
        "proyectos/lista.html", 
        {
            "proyectos": proyectos, 
            "titulo_seccion": "Validación de Inconsistencias",
            "seccion_actual": "validaciones"
        }
    )


# ==========================================
# 📥 4. CARGA MASIVA DE EXCEL
# ==========================================

def index_descargas(request):
    return render(request, "descargas/index.html")


def subir_excel(request):
    if request.method == "POST" and request.FILES.get("archivo_excel"):
        archivo = request.FILES["archivo_excel"]
        nombre_archivo = archivo.name.lower()

        # 1. Validación de extensión del archivo
        if not (nombre_archivo.endswith('.xlsx') or nombre_archivo.endswith('.xls')):
            messages.error(request, "Error: El archivo no es un formato de Excel válido (.xlsx o .xls).")
            return redirect('subir_excel')

        # 2. Registrar el intento de carga en la base de datos
        registro = RegistroCarga.objects.create(
            archivo=archivo,
            usuario=request.user if request.user.is_authenticated else None,
            estado_carga='En Proceso'
        )

        try:
            # 3. Leer archivo con pandas y limpiar nombres de columnas
            df = pd.read_excel(archivo)
            df.columns = df.columns.astype(str).str.strip()
            contador_registros = 0

            for idx, fila in df.iterrows():
                val_rcn = ""
                val_sr = ""

                # Obtener categoría si existe
                categoria = str(fila['Categoría']).strip().upper() if 'Categoría' in df.columns and pd.notna(fila['Categoría']) else ""

                # --- LÓGICA MEJORADA DE LECTURA Y SEPARACIÓN DE FOLIOS (RCN / SR) ---
                if 'Folio (RCN / SR)' in df.columns:
                    folio_txt = str(fila['Folio (RCN / SR)']).strip() if pd.notna(fila['Folio (RCN / SR)']) else ""
                    
                    if folio_txt.endswith('.0'):
                        folio_txt = folio_txt[:-2]

                    if folio_txt.lower() in ['nan', '—', 'none', '']:
                        folio_txt = ""

                    if folio_txt:
                        # Si la celda contiene ambas nomenclaturas (ej: "RCN-123 / SR-456" o "RCN-SR")
                        if 'RCN' in folio_txt.upper() and 'SR' in folio_txt.upper():
                            partes = folio_txt.replace('/', '-').split('-')
                            for parte in partes:
                                p_clean = parte.strip()
                                if 'RCN' in p_clean.upper():
                                    val_rcn = p_clean
                                elif 'SR' in p_clean.upper():
                                    val_sr = p_clean
                        # Si es explícitamente un RCN
                        elif folio_txt.upper().startswith('RCN') or 'RCN' in categoria:
                            val_rcn = folio_txt
                            val_sr = ""
                        # Si es únicamente un SR o un número de folio SR
                        else:
                            val_sr = folio_txt
                            val_rcn = ""
                else:
                    # Lectura si vienen en columnas independientes 'RCN' y 'SR'
                    if 'RCN' in df.columns and pd.notna(fila['RCN']):
                        rcn_str = str(fila['RCN']).strip()
                        if rcn_str.endswith('.0'):
                            rcn_str = rcn_str[:-2]
                        if rcn_str.lower() not in ['nan', '—', 'none', '']:
                            val_rcn = rcn_str

                    if 'SR' in df.columns and pd.notna(fila['SR']):
                        sr_str = str(fila['SR']).strip()
                        if sr_str.endswith('.0'):
                            sr_str = sr_str[:-2]
                        if sr_str.lower() not in ['nan', '—', 'none', '']:
                            val_sr = sr_str

                # --- PROYECTO ---
                if 'Nombre / Descripción del Proyecto' in df.columns:
                    val_proyecto = str(fila['Nombre / Descripción del Proyecto']).strip() if pd.notna(fila['Nombre / Descripción del Proyecto']) else ""
                elif 'Proyecto' in df.columns:
                    val_proyecto = str(fila['Proyecto']).strip() if pd.notna(fila['Proyecto']) else ""
                else:
                    val_proyecto = ""

                if val_proyecto.lower() in ['nan', 'sin nombre asignado', 'none']:
                    val_proyecto = ""

                # --- RESPONSABLE ---
                val_responsable = str(fila['Responsable']).strip() if 'Responsable' in df.columns and pd.notna(fila['Responsable']) and str(fila['Responsable']).strip().lower() not in ['nan', 'none'] else "Sin asignar"

                # --- ESTADO ---
                if 'Estado' in df.columns and pd.notna(fila['Estado']) and str(fila['Estado']).strip().lower() not in ['nan', 'none']:
                    val_estado = str(fila['Estado']).strip().lower().replace(' ', '_')
                else:
                    val_estado = 'inicial'

                # --- PRIORIDAD ---
                val_prioridad = str(fila['Prioridad']).strip().lower() if 'Prioridad' in df.columns and pd.notna(fila['Prioridad']) and str(fila['Prioridad']).strip().lower() not in ['nan', 'none'] else 'media'

                # Omitir filas que no tengan información relevante
                if not (val_rcn or val_sr or val_proyecto or (val_responsable and val_responsable != "Sin asignar")):
                    continue

                # --- BÚSQUEDA Y PREVENCIÓN DE DUPLICADOS ---
                proyectos_existentes = Proyecto.objects.none()

                if val_rcn and val_sr:
                    proyectos_existentes = Proyecto.objects.filter(rcn=val_rcn, sr=val_sr)
                elif val_rcn:
                    proyectos_existentes = Proyecto.objects.filter(rcn=val_rcn)
                elif val_sr:
                    proyectos_existentes = Proyecto.objects.filter(sr=val_sr)
                elif val_proyecto and val_responsable != "Sin asignar":
                    proyectos_existentes = Proyecto.objects.filter(proyecto=val_proyecto, responsable=val_responsable)
                elif val_proyecto:
                    proyectos_existentes = Proyecto.objects.filter(proyecto=val_proyecto)

                # --- ACTUALIZAR O CREAR ---
                if proyectos_existentes.exists():
                    p_obj = proyectos_existentes.first()
                    p_obj.rcn = val_rcn
                    p_obj.sr = val_sr
                    p_obj.proyecto = val_proyecto
                    p_obj.responsable = val_responsable
                    p_obj.estado = val_estado
                    p_obj.prioridad = val_prioridad
                    p_obj.save()

                    # Eliminar duplicados adicionales si existían previamente en la base de datos
                    if proyectos_existentes.count() > 1:
                        proyectos_existentes.exclude(id=p_obj.id).delete()
                else:
                    Proyecto.objects.create(
                        rcn=val_rcn,
                        sr=val_sr,
                        proyecto=val_proyecto,
                        responsable=val_responsable,
                        estado=val_estado,
                        prioridad=val_prioridad
                    )
                    contador_registros += 1

            # 4. Finalización exitosa
            registro.registros_creados = contador_registros
            registro.estado_carga = 'Exitoso'
            registro.save()

            messages.success(request, f"¡Éxito! Archivo procesado correctamente. Nuevos registros agregados: {contador_registros}.")
            return redirect('lista_proyectos')

        except Exception as e:
            # 5. Manejo de excepciones durante la lectura/carga
            registro.estado_carga = 'Fallido'
            registro.save()
            messages.error(request, f"Error al procesar el archivo Excel: {str(e)}")
            return redirect('subir_excel')

    return render(request, "descargas/index.html")


# ==========================================
# 📊 5. EXPORTADORES (EXCEL Y PDF)
# ==========================================

def exportar_proyectos_excel(request):
    busqueda = request.GET.get('buscar', '').strip()
    proyectos = Proyecto.objects.all().order_by('-id')

    if busqueda:
        proyectos = proyectos.filter(
            Q(rcn__icontains=busqueda) | 
            Q(sr__icontains=busqueda) |
            Q(proyecto__icontains=busqueda) | 
            Q(responsable__icontains=busqueda)
        )

    datos_excel = []

    for p in proyectos:
        folio = p.rcn if (p.rcn and p.rcn.strip()) else (p.sr if (p.sr and p.sr.strip()) else "—")

        if p.rcn and p.rcn.strip():
            categoria = "RCN"
        elif p.sr and str(p.sr).upper().startswith('SR'):
            categoria = "SR"
        elif p.estado and str(p.estado).lower() == 'en_proceso':
            categoria = "RCN ACTIVO"
        else:
            categoria = "BACKLOG"

        estado_map = {
            'en_proceso': 'En Proceso',
            'concluido': 'Concluido',
            'cancelado': 'Cancelado',
            'inicial': 'Inicial'
        }
        estado_texto = estado_map.get(str(p.estado).lower(), str(p.estado).title() if p.estado else "Inicial")
        prioridad_texto = str(p.prioridad).capitalize() if p.prioridad else "Media"

        datos_excel.append({
            'Categoría': categoria,
            'Folio (RCN / SR)': folio,
            'Nombre / Descripción del Proyecto': p.proyecto or "Sin nombre asignado",
            'Responsable': p.responsable or "Sin asignar",
            'Estado': estado_texto,
            'Prioridad': prioridad_texto
        })

    df = pd.DataFrame(datos_excel)

    if df.empty:
        df = pd.DataFrame(columns=[
            'Categoría', 'Folio (RCN / SR)', 'Nombre / Descripción del Proyecto', 
            'Responsable', 'Estado', 'Prioridad'
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Reporte_General_Proyectos.xlsx"'

    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Proyectos Activos')

    return response


def exportar_proyectos_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Reporte_General_Proyectos.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    styles = getSampleStyleSheet()

    titulo_style = ParagraphStyle(
        'TituloReporte',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1a4d38'),
        spaceAfter=12
    )

    story.append(Paragraph("Tablero Control de Proyectos", titulo_style))
    story.append(Paragraph("Reporte Ejecutivo de Estatus General en Base de Datos", styles['Normal']))
    story.append(Spacer(1, 15))

    proyectos = Proyecto.objects.all().order_by('-id')
    datos_tabla = [['Categoría', 'Folio', 'Proyecto', 'Responsable', 'Estado', 'Prioridad']]

    for p in proyectos:
        fol = p.rcn if (p.rcn and p.rcn.strip()) else (p.sr if (p.sr and p.sr.strip()) else "—")

        if p.rcn and p.rcn.strip():
            cat = "RCN"
        elif p.sr and str(p.sr).upper().startswith('SR'):
            cat = "SR"
        elif p.estado and str(p.estado).lower() == 'en_proceso':
            cat = "RCN ACTIVO"
        else:
            cat = "BACKLOG"

        datos_tabla.append([
            cat,
            fol,
            p.proyecto or "Sin nombre",
            p.responsable if p.responsable else 'Sin asignar',
            str(p.estado).replace('_', ' ').title() if p.estado else 'Inicial',
            str(p.prioridad).capitalize() if p.prioridad else 'Media'
        ])

    tabla_reporte = Table(datos_tabla, colWidths=[70, 70, 150, 100, 80, 70])
    style_table = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a4d38')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])
    tabla_reporte.setStyle(style_table)
    story.append(tabla_reporte)

    doc.build(story)
    return response