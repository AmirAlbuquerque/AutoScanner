import sqlite3
from contextlib import contextmanager
import src.database.infrastructure.repositories.brands_db as db


def setup_db(monkeypatch):
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("CREATE TABLE brands (id TEXT PRIMARY KEY, name TEXT)")
    conn.commit()

    @contextmanager
    def fake_conn():
        yield conn
        conn.commit()

    monkeypatch.setattr(db, "get_conn", fake_conn)
    return conn


def test_create_and_get_brand(monkeypatch):
    setup_db(monkeypatch)
    brand_id = db.create_brand("BMW")

    brand = db.get_brand(brand_id)
    assert brand["name"] == "BMW"


def test_list_brands_order(monkeypatch):
    conn = setup_db(monkeypatch)
    conn.execute("INSERT INTO brands VALUES ('1','Audi')")
    conn.execute("INSERT INTO brands VALUES ('2','BMW')")
    conn.commit()

    brands = db.list_brands()
    assert brands[0]["name"] == "Audi"