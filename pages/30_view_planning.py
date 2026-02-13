import streamlit as st
from datetime import date

from src.ui.session import require_role
from src.services import planning_service

try:
    from src.ui.layout import header, sidebar_nav
except Exception:
    header = None
    sidebar_nav = None


st.set_page_config(page_title="Planejamentos - Coordenador", page_icon="🗓️", layout="wide")

actor_payload = require_role("COORDENADOR")

if header:
    header("Planejamento Semanal", "Visão do coordenador")
if sidebar_nav:
    sidebar_nav(actor_payload["role"])


def _fmt_date(iso: str) -> str:
    # iso "YYYY-MM-DD"
    if not iso:
        return "-"
    try:
        y, m, d = iso.split("-")
        return f"{d}/{m}/{y}"
    except Exception:
        return iso


def _render_overview_table(items: list[dict]) -> None:
    if not items:
        st.info("Nenhum planejamento encontrado para sua região.")
        return

    rows = []
    for p in items:
        rows.append({
            "Semana (início)": _fmt_date(p.get("week_start")),
            "Status": p.get("status"),
            "Atribuições": int(p.get("assignments_count") or 0),
            "Criado em": p.get("created_at", "")[:19].replace("T", " "),
            "planning_id": p.get("id"),
        })

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
        column_config={
            "planning_id": st.column_config.TextColumn("planning_id", disabled=True, width="small"),
        }
    )


def _render_planning_detail(planning_id: str) -> None:
    data = planning_service.coordinator_view_planning(actor_payload, planning_id)
    planning = data["planning"]
    assignments = data["assignments"]

    # ----- cards -----
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Região", planning.get("region", "-"))
    with c2:
        st.metric("Semana (início)", _fmt_date(planning.get("week_start")))
    with c3:
        st.metric("Status", planning.get("status", "-"))
    with c4:
        st.metric("Atribuições", len(assignments))

    st.divider()

    st.markdown("### Atribuições (Lojas x Pesquisadores)")

    if not assignments:
        st.warning("Este planejamento ainda não possui atribuições.")
        return

    rows = []
    for a in assignments:
        rows.append({
            "Loja": a.get("store_name"),
            "Região": a.get("store_region"),
            "Status Loja": a.get("store_status"),
            "Pesquisador": a.get("researcher_name"),
            "Email": a.get("researcher_email"),
            "assignment_id": a.get("assignment_id"),
        })

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
        column_config={
            "assignment_id": st.column_config.TextColumn("assignment_id", disabled=True, width="small"),
        }
    )


# =========================
# Página
# =========================
st.markdown("## 🗓️ Planejamentos da sua região")

with st.container(border=True):
    st.markdown("### 📌 Overview")
    try:
        overview = planning_service.coordinator_list_plannings_overview(actor_payload, limit=200)
    except Exception as e:
        st.error(str(e))
        st.stop()

    _render_overview_table(overview)

    st.markdown("---")
    st.markdown("### 🔎 Visualizar um planejamento")

    planning_ids = [p["id"] for p in overview] if overview else []

    selected = st.selectbox(
        "Selecione um planejamento",
        options=[""] + planning_ids,
        format_func=lambda x: "Selecione..." if x == "" else x,
    )

if selected:
    with st.container(border=True):
        st.markdown("### 🧾 Detalhes do planejamento")
        try:
            _render_planning_detail(selected)
        except Exception as e:
            st.error(str(e))