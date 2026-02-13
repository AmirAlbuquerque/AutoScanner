import streamlit as st
from src.ui.session import require_role
from src.services import planning_service

st.set_page_config(page_title="Minha semana", layout="wide")

user_payload = require_role("PESQUISADOR")

st.title("Minha Semana (Pesquisador)")

data = planning_service.researcher_view_current_week(user_payload)

if data["planning"] is None:
    st.info(data["message"])
    st.stop()

planning = data["planning"]
st.success(f"Planejamento {planning['id']} | Semana iniciando em {planning['week_start']} | Status: {planning['status']}")

assignments = data["assignments"]
if not assignments:
    st.warning("Nenhuma loja atribuída a você nesta semana.")
else:
    st.subheader("Lojas atribuídas")
    st.dataframe(assignments, use_container_width=True, hide_index=True)