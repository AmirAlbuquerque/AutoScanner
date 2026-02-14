import pytest
from types import SimpleNamespace
import src.services.catalog_service as sut


def actor(role="GERENTE", id="u1"):
    return SimpleNamespace(role=role, id=id)


@pytest.fixture
def deps(monkeypatch):
    calls = {
        "ensure_manager": 0,
        "create_brand": 0,
        "get_brand": True,
    }

    class AuthMock:
        def require_authenticated(self, payload):
            return actor()

        def require_active_user(self, actor):
            return actor

    def ensure_manager(a):
        calls["ensure_manager"] += 1

    class BrandsMock:
        def list_brands(self):
            return [{"id": "b1"}]

        def create_brand(self, name):
            calls["create_brand"] += 1
            return "brand-1"

        def get_brand(self, brand_id):
            return {"id": brand_id} if calls["get_brand"] else None

        def update_brand(self, brand_id, name):
            pass

        def delete_brand(self, brand_id):
            pass

    monkeypatch.setattr(sut, "auth_service", AuthMock())
    monkeypatch.setattr(sut.catalog_rules, "ensure_manager", ensure_manager)
    monkeypatch.setattr(sut, "brands_db", BrandsMock())

    return calls


def test_manager_list_brands(deps):
    result = sut.manager_list_brands({"x": 1})
    assert result == [{"id": "b1"}]


def test_manager_create_brand(deps):
    result = sut.manager_create_brand({"x": 1}, "  BMW  ")
    assert result == "brand-1"
    assert deps["create_brand"] == 1


def test_manager_update_brand_not_found(monkeypatch):
    import src.services.catalog_service as sut

    class AuthMock:
        def require_authenticated(self, payload):
            return actor()

        def require_active_user(self, actor):
            return actor

    class BrandsMock:
        def get_brand(self, brand_id):
            return None

    monkeypatch.setattr(sut, "auth_service", AuthMock())
    monkeypatch.setattr(sut, "brands_db", BrandsMock())
    monkeypatch.setattr(sut.catalog_rules, "ensure_manager", lambda a: None)

    with pytest.raises(ValueError):
        sut.manager_update_brand({}, "invalid", "Name")