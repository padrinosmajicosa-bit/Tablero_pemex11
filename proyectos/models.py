from django.db import models


class Proyecto(models.Model):
    rcn = models.CharField(max_length=50, blank=True, null=True, verbose_name="Folio RCN")
    sr = models.CharField(max_length=50, blank=True, null=True, verbose_name="Folio SR")
    proyecto = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nombre del Proyecto")
    responsable = models.CharField(max_length=150, blank=True, null=True, verbose_name="Responsable")
    estado = models.CharField(max_length=100, blank=True, null=True, verbose_name="Estado")
    prioridad = models.CharField(max_length=50, blank=True, null=True, verbose_name="Prioridad")
    fecha_inicio = models.DateField(blank=True, null=True, verbose_name="Fecha de Inicio")
    fecha_fin = models.DateField(blank=True, null=True, verbose_name="Fecha de Término")
    fase = models.CharField(max_length=100, blank=True, null=True, verbose_name="Fase del Proyecto")

    class Meta:
        db_table = "proyectos"
        managed = True
        verbose_name = "Proyecto"
        verbose_name_plural = "Proyectos"

    def __str__(self):
        return self.proyecto or f"Proyecto {self.pk}"