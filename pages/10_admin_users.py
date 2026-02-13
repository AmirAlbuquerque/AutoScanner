import streamlit as st
from src.ui.session import require_role
from src.ui.layout import header, sidebar_nav
from src.services import user_service

st.set_page_config(page_title="Admin - Usuários", page_icon="👤", layout="wide")

user = require_role("ADMIN")
header("Administração", "Usuários do sistema")
sidebar_nav(user["role"])

tabs = st.tabs(["Listar", "Criar", "Editar", "Senha", "Excluir"])

# -------- Listar --------
with tabs[0]:
    st.subheader("Usuários cadastrados")
    users = user_service.admin_list_users(user)
    st.dataframe(users, use_container_width=True, hide_index=True)

# -------- Criar --------
with tabs[1]:
    st.subheader("Criar usuário")
    with st.form("create_user_form", clear_on_submit=True):
        name = st.text_input("Nome*", max_chars=120)
        email = st.text_input("Email*", max_chars=200)
        role = st.selectbox("Role*", ["ADMIN","GERENTE","COORDENADOR","PESQUISADOR","LOJISTA"])
        region = st.text_input("Região (opcional)", placeholder="ex: Sudeste")
        password = st.text_input("Senha*", type="password")
        active = st.checkbox("Ativo", value=True)

        submitted = st.form_submit_button("Criar", type="primary")
        if submitted:
            try:
                new_id = user_service.admin_create_user(
                    actor_payload=user,
                    name=name,
                    email=email,
                    role=role,
                    region=region.strip() or None,
                    password=password,
                    active=1 if active else 0
                )
                st.success(f"Usuário criado: {new_id}")
            except Exception as e:
                st.error(str(e))

# -------- Editar --------
with tabs[2]:
    st.subheader("Editar usuário")
    users = user_service.admin_list_users(user)
    options = {f"{u['name']} <{u['email']}> ({u['role']})": u["id"] for u in users}
    label = st.selectbox("Selecione um usuário", list(options.keys()) if options else ["(vazio)"])
    if options:
        user_id = options[label]
        data = user_service.admin_get_user(user, user_id)
        if data:
            with st.form("edit_user_form"):
                name = st.text_input("Nome", value=data["name"])
                email = st.text_input("Email", value=data["email"])
                role = st.selectbox("Role", ["ADMIN","GERENTE","COORDENADOR","PESQUISADOR","LOJISTA"],
                                    index=["ADMIN","GERENTE","COORDENADOR","PESQUISADOR","LOJISTA"].index(data["role"]))
                region = st.text_input("Região", value=data["region"] or "")
                active = st.checkbox("Ativo", value=bool(int(data["active"])))
                submitted = st.form_submit_button("Salvar alterações", type="primary")
                if submitted:
                    try:
                        user_service.admin_update_user(
                            actor_payload=user,
                            user_id=user_id,
                            name=name,
                            email=email,
                            role=role,
                            region=region.strip() or None,
                            active=1 if active else 0
                        )
                        st.success("Atualizado.")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

# -------- Senha --------
with tabs[3]:
    st.subheader("Resetar senha de usuário")
    users = user_service.admin_list_users(user)
    options = {f"{u['name']} <{u['email']}>": u["id"] for u in users}
    label = st.selectbox("Usuário", list(options.keys()) if options else ["(vazio)"], key="pw_user")
    if options:
        user_id = options[label]
        new_pw = st.text_input("Nova senha (mínimo 6)", type="password")
        if st.button("Atualizar senha", type="primary"):
            try:
                user_service.admin_set_password(user, user_id, new_pw)
                st.success("Senha atualizada.")
            except Exception as e:
                st.error(str(e))

# -------- Excluir --------
with tabs[4]:
    st.subheader("Excluir usuário")
    st.warning("A exclusão é definitiva.")
    users = user_service.admin_list_users(user)
    options = {f"{u['name']} <{u['email']}>": u["id"] for u in users}
    label = st.selectbox("Usuário para excluir", list(options.keys()) if options else ["(vazio)"], key="del_user")
    if options:
        user_id = options[label]
        confirm = st.text_input('Digite "EXCLUIR" para confirmar')
        if st.button("Excluir", type="primary", disabled=(confirm != "EXCLUIR")):
            try:
                user_service.admin_delete_user(user, user_id)
                st.success("Usuário excluído.")
                st.rerun()
            except Exception as e:
                st.error(str(e))