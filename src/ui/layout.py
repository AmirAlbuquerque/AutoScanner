import base64
from pathlib import Path
import streamlit as st
from src.ui.session import is_logged_in, current_user, logout

def inject_css():
    st.markdown(
        """
        <style>
            .muted { color: rgba(49,51,63,.65); }
            .title { font-weight: 800; font-size: 20px; }
            .logo{
            border-radius: 18px;
            padding: 26px 26px;
            background: radial-gradient(1200px 400px at 20% 0%, #0b4d75 0%, rgba(11,77,117,0.0) 70%),
                        linear-gradient(90deg, #0a3f65 0%, #0a89a8 60%, #0aa1b5 100%);
            color: #ffffff !important;
            margin-bottom: 16px;
            }

            .logo-row{
            display:flex;
            align-items:center;
            gap: 16px;
            }

            .logo-logo{
            height: 100px;
            width: auto;
            display:block;
            }

            .logo-title{
            font-size: 42px;
            font-weight: 800;
            line-height: 1.05;
            color: #ffffff;
            margin: 0;
            }

            .logo-subtitle{
            margin-top: 8px;
            font-size: 14px;
            opacity: 0.92;
            color: #ffffff;
            max-width: 720px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

def img_to_data_uri(path: str) -> str:
    base_dir = Path(__file__).resolve().parent  # aponta para src/ui
    img_path = base_dir / path

    if not img_path.exists():
        return ""

    mime = "image/png" if img_path.suffix.lower() == ".png" else "image/jpeg"
    data = base64.b64encode(img_path.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{data}"

def render_logo(title: str, subtitle: str, logo_path: str = "logo-branca.png"):
    logo_uri = img_to_data_uri(logo_path)

    st.markdown(
        f"""
        <div class="logo">
          <div class="logo-row">
            <img src="{logo_uri}" class="logo-logo" alt="logo"/>
            <div class="logo-text">
              <div class="logo-title">{title}</div>
              <div class="logo-subtitle">{subtitle}</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def header(title: str, subtitle: str | None = None, admin_target: str = "pages/10_admin_users.py"):
    inject_css()
    left, right = st.columns([6, 2], vertical_alignment="center")

    with left:
        render_logo(title, subtitle)

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
