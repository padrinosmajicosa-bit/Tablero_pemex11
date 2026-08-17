from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # 1. Administrador de Django
    path('admin/', admin.site.urls),
    
    # 2. Rutas principales (conecta todo a la app proyectos)
    path('', include('proyectos.urls')),
]
