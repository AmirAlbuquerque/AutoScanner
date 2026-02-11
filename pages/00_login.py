import streamlit as st
from src.services.auth_service import login
from src.ui.session import is_logged_in

st.set_page_config(page_title="AutoScanner - Login", layout="centered")

st.title("AutoScanner")
st.subheader("Login")

if is_logged_in():
    st.success("Você já está logado.")
    st.page_link("app.py", label="Ir para Home", icon="🏠")
    st.stop()

email = st.text_input("Email", placeholder="admin@autoscanner.local")
password = st.text_input("Senha", type="password")

if st.button("Entrar", type="primary", use_container_width=True):
    ok, token_or_msg, payload = login(email, password)
    if not ok:
        st.error(token_or_msg)
    else:
        st.session_state["token"] = token_or_msg
        st.session_state["user"] = payload
        st.success("Login realizado.")
        st.rerun()