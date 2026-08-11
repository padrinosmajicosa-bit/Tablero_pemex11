from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # 1. Ruta del Administrador de Django
    path('admin/', admin.site.urls),
    
    # 2. Ruta del Dashboard/Inicio
    path('', include('dashboard.urls')),
    
    # 3. Ruta de la aplicación de Proyectos
    path('proyectos/', include('proyectos.urls')),
    
    # 4. Ruta de la aplicación de Descargas (Carga masiva / Reportes)
    path('descargas/', include('descargas.urls')),
]


