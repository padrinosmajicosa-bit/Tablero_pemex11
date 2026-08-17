from django.urls import path
from . import views

urlpatterns = [
    # 📊 Dashboard Principal
    path("", views.dashboard, name="dashboard"),

    # 📋 Tabla General con Todos los Proyectos
    path("proyectos/", views.lista_proyectos, name="lista_proyectos"),

    # ✏️ Operaciones CRUD
    path("nuevo/", views.nuevo_proyecto, name="nuevo_proyecto"),
    path("detalle/<int:pk>/", views.detalle_proyecto, name="detalle_proyecto"),
    path("editar/<int:pk>/", views.editar_proyecto, name="editar_proyecto"),
    path("eliminar/<int:pk>/", views.eliminar_proyecto, name="eliminar_proyecto"),

    # 🎯 Rutas de Filtros y Módulos
    path("rcn/", views.lista_rcn, name="lista_rcn"),
    path("sr/", views.lista_sr, name="lista_sr"),
    path("backlog/", views.lista_backlog, name="lista_backlog"),
    path("rcn-activo/", views.lista_rcn_activo, name="lista_rcn_activo"),
    path("validaciones/", views.vista_validaciones, name="vista_validaciones"),

    # 📥 Carga Masiva y Descargas
    path("descargas/", views.index_descargas, name="index_descargas"),
    path("subir-excel/", views.subir_excel, name="subir_excel"),

    # 📊 Exportadores (Compatibilidad para 'exportar_excel' y 'exportar_proyectos_excel')
    path("exportar/excel/", views.exportar_proyectos_excel, name="exportar_excel"),
    path("exportar/excel-proyectos/", views.exportar_proyectos_excel, name="exportar_proyectos_excel"),
    path("exportar/pdf/", views.exportar_proyectos_pdf, name="exportar_pdf"),
    path("exportar/pdf-proyectos/", views.exportar_proyectos_pdf, name="exportar_proyectos_pdf"),
]