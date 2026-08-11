from django.db import models


class Proyecto(models.Model):
    rcn = models.CharField(max_length=50, blank=True, null=True)
    sr = models.CharField(max_length=50, blank=True, null=True)
    proyecto = models.CharField(max_length=255, blank=True, null=True)
    responsable = models.CharField(max_length=150, blank=True, null=True)
    estado = models.CharField(max_length=100, blank=True, null=True)
    prioridad = models.CharField(max_length=50, blank=True, null=True)
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)
    fase = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = "proyectos"
        managed = False  # Mantiene la tabla administrada externamente (ej. PostgreSQL previa)

    def __str__(self):
        return self.proyecto or f"Proyecto {self.id}"