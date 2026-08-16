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
# ESTILOS (tema agua / minimalista)
# ----------------------------------------------------------------------------
st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(180deg, #eef4f8 0%, #f4f7f9 100%);
        }

        .header-container {
            text-align: center;
            padding: 1.2rem 0 0.8rem 0;
        }

        .header-title {
            color: #123a5e;
            font-size: 2.1rem;
            font-weight: 800;
            margin-bottom: 0.3rem;
        }

        .header-subtitle {
            color: #5c7891;
            font-size: 0.95rem;
        }

        .header-line {
            border: none;
            border-top: 1px solid #d3dfe6;
            width: 70%;
            margin: 0.8rem auto 1.4rem auto;
        }

        .metric-card {
            background-color: #ffffff;
            border-radius: 14px;
            padding: 0.9rem 1rem 0.6rem 1rem;
            box-shadow: 0 1px 4px rgba(18, 58, 94, 0.08);
            margin-bottom: 0.9rem;
        }

        .metric-card label {
            color: #123a5e !important;
            font-weight: 700 !important;
        }

        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input {
            border-radius: 8px !important;
            border: 1px solid #cfe0ea !important;
        }

        .stButton > button {
            background-color: #1c6fa8;
            color: white;
            font-weight: 700;
            border-radius: 10px;
            padding: 0.55rem 1.6rem;
            border: none;
            width: 100%;
        }

        .stButton > button:hover {
            background-color: #14547f;
            color: white;
        }

        .badge {
            text-align: center;
            padding: 0.9rem;
            border-radius: 12px;
            font-size: 1.4rem;
            font-weight: 800;
            color: white;
            margin-top: 1rem;
        }

        .badge-verde { background-color: #2e9e5b; }
        .badge-amarillo { background-color: #e0a11c; }
        .badge-rojo { background-color: #d1453a; }

        .prob-text {
            text-align: center;
            color: #4a6072;
            font-size: 0.95rem;
            margin-top: 0.4rem;
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
# DEFINICIÓN DE CAMPOS
# ----------------------------------------------------------------------------
# Campos de texto (pueden incluir el prefijo "<" además de números, p. ej. "<0.01")
text_fields = [
    ("ALC_mg/L", "Alcalinidad (ALC)", "mg/L", "215.5"),
    ("AS_TOT_mg/L", "Arsénico Total (AS)", "mg/L", "<0.01"),
    ("COLI_FEC_NMP/100_mL", "Coliformes Fecales (COLI FEC)", "NMP/100 mL", "<1.1"),
    ("CONDUCT_mS/cm", "Conductividad", "mS/cm", "815.0"),
    ("CR_TOT_mg/L", "Cromo Total (CR)", "mg/L", "<0.004"),
    ("DUR_mg/L", "Dureza", "mg/L", "245.3"),
    ("FE_TOT_mg/L", "Hierro Total (FE)", "mg/L", "0.35"),
    ("FLUORUROS_mg/L", "Fluoruros", "mg/L", "0.5"),
    ("MN_TOT_mg/L", "Manganeso Total (MN)", "mg/L", "0.15"),
    ("N_NO3_mg/L", "Nitratos (N-NO3)", "mg/L", "2.08"),
    ("SDT_M_mg/L", "Sólidos Disueltos Totales (SDT)", "mg/L", "550.4"),
]

# Campos numéricos puros
numeric_fields = [
    ("LATITUD", "Latitud", 22.62),
    ("LONGITUD", "Longitud", -102.17),
]

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
    if not value:
        return False
    if value == "<":
        return False
    # Permite "<numero" o un número simple
    pattern = r"^<?\d+(\.\d+)?$"
    return bool(re.match(pattern, value))


# ----------------------------------------------------------------------------
# FORMULARIO DE ENTRADA
# ----------------------------------------------------------------------------
st.markdown("#### Parámetros de la muestra")

inputs = {}
cols = st.columns(3)

for i, (key, label, unit, default) in enumerate(text_fields):
    with cols[i % 3]:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        val = st.text_input(f"{label} ({unit})", value=default, key=key)
        st.markdown("</div>", unsafe_allow_html=True)
        inputs[key] = val

lat_col, lon_col = st.columns(2)
with lat_col:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    lat_val = st.number_input("Latitud", value=numeric_fields[0][2], format="%.4f")
    st.markdown("</div>", unsafe_allow_html=True)
with lon_col:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    lon_val = st.number_input("Longitud", value=numeric_fields[1][2], format="%.4f")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# BOTÓN DE EVALUACIÓN
# ----------------------------------------------------------------------------
if st.button("Evaluar"):
    # Validar todos los campos de texto
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

                semaforo = result.get("semaforo", "")
                probabilidades = result.get("probabilidades", {})
                prob = probabilidades.get(semaforo)

                badge_class = {
                    "Verde": "badge-verde",
                    "Amarillo": "badge-amarillo",
                    "Rojo": "badge-rojo",
                }.get(semaforo, "badge-amarillo")

                icon = {"Verde": "✅", "Amarillo": "⚠️", "Rojo": "🚫"}.get(semaforo, "")

                st.markdown(
                    f'<div class="badge {badge_class}">{icon} {semaforo}</div>',
                    unsafe_allow_html=True,
                )

                if prob is not None:
                    st.markdown(
                        f'<div class="prob-text">Probabilidad estimada: {prob * 100:.1f}%</div>',
                        unsafe_allow_html=True,
                    )

                with st.expander("Ver todas las probabilidades"):
                    for clase, valor in probabilidades.items():
                        st.write(f"**{clase}:** {valor * 100:.1f}%")

            except requests.exceptions.RequestException as e:
                st.error(f"Ocurrió un error al conectar con el servicio de predicción: {e}")
            except ValueError:
                st.error("La respuesta del servicio no pudo interpretarse correctamente.")
