from typing import Any, Optional

from src.services import auth_service
from src.database.infrastructure.repositories import brands_db, models_db, versions_db
from src.domain import catalog_rules

def _get_actor(payload):
    actor = auth_service.require_authenticated(payload)
    return auth_service.require_active_user(actor)

# BRANDS
def manager_list_brands(actor_payload: dict[str, Any]) -> list[dict[str, Any]]:
    actor = _get_actor(actor_payload)
    catalog_rules.ensure_manager(actor)
    return brands_db.list_brands()

def manager_create_brand(actor_payload: dict[str, Any], name: str) -> str:
    actor = _get_actor(actor_payload)
    catalog_rules.ensure_manager(actor)

    name = catalog_rules.validate_brand_name(name)
    return brands_db.create_brand(name)

def manager_update_brand(actor_payload: dict[str, Any], brand_id: str, name: str) -> None:
    actor = _get_actor(actor_payload)
    catalog_rules.ensure_manager(actor)

    if not brands_db.get_brand(brand_id):
        raise ValueError("Marca não encontrada.")

    name = catalog_rules.validate_brand_name(name)
    brands_db.update_brand(brand_id, name)

def manager_delete_brand(actor_payload: dict[str, Any], brand_id: str) -> None:
    actor = _get_actor(actor_payload)
    catalog_rules.ensure_manager(actor)
    brands_db.delete_brand(brand_id)

# MODELS

def manager_list_models(actor_payload: dict[str, Any], brand_id: str) -> list[dict[str, Any]]:
    actor = _get_actor(actor_payload)
    catalog_rules.ensure_manager(actor)

    if not models_db.get_brand(brand_id):
        raise ValueError("Marca não encontrada.")

    return models_db.list_models_by_brand(brand_id)

def manager_create_model(actor_payload: dict[str, Any], brand_id: str, name: str) -> str:
    actor = _get_actor(actor_payload)
    catalog_rules.ensure_manager(actor)

    if not models_db.get_brand(brand_id):
        raise ValueError("Marca não encontrada.")

    name = catalog_rules.validate_model_name(name)
    return models_db.create_model(brand_id, name)

def manager_update_model(actor_payload: dict[str, Any], model_id: str, name: str) -> None:
    actor = _get_actor(actor_payload)
    catalog_rules.ensure_manager(actor)

    if not models_db.get_model(model_id):
        raise ValueError("Modelo não encontrado.")

    name = catalog_rules.validate_model_name(name)
    models_db.update_model(model_id, name)

def manager_delete_model(actor_payload: dict[str, Any], model_id: str) -> None:
    actor = _get_actor(actor_payload)
    catalog_rules.ensure_manager(actor)

    models_db.delete_model(model_id)

# VERSIONS

def manager_list_versions(actor_payload: dict[str, Any], model_id: str) -> list[dict[str, Any]]:
    actor = _get_actor(actor_payload)
    catalog_rules.ensure_manager(actor)

    if not versions_db.get_model(model_id):
        raise ValueError("Modelo não encontrado.")

    return versions_db.list_versions_by_model(model_id)

def manager_create_version(
    actor_payload: dict[str, Any],
    model_id: str,
    name: str,
    image_url: Optional[str] = None,
) -> str:
    actor = _get_actor(actor_payload)
    catalog_rules.ensure_manager(actor)

    if not versions_db.get_model(model_id):
        raise ValueError("Modelo não encontrado.")

    name = catalog_rules.validate_version_name(name)
    image_url = catalog_rules.normalize_image_url(image_url)

    return versions_db.create_version(model_id, name, image_url)

def manager_update_version(
    actor_payload: dict[str, Any],
    version_id: str,
    name: str,
    image_url: Optional[str] = None,
) -> None:
    actor = _get_actor(actor_payload)
    catalog_rules.ensure_manager(actor)

    if not versions_db.get_version(version_id):
        raise ValueError("Versão não encontrada.")

    name = catalog_rules.validate_version_name(name)
    image_url = catalog_rules.normalize_image_url(image_url)

    versions_db.update_version(version_id, name, image_url)

def manager_delete_version(actor_payload: dict[str, Any], version_id: str) -> None:
    actor = _get_actor(actor_payload)
    catalog_rules.ensure_manager(actor)

    versions_db.delete_version(version_id)