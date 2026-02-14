import streamlit as st
from typing import Any, Optional
from src.services.auth_service import decode_token

def is_logged_in() -> bool:
    token = st.session_state.get("token")
    if not token:
        return False
    payload = decode_token(token)
    if not payload:
        st.session_state.pop("token", None)
        st.session_state.pop("user", None)
        return False
    st.session_state["user"] = payload
    return True

def current_user() -> Optional[dict[str, Any]]:
    if not is_logged_in():
        return None
    return st.session_state.get("user")

def require_login() -> dict[str, Any]:
    user = current_user()
    if not user:
        st.warning("Faça login para acessar esta página.")
        st.switch_page("pages/00_login.py")
        st.stop()
    return user

def require_role(*roles: str) -> dict[str, Any]:
    user = require_login()
    if user.get("role") not in roles:
        st.error("Você não tem permissão para acessar esta página.")
        st.switch_page("app.py")
        st.stop()
    return user

def logout() -> None:
    st.session_state.pop("token", None)
    st.session_state.pop("user", None)
    st.switch_page("app.py")