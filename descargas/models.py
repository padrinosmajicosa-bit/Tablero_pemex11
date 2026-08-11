from django.db import models
from django.contrib.auth.models import User

class RegistroCarga(models.Model):
    archivo = models.FileField(upload_to='cargas_excel/')
    fecha_subida = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    registros_creados = models.IntegerField(default=0)
    estado_carga = models.CharField(max_length=50, default='Exitoso')

    def __str__(self):
        return f"Carga {self.id} - {self.fecha_subida.strftime('%d/%m/%Y %H:%M')}"