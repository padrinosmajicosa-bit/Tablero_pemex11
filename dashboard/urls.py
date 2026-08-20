from django.urls import path
from . import views

urlpatterns = [
    # Ruta principal del dashboard (si la tienes aquí) o tus otras rutas
    path("", views.inicio, name="dashboard"),
    
    # 📥 Agrega estas rutas junto con las demás dentro de la misma lista:
    path('descargar/excel/', views.descargar_excel, name='descargar_excel'),
    path('descargar/pdf/', views.descargar_pdf, name='descargar_pdf'),
]