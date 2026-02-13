import pytest
from types import SimpleNamespace
import src.domain.user_rules as user_rule
import src.domain.store_rules as store_rule
import src.domain.catalog_rules as catalog_rule
import src.domain.capture_rules as capture_rule


def actor(*, role: str, region: str | None = None, id: str = "actor-1"):
    """Factory simples para simular Actor (evita depender da implementação real)."""
    return SimpleNamespace(role=role, region=region, id=id)


# -------------------------
# user_rule.ensure_admin
# -------------------------

def test_ensure_admin_allows_admin():
    user_rule.ensure_admin(actor(role="ADMIN"))  # não deve lançar


@pytest.mark.parametrize("role", ["", "NORMAL", "LOJISTA", "PESQUISADOR", "COORDENADOR", "GERENTE"])
def test_ensure_admin_denies_non_admin(role: str):
    with pytest.raises(PermissionError, match="ADMIN"):
        user_rule.ensure_admin(actor(role=role))


# -------------------------
# catalog_rule.ensure_manager
# -------------------------

def test_ensure_manager_allows_manager():
    catalog_rule.ensure_manager(actor(role="GERENTE"))  # não deve lançar


@pytest.mark.parametrize("role", ["ADMIN", "LOJISTA", "PESQUISADOR", "COORDENADOR"])
def test_ensure_manager_denies_non_manager(role: str):
    with pytest.raises(PermissionError, match="GERENTE"):
        catalog_rule.ensure_manager(actor(role=role))


# -------------------------
# store_rule.ensure_store_submitter
# -------------------------

@pytest.mark.parametrize("role", ["LOJISTA", "PESQUISADOR"])
def test_ensure_store_submitter_allows(role: str):
    store_rule.ensure_store_submitter(actor(role=role))


@pytest.mark.parametrize("role", ["ADMIN", "COORDENADOR", "GERENTE", "NORMAL"])
def test_ensure_store_submitter_denies(role: str):
    with pytest.raises(PermissionError, match="LOJISTA|PESQUISADOR"):
        store_rule.ensure_store_submitter(actor(role=role))


# -------------------------
# store_rule.ensure_coordinator
# -------------------------

def test_ensure_coordinator_allows():
    store_rule.ensure_coordinator(actor(role="COORDENADOR"))


@pytest.mark.parametrize("role", ["ADMIN", "LOJISTA", "PESQUISADOR", "GERENTE", "NORMAL"])
def test_ensure_coordinator_denies(role: str):
    with pytest.raises(PermissionError, match="COORDENADOR"):
        store_rule.ensure_coordinator(actor(role=role))


# -------------------------
# store_rule.ensure_same_region
# -------------------------

def test_ensure_same_region_allows_when_same():
    store_rule.ensure_same_region(actor(role="COORDENADOR", region="SP"), target_region="SP")


def test_ensure_same_region_denies_when_actor_has_no_region():
    with pytest.raises(PermissionError, match="sem região"):
        store_rule.ensure_same_region(actor(role="COORDENADOR", region=None), target_region="SP")


def test_ensure_same_region_denies_when_different():
    with pytest.raises(PermissionError, match="fora da sua região"):
        store_rule.ensure_same_region(actor(role="COORDENADOR", region="RJ"), target_region="SP")


# -------------------------
# store_rule.ensure_can_approve_store (coordinator + same region)
# -------------------------

def test_ensure_can_approve_store_allows_when_coordinator_same_region():
    store_rule.ensure_can_approve_store(actor(role="COORDENADOR", region="SP"), store_region="SP")


def test_ensure_can_approve_store_denies_when_not_coordinator():
    with pytest.raises(PermissionError, match="COORDENADOR"):
        store_rule.ensure_can_approve_store(actor(role="ADMIN", region="SP"), store_region="SP")


def test_ensure_can_approve_store_denies_when_region_diff():
    with pytest.raises(PermissionError, match="fora da sua região"):
        store_rule.ensure_can_approve_store(actor(role="COORDENADOR", region="RJ"), store_region="SP")


# -------------------------
# store_rule.ensure_can_manage_own_store
# -------------------------

def test_ensure_can_manage_own_store_allows_own_store():
    store_rule.ensure_can_manage_own_store(actor(role="LOJISTA", id="u1"), store_owner_id="u1")


def test_ensure_can_manage_own_store_denies_when_not_lojista():
    with pytest.raises(PermissionError, match="LOJISTA"):
        store_rule.ensure_can_manage_own_store(actor(role="PESQUISADOR", id="u1"), store_owner_id="u1")


def test_ensure_can_manage_own_store_denies_when_other_owner():
    with pytest.raises(PermissionError, match="suas próprias lojas"):
        store_rule.ensure_can_manage_own_store(actor(role="LOJISTA", id="u1"), store_owner_id="u2")


# -------------------------
# capture_rule.ensure_researcher
# -------------------------

def test_ensure_researcher_allows():
    capture_rule.ensure_researcher(actor(role="PESQUISADOR"))


@pytest.mark.parametrize("role", ["ADMIN", "LOJISTA", "COORDENADOR", "GERENTE", "NORMAL"])
def test_ensure_researcher_denies(role: str):
    with pytest.raises(PermissionError, match="PESQUISADOR"):
        capture_rule.ensure_researcher(actor(role=role))


# -------------------------
# capture_rule.ensure_can_capture
# -------------------------

def test_ensure_can_capture_allows_when_researcher_and_store_aprovada_and_assigned_true():
    capture_rule.ensure_can_capture(
        actor=actor(role="PESQUISADOR"),
        store_status="APROVADA",
        assigned_to_researcher=True,
        planning_status="PUBLICADO",
    )


def test_ensure_can_capture_allows_when_assigned_is_none():
    capture_rule.ensure_can_capture(
        actor=actor(role="PESQUISADOR"),
        store_status="APROVADA",
        assigned_to_researcher=None,
        planning_status="PUBLICADO",
    )


def test_ensure_can_capture_denies_when_not_researcher():
    with pytest.raises(PermissionError, match="PESQUISADOR"):
        capture_rule.ensure_can_capture(
            actor=actor(role="ADMIN"),
            store_status="APROVADA",
            assigned_to_researcher=True,
            planning_status="PUBLICADO",
        )


def test_ensure_can_capture_denies_when_store_not_aprovada():
    with pytest.raises(PermissionError, match="APROVADA"):
        capture_rule.ensure_can_capture(
            actor=actor(role="PESQUISADOR"),
            store_status="PENDENTE",
            assigned_to_researcher=True,
            planning_status="PUBLICADO",
        )


def test_ensure_can_capture_denies_when_assigned_false():
    with pytest.raises(PermissionError, match="não atribuída"):
        capture_rule.ensure_can_capture(
            actor=actor(role="PESQUISADOR"),
            store_status="APROVADA",
            assigned_to_researcher=False,
            planning_status="PUBLICADO",
        )


def test_ensure_can_capture_denies_when_planning_status_false():
    with pytest.raises(PermissionError, match="PUBLICADO"):
        capture_rule.ensure_can_capture(
            actor=actor(role="PESQUISADOR"),
            store_status="APROVADA",
            assigned_to_researcher=True,
            planning_status="RASCUNHO",
        )
