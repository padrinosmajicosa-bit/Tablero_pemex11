from django.urls import path
from . import views

urlpatterns = [
    # Tu ruta actual de la pantalla de descargas...
    path('', views.index, name='descargas_index'), 
    
    # Ruta para procesar la subida masiva del formulario
    path('subir/', views.subir_excel, name='subir_excel'),
    
    # 🔥 NUEVA RUTA:
    path('exportar/excel/', views.exportar_proyectos_excel, name='exportar_excel'),

# 🔥 NUEVA RUTA PARA PDF:
    path('exportar/pdf/', views.exportar_proyectos_pdf, name='exportar_pdf'),


]


    
    