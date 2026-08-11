import requests
from django.shortcuts import render
from proyectos.models import Proyecto  # Mantienes tus consultas directas a PostgreSQL

def inicio(request):
    # -------------------------------------------------------------
    # 1. TUS CONTEOS DESDE POSTGRESQL (Se mantienen igual)
    # -------------------------------------------------------------
    total_proyectos = Proyecto.objects.count()
    proyectos_inicial = Proyecto.objects.filter(estado__iexact='inicial').count()
    proyectos_proceso = Proyecto.objects.filter(estado__iexact='en_proceso').count()
    prioridad_alta = Proyecto.objects.filter(prioridad__iexact='alta').count()

    # -------------------------------------------------------------
    # 2. CONEXIÓN A LA API DE REDMINE PARA ALIMENTAR EL TABLERO
    # -------------------------------------------------------------
    url_redmine = "http://localhost:3000/issues.json?include=custom_fields"
    
    # ⚠️ REEMPLAZA ESTA CADENA POR TU CLAVE COPIADA DE REDMINE
    api_key_redmine = "8c195b5a138f1d45d4bf5a12841be6c2cfded361" 
    
    headers = {
        "X-Redmine-API-Key": api_key_redmine
    }
    
    peticiones_redmine = []
    
    try:
        response = requests.get(url_redmine, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            issues = data.get('issues', [])
            
            for item in issues:
                # Mapeamos los campos personalizados (Fase, Estado de Salud, etc.)
                cf_dict = {cf['name']: cf.get('value', '') for cf in item.get('custom_fields', [])}
                
                peticiones_redmine.append({
                    'id': item.get('id'),
                    'asunto': item.get('subject'),
                    'estado': item.get('status', {}).get('name'),
                    'prioridad': item.get('priority', {}).get('name'),
                    'fase': cf_dict.get('Fase', '-'),
                    'estado_salud': cf_dict.get('Estado de Salud', '-'),
                    'id_requerimiento': cf_dict.get('ID Requerimiento', '-'),
                    'consultor': cf_dict.get('Consultor/Asignado', '-'),
                })
    except Exception as e:
        print(f"⚠️ Error al conectar con la API de Redmine: {e}")

    # -------------------------------------------------------------
    # 3. ENVIAMOS TODO AL TEMPLATE
    # -------------------------------------------------------------
    contexto = {
        "rcn": total_proyectos,        
        "sr": proyectos_proceso,       
        "backlog": proyectos_inicial,  
        "alertas": prioridad_alta,     
        "peticiones": peticiones_redmine,  # 👈 ¡Lista viva desde Redmine!
    }
    
    return render(request, "dashboard/index.html", contexto)