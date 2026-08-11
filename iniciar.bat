@echo off
echo Configurando entorno local para esta PC...

:: 1. Revisa si existe la carpeta 'env_local' en esta PC
if not exist env_local (
    echo Creando entorno virtual local...
    python -m venv env_local
    call env_local\Scripts\activate.bat
    echo Instalando dependencias...
    if exist requirements.txt (
        pip install -r requirements.txt
    ) else (
        pip install django
    )
) else (
    call env_local\Scripts\activate.bat
)

:: 2. Levanta el servidor de Django
echo Iniciando servidor...
python manage.py runserver
pause