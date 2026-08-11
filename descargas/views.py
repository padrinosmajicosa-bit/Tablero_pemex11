from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse  # Necesario para descargar archivos
from django.db.models import Q
from proyectos.models import Proyecto  # Modelo donde se guardan los proyectos
from .models import RegistroCarga      # Historial de auditoría
import pandas as pd

# Elementos necesarios de ReportLab para el PDF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


# ==========================================
# 📌 1. VISTAS DE NAVEGACIÓN (BARRA LATERAL)
# ==========================================

# A. Dashboard General / Lista Completa
def lista_proyectos(request):
    query = request.GET.get('q', '').strip()
    proyectos = Proyecto.objects.all().order_by('-id')

    if query:
        proyectos = proyectos.filter(
            Q(rcn__icontains=query) |
            Q(sr__icontains=query) |
            Q(proyecto__icontains=query) |
            Q(responsable__icontains=query)
        )

    context = {
        'proyectos': proyectos,
        'titulo_seccion': 'Todos los Proyectos',
        'seccion_actual': 'dashboard',
        'query': query,
    }
    return render(request, "proyectos/lista_proyectos.html", context)


# B. Módulo RCN (Registros con RCN asignado)
def vista_rcn(request):
    query = request.GET.get('q', '').strip()
    proyectos = Proyecto.objects.filter(rcn__isnull=False).exclude(rcn='').exclude(rcn='—').order_by('-id')

    if query:
        proyectos = proyectos.filter(
            Q(rcn__icontains=query) |
            Q(proyecto__icontains=query) |
            Q(responsable__icontains=query)
        )

    context = {
        'proyectos': proyectos,
        'titulo_seccion': 'Proyectos RCN',
        'seccion_actual': 'rcn',
        'query': query,
    }
    return render(request, "proyectos/lista_proyectos.html", context)


# C. Módulo SR (Registros con SR asignado)
def vista_sr(request):
    query = request.GET.get('q', '').strip()
    proyectos = Proyecto.objects.filter(sr__isnull=False).exclude(sr='').exclude(sr='—').order_by('-id')

    if query:
        proyectos = proyectos.filter(
            Q(sr__icontains=query) |
            Q(proyecto__icontains=query) |
            Q(responsable__icontains=query)
        )

    context = {
        'proyectos': proyectos,
        'titulo_seccion': 'Solicitudes de Requerimiento (SR)',
        'seccion_actual': 'sr',
        'query': query,
    }
    return render(request, "proyectos/lista_proyectos.html", context)


# D. Módulo Backlog (Proyectos en fase inicial o sin folio RCN/SR)
def vista_backlog(request):
    query = request.GET.get('q', '').strip()
    proyectos = Proyecto.objects.filter(
        Q(rcn__isnull=True) | Q(rcn='') | Q(rcn='—'),
        Q(sr__isnull=True) | Q(sr='') | Q(sr='—')
    ).exclude(estado='en_proceso').order_by('-id')

    if query:
        proyectos = proyectos.filter(
            Q(proyecto__icontains=query) |
            Q(responsable__icontains=query)
        )

    context = {
        'proyectos': proyectos,
        'titulo_seccion': 'Backlog de Proyectos',
        'seccion_actual': 'backlog',
        'query': query,
    }
    return render(request, "proyectos/lista_proyectos.html", context)


# E. Módulo RCN Activo (Proyectos con estado 'en_proceso')
def vista_rcn_activo(request):
    query = request.GET.get('q', '').strip()
    proyectos = Proyecto.objects.filter(estado='en_proceso').order_by('-id')

    if query:
        proyectos = proyectos.filter(
            Q(rcn__icontains=query) |
            Q(sr__icontains=query) |
            Q(proyecto__icontains=query) |
            Q(responsable__icontains=query)
        )

    context = {
        'proyectos': proyectos,
        'titulo_seccion': 'Proyectos RCN Activos',
        'seccion_actual': 'rcn_activo',
        'query': query,
    }
    return render(request, "proyectos/lista_proyectos.html", context)


# F. Módulo Validaciones
def vista_validaciones(request):
    # Filtra proyectos sin responsable asignado o sin nombre para corregir inconsistencias
    proyectos = Proyecto.objects.filter(
        Q(responsable__isnull=True) | Q(responsable='Sin asignar') |
        Q(proyecto__isnull=True) | Q(proyecto='')
    ).order_by('-id')

    context = {
        'proyectos': proyectos,
        'titulo_seccion': 'Validación de Inconsistencias',
        'seccion_actual': 'validaciones',
    }
    return render(request, "proyectos/lista_proyectos.html", context)


# G. Módulo Reportes (Vista de resumen y exportación)
def vista_reportes(request):
    return render(request, "descargas/index.html")


# ==========================================
# 📥 2. PANTALLA PRINCIPAL DE DESCARGAS
# ==========================================
def index(request):
    return render(request, "descargas/index.html")


