import uuid
import bcrypt
from datetime import datetime, timezone
from src.database.infrastructure.connection import get_conn

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def create_tables() -> None:
    #Criação da tabela users
    with get_conn() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            role TEXT NOT NULL CHECK(role IN ('ADMIN','GERENTE','COORDENADOR','PESQUISADOR','LOJISTA')),
            region TEXT,
            password_hash TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        );
        """)

        # Cria a tabela de stores
        conn.execute("""
        CREATE TABLE IF NOT EXISTS stores (
            id TEXT PRIMARY KEY,
            owner_id TEXT,
            name TEXT NOT NULL,
            region TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('PENDENTE','APROVADA','REPROVADA','INATIVA')),
            rejection_reason TEXT,
            approved_by TEXT,
            approved_at TEXT,
            created_by TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT,
            FOREIGN KEY(owner_id) REFERENCES users(id),
            FOREIGN KEY(approved_by) REFERENCES users(id),
            FOREIGN KEY(created_by) REFERENCES users(id)
        );
        """)

        # Criação da tabela de brands
        conn.execute("""
        CREATE TABLE IF NOT EXISTS brands (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        );
        """)

        #Criação da tabela de models
        conn.execute("""
        CREATE TABLE IF NOT EXISTS models (
            id TEXT PRIMARY KEY,
            brand_id TEXT NOT NULL,
            name TEXT NOT NULL,
            UNIQUE(brand_id, name),
            FOREIGN KEY(brand_id) REFERENCES brands(id)
        );
        """)

        #Criação da tabela de versions
        conn.execute("""
        CREATE TABLE IF NOT EXISTS versions (
            id TEXT PRIMARY KEY,
            model_id TEXT NOT NULL,
            name TEXT NOT NULL,
            image_url TEXT,
            UNIQUE(model_id, name),
            FOREIGN KEY(model_id) REFERENCES models(id)
        );
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS captures (
            id TEXT PRIMARY KEY,
            store_id TEXT NOT NULL,
            researcher_id TEXT NOT NULL,
            capture_date TEXT NOT NULL,   -- timestamp
            capture_month TEXT NOT NULL,  -- YYYY-MM (competência)
            created_at TEXT NOT NULL,
            FOREIGN KEY(store_id) REFERENCES stores(id),
            FOREIGN KEY(researcher_id) REFERENCES users(id)
        );
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS vehicle_captures (
            id TEXT PRIMARY KEY,
            capture_id TEXT NOT NULL,
            brand_id TEXT NOT NULL,
            model_id TEXT NOT NULL,
            version_id TEXT NOT NULL,
            year_fabrication INTEGER NOT NULL,
            price REAL NOT NULL CHECK(price >= 0),
            created_at TEXT NOT NULL,
            FOREIGN KEY(capture_id) REFERENCES captures(id),
            FOREIGN KEY(brand_id) REFERENCES brands(id),
            FOREIGN KEY(model_id) REFERENCES models(id),
            FOREIGN KEY(version_id) REFERENCES versions(id)
        );
        """)
        
        #Criação da tabela de planejamentos semanais
        conn.execute("""
        CREATE TABLE IF NOT EXISTS weekly_plannings (
            id TEXT PRIMARY KEY,
            coordinator_id TEXT NOT NULL,
            region TEXT NOT NULL,
            week_start TEXT NOT NULL, -- YYYY-MM-DD
            status TEXT NOT NULL CHECK(status IN ('RASCUNHO','PUBLICADO')),
            created_at TEXT NOT NULL,
            FOREIGN KEY(coordinator_id) REFERENCES users(id),
            UNIQUE(region, week_start)
        );
        """)

        #Criação da tabela de atribuições de planejamento
        conn.execute("""
        CREATE TABLE IF NOT EXISTS planning_assignments (
            id TEXT PRIMARY KEY,
            planning_id TEXT NOT NULL,
            store_id TEXT NOT NULL,
            researcher_id TEXT NOT NULL,
            FOREIGN KEY(planning_id) REFERENCES weekly_plannings(id),
            FOREIGN KEY(store_id) REFERENCES stores(id),
            FOREIGN KEY(researcher_id) REFERENCES users(id),
            UNIQUE(planning_id, store_id, researcher_id)
        );
        """)

        # Criação da tabela de snapshots de preços
        conn.execute("""
        CREATE TABLE IF NOT EXISTS price_snapshots (
            id TEXT PRIMARY KEY,
            region TEXT NOT NULL,
            brand_id TEXT NOT NULL,
            model_id TEXT NOT NULL,
            version_id TEXT NOT NULL,
            year_model INTEGER NOT NULL,
            ref_month TEXT NOT NULL,       -- YYYY-MM
            fipe_price REAL,
            avg_price REAL,
            samples INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY(brand_id) REFERENCES brands(id),
            FOREIGN KEY(model_id) REFERENCES models(id),
            FOREIGN KEY(version_id) REFERENCES versions(id),
            UNIQUE(region, brand_id, model_id, COALESCE(version_id, ''), COALESCE(year_model, -1), ref_month)
        );
        """)

        # Criação da tabela de consultas públicas
        conn.execute("""
        CREATE TABLE IF NOT EXISTS public_queries (
            id TEXT PRIMARY KEY,
            brand_id TEXT NOT NULL,
            model_id TEXT NOT NULL,
            version_id TEXT NOT NULL,
            year_model INTEGER NOT NULL,
            region TEXT NOT NULL,
            created_at TEXT NOT NULL,
            actor_user_id TEXT,
            FOREIGN KEY(actor_user_id) REFERENCES users(id)
        );
        """)

def seed_admin(email: str = "admin@autoscanner.local", password: str = "admin123") -> None:
    """Cria admin padrão se não existir. Troque depois."""
    pw_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    with get_conn() as conn:
        row = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if row:
            return
        conn.execute(
            """
            INSERT INTO users (id, name, email, role, region, password_hash, active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (str(uuid.uuid4()), "Admin", email, "ADMIN", None, pw_hash, 1, now_iso())
        )

def init_db() -> None:
    create_tables()
    seed_admin()
