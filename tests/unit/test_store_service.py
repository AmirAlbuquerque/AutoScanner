import pytest
from types import SimpleNamespace
import src.services.store_service as store_service

@pytest.fixture
def actor_payload():
    return {"email": "x@y.com"}

def actor(*, role: str, region: str | None = None, id: str = "u-1"):
    return SimpleNamespace(id=id, role=role, region=region)


@pytest.fixture
def mocks(monkeypatch):
    calls = {
        "require_authenticated": 0,
        "require_active_user": 0,
        "ensure_store_submitter": 0,
        "ensure_can_approve_store": 0,
        "db_create_store": [],
        "db_get_store": [],
        "db_approve_store": [],
    }

    # auth_service
    class AuthMock:
        def require_authenticated(self, payload):
            calls["require_authenticated"] += 1
            return actor(role="LOJISTA", region="SP", id="u-lojista")

        def require_active_user(self, act):
            calls["require_active_user"] += 1
            return None

    # rules
    def ensure_store_submitter(act):
        calls["ensure_store_submitter"] += 1

    def ensure_can_approve_store(act, store_region: str):
        calls["ensure_can_approve_store"] += 1

    # stores_db
    class StoresDbMock:
        def create_store(self, **kwargs):
            calls["db_create_store"].append(kwargs)
            return "store-123"

        def get_store(self, store_id: str):
            calls["db_get_store"].append(store_id)
            return {"id": store_id, "region": "SP"}

        def approve_store(self, *args, **kwargs):
            calls["db_approve_store"].append((args, kwargs))

    monkeypatch.setattr(store_service, "auth_service", AuthMock())
    monkeypatch.setattr(store_service, "ensure_store_submitter", ensure_store_submitter)
    monkeypatch.setattr(store_service, "ensure_can_approve_store", ensure_can_approve_store)
    monkeypatch.setattr(store_service, "stores_db", StoresDbMock())

    return calls


def test_service_create_store_calls_auth_rules_and_db(mocks, actor_payload):
    store_in = {"name": "Loja X", "region": "SP", "owner_id": "u-lojista", "status": "PENDENTE", "created_at": "2026-02-13T00:00:00Z"}

    out = store_service.create_store(actor_payload, store_in)

    assert out == "store-123"
    assert mocks["require_authenticated"] == 1
    assert mocks["require_active_user"] == 1
    assert mocks["ensure_store_submitter"] == 1

    assert len(mocks["db_create_store"]) == 1
    call = mocks["db_create_store"][0]
    assert call["created_by"] == "u-lojista"  # vindo do actor.id
    assert call["name"] == "Loja X"
    assert call["region"] == "SP"
