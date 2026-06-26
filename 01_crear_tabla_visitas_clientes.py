# ============================================================
# SCRIPT: CREAR ESQUEMA Y TABLA DE VISITAS COMERCIALES
# ============================================================

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# ============================================================
# CARGAR VARIABLES DE ENTORNO
# ============================================================

load_dotenv()

PGUSER = os.getenv("PGUSER")
PGPASSWORD = os.getenv("PGPASSWORD")
PGHOST = os.getenv("PGHOST")
PGPORT = os.getenv("PGPORT")
PGDATABASE = os.getenv("PGDATABASE")

# ============================================================
# VALIDAR VARIABLES DE ENTORNO
# ============================================================

variables_requeridas = {
    "PGUSER": PGUSER,
    "PGPASSWORD": PGPASSWORD,
    "PGHOST": PGHOST,
    "PGPORT": PGPORT,
    "PGDATABASE": PGDATABASE,
}

variables_faltantes = [
    nombre for nombre, valor in variables_requeridas.items()
    if not valor
]

if variables_faltantes:
    raise ValueError(
        f"Faltan variables de entorno en el archivo .env: {variables_faltantes}"
    )

# ============================================================
# CREAR CONEXIÓN A POSTGRESQL
# ============================================================

database_url = (
    f"postgresql+psycopg2://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}"
)

engine = create_engine(database_url)

# ============================================================
# SQL: CREAR ESQUEMA Y TABLA
# ============================================================

crear_esquema = """
CREATE SCHEMA IF NOT EXISTS cerosa_comercial;
"""

crear_tabla = """
CREATE TABLE IF NOT EXISTS cerosa_comercial.visitas_clientes (
    id SERIAL PRIMARY KEY,

    fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    fecha_visita DATE NOT NULL,

    vendedor TEXT NOT NULL,

    cliente TEXT NOT NULL,

    producto_interes TEXT NOT NULL,

    tareas_visita TEXT,

    comentario TEXT,

    creado_desde TEXT NOT NULL DEFAULT 'app_visitas'
);
"""

verificar_tabla = """
SELECT 
    table_schema,
    table_name
FROM information_schema.tables
WHERE table_schema = 'cerosa_comercial'
  AND table_name = 'visitas_clientes';
"""

verificar_columnas = """
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'cerosa_comercial'
  AND table_name = 'visitas_clientes'
ORDER BY ordinal_position;
"""

# ============================================================
# EJECUTAR PROCESO
# ============================================================

try:
    with engine.begin() as conn:

        # 1. Probar conexión
        resultado = conn.execute(text("SELECT 1 AS prueba;"))
        valor = resultado.scalar()

        print("Conexión exitosa a PostgreSQL.")
        print(f"Resultado de prueba: {valor}")

        # 2. Crear esquema
        conn.execute(text(crear_esquema))
        print("Esquema cerosa_comercial verificado/creado correctamente.")

        # 3. Crear tabla
        conn.execute(text(crear_tabla))
        print("Tabla visitas_clientes verificada/creada correctamente.")

        # 4. Verificar existencia de tabla
        tabla = conn.execute(text(verificar_tabla)).fetchone()

        if tabla:
            print("\nTabla encontrada:")
            print(f"Esquema: {tabla.table_schema}")
            print(f"Tabla: {tabla.table_name}")
        else:
            print("No se encontró la tabla visitas_clientes.")

        # 5. Mostrar columnas creadas
        columnas = conn.execute(text(verificar_columnas)).fetchall()

        print("\nColumnas de la tabla:")
        for columna in columnas:
            print(
                f"- {columna.column_name} | "
                f"{columna.data_type} | "
                f"Nullable: {columna.is_nullable} | "
                f"Default: {columna.column_default}"
            )

except Exception as e:
    print("Error durante la conexión o creación de tabla.")
    print(e)