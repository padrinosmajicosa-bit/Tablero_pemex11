import psycopg2

try:
    conn = psycopg2.connect(
        dbname="redmine",
        user="redmine",
        password="1234",
        host="localhost",
        port="5432"
    )
    print("\n✅ ¡CONEXIÓN EXITOSA A POSTGRESQL!\n")
    conn.close()
except Exception as e:
    print("\n❌ ERROR DE CONEXIÓN:")
    # Decodificamos usando la codificación nativa de Windows (CP1252)
    if hasattr(e, 'args') and isinstance(e.args[0], bytes):
        print(e.args[0].decode('cp1252', errors='replace'))
    else:
        print(str(e).encode('ascii', errors='replace').decode('ascii'))