from django.db import models


class IssueRedmine(models.Model):
    id = models.IntegerField(primary_key=True)
    subject = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status_id = models.IntegerField()
    priority_id = models.IntegerField()
    created_on = models.DateTimeField()
    updated_on = models.DateTimeField()

    class Meta:
        managed = False  # Django NO modificará la estructura de esta tabla
        db_table = "issues"  # Tabla original de Redmine en PostgreSQL

    def __str__(self):
        return f"#{self.id} - {self.subject}"


class Requerimiento(models.Model):
    TIPO_CHOICES = [
        ("ACTIVOS", "Activos"),
        ("BACKLOG", "Backlog"),
        ("CONCLUIDOS", "Concluidos"),
        ("SR", "Solicitud de Requerimiento (SR)"),
        ("RCN", "RCN"),
    ]

    # Identificación básica
    folio = models.CharField(max_length=50, unique=True, verbose_name="Folio / ID")
    grupo_tarea = models.CharField(max_length=100, blank=True, null=True, verbose_name="Grupo de tarea")
    asignado_a = models.CharField(max_length=255, blank=True, null=True, verbose_name="Asignado a")
    asunto = models.TextField(verbose_name="Asunto / Descripción")

    # Estatus y Clasificación
    estado = models.CharField(max_length=100, default="Backlog", verbose_name="Estado")
    prioridad_ept = models.CharField(max_length=50, blank=True, null=True, verbose_name="Prioridad EPT")
    fase = models.CharField(max_length=150, blank=True, null=True, verbose_name="Fase")
    impacto_otros = models.TextField(blank=True, null=True, verbose_name="Impacto de Otros Proyectos")

    # Pestaña/Sección del Excel a la que pertenece
    tipo_requerimiento = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default="BACKLOG",
        verbose_name="Tipo / Pestaña",
    )

    # Auditoría de registros
    creado_el = models.DateTimeField(auto_now_add=True)
    actualizado_el = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "requerimientos"
        verbose_name = "Requerimiento"
        verbose_name_plural = "Requerimientos"

    def __str__(self):
        return f"{self.folio} | {self.grupo_tarea or 'N/A'} - {self.asunto[:40]}"