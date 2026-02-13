import streamlit as st
from src.services.auth_service import login
from src.ui.session import is_logged_in
from src.ui.layout import header

st.set_page_config(page_title="AutoScanner - Login", page_icon="🔐", layout="centered")

header("AutoScanner", "Área Administrativa • Login")

if is_logged_in():
    st.success("Você já está logado.")
    st.page_link("app.py", label="Ir para Home", icon="🏠")
    st.stop()

with st.form("login_form"):
    email = st.text_input("Email", placeholder="admin@autoscanner.local")
    password = st.text_input("Senha", type="password")
    submitted = st.form_submit_button("Entrar", type="primary", use_container_width=True)

if submitted:
    ok, token_or_msg, payload = login(email, password)
    if not ok:
        st.error(token_or_msg)
    else:
        st.session_state["token"] = token_or_msg
        st.session_state["user"] = payload
        st.success("Login realizado.")
        st.switch_page("pages/10_admin_users.py")

st.page_link("app.py", label="← Voltar para Home", icon="🏠")
