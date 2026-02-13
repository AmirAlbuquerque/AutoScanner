import streamlit as st
from src.database.infrastructure.init_db import init_db
from src.ui.session import is_logged_in, current_user, logout

init_db()

st.set_page_config(page_title="AutoScanner", page_icon="🚗", layout="wide")

# ---------- Header padrão ----------
left, right = st.columns([6, 2], vertical_alignment="center")
with left:
    st.markdown("## 🚗 AutoScanner")
    st.caption("Consulta pública de preços veiculares")

with right:
    if is_logged_in():
        u = current_user() or {}
        st.caption(f"{u.get('name')} • {u.get('role')}")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Admin", use_container_width=True):
                st.switch_page("pages/10_admin_users.py")
        with c2:
            if st.button("Sair", use_container_width=True):
                logout()
    else:
        if st.button("Área Administrativa", use_container_width=True):
            st.switch_page("pages/00_login.py")

st.divider()

# ---------- Home (consulta) ----------
# Aqui você vai colocar sua Home bonita igual as imagens.
# Por enquanto deixo um placeholder pra não travar o app:
st.info("Home pública: aqui entra a tela de consulta (marca/modelo/ano/região + resultados).")
