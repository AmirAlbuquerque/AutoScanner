import sqlite3
from contextlib import contextmanager
import src.database.infrastructure.repositories.models_db as db


def setup_db(monkeypatch):
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("CREATE TABLE models (id TEXT PRIMARY KEY, brand_id TEXT, name TEXT)")
    conn.commit()

    @contextmanager
    def fake_conn():
        yield conn
        conn.commit()

    monkeypatch.setattr(db, "get_conn", fake_conn)
    return conn


def test_create_and_list_model(monkeypatch):
    setup_db(monkeypatch)
    model_id = db.create_model("b1", "X5")

    models = db.list_models_by_brand("b1")
    assert models[0]["name"] == "X5"