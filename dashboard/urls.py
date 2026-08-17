from django.urls import path
from . import views

urlpatterns = [
    # Redirige a la vista del dashboard principal
    path("", views.dashboard, name="dashboard"),
]