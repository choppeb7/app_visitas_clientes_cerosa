# ============================================================
# APP STREAMLIT: REGISTRO DE VISITAS COMERCIALES
# ============================================================

import streamlit as st
from sqlalchemy import create_engine, text
from datetime import date

# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

st.set_page_config(
    page_title="Registro de Visitas Comerciales",
    page_icon="📍",
    layout="centered"
)

st.title("📍 Registro de Visitas Comerciales")
st.caption("Formulario interno para registrar visitas de vendedores a clientes.")

# ============================================================
# CONEXIÓN A POSTGRESQL
# ============================================================

@st.cache_resource
def get_engine():
    user = st.secrets["PGUSER"]
    password = st.secrets["PGPASSWORD"]
    host = st.secrets["PGHOST"]
    port = st.secrets["PGPORT"]
    dbname = st.secrets["PGDATABASE"]

    database_url = (
        f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
    )

    return create_engine(database_url)


try:
    engine = get_engine()

    with engine.connect() as conn:
        conn.execute(text("SELECT 1;"))

except Exception as e:
    st.error("No se pudo conectar a la base de datos.")
    st.exception(e)
    st.stop()

# ============================================================
# LISTAS DESPLEGABLES
# ============================================================

vendedores = [
    "Omar Moreno",
    "Gustavo",
    "Raul Gonzales",
    "Daniel Flores",
    "Nestor Escamilla",
    "Christian Hoppe",
    "Liliana Martinez",
    "Cristian Cruz",
    "Pablo Zuleta",
    "Roberto Vega",
    "Max Dreyfus",
    "Bladimiro Torres",
    "Yesenia Quijano",
    "Karla Duran",
    "Claudia Morales",
    "Oscar Valle"
]

productos_interes = [
    "Bandas",
    "Motores",
    "Motorreductores",
    "Reductores",
    "Guardamotores",
    "Interruptores",
    "PLC",
    "Módulos",
    "Instrumentación",
    "Rodamientos",
    "Poleas",
    "Correas",
    "Banda modular",
    "Cadenas",
    "Gabinetes",
    "Variadores",
    "Arrancadores",
    "Botonería",
    "Contactores",
    "Acoples",
    "Medición de energía",
    "Otros"
]

# ============================================================
# FORMULARIO PRINCIPAL
# ============================================================

with st.form("formulario_visita", clear_on_submit=True):

    vendedor = st.selectbox(
        "Vendedor",
        vendedores,
        index=None,
        placeholder="Seleccione el vendedor"
    )

    cliente = st.text_input(
        "Cliente visitado",
        placeholder="Ejemplo: Industrias XYZ, Ingenio ABC, Planta San Salvador..."
    )

    fecha_visita = st.date_input(
        "Fecha de visita",
        value=date.today()
    )

    producto_interes = st.selectbox(
        "Producto de interés",
        productos_interes,
        index=None,
        placeholder="Seleccione el producto de interés"
    )

    tareas_visita = st.text_area(
        "Tareas de la visita",
        placeholder="Ejemplo: Levantamiento de datos, revisión de aplicación, seguimiento de cotización..."
    )

    comentario = st.text_area(
        "Comentario de la visita",
        placeholder="Ejemplo: Cliente solicita cotización de variador para motor de 10 HP..."
    )

    enviar = st.form_submit_button("Guardar visita")

# ============================================================
# VALIDACIÓN E INSERCIÓN EN POSTGRESQL
# ============================================================

if enviar:

    errores = []

    if vendedor is None:
        errores.append("Debe seleccionar un vendedor.")

    if not cliente.strip():
        errores.append("Debe ingresar el nombre del cliente visitado.")

    if producto_interes is None:
        errores.append("Debe seleccionar un producto de interés.")

    if not tareas_visita.strip():
        errores.append("Debe ingresar las tareas de la visita.")

    if not comentario.strip():
        errores.append("Debe ingresar un comentario de la visita.")

    if errores:
        for error in errores:
            st.error(error)
        st.stop()

    insert_query = text("""
        INSERT INTO cerosa_comercial.visitas_clientes (
            fecha_visita,
            vendedor,
            cliente,
            producto_interes,
            tareas_visita,
            comentario
        )
        VALUES (
            :fecha_visita,
            :vendedor,
            :cliente,
            :producto_interes,
            :tareas_visita,
            :comentario
        );
    """)

    params = {
        "fecha_visita": fecha_visita,
        "vendedor": vendedor,
        "cliente": cliente.strip(),
        "producto_interes": producto_interes,
        "tareas_visita": tareas_visita.strip(),
        "comentario": comentario.strip()
    }

    try:
        with engine.begin() as conn:
            conn.execute(insert_query, params)

        st.success("Visita registrada correctamente.")

    except Exception as e:
        st.error("Ocurrió un error al guardar la visita.")
        st.exception(e)

# ============================================================
# PANEL BÁSICO DE CONSULTA
# ============================================================

st.divider()

st.subheader("📊 Últimas visitas registradas")

try:
    query_ultimas_visitas = text("""
        SELECT
            fecha_visita,
            vendedor,
            cliente,
            producto_interes,
            tareas_visita,
            comentario,
            fecha_registro
        FROM cerosa_comercial.visitas_clientes
        ORDER BY fecha_registro DESC
        LIMIT 20;
    """)

    with engine.connect() as conn:
        result = conn.execute(query_ultimas_visitas)
        rows = result.fetchall()
        columns = result.keys()

    if rows:
        import pandas as pd

        df_visitas = pd.DataFrame(rows, columns=columns)

        st.dataframe(
            df_visitas,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Todavía no hay visitas registradas.")

except Exception as e:
    st.warning("No se pudieron cargar las últimas visitas.")
    st.exception(e)