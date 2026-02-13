import pytest
from types import SimpleNamespace
import src.domain.catalog_rules as rules


def actor(role):
    return SimpleNamespace(role=role)


# ---- ensure_manager ----

def test_ensure_manager_allows():
    rules.ensure_manager(actor("GERENTE"))


def test_ensure_manager_denies():
    with pytest.raises(PermissionError):
        rules.ensure_manager(actor("ADMIN"))


# ---- name validations ----

@pytest.mark.parametrize("fn", [
    rules.validate_brand_name,
    rules.validate_model_name,
    rules.validate_version_name,
])
def test_validate_name_ok(fn):
    assert fn("  Teste  ") == "Teste"


@pytest.mark.parametrize("fn", [
    rules.validate_brand_name,
    rules.validate_model_name,
    rules.validate_version_name,
])
def test_validate_name_invalid(fn):
    with pytest.raises(ValueError):
        fn("   ")


# ---- normalize_image_url ----

def test_normalize_image_url_none():
    assert rules.normalize_image_url(None) is None


def test_normalize_image_url_strip():
    assert rules.normalize_image_url("  http://img.com  ") == "http://img.com"


def test_normalize_image_url_empty():
    assert rules.normalize_image_url("   ") is None