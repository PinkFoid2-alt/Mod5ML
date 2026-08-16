import streamlit as st
import requests

API_URL = "https://codigos-mod-5-machine-learning.onrender.com/predict"

st.set_page_config(
    page_title="Clasificador de Aguas",
    page_icon="💧",
    layout="centered",
)

# --- Estilos ---
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #f0f9fb 0%, #ffffff 100%);
    }
    .main-title {
        text-align: center;
        color: #0a5d7a;
        font-size: 2.1rem;
        font-weight: 700;
        margin-bottom: 0.1rem;
    }
    .subtitle {
        text-align: center;
        color: #5b8a9a;
        font-size: 0.95rem;
        margin-bottom: 1.8rem;
    }
    div[data-testid="stForm"] {
        background-color: #ffffff;
        border: 1px solid #d9edf2;
        border-radius: 16px;
        padding: 1.6rem 1.8rem;
        box-shadow: 0 2px 12px rgba(10, 93, 122, 0.06);
    }
    .stButton > button {
        background-color: #0a8fb0;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 0.5rem 1.2rem;
        font-weight: 600;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #076e88;
        color: white;
    }
    .badge {
        display: inline-block;
        padding: 0.5rem 1.4rem;
        border-radius: 999px;
        font-weight: 700;
        font-size: 1.2rem;
        color: white;
    }
    .result-box {
        text-align: center;
        padding: 1.4rem;
        border-radius: 16px;
        margin-top: 1.4rem;
        background-color: #fafefe;
        border: 1px solid #e3f2f5;
    }
</style>
""", unsafe_allow_html=True)

COLORES = {
    "Verde": "#2ea043",
    "Amarillo": "#e8a800",
    "Rojo": "#d1373f",
}

st.markdown('<div class="main-title">💧 Clasificador de Aguas Subterráneas</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Ingresa los parámetros fisicoquímicos para estimar la calidad del agua</div>', unsafe_allow_html=True)

with st.form("form_prediccion"):
    col1, col2 = st.columns(2)
    with col1:
        ph = st.number_input("pH", min_value=0.0, max_value=14.0, value=7.0, step=0.1)
        turbidez = st.number_input("Turbidez (NTU)", min_value=0.0, value=5.0, step=0.1)
        oxigeno_disuelto = st.number_input("Oxígeno disuelto (mg/L)", min_value=0.0, value=6.0, step=0.1)
    with col2:
        conductividad = st.number_input("Conductividad (µS/cm)", min_value=0.0, value=500.0, step=1.0)
        temperatura = st.number_input("Temperatura (°C)", min_value=-10.0, value=20.0, step=0.1)

    enviar = st.form_submit_button("Clasificar agua")

if enviar:
    payload = {
        "ph": ph,
        "turbidez": turbidez,
        "oxigeno_disuelto": oxigeno_disuelto,
        "conductividad": conductividad,
        "temperatura": temperatura,
    }

    with st.spinner("Consultando el modelo..."):
        try:
            respuesta = requests.post(API_URL, json=payload, timeout=30)
            respuesta.raise_for_status()
            data = respuesta.json()

            semaforo = data.get("semaforo")
            probabilidades = data.get("probabilidades", {})
            prob_clase = probabilidades.get(semaforo)

            color = COLORES.get(semaforo, "#888888")

            bloque_html = f"""
            <div class="result-box">
                <div style="color:#5b8a9a; font-size:0.9rem; margin-bottom:0.5rem;">Clasificación del agua</div>
                <span class="badge" style="background-color:{color};">{semaforo}</span>
            """
            if prob_clase is not None:
                bloque_html += f"""
                <div style="color:#5b8a9a; font-size:0.9rem; margin-top:0.9rem;">
                    Probabilidad estimada: <strong style="color:{color};">{prob_clase * 100:.1f}%</strong>
                </div>
                """
            bloque_html += "</div>"

            st.markdown(bloque_html, unsafe_allow_html=True)

            if probabilidades:
                st.write("")
                st.caption("Distribución de probabilidades")
                for clase, prob in probabilidades.items():
                    st.markdown(f"**{clase}** — {prob * 100:.1f}%")
                    st.progress(min(max(prob, 0.0), 1.0))

        except requests.exceptions.RequestException as e:
            st.error(f"No se pudo conectar con el modelo: {e}")
