import re
import requests
import streamlit as st
 
# ----------------------------------------------------------------------------
# CONFIGURACIÓN GENERAL
# ----------------------------------------------------------------------------
API_URL = "https://codigos-mod-5-machine-learning.onrender.com/predict"
 
st.set_page_config(
    page_title="Clasificador de Aguas Subterráneas",
    page_icon="💧",
    layout="centered",
)
 
# ----------------------------------------------------------------------------
# ESTILOS (tema agua / minimalista) — colores fijos, no dependen del modo
# oscuro/claro del navegador del usuario (se refuerzan con !important)
# ----------------------------------------------------------------------------
st.markdown(
    """
    <style>
        html, body, .stApp {
            background-color: #f4f7f9 !important;
            color: #123a5e !important;
        }
 
        [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #f4f7f9 !important;
        }
 
        .header-container {
            text-align: center;
            padding: 1.2rem 0 0.4rem 0;
        }
 
        .header-title {
            color: #123a5e !important;
            font-size: 2.2rem;
            font-weight: 800;
            margin-bottom: 0.3rem;
        }
 
        .header-subtitle {
            color: #5c7891 !important;
            font-size: 0.95rem;
        }
 
        .header-line {
            border: none;
            border-top: 1px solid #d3dfe6;
            width: 70%;
            margin: 0.8rem auto 1rem auto;
        }
 
        .coords-row {
            text-align: center;
            color: #4a6072 !important;
            font-size: 1rem;
            margin-bottom: 1.2rem;
        }
 
        .metric-card {
            background-color: #ffffff !important;
            border-radius: 14px;
            padding: 0.9rem 1rem 0.6rem 1rem;
            box-shadow: 0 1px 4px rgba(18, 58, 94, 0.10);
            margin-bottom: 0.9rem;
            border: 1px solid #e6edf2;
        }
 
        .metric-card * {
            color: #123a5e !important;
        }
 
        div[data-testid="stTextInput"] label,
        div[data-testid="stNumberInput"] label {
            color: #123a5e !important;
            font-weight: 700 !important;
        }
 
        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input {
            border-radius: 8px !important;
            border: 1px solid #cfe0ea !important;
            background-color: #fbfdfe !important;
            color: #123a5e !important;
        }
 
        .stButton > button {
            background-color: #1c6fa8 !important;
            color: #ffffff !important;
            font-weight: 700;
            border-radius: 10px;
            padding: 0.6rem 1.6rem;
            border: none;
            width: 100%;
        }
 
        .stButton > button:hover {
            background-color: #14547f !important;
            color: #ffffff !important;
        }
 
        .rating-bar {
            display: flex;
            align-items: center;
            gap: 0.6rem;
            background-color: #ffffff !important;
            border-radius: 14px;
            padding: 0.9rem 1.1rem;
            border: 1px solid #e6edf2;
            box-shadow: 0 1px 4px rgba(18, 58, 94, 0.10);
            margin-top: 0.4rem;
            flex-wrap: wrap;
        }
 
        .rating-label {
            color: #123a5e !important;
            font-weight: 700;
            margin-right: 0.4rem;
            white-space: nowrap;
        }
 
        .badge-pill {
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-weight: 700;
            color: #ffffff !important;
            opacity: 0.35;
            white-space: nowrap;
        }
 
        .badge-pill.active {
            opacity: 1;
        }
 
        .badge-verde { background-color: #2e9e5b !important; }
        .badge-amarillo { background-color: #e0a11c !important; }
        .badge-rojo { background-color: #d1453a !important; }
 
        .prob-text {
            text-align: center;
            color: #4a6072 !important;
            font-size: 0.95rem;
            margin-top: 0.6rem;
        }
 
        div[data-testid="stExpander"] {
            background-color: #ffffff !important;
            border-radius: 10px;
            border: 1px solid #e6edf2;
        }
 
        div[data-testid="stExpander"] * {
            color: #123a5e !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
 
# ----------------------------------------------------------------------------
# ENCABEZADO
# ----------------------------------------------------------------------------
st.markdown(
    """
    <div class="header-container">
        <div class="header-title">💧 Clasificador de Aguas Subterráneas</div>
        <div class="header-subtitle">Evaluación de la calidad del agua mediante modelo predictivo</div>
    </div>
    <hr class="header-line">
    """,
    unsafe_allow_html=True,
)
 
# ----------------------------------------------------------------------------
# LATITUD / LONGITUD (arriba, como en la imagen de referencia)
# ----------------------------------------------------------------------------
lat_col, lon_col = st.columns(2)
with lat_col:
    lat_val = st.number_input("Latitud", value=22.62, format="%.4f")
with lon_col:
    lon_val = st.number_input("Longitud", value=-102.17, format="%.4f")
 
st.markdown("<br>", unsafe_allow_html=True)
 
# ----------------------------------------------------------------------------
# CAMPOS DE PARÁMETROS (texto, aceptan prefijo "<")
# ----------------------------------------------------------------------------
text_fields = [
    ("ALC_mg/L", "Alcalinidad (ALC)", "mg/L", "215.5"),
    ("AS_TOT_mg/L", "Arsénico Total (AS)", "mg/L", "<0.01"),
    ("COLI_FEC_NMP/100_mL", "Coli. Fecales (COLI FEC)", "NMP/100 mL", "<1.1"),
    ("CONDUCT_mS/cm", "Conductividad", "mS/cm", "815.0"),
    ("CR_TOT_mg/L", "Cromo Total (CR)", "mg/L", "<0.004"),
    ("DUR_mg/L", "Dureza", "mg/L", "245.3"),
    ("FE_TOT_mg/L", "Hierro Total (FE)", "mg/L", "0.35"),
    ("FLUORUROS_mg/L", "Fluoruros", "mg/L", "0.5"),
    ("MN_TOT_mg/L", "Manganeso Total (MN)", "mg/L", "0.15"),
    ("N_NO3_mg/L", "Nitratos (N-NO3)", "mg/L", "2.08"),
    ("SDT_M_mg/L", "SDT (Sólidos Disueltos Totales)", "mg/L", "550.4"),
]
 
inputs = {}
cols = st.columns(3)
 
for i, (key, label, unit, default) in enumerate(text_fields):
    with cols[i % 3]:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        val = st.text_input(f"{label} ({unit})", value=default, key=key)
        st.markdown("</div>", unsafe_allow_html=True)
        inputs[key] = val
 
# ----------------------------------------------------------------------------
# VALIDACIÓN
# ----------------------------------------------------------------------------
def is_valid_value(value: str) -> bool:
    """
    Valida que el valor no esté vacío y no sea únicamente el carácter '<'.
    Acepta números normales ('215.5') y valores con prefijo '<' seguido
    de un número ('<0.01').
    """
    value = value.strip()
    if not value or value == "<":
        return False
    pattern = r"^<?\d+(\.\d+)?$"
    return bool(re.match(pattern, value))
 
 
# ----------------------------------------------------------------------------
# BARRA DE CALIFICACIÓN + BOTÓN EVALUAR (estilo similar a la imagen)
# ----------------------------------------------------------------------------
if "resultado" not in st.session_state:
    st.session_state["resultado"] = None
 
st.markdown("<br>", unsafe_allow_html=True)
 
bar_col, btn_col = st.columns([3, 1])
 
semaforo_actual = (
    st.session_state["resultado"]["semaforo"] if st.session_state["resultado"] else None
)
 
badges_html = f"""
<div class="rating-bar">
    <span class="rating-label">Calificación del Agua:</span>
    <span class="badge-pill badge-verde {'active' if semaforo_actual == 'Verde' else ''}">✔ Buena</span>
    <span class="badge-pill badge-amarillo {'active' if semaforo_actual == 'Amarillo' else ''}">⚠ Aceptable</span>
    <span class="badge-pill badge-rojo {'active' if semaforo_actual == 'Rojo' else ''}">✖ No Apta</span>
</div>
"""
 
with bar_col:
    st.markdown(badges_html, unsafe_allow_html=True)
 
with btn_col:
    evaluar = st.button("Evaluar")
 
# ----------------------------------------------------------------------------
# LÓGICA DE EVALUACIÓN
# ----------------------------------------------------------------------------
if evaluar:
    invalid_fields = [
        label for key, label, unit, _ in text_fields
        if not is_valid_value(inputs[key])
    ]
 
    if invalid_fields:
        st.error(
            "Por favor corrige los siguientes campos (no pueden estar vacíos "
            "ni contener únicamente '<'): " + ", ".join(invalid_fields)
        )
    else:
        payload = {key: inputs[key].strip() for key, _, _, _ in text_fields}
        payload["LATITUD"] = lat_val
        payload["LONGITUD"] = lon_val
 
        with st.spinner("Evaluando calidad del agua..."):
            try:
                response = requests.post(API_URL, json=payload, timeout=30)
                response.raise_for_status()
                result = response.json()
                st.session_state["resultado"] = result
                st.rerun()
            except requests.exceptions.RequestException as e:
                st.error(f"Ocurrió un error al conectar con el servicio de predicción: {e}")
            except ValueError:
                st.error("La respuesta del servicio no pudo interpretarse correctamente.")
 
# ----------------------------------------------------------------------------
# MOSTRAR PROBABILIDAD DEL RESULTADO ACTUAL
# ----------------------------------------------------------------------------
if st.session_state["resultado"]:
    result = st.session_state["resultado"]
    semaforo = result.get("semaforo", "")
    probabilidades = result.get("probabilidades", {})
    prob = probabilidades.get(semaforo)
 
    if prob is not None:
        st.markdown(
            f'<div class="prob-text">Probabilidad estimada de "{semaforo}": {prob * 100:.1f}%</div>',
            unsafe_allow_html=True,
        )
 
    with st.expander("Ver todas las probabilidades"):
        for clase, valor in probabilidades.items():
            st.write(f"**{clase}:** {valor * 100:.1f}%")
 
