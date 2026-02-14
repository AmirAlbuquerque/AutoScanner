# tests/unit/test_user_service.py
from __future__ import annotations

import re
import pytest

import src.services.user_service as sut


@pytest.fixture
def actor_payload() -> dict:
    return {"email": "admin@corp.com"}


@pytest.fixture
def actor() -> dict:
    return {"id": "actor-1", "email": "admin@corp.com", "role": "ADMIN", "active": 1}


@pytest.fixture
def fixed_now(monkeypatch) -> str:
    fixed = "2026-02-12T00:00:00+00:00"
    monkeypatch.setattr(sut, "_now", lambda: fixed)
    return fixed


@pytest.fixture
def mocks(monkeypatch, actor):
    calls = {
        "create_user": [],
        "list_users": 0,
        "get_user": [],
        "update_user": [],
        "set_password": [],
        "delete_user": [],
        "hash_password": [],
        "ensure_admin": 0,
    }

    class AuthMock:
        def _require_admin(self, payload):  # usado no create
            return None

        def require_authenticated(self, payload):  # usado em list/get/update/set_password/delete
            return {"id": "actor-1", "email": "admin@corp.com"}

        def require_active_user(self, actor_in):
            return actor

        def _hash_password(self, pw: str) -> str:
            calls["hash_password"].append(pw)
            return f"hash({pw})"

    class RulesMock:
        def ensure_admin(self, actor_in):
            calls["ensure_admin"] += 1

    class UserDbMock:
        def create_user(self, *, user_id, name, email, role, region, password_hash, active, created_at):
            calls["create_user"].append(
                dict(
                    user_id=user_id,
                    name=name,
                    email=email,
                    role=role,
                    region=region,
                    password_hash=password_hash,
                    active=active,
                    created_at=created_at,
                )
            )

        def list_users(self):
            calls["list_users"] += 1
            return [{"id": "u1"}]

        def get_user(self, user_id: str):
            calls["get_user"].append(user_id)
            return {"id": user_id}

        def update_user(self, name, email, role, region, active, user_id):
            calls["update_user"].append(
                dict(name=name, email=email, role=role, region=region, active=active, user_id=user_id)
            )

        def set_password(self, password_hash, user_id):
            calls["set_password"].append(dict(password_hash=password_hash, user_id=user_id))

        def delete_user(self, user_id):
            calls["delete_user"].append(user_id)

    class LoggerMock:
        def info(self, msg: str):
            # mantemos, mas não valida (arquivo enxuto)
            pass

    monkeypatch.setattr(sut, "auth_service", AuthMock())
    monkeypatch.setattr(sut, "user_rules", RulesMock())
    monkeypatch.setattr(sut, "user_db", UserDbMock())
    monkeypatch.setattr(sut, "logger", LoggerMock())

    return calls


# -----------------------
# CREATE
# -----------------------
def test_create_user_crud_happy_path(mocks, actor_payload, fixed_now):
    user_id = sut.admin_create_user(
        actor_payload=actor_payload,
        name="  John Doe ",
        email="  JOHN@EXAMPLE.COM ",
        role=" lojista ",
        region="SP",
        password="secret1",
        active=1,
    )

    assert re.fullmatch(r"[0-9a-fA-F-]{36}", user_id)

    assert mocks["hash_password"] == ["secret1"]
    assert len(mocks["create_user"]) == 1

    call = mocks["create_user"][0]
    assert call["password_hash"] == "hash(secret1)"
    # Normalizações importantes do create
    assert call["user_id"] == user_id
    assert call["name"] == "John Doe"
    assert call["email"] == "john@example.com"
    assert call["role"] == "LOJISTA"
    assert call["region"] == "SP"
    assert call["active"] == 1
    assert call["created_at"] == fixed_now


# -----------------------
# READ (list + get)
# -----------------------
def test_list_users_crud(mocks, actor_payload):
    out = sut.admin_list_users(actor_payload)
    assert out == [{"id": "u1"}]
    assert mocks["list_users"] == 1
    assert mocks["ensure_admin"] == 1


def test_get_user_crud(mocks, actor_payload):
    out = sut.admin_get_user(actor_payload, user_id="u-123")
    assert out == {"id": "u-123"}
    assert mocks["get_user"] == ["u-123"]
    assert mocks["ensure_admin"] == 1


# -----------------------
# UPDATE
# -----------------------
def test_update_user_crud(mocks, actor_payload):
    sut.admin_update_user(
        actor_payload=actor_payload,
        user_id="u-1",
        name="New Name",
        email="  X@Y.COM ",
        role=" gerente ",
        region=None,
        active=0,
    )

    assert len(mocks["update_user"]) == 1
    call = mocks["update_user"][0]
    assert call["user_id"] == "u-1"
    assert call["email"] == "x@y.com"
    assert call["role"] == "GERENTE"
    assert call["active"] == 0
    assert mocks["ensure_admin"] == 1


# -----------------------
# DELETE
# -----------------------
def test_delete_user_crud(mocks, actor_payload):
    sut.admin_delete_user(actor_payload, user_id="u-del")
    assert mocks["delete_user"] == ["u-del"]
    assert mocks["ensure_admin"] == 1


# -----------------------
# Caso negativo essencial (1 só)
# -----------------------
def test_update_user_invalid_role_raises(mocks, actor_payload):
    with pytest.raises(ValueError, match="Role inválida"):
        sut.admin_update_user(
            actor_payload=actor_payload,
            user_id="u-1",
            name="Name",
            email="a@b.com",
            role="invalid",
            region=None,
            active=1,
        )
