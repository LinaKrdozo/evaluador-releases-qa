# 📊 Evaluador Inteligente de Releases QA

App de Streamlit del **Sistema Inteligente para Consolidación y Evaluación Automática de Evidencias de Pruebas de Software**.

## Arquitectura

1. **n8n (flujo 1):** lee el Excel de pruebas desde Google Sheets, crea las tarjetas en Jira (En revisión / Bloqueado / Terminado) y genera el JSON consolidado de la release.
2. **Claude (proyecto con skills):** `analista-releases-qa` emite el veredicto (GO / GO_CON_OBSERVACIONES / NO_GO), `auditor-releases-qa` lo verifica e `informe-ejecutivo-qa` genera el informe en PDF con la identidad corporativa.
3. **Esta app + n8n (flujo 2):** se sube el PDF y n8n lo envía por correo al equipo, informando el resultado de la release.

## Ejecutar en local

```bash
pip install -r requirements.txt
# copia .streamlit/secrets.toml.example como .streamlit/secrets.toml y pega la URL del webhook
streamlit run app.py
```

## Desplegar en Streamlit Community Cloud

1. Sube este repositorio a GitHub.
2. En [share.streamlit.io](https://share.streamlit.io): **Create app** → repositorio → `app.py`.
3. En **Advanced settings → Secrets** agrega:
   ```toml
   N8N_WEBHOOK_URL = "https://TU-N8N/webhook/informe-release"
   ```
4. **Deploy**.

## Datos que envía al webhook

| Campo | Descripción |
|---|---|
| `data` (archivo) | Informe ejecutivo en PDF |
| `release` | Número de la release |
| `veredicto` | GO, GO_CON_OBSERVACIONES, NO_GO o REQUIERE_DECISION_HUMANA |
| `riesgo` | Crítico, Alto, Medio o Bajo |
| `dictamen` | CONFORME, CONFORME CON HALLAZGOS o NO CONFORME |
| `destinatarios` | Correos separados por coma |
| `comentario` | Resumen o comentario opcional |
