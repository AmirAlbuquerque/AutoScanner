import streamlit as st
from src.ui.session import is_logged_in, current_user, logout

def inject_css():
    st.markdown(
        """
        <style>
          .card { border: 1px solid rgba(49,51,63,.15); border-radius: 12px; padding: 16px 18px; background: white; }
          .muted { color: rgba(49,51,63,.65); }
          .title { font-weight: 800; font-size: 20px; }
        </style>
        """,
        unsafe_allow_html=True,
    )

def header(title: str, subtitle: str | None = None, admin_target: str = "pages/10_admin_users.py"):
    inject_css()
    left, right = st.columns([6, 2], vertical_alignment="center")

    with left:
        st.markdown(f"<div class='title'>🚗 {title}</div>", unsafe_allow_html=True)
        if subtitle:
            st.markdown(f"<div class='muted'>{subtitle}</div>", unsafe_allow_html=True)

    with right:
        if is_logged_in():
            u = current_user() or {}
            st.caption(f"{u.get('name')} • {u.get('role')}")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Admin", use_container_width=True):
                    st.switch_page(admin_target)
            with c2:
                if st.button("Sair", use_container_width=True):
                    logout()
        else:
            if st.button("Área Administrativa", use_container_width=True):
                st.switch_page("pages/00_login.py")

    st.divider()

def sidebar_nav(role: str):
    st.sidebar.markdown("### Navegação")

    st.sidebar.page_link("app.py", label="Home", icon="🏠")

    if role == "ADMIN":
        st.sidebar.page_link("pages/10_admin_users.py", label="Usuários", icon="👤")
    if role == "COORDENADOR":
        st.sidebar.page_link("pages/30_view_planning.py", label="Planejamentos", icon="🗓️")
    if role == "PESQUISADOR":
        st.sidebar.page_link("pages/31_research_week.py", label="Minha semana", icon="✅")
