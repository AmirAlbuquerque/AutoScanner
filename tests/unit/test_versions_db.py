import sqlite3
from contextlib import contextmanager
import src.database.infrastructure.repositories.versions_db as db


def setup_db(monkeypatch):
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE versions (
            id TEXT PRIMARY KEY,
            model_id TEXT,
            name TEXT,
            image_url TEXT
        )
    """)
    conn.commit()

    @contextmanager
    def fake_conn():
        yield conn
        conn.commit()

    monkeypatch.setattr(db, "get_conn", fake_conn)
    return conn


def test_create_and_get_version(monkeypatch):
    setup_db(monkeypatch)
    version_id = db.create_version("m1", "Sport", None)

    version = db.get_version(version_id)
    assert version["name"] == "Sport"