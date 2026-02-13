import streamlit as st
from src.ui.session import current_user, is_logged_in
from src.database.infrastructure.init_db import init_db
init_db()

st.set_page_config(page_title="AutoScanner", layout="wide")

st.title("AutoScanner")


if not is_logged_in():
    st.info("Você não está logado. Vá para a página de Login.")
    st.page_link("pages/00_login.py", label="Ir para Login", icon="🔐")
    st.stop()

user = current_user()
st.success(f"Bem-vinda(o), {user.get('name')}! Role: {user.get('role')}")

# Links úteis
st.page_link("pages/10_admin_users.py", label="Admin - Usuários", icon="👤")