# ==========================================
# 🔄 3. MOTOR DE CARGA MASIVA SEGURO Y FLEXIBLE
# ==========================================
def subir_excel(request):
    if request.method == "POST" and request.FILES.get("archivo_excel"):
        archivo = request.FILES["archivo_excel"]
        nombre_archivo = archivo.name.lower()

        if not (nombre_archivo.endswith('.xlsx') or nombre_archivo.endswith('.xls')):
            messages.error(request, "Error: El archivo seleccionado no es un formato de Excel válido (.xlsx o .xls).")
            return redirect('subir_excel')
        
        registro = RegistroCarga.objects.create(
            archivo=archivo,
            usuario=request.user if request.user.is_authenticated else None,
            estado_carga='En Proceso'
        )
        
        try:
            df = pd.read_excel(archivo)
            df.columns = df.columns.astype(str).str.strip()

            contador_registros = 0
            
            for idx, fila in df.iterrows():
                val_rcn = ""
                val_sr = ""
                
                if 'Folio (RCN / SR)' in df.columns:
                    folio_txt = str(fila['Folio (RCN / SR)']).strip() if pd.notna(fila['Folio (RCN / SR)']) else ""
                    if folio_txt.upper().startswith('RCN'):
                        val_rcn = folio_txt
                    elif folio_txt.upper().startswith('SR'):
                        val_sr = folio_txt
                else:
                    if 'RCN' in df.columns and pd.notna(fila['RCN']) and str(fila['RCN']).strip().lower() not in ['nan', '—', '']:
                        val_rcn = str(fila['RCN']).strip()
                    if 'SR' in df.columns and pd.notna(fila['SR']) and str(fila['SR']).strip().lower() not in ['nan', '—', '']:
                        val_sr = str(int(fila['SR'])).strip() if isinstance(fila['SR'], (int, float)) else str(fila['SR']).strip()

                if 'Nombre / Descripción del Proyecto' in df.columns:
                    val_proyecto = str(fila['Nombre / Descripción del Proyecto']).strip() if pd.notna(fila['Nombre / Descripción del Proyecto']) else ""
                elif 'Proyecto' in df.columns:
                    val_proyecto = str(fila['Proyecto']).strip() if pd.notna(fila['Proyecto']) else ""
                else:
                    val_proyecto = ""
                
                if val_proyecto.lower() in ['nan', 'sin nombre asignado']:
                    val_proyecto = ""

                val_responsable = str(fila['Responsable']).strip() if 'Responsable' in df.columns and pd.notna(fila['Responsable']) and str(fila['Responsable']).strip().lower() != 'nan' else "Sin asignar"
                
                if 'Estado' in df.columns and pd.notna(fila['Estado']) and str(fila['Estado']).strip().lower() != 'nan':
                    val_estado = str(fila['Estado']).strip().lower().replace(' ', '_')
                else:
                    val_estado = 'inicial'

                val_prioridad = str(fila['Prioridad']).strip().lower() if 'Prioridad' in df.columns and pd.notna(fila['Prioridad']) and str(fila['Prioridad']).strip().lower() != 'nan' else 'media'

                if not (val_rcn or val_sr or val_proyecto or (val_responsable and val_responsable != "Sin asignar")):
                    continue

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
                else:
                    proyectos_existentes = Proyecto.objects.none()

                if proyectos_existentes.exists():
                    p_obj = proyectos_existentes.first()
                    p_obj.rcn = val_rcn
                    p_obj.sr = val_sr
                    p_obj.proyecto = val_proyecto
                    p_obj.responsable = val_responsable
                    p_obj.estado = val_estado
                    p_obj.prioridad = val_prioridad
                    p_obj.save()
                    
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

            registro.registros_creados = contador_registros
            registro.estado_carga = 'Exitoso'
            registro.save()
            
            messages.success(request, f"¡Éxito! Archivo procesado correctamente. Nuevos registros agregados: {contador_registros}.")
            return redirect('lista_proyectos')

        except Exception as e:
            registro.estado_carga = 'Fallido'
            registro.save()
            messages.error(request, f"Error al procesar el archivo Excel: {str(e)}")
            return redirect('subir_excel')

    if request.method == "POST":
        messages.warning(request, "Por favor, selecciona un archivo de Excel antes de presionar el botón.")
        
    return render(request, "descargas/index.html")


# ==========================================
# 📊 4. EXPORTADOR DE REPORTES A EXCEL
# ==========================================
def exportar_proyectos_excel(request):
    proyectos = Proyecto.objects.all().order_by('-id')
    datos_excel = []
    
    for p in proyectos:
        if p.rcn and str(p.rcn).strip():
            categoria = "RCN"
        elif p.sr and str(p.sr).strip():
            categoria = "SR"
        elif p.estado and str(p.estado).lower() == 'en_proceso':
            categoria = "RCN ACTIVO"
        else:
            categoria = "BACKLOG"
            
        folio = p.rcn if (p.rcn and str(p.rcn).strip()) else (p.sr if (p.sr and str(p.sr).strip()) else "—")
        
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


# ==========================================
# 📄 5. EXPORTADOR DE REPORTES A PDF
# ==========================================
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
        if p.rcn and str(p.rcn).strip():
            cat = "RCN"
        elif p.sr and str(p.sr).strip():
            cat = "SR"
        elif p.estado and str(p.estado).lower() == 'en_proceso':
            cat = "RCN ACTIVO"
        else:
            cat = "BACKLOG"
            
        fol = p.rcn if (p.rcn and str(p.rcn).strip()) else (p.sr if (p.sr and str(p.sr).strip()) else "—")
        
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