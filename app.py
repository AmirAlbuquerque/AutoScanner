import streamlit as st
from datetime import datetime
from src.database.infrastructure.init_db import init_db
from src.ui.session import is_logged_in, current_user, logout
from src.services import catalog_service
from src.services.public_queries_service import public_query_prices

init_db()

st.set_page_config(page_title="AutoScanner", page_icon="🚗", layout="wide")


# --------------------------
# CSS simples (visual)
# --------------------------
st.markdown(
    """
    <style>
      .card { border: 1px solid rgba(49,51,63,.15); border-radius: 12px; padding: 16px 18px;}
      .card-title { font-weight: 800; font-size: 16px; margin-bottom: 8px; }
      .muted { color: rgba(49,51,63,.65); }
      .big { font-size: 34px; font-weight: 900; letter-spacing: -0.5px; }
      .pill { display:inline-block; padding: 4px 10px; border-radius: 999px; border: 1px solid rgba(49,51,63,.15); }
    </style>
    """,
    unsafe_allow_html=True,
)


def brl(v: float) -> str:
    s = f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"


# --------------------------
# Header
# --------------------------
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


# --------------------------
# Form de consulta (igual ao mock)
# --------------------------
st.markdown("<div class='card'><div class='card-title'>🔎 Consultar Preço de Veículo</div>", unsafe_allow_html=True)

brands = catalog_service.public_list_brands()
brand_options = [("", "Selecione")] + [(b["id"], b["name"]) for b in brands]

col1, col2, col3, col4, col5 = st.columns([3, 3, 3, 2, 2])

with col1:
    brand_id = st.selectbox(
        "Marca *",
        options=[x[0] for x in brand_options],
        format_func=lambda v: dict(brand_options).get(v, "Selecione"),
    )

models = catalog_service.public_list_models(brand_id) if brand_id else []
model_options = [("", "Selecione")] + [(m["id"], m["name"]) for m in models]

with col2:
    model_id = st.selectbox(
        "Modelo *",
        options=[x[0] for x in model_options],
        format_func=lambda v: dict(model_options).get(v, "Selecione"),
        disabled=not bool(brand_id),
    )

versions = catalog_service.public_list_versions(model_id) if model_id else []
version_options = [("", "Todas")] + [(v["id"], v["name"]) for v in versions]

with col3:
    version_id_raw = st.selectbox(
        "Versão",
        options=[x[0] for x in version_options],
        format_func=lambda v: dict(version_options).get(v, "Todas"),
        disabled=not bool(model_id),
    )
    version_id = version_id_raw or None

with col4:
    year_opt = st.selectbox("Ano", options=["Todos"] + [str(y) for y in range(2010, datetime.now().year + 1)])
    year_fabrication = None if year_opt == "Todos" else int(year_opt)

with col5:
    region = st.selectbox("Região", options=["Grande Belo Horizonte", "São Paulo", "Rio de Janeiro", "Curitiba"])

col6, col7 = st.columns([3, 1])
with col6:
    # competência do mês (YYYY-MM)
    default_month = datetime.now().strftime("%Y-%m")
    capture_month = st.text_input("Mês (YYYY-MM)", value=default_month, help="Competência para calcular média e lista por loja.")

with col7:
    submit = st.button("Consultar", type="primary", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)


# --------------------------
# Resultado
# --------------------------
if "last_query" not in st.session_state:
    st.session_state.last_query = None

if submit:
    if not brand_id or not model_id:
        st.warning("Selecione Marca e Modelo.")
        st.session_state.last_query = None
    else:
        try:
            actor_user_id = (current_user() or {}).get("id") if is_logged_in() else None

            result = public_query_prices(
                region=region,
                capture_month=capture_month,
                brand_id=brand_id,
                model_id=model_id,
                version_id=version_id,
                year_fabrication=year_fabrication,
                actor_user_id=actor_user_id,
            )

            st.session_state.last_query = result
        except Exception as e:
            st.error(str(e))
            st.session_state.last_query = None


if st.session_state.last_query is None:
    st.markdown(
        """
        <div style="text-align:center; padding: 56px 0;">
          <div style="font-size:54px; opacity:0.35;">🚙</div>
          <div style="font-size:22px; font-weight:800; margin-top:10px;">Consulte preços de veículos</div>
          <div class="muted" style="margin-top:6px;">Selecione marca e modelo para começar</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()


result = st.session_state.last_query

# Cards
c1, c2 = st.columns(2, gap="large")
with c1:
    st.markdown("<div class='card'><div class='card-title'>📈 Média Mensal</div>", unsafe_allow_html=True)
    if result.monthly_avg is None:
        st.markdown("<div class='muted'>Sem dados de média disponíveis.</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='big'>{brl(result.monthly_avg)}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='muted'>{result.monthly_samples} amostras no mês {capture_month}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='card'><div class='card-title'>💲 Tabela FIPE</div>", unsafe_allow_html=True)
    if result.fipe_price is None:
        st.markdown("<div class='muted'>Sem integração FIPE (a implementar).</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='big'>{brl(result.fipe_price)}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='muted'>Ref: {result.fipe_ref or '-'}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

# Preços por loja
st.markdown("<div class='card'><div class='card-title'>🏬 Preços por Loja</div>", unsafe_allow_html=True)
if not result.store_prices:
    st.markdown("<div class='muted'>Nenhuma coleta encontrada para os filtros selecionados.</div>", unsafe_allow_html=True)
else:
    rows = []
    for r in result.store_prices:
        rows.append({
            "Loja": r.get("store_name"),
            "Região": r.get("store_region"),
            "Data captura": (r.get("capture_date") or "")[:19].replace("T", " "),
            "Preço": brl(float(r.get("price") or 0)),
            "store_id": r.get("store_id"),
        })
    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
        column_config={"store_id": st.column_config.TextColumn("store_id", width="small", disabled=True)},
    )
st.markdown("</div>", unsafe_allow_html=True)
