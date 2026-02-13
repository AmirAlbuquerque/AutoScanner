from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

import bcrypt

from src.database.infrastructure.init_db import init_db
from src.database.infrastructure.connection import get_conn


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uuid() -> str:
    return str(uuid.uuid4())


def _hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _get_one(conn, sql: str, params: tuple[Any, ...]) -> Optional[dict]:
    row = conn.execute(sql, params).fetchone()
    return dict(row) if row else None


def run_seed() -> None:
    """
    Seed para testar médias gerais por marca/modelo/versão:
      - 1 região
      - 8 lojas (mesma região)
      - 2 marcas
      - 2 modelos por marca
      - 2 versões por modelo (8 versões no total)
      - 1 captura por loja no mês (8 captures)
      - cada captura contém todas as versões (8*8 = 64 vehicle_captures)
    """

    init_db()

    REGION = "Grande Belo Horizonte"
    MONTH = "2026-02"
    CAPTURE_DATE = "2026-02-15T10:00:00+00:00"
    YEAR_FAB = 2023

    PASSWORD = "admin123"  # senha única para todos os usuários seed

    with get_conn() as conn:
        print("📦 DB:", conn.execute("PRAGMA database_list").fetchall())

        # -------------------------
        # USERS (idempotente por email)
        # -------------------------
        def get_or_create_user(name: str, email: str, role: str, region: Optional[str]) -> str:
            email_norm = email.strip().lower()
            existing = _get_one(conn, "SELECT id FROM users WHERE email = ?", (email_norm,))
            if existing:
                return existing["id"]

            uid = _uuid()
            conn.execute(
                """
                INSERT INTO users (id, name, email, role, region, password_hash, active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 1, ?)
                """,
                (uid, name, email_norm, role, region, _hash_password(PASSWORD), _now_iso()),
            )
            return uid

        admin_id = get_or_create_user("Admin", "admin@auto.com", "ADMIN", None)
        coord_id = get_or_create_user("Carlos Coordenador", "coord@auto.com", "COORDENADOR", REGION)
        pesquisador_id = get_or_create_user("Pedro Pesquisador", "pesq@auto.com", "PESQUISADOR", REGION)
        lojista_id = get_or_create_user("Lojista BH", "lojista@auto.com", "LOJISTA", REGION)

        # -------------------------
        # CATALOG helpers
        # -------------------------
        def get_or_create_brand(name: str) -> str:
            row = _get_one(conn, "SELECT id FROM brands WHERE name = ?", (name,))
            if row:
                return row["id"]
            bid = _uuid()
            conn.execute("INSERT INTO brands (id, name) VALUES (?, ?)", (bid, name))
            return bid

        def get_or_create_model(brand_id: str, name: str) -> str:
            row = _get_one(conn, "SELECT id FROM models WHERE brand_id = ? AND name = ?", (brand_id, name))
            if row:
                return row["id"]
            mid = _uuid()
            conn.execute("INSERT INTO models (id, brand_id, name) VALUES (?, ?, ?)", (mid, brand_id, name))
            return mid

        def get_or_create_version(model_id: str, name: str) -> str:
            row = _get_one(conn, "SELECT id FROM versions WHERE model_id = ? AND name = ?", (model_id, name))
            if row:
                return row["id"]
            vid = _uuid()
            conn.execute(
                "INSERT INTO versions (id, model_id, name, image_url) VALUES (?, ?, ?, ?)",
                (vid, model_id, name, None),
            )
            return vid

        # -------------------------
        # 2 marcas, 2 modelos cada, 2 versões cada
        # -------------------------
        toyota = get_or_create_brand("Toyota")
        honda = get_or_create_brand("Honda")

        # “2 veículos para cada” => 2 modelos por marca
        corolla = get_or_create_model(toyota, "Corolla")
        hilux = get_or_create_model(toyota, "Hilux")

        civic = get_or_create_model(honda, "Civic")
        hrv = get_or_create_model(honda, "HR-V")

        # 2 versões por modelo => 8 versões no total
        versions = [
            # Toyota Corolla
            (toyota, corolla, "Corolla GLi 2.0 CVT", 118000.0),
            (toyota, corolla, "Corolla XEi 2.0 CVT", 128000.0),

            # Toyota Hilux
            (toyota, hilux, "Hilux SR 2.8 4x4", 240000.0),
            (toyota, hilux, "Hilux SRX 2.8 4x4", 265000.0),

            # Honda Civic
            (honda, civic, "Civic EXL 2.0 CVT", 142000.0),
            (honda, civic, "Civic Touring 1.5 Turbo", 158000.0),

            # Honda HR-V
            (honda, hrv, "HR-V EX 1.5", 128000.0),
            (honda, hrv, "HR-V EXL 1.5", 135000.0),
        ]

        version_rows: list[dict[str, Any]] = []
        for brand_id, model_id, version_name, base_price in versions:
            version_id = get_or_create_version(model_id, version_name)
            version_rows.append(
                {
                    "brand_id": brand_id,
                    "model_id": model_id,
                    "version_id": version_id,
                    "version_name": version_name,
                    "base_price": float(base_price),
                }
            )

        # -------------------------
        # 8 lojas (mesma região) - aprovadas
        # -------------------------
        store_names = [
            "Auto BH Centro",
            "BH Motors Pampulha",
            "VendaCar Savassi",
            "Prime Veículos Barreiro",
            "Autoshop Contagem",
            "Via Car Betim",
            "Classificados BH Norte",
            "Elite Seminovos BH",
        ]

        def get_or_create_store(name: str, region: str) -> str:
            row = _get_one(conn, "SELECT id FROM stores WHERE name = ? AND region = ?", (name, region))
            if row:
                return row["id"]

            sid = _uuid()
            conn.execute(
                """
                INSERT INTO stores
                (id, owner_id, name, region, status, rejection_reason, approved_by, approved_at, created_by, created_at, updated_at)
                VALUES (?, ?, ?, ?, 'APROVADA', NULL, ?, ?, ?, ?, NULL)
                """,
                (sid, lojista_id, name, region, coord_id, _now_iso(), lojista_id, _now_iso()),
            )
            return sid

        store_ids = [get_or_create_store(n, REGION) for n in store_names]

        # -------------------------
        # Captures: 1 por loja no mês
        # idempotente por (store_id, capture_month)
        # -------------------------
        def get_or_create_capture(store_id: str, capture_month: str) -> str:
            row = _get_one(
                conn,
                "SELECT id FROM captures WHERE store_id = ? AND capture_month = ?",
                (store_id, capture_month),
            )
            if row:
                return row["id"]

            cid = _uuid()
            conn.execute(
                """
                INSERT INTO captures
                (id, store_id, researcher_id, capture_date, capture_month, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (cid, store_id, pesquisador_id, CAPTURE_DATE, capture_month, _now_iso()),
            )
            return cid

        capture_ids = [get_or_create_capture(sid, MONTH) for sid in store_ids]

        # -------------------------
        # vehicle_captures: todas as versões em todas as lojas
        # => 8 lojas * 8 versões = 64 linhas
        #
        # Variação por loja para dar dispersão (e média fazer sentido)
        # -------------------------
        multipliers_by_store_index = [0.97, 0.985, 0.99, 1.00, 1.01, 1.015, 1.02, 1.03]

        def exists_vehicle_capture(capture_id: str, version_id: str, year_fabrication: int) -> bool:
            r = _get_one(
                conn,
                """
                SELECT id FROM vehicle_captures
                WHERE capture_id = ? AND version_id = ? AND year_fabrication = ?
                """,
                (capture_id, version_id, int(year_fabrication)),
            )
            return bool(r)

        inserted = 0
        for i, (cap_id, store_id) in enumerate(zip(capture_ids, store_ids)):
            mult = multipliers_by_store_index[i % len(multipliers_by_store_index)]
            for v in version_rows:
                if exists_vehicle_capture(cap_id, v["version_id"], YEAR_FAB):
                    continue

                price = round(v["base_price"] * mult, 2)
                conn.execute(
                    """
                    INSERT INTO vehicle_captures
                    (id, capture_id, brand_id, model_id, version_id, year_fabrication, price, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (_uuid(), cap_id, v["brand_id"], v["model_id"], v["version_id"], YEAR_FAB, float(price), _now_iso()),
                )
                inserted += 1

    print("✅ Seed concluída.")
    print(f"📍 Região: {REGION} | 🏬 Lojas: {len(store_names)} | 📅 Mês: {MONTH}")
    print(f"🚗 Versões: {len(version_rows)} | vehicle_captures inseridos agora: {inserted}")
    print("🔐 Logins seed (senha única):", PASSWORD)
    print("   admin@auto.com | coord@auto.com | pesq@auto.com | lojista@auto.com")