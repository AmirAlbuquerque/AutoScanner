# tests/unit/test_store_service_simple.py
from __future__ import annotations

from types import SimpleNamespace
import pytest

import src.services.store_service as sut


def actor(*, role: str, region: str | None = None, id: str = "u-1"):
    return SimpleNamespace(id=id, role=role, region=region)


@pytest.fixture
def actor_payload():
    return {"email": "x@y.com"}


@pytest.fixture
def deps(monkeypatch):
    """
    Mocks mínimos, focados em:
    - auth_service: require_authenticated + require_active_user
    - rules: ensure_store_submitter + ensure_can_approve_store
    - stores_db: create_store + get_store + approve_store
    """
    calls = {
        "auth.require_authenticated": 0,
        "auth.require_active_user": 0,
        "rule.ensure_store_submitter": 0,
        "rule.ensure_can_approve_store": 0,
        "db.create_store": 0,
        "db.get_store": [],
        "db.approve_store": [],  # armazena tuplas (args, kwargs)
    }

    # ---------- auth_service ----------
    class AuthMock:
        def __init__(self):
            # por padrão, loja é criada por LOJISTA
            self._actor = actor(role="LOJISTA", region="SP", id="u-lojista")

        def set_actor(self, a):
            self._actor = a

        def require_authenticated(self, payload):
            calls["auth.require_authenticated"] += 1
            return self._actor

        def require_active_user(self, a):
            calls["auth.require_active_user"] += 1
            return None

    auth = AuthMock()

    # ---------- rules ----------
    def ensure_store_submitter(a):
        calls["rule.ensure_store_submitter"] += 1
        # aqui poderia levantar PermissionError em teste negativo, se quiser

    def ensure_can_approve_store(a, store_region: str):
        calls["rule.ensure_can_approve_store"] += 1

    # ---------- stores_db ----------
    class StoresDbMock:
        def create_store(self, **kwargs):
            calls["db.create_store"] += 1
            return "store-123"

        def get_store(self, store_id: str):
            calls["db.get_store"].append(store_id)
            return {"id": store_id, "region": "SP"}

        def approve_store(self, *args, **kwargs):
            calls["db.approve_store"].append((args, kwargs))

    db = StoresDbMock()

    # aplica patches no módulo do service
    monkeypatch.setattr(sut, "auth_service", auth)
    monkeypatch.setattr(sut, "ensure_store_submitter", ensure_store_submitter)
    monkeypatch.setattr(sut, "ensure_can_approve_store", ensure_can_approve_store)
    monkeypatch.setattr(sut, "stores_db", db)

    return calls, auth


def test_create_store_calls_auth_rules_and_db(actor_payload, deps):
    calls, _auth = deps

    store_in = {
        "name": "Loja X",
        "region": "SP",
        "owner_id": "u-lojista",
        "status": "PENDENTE",
        "created_at": "2026-02-13T00:00:00Z",
    }

    store_id = sut.create_store(actor_payload, store_in)

    assert store_id == "store-123"
    assert calls["auth.require_authenticated"] == 1
    assert calls["auth.require_active_user"] == 1
    assert calls["rule.ensure_store_submitter"] == 1
    assert calls["db.create_store"] == 1


def test_approve_store_fetches_store_checks_rule_and_calls_db(actor_payload, deps):
    calls, auth = deps

    # para aprovação, simulamos COORDENADOR na mesma região
    auth.set_actor(actor(role="COORDENADOR", region="SP", id="u-coord"))

    sut.approve_store(actor_payload, "store-999")

    assert calls["auth.require_authenticated"] == 1
    assert calls["auth.require_active_user"] == 1

    # buscou loja para obter região
    assert calls["db.get_store"] == ["store-999"]

    # regra de aprovação foi chamada
    assert calls["rule.ensure_can_approve_store"] == 1

    # approve_store foi chamado (store_id é posicional!)
    assert len(calls["db.approve_store"]) == 1
    args, kwargs = calls["db.approve_store"][0]
    assert args[0] == "store-999"
    assert args[1] == "u-coord"