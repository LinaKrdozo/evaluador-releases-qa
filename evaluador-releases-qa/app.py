"""
Evaluador Inteligente de Releases QA
App de Streamlit que envía el informe ejecutivo (PDF generado por Claude)
a un flujo de n8n, que lo reenvía por correo al equipo.
"""
import re

import requests
import streamlit as st

# --------------------------------------------------------------------------
# Configuración
# --------------------------------------------------------------------------
st.set_page_config(page_title="Evaluador de Releases QA", page_icon="📊", layout="centered")

VEREDICTOS = ["NO_GO", "GO_CON_OBSERVACIONES", "GO", "REQUIERE_DECISION_HUMANA"]
RIESGOS = ["Crítico", "Alto", "Medio", "Bajo"]
DICTAMENES = ["CONFORME", "CONFORME CON HALLAZGOS", "NO CONFORME"]
COLORES = {"GO": "#2E7D32", "GO_CON_OBSERVACIONES": "#F9A825",
           "NO_GO": "#C62828", "REQUIERE_DECISION_HUMANA": "#6A1B9A"}
PATRON_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

try:
    WEBHOOK = st.secrets["N8N_WEBHOOK_URL"]
except (KeyError, FileNotFoundError):
    WEBHOOK = None

# --------------------------------------------------------------------------
# Encabezado
# --------------------------------------------------------------------------
st.title("📊 Evaluador Inteligente de Releases QA")
st.caption("Sube el informe ejecutivo generado por Claude y notifica al equipo por correo.")

if not WEBHOOK:
    st.error("Falta configurar el secreto **N8N_WEBHOOK_URL** "
             "(en Streamlit Cloud: ⋮ → Settings → Secrets).")
    st.stop()

with st.expander("¿Cómo funciona?"):
    st.markdown(
        "1. **n8n** carga los casos del Excel en Jira y genera el JSON de la release.\n"
        "2. **Claude** (proyecto con las skills analista, auditor e informe ejecutivo) "
        "evalúa la release y genera el informe en PDF.\n"
        "3. Desde esta app subes el PDF y **n8n** lo envía por correo al equipo."
    )

# --------------------------------------------------------------------------
# Formulario
# --------------------------------------------------------------------------
with st.form("envio", clear_on_submit=False):
    pdf = st.file_uploader("Informe ejecutivo (PDF)", type="pdf")

    c1, c2 = st.columns(2)
    release = c1.text_input("Release", value="2.5.0")
    veredicto = c2.selectbox("Veredicto final auditado", VEREDICTOS)
    riesgo = c1.selectbox("Nivel de riesgo", RIESGOS)
    dictamen = c2.selectbox("Dictamen del auditor", DICTAMENES)

    destinatarios = st.text_input("Correos del equipo",
                                  placeholder="qa@empresa.com, lider@empresa.com")
    comentario = st.text_area("Resumen o comentario (opcional)", height=90,
                              placeholder="Pega aquí el resumen ejecutivo que generó Claude")

    enviar = st.form_submit_button("📨 Enviar al equipo", use_container_width=True)

# --------------------------------------------------------------------------
# Envío
# --------------------------------------------------------------------------
if enviar:
    correos = [c.strip() for c in destinatarios.split(",") if c.strip()]
    invalidos = [c for c in correos if not PATRON_CORREO.match(c)]

    if pdf is None:
        st.error("Adjunta el informe en PDF.")
    elif not release.strip():
        st.error("Escribe el número de la release.")
    elif not correos:
        st.error("Escribe al menos un correo.")
    elif invalidos:
        st.error(f"Revisa estos correos: {', '.join(invalidos)}")
    else:
        with st.spinner("Enviando informe..."):
            try:
                r = requests.post(
                    WEBHOOK,
                    files={"data": (pdf.name, pdf.getvalue(), "application/pdf")},
                    data={
                        "release": release.strip(),
                        "veredicto": veredicto,
                        "riesgo": riesgo,
                        "dictamen": dictamen,
                        "destinatarios": ", ".join(correos),
                        "comentario": comentario.strip(),
                    },
                    timeout=60,
                )
            except requests.RequestException as e:
                st.error(f"No se pudo conectar con n8n: {e}")
            else:
                if r.ok:
                    st.success(f"Informe de la Release {release} enviado a {len(correos)} destinatario(s) ✅")
                    st.markdown(
                        f"<div style='background:{COLORES[veredicto]};color:#fff;padding:14px;"
                        f"border-radius:8px;text-align:center;font-size:20px'>"
                        f"<b>{veredicto}</b><br><span style='font-size:14px'>"
                        f"Riesgo: {riesgo} · Dictamen: {dictamen}</span></div>",
                        unsafe_allow_html=True,
                    )
                elif r.status_code == 404:
                    st.error("n8n respondió 404: activa el workflow y usa la Production URL del Webhook.")
                else:
                    st.error(f"n8n respondió con error {r.status_code}: {r.text[:300]}")

st.divider()
st.caption("Sistema Inteligente para Consolidación y Evaluación Automática de Evidencias de Pruebas de Software")
