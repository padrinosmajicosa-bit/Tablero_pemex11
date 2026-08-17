from django.shortcuts import render
from dashboard.models import IssueRedmine
from proyectos.models import Proyecto


def inicio(request):
    """
    📊 Vista principal del Dashboard.
    Consulta métricas e incidentes directamente desde la base de datos de Redmine.
    """
    # -------------------------------------------------------------
    # 1. CONSULTA DIRECTA A POSTGRESQL (Tabla 'issues' de Redmine)
    # -------------------------------------------------------------
    try:
        # Total de requerimientos/issues registrados
        total_issues = IssueRedmine.objects.count()

        # Conteos por estado (1: Nuevo/Backlog, 2: En Proceso/SR)
        backlog_count = IssueRedmine.objects.filter(status_id=1).count()
        sr_count = IssueRedmine.objects.filter(status_id=2).count()

        # Conteo de prioridades altas u urgentes (priority_id >= 2)
        alertas_count = IssueRedmine.objects.filter(priority_id__gte=2).count()

        # Obtener los registros ordenados por fecha de creación (últimos 50)
        peticiones_db = IssueRedmine.objects.all().order_by("-created_on")[:50]

        peticiones = []
        for item in peticiones_db:
            # Mapeo de estados según status_id
            if item.status_id == 1:
                estado_str = "Nuevo"
            elif item.status_id == 2:
                estado_str = "En Proceso"
            elif item.status_id == 5:
                estado_str = "Cerrado"
            else:
                estado_str = "En Revisión"

            # Mapeo de prioridades según priority_id
            prioridad_str = "Alta" if item.priority_id >= 2 else "Normal"

            peticiones.append(
                {
                    "id": item.id,
                    "asunto": item.subject,
                    "estado": estado_str,
                    "prioridad": prioridad_str,
                    "fase": "-",
                    "estado_salud": "Estable",
                    "id_requerimiento": f"REQ-{item.id}",
                    "consultor": "Sin Asignar",
                }
            )

    except Exception as e:
        print(f"⚠️ Error al consultar la base de datos de PostgreSQL: {e}")
        total_issues = 0
        sr_count = 0
        backlog_count = 0
        alertas_count = 0
        peticiones = []

    # -------------------------------------------------------------
    # 2. ENVIAR CONTEXTO AL TEMPLATE
    # -------------------------------------------------------------
    contexto = {
        "rcn": total_issues,
        "sr": sr_count,
        "backlog": backlog_count,
        "alertas": alertas_count,
        "peticiones": peticiones,
    }

    return render(request, "dashboard/index.html", contexto)