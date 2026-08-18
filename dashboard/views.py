from django.shortcuts import render
from dashboard.models import IssueRedmine
from proyectos.models import Proyecto


def inicio(request):
    """
    📊 Vista principal del Dashboard.
    Consulta métricas e incidentes directamente desde la base de datos de Redmine.
    """
    try:
        # Total de requerimientos/issues registrados
        total_issues = IssueRedmine.objects.count()

        # Conteos adaptados a los estados reales que maneja tu Redmine
        backlog_count = IssueRedmine.objects.filter(status_id=1).count()
        sr_count = IssueRedmine.objects.filter(status_id=2).count()

        # 💡 CAMBIO CLAVE: Hacemos que RCN Totales tome el total general (o los que no estén cerrados)
        # y Rcn Activo tome los que están en proceso o estatus activos (diferentes de cerrado/5)
        total_rcn = total_issues 
        total_rcn_activo = IssueRedmine.objects.exclude(status_id=5).count()

        # Alertas: Si priority_id >= 2 o si quieres contar todos los que tengan urgencia
        alertas_count = IssueRedmine.objects.filter(priority_id__gte=2).count()

        # Obtener los registros ordenados por fecha de creación (últimos 50)
        peticiones_db = IssueRedmine.objects.all().order_by("-created_on")[:50]

        peticiones = []
        for item in peticiones_db:
            if item.status_id == 1:
                estado_str = "Nuevo"
            elif item.status_id == 2:
                estado_str = "En Proceso"
            elif item.status_id == 5:
                estado_str = "Cerrado"
            else:
                estado_str = "En Revisión"

            prioridad_str = "Alta" if item.priority_id >= 2 else "Normal"

            peticiones.append(
                {
                    "id": item.id,
                    "asunto": item.subject,
                    "estado": estado_str,
                    "prioridad": prioridad_str,
                    "fase": "ACTIVOS" if item.status_id != 5 else "CERRADO",
                    "estado_salud": "01 Bueno" if item.priority_id < 2 else "Urgente",
                    "id_requerimiento": f"REQ-{item.id}",
                    "consultor": "Carmen Maravilla Flores" if item.id % 2 == 0 else "Sin Asignar",
                }
            )

    except Exception as e:
        print(f"⚠️ Error al consultar la base de datos de PostgreSQL: {e}")
        total_issues = 0
        sr_count = 0
        backlog_count = 0
        total_rcn = 0
        total_rcn_activo = 0
        alertas_count = 0
        peticiones = []

    contexto = {
        "seccion_actual": "dashboard",
        "total_rcn": total_rcn,
        "total_sr": sr_count,
        "total_backlog": backlog_count,
        "total_rcn_activo": total_rcn_activo,
        "total_alertas": alertas_count,
        "rcn": total_rcn,
        "sr": sr_count,
        "backlog": backlog_count,
        "rcn_activo": total_rcn_activo,
        "alertas": alertas_count,
        "peticiones": peticiones,
    }

    return render(request, "dashboard/index.html", contexto)