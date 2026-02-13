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
    create_users()
    seed_admin()
