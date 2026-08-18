from django.db import models

class Proyecto(models.Model):
    # Identificadores y folios
    rcn = models.CharField(max_length=100, blank=True, null=True)
    sr = models.CharField(max_length=100, blank=True, null=True)
    proyecto = models.TextField(blank=True, null=True)  # Asunto / Descripción
    
    # Responsables y Clasificaciones
    responsable = models.CharField(max_length=255, blank=True, null=True)
    estado = models.CharField(max_length=100, blank=True, null=True)
    prioridad = models.CharField(max_length=100, blank=True, null=True)
    fase = models.CharField(max_length=100, blank=True, null=True)
    
    # Nuevos campos detallados
    clasificacion_requerimiento = models.CharField(max_length=255, blank=True, null=True)
    grupo_tarea = models.CharField(max_length=255, blank=True, null=True)
    prioridad_negocio = models.CharField(max_length=100, blank=True, null=True)
    impacto_otros_proyectos = models.TextField(blank=True, null=True)
    capacidades_acciones_sti = models.TextField(blank=True, null=True)
    edo_salud = models.CharField(max_length=100, blank=True, null=True)
    area_responsable_habilitacion = models.CharField(max_length=255, blank=True, null=True)
    area_apoyo_habilitacion = models.CharField(max_length=255, blank=True, null=True)
    fuente_negocio = models.CharField(max_length=255, blank=True, null=True)
    prioridad_ept = models.CharField(max_length=100, blank=True, null=True)
    consultor_negocio = models.CharField(max_length=255, blank=True, null=True)
    
    # Campos de concluidos, backlog y activos
    do_campo = models.CharField(max_length=255, blank=True, null=True)
    situacion_actual = models.TextField(blank=True, null=True)
    resumen_acciones = models.TextField(blank=True, null=True)
    fabrica_software = models.CharField(max_length=255, blank=True, null=True)
    tipo_proyecto = models.CharField(max_length=255, blank=True, null=True)
    categoria_proyecto = models.CharField(max_length=255, blank=True, null=True)
    
    # Métricas numéricas de avance y prioridades origen
    pct_planeado = models.CharField(max_length=50, blank=True, null=True)
    pct_ponderado = models.CharField(max_length=50, blank=True, null=True)
    subdireccion_solicitante = models.CharField(max_length=255, blank=True, null=True)
    prioridad_origen = models.CharField(max_length=100, blank=True, null=True)
    tiempo_dedicado = models.CharField(max_length=100, blank=True, null=True)
    tiempo_total_dedicado = models.CharField(max_length=100, blank=True, null=True)

    # Fechas
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)
    f_inicio_base = models.DateField(blank=True, null=True)
    f_fin_base = models.DateField(blank=True, null=True)
    f_inicio_entendimiento = models.DateField(blank=True, null=True)
    f_fin_entendimiento = models.DateField(blank=True, null=True)
    f_inicio_habilitacion = models.DateField(blank=True, null=True)
    f_fin_habilitacion = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.proyecto or 'Sin nombre'} ({self.rcn or self.sr or 'Sin Folio'})"
    