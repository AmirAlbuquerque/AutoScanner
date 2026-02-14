import sqlite3
from contextlib import contextmanager
import pytest
import src.database.infrastructure.repositories.stores_db as stores_db


DDL = """
CREATE TABLE IF NOT EXISTS stores (
    id TEXT PRIMARY KEY,
    owner_id TEXT,
    name TEXT NOT NULL,
    region TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('PENDENTE','APROVADA','REPROVADA','INATIVA')),
    rejection_reason TEXT,
    approved_by TEXT,
    approved_at TEXT,
    created_by TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT
);
"""

@pytest.fixture
def memdb(monkeypatch):
    """
    Cria uma conexão SQLite em memória e substitui get_conn() do stores_db.
    Mantém row_factory=sqlite3.Row para compatibilidade com dict(row).
    """
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute(DDL)
    conn.commit()

    @contextmanager
    def _get_conn():
        # Comportamento semelhante: "with get_conn() as conn:"
        try:
            yield conn
            conn.commit()
        finally:
            pass

    monkeypatch.setattr(stores_db, "get_conn", _get_conn)
    yield conn
    conn.close()

def _seed_store(conn: sqlite3.Connection, **kwargs) -> str:
    """
    Insere store diretamente para facilitar cenários de teste.
    Campos obrigatórios: id, name, region, status, created_by, created_at.
    """
    defaults = dict(
        id="s-1",
        owner_id=None,
        name="Loja 1",
        region="SP",
        status="PENDENTE",
        rejection_reason=None,
        approved_by=None,
        approved_at=None,
        created_by="u-admin",
        created_at="2026-02-01T00:00:00Z",
        updated_at=None,
    )
    defaults.update(kwargs)

    conn.execute(
        """
        INSERT INTO stores (
            id, owner_id, name, region, status, rejection_reason,
            approved_by, approved_at, created_by, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            defaults["id"],
            defaults["owner_id"],
            defaults["name"],
            defaults["region"],
            defaults["status"],
            defaults["rejection_reason"],
            defaults["approved_by"],
            defaults["approved_at"],
            defaults["created_by"],
            defaults["created_at"],
            defaults["updated_at"],
        ),
    )
    conn.commit()
    return defaults["id"]

# -------------------------
# CREATE + GET + EXISTS
# -------------------------

def test_create_store_then_get_and_exists(memdb):
    store_id = stores_db.create_store(
        name="Nova Loja",
        region="SP",
        created_by="u1",
        owner_id="owner-1",
        status="PENDENTE",
        created_at="2026-02-10T10:00:00Z",
        updated_at=None,
    )

    assert isinstance(store_id, str)

    assert stores_db.store_exists(store_id) is True

    store = stores_db.get_store(store_id)
    assert store is not None
    assert store["id"] == store_id
    assert store["name"] == "Nova Loja"
    assert store["region"] == "SP"
    assert store["status"] == "PENDENTE"
    assert store["owner_id"] == "owner-1"
    assert store["created_by"] == "u1"
    assert store["created_at"] == "2026-02-10T10:00:00Z"


def test_get_store_returns_none_when_not_found(memdb):
    assert stores_db.get_store("missing") is None
    assert stores_db.store_exists("missing") is False

# -------------------------
# LIST (filters + pagination + ordering)
# -------------------------

def test_list_stores_filters_and_order(memdb):
    # created_at DESC
    _seed_store(memdb, id="s-old", region="SP", status="PENDENTE", owner_id="o1", created_by="u1", created_at="2026-02-01T00:00:00Z")
    _seed_store(memdb, id="s-new", region="SP", status="APROVADA", owner_id="o2", created_by="u1", created_at="2026-02-05T00:00:00Z")
    _seed_store(memdb, id="s-rj", region="RJ", status="PENDENTE", owner_id="o1", created_by="u2", created_at="2026-02-03T00:00:00Z")

    # filtro por region
    sp = stores_db.list_stores(region="SP")
    assert [r["id"] for r in sp] == ["s-new", "s-old"]

    # filtro por status
    pend = stores_db.list_stores(status="PENDENTE")
    assert set(r["id"] for r in pend) == {"s-old", "s-rj"}

    # filtro por owner_id + created_by
    f = stores_db.list_stores(owner_id="o1", created_by="u1")
    assert [r["id"] for r in f] == ["s-old"]

    # paginação
    all_rows = stores_db.list_stores(limit=2, offset=0)
    assert len(all_rows) == 2
    next_rows = stores_db.list_stores(limit=2, offset=2)
    assert len(next_rows) == 1


def test_list_pending_stores_by_region_orders_asc(memdb):
    _seed_store(memdb, id="s1", region="SP", status="PENDENTE", created_at="2026-02-01T00:00:00Z")
    _seed_store(memdb, id="s2", region="SP", status="PENDENTE", created_at="2026-02-02T00:00:00Z")
    _seed_store(memdb, id="s3", region="SP", status="APROVADA", created_at="2026-02-03T00:00:00Z")

    rows = stores_db.list_pending_stores_by_region("SP")
    assert [r["id"] for r in rows] == ["s1", "s2"]  # ASC por created_at

# -------------------------
# UPDATE BASIC
# -------------------------

def test_update_store_basic_updates_fields(memdb):
    _seed_store(memdb, id="s-upd", name="A", region="SP", owner_id=None, status="PENDENTE")

    stores_db.update_store_basic(
        store_id="s-upd",
        name="B",
        region="RJ",
        owner_id="owner-9",
        updated_at="2026-02-10T00:00:00Z",
    )

    row = stores_db.get_store("s-upd")
    assert row["name"] == "B"
    assert row["region"] == "RJ"
    assert row["owner_id"] == "owner-9"
    assert row["updated_at"] == "2026-02-10T00:00:00Z"

# -------------------------
# STATUS TRANSITIONS
# -------------------------

def test_approve_store_sets_status_and_clears_rejection(memdb):
    _seed_store(memdb, id="s-appr", status="PENDENTE", rejection_reason="x")

    stores_db.approve_store(
        store_id="s-appr",
        approved_by="coord-1",
        approved_at="2026-02-11T00:00:00Z",
        updated_at="2026-02-11T00:00:00Z",
    )

    row = stores_db.get_store("s-appr")
    assert row["status"] == "APROVADA"
    assert row["rejection_reason"] is None
    assert row["approved_by"] == "coord-1"
    assert row["approved_at"] == "2026-02-11T00:00:00Z"


def test_reject_store_sets_status_and_reason(memdb):
    _seed_store(memdb, id="s-rej", status="PENDENTE")

    stores_db.reject_store(
        store_id="s-rej",
        approved_by="coord-2",
        approved_at="2026-02-12T00:00:00Z",
        rejection_reason="Docs incompletos",
        updated_at="2026-02-12T00:00:00Z",
    )

    row = stores_db.get_store("s-rej")
    assert row["status"] == "REPROVADA"
    assert row["rejection_reason"] == "Docs incompletos"
    assert row["approved_by"] == "coord-2"


def test_inactivate_store_sets_status(memdb):
    _seed_store(memdb, id="s-inact", status="APROVADA")

    stores_db.inactivate_store(store_id="s-inact", updated_at="2026-02-13T00:00:00Z")

    row = stores_db.get_store("s-inact")
    assert row["status"] == "INATIVA"
    assert row["updated_at"] == "2026-02-13T00:00:00Z"