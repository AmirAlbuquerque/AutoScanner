import streamlit as st

from src.ui.session import require_role
from src.services import planning_service

st.set_page_config(page_title="Planejamento - Visualização", layout="wide")

user_payload = require_role("COORDENADOR")

st.title("Planejamento Semanal (Coordenador)")

# Overview
st.subheader("Planejamentos da minha região")
rows = planning_service.coordinator_list_plannings_overview(user_payload)

if not rows:
    st.info("Nenhum planejamento encontrado.")
    st.stop()

st.dataframe(rows, use_container_width=True, hide_index=True)

planning_ids = [r["id"] for r in rows]
selected = st.selectbox("Abrir planejamento", planning_ids)

if selected:
    data = planning_service.coordinator_view_planning(user_payload, selected)
    header = data["planning"]
    assignments = data["assignments"]

    st.divider()
    st.subheader("Detalhes do planejamento")

    col1, col2, col3 = st.columns(3)
    col1.metric("Região", header["region"])
    col2.metric("Semana (início)", header["week_start"])
    col3.metric("Status", header["status"])

    st.caption(f"Coordenador: {header['coordinator_name']} ({header['coordinator_email']})")

    st.subheader("Atribuições (loja x pesquisador)")
    if not assignments:
        st.warning("Planejamento sem atribuições.")
    else:
        st.dataframe(assignments, use_container_width=True, hide_index=True)