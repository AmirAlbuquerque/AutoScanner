import streamlit as st
from datetime import date

from src.ui.session import require_role
from src.services import planning_service

try:
    from src.ui.layout import header, sidebar_nav
except Exception:
    header = None
    sidebar_nav = None


st.set_page_config(page_title="Minha Semana - Pesquisador", page_icon="✅", layout="wide")

actor_payload = require_role("PESQUISADOR")

if header:
    header("Minha Semana", "Tarefas atribuídas no planejamento semanal")
if sidebar_nav:
    sidebar_nav(actor_payload["role"])


def _fmt_date(iso: str) -> str:
    if not iso:
        return "-"
    try:
        y, m, d = iso.split("-")
        return f"{d}/{m}/{y}"
    except Exception:
        return iso


st.markdown("## ✅ Minhas tarefas da semana")

with st.container(border=True):
    col1, col2 = st.columns([2, 3], vertical_alignment="bottom")
    with col1:
        selected_day = st.date_input("Data de referência", value=date.today())
    with col2:
        st.caption("A consulta considera a semana iniciando na segunda-feira (week_start).")

    try:
        data = planning_service.researcher_view_current_week(actor_payload, today=selected_day)
    except Exception as e:
        st.error(str(e))
        st.stop()

planning = data.get("planning")
assignments = data.get("assignments") or []
message = data.get("message")

if not planning:
    st.info(message or "Nenhum planejamento encontrado para esta semana.")
    st.stop()

# cards
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Região", planning.get("region", "-"))
with c2:
    st.metric("Semana (início)", _fmt_date(planning.get("week_start")))
with c3:
    st.metric("Status", planning.get("status", "-"))
with c4:
    st.metric("Minhas lojas", len(assignments))

st.divider()

st.markdown("### 🏬 Lojas atribuídas")

if not assignments:
    st.warning("Você não possui lojas atribuídas neste planejamento.")
else:
    rows = []
    for a in assignments:
        rows.append({
            "Loja": a.get("store_name"),
            "Região": a.get("store_region"),
            "Status Loja": a.get("store_status"),
            "Semana (início)": _fmt_date(a.get("week_start")),
            "Status Planejamento": a.get("planning_status"),
            "store_id": a.get("store_id"),
            "assignment_id": a.get("assignment_id"),
        })

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
        column_config={
            "store_id": st.column_config.TextColumn("store_id", disabled=True, width="small"),
            "assignment_id": st.column_config.TextColumn("assignment_id", disabled=True, width="small"),
        }
    )