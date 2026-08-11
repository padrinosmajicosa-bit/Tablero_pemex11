from django.urls import path
from . import views

urlpatterns = [
    # 📊 Dashboard Principal (Tarjetas y Gráficos)
    path("", views.dashboard, name="dashboard"),

    # 📋 Tabla General con Todos los Proyectos
    path("proyectos/", views.lista_proyectos, name="lista_proyectos"),

    # ✏️ Operaciones CRUD
    path("nuevo/", views.nuevo_proyecto, name="nuevo_proyecto"),
    path("editar/<int:pk>/", views.editar_proyecto, name="editar_proyecto"),
    path("eliminar/<int:pk>/", views.eliminar_proyecto, name="eliminar_proyecto"),

    # 🎯 Rutas de Filtros del Menú Lateral
    path("rcn/", views.lista_rcn, name="lista_rcn"),
    path("sr/", views.lista_sr, name="lista_sr"),
    path("backlog/", views.lista_backlog, name="lista_backlog"),
    path("rcn-activo/", views.lista_rcn_activo, name="lista_rcn_activo"),
    path("validaciones/", views.vista_validaciones, name="vista_validaciones"),

    # 📥 Carga Masiva y Auditoría
    path("descargas/", views.index_descargas, name="index_descargas"),
    path("subir-excel/", views.subir_excel, name="subir_excel"),

    # 📊 Exportadores
    path("exportar/excel/", views.exportar_proyectos_excel, name="exportar_excel"),
    path("exportar/pdf/", views.exportar_proyectos_pdf, name="exportar_pdf"),
]