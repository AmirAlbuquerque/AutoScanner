import uuid
from typing import Any, Optional

from src.database.infrastructure.connection import get_conn

def get_store(store_id: str) -> Optional[dict[str, Any]]:
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT id, owner_id, name, region, status, rejection_reason,
                   approved_by, approved_at, created_by, created_at, updated_at
            FROM stores
            WHERE id = ?
            """,
            (store_id,),
        ).fetchone()
    return dict(row) if row else None

def list_stores(
    *,
    region: Optional[str] = None,
    status: Optional[str] = None,
    owner_id: Optional[str] = None,
    created_by: Optional[str] = None,
    limit: int = 200,
    offset: int = 0,
) -> list[dict[str, Any]]:
    where = []
    params: list[Any] = []

    if region:
        where.append("region = ?")
        params.append(region)

    if status:
        where.append("status = ?")
        params.append(status)

    if owner_id:
        where.append("owner_id = ?")
        params.append(owner_id)

    if created_by:
        where.append("created_by = ?")
        params.append(created_by)

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    with get_conn() as conn:
        rows = conn.execute(
            f"""
            SELECT id, owner_id, name, region, status, rejection_reason,
                   approved_by, approved_at, created_by, created_at, updated_at
            FROM stores
            {where_sql}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            (*params, int(limit), int(offset)),
        ).fetchall()

    return [dict(r) for r in rows]


def list_pending_stores_by_region(region: str, limit: int = 200) -> list[dict[str, Any]]:
    """
    Para COORDENADOR: lojas pendentes na região dele.
    """
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, owner_id, name, region, status, rejection_reason,
                   approved_by, approved_at, created_by, created_at, updated_at
            FROM stores
            WHERE region = ? AND status = 'PENDENTE'
            ORDER BY created_at ASC
            LIMIT ?
            """,
            (region, int(limit)),
        ).fetchall()
    return [dict(r) for r in rows]

def store_exists(store_id: str) -> bool:
    with get_conn() as conn:
        row = conn.execute("SELECT 1 FROM stores WHERE id = ? LIMIT 1", (store_id,)).fetchone()
    return bool(row)

# Insert / Update base
def create_store(
    *,
    name: str,
    region: str,
    created_by: str,
    owner_id: Optional[str],
    status: str,
    created_at: str,
    updated_at: Optional[str] = None,
) -> str:
    """
    Cria loja. Use status='PENDENTE' no fluxo normal.
    """
    store_id = str(uuid.uuid4())
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO stores (
                id, owner_id, name, region, status, rejection_reason,
                approved_by, approved_at, created_by, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, NULL, NULL, NULL, ?, ?, ?)
            """,
            (store_id, owner_id, name, region, status, created_by, created_at, updated_at),
        )
    return store_id

def update_store_basic(
    *,
    store_id: str,
    name: str,
    region: str,
    owner_id: Optional[str],
    updated_at: str,
) -> None:

    with get_conn() as conn:
        conn.execute(
            """
            UPDATE stores
            SET name = ?,
                region = ?,
                owner_id = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (name, region, owner_id, updated_at, store_id),
        )

# Status transitions (approve/reject/inactivate)

def approve_store(
    *,
    store_id: str,
    approved_by: str,
    approved_at: str,
    updated_at: str,
) -> None:
    """
    PENDENTE -> APROVADA
    Limpa rejection_reason
    """
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE stores
            SET status = 'APROVADA',
                rejection_reason = NULL,
                approved_by = ?,
                approved_at = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (approved_by, approved_at, updated_at, store_id),
        )

def reject_store(
    *,
    store_id: str,
    approved_by: str,
    approved_at: str,
    rejection_reason: str,
    updated_at: str,
) -> None:
    """
    PENDENTE -> REPROVADA
    """
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE stores
            SET status = 'REPROVADA',
                rejection_reason = ?,
                approved_by = ?,
                approved_at = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (rejection_reason, approved_by, approved_at, updated_at, store_id),
        )

def inactivate_store(
    *,
    store_id: str,
    updated_at: str,
) -> None:
    status = "INATIVA"
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE stores
            SET status = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (status, updated_at, store_id),
        )

def get_store_region_and_status(store_id: str) -> Optional[dict[str, Any]]:
    """
    Retorna só os campos que o service precisa para autorização/fluxo.
    """
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, region, status, owner_id, created_by FROM stores WHERE id = ?",
            (store_id,),
        ).fetchone()
    return dict(row) if row else None


def list_approved_stores_by_region(region: str, limit: int = 200) -> list[dict[str, Any]]:
    """
    Para pesquisador selecionar loja APROVADA na região.
    """
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, owner_id, name, region, status, created_at, updated_at
            FROM stores
            WHERE region = ? AND status = 'APROVADA'
            ORDER BY name ASC
            LIMIT ?
            """,
            (region, int(limit)),
        ).fetchall()
    return [dict(r) for r in rows]