import uuid
import bcrypt
from datetime import datetime, timezone
from src.database.infrastructure.connection import get_conn

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def create_users() -> None:
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

if __name__ == "__main__":
    init_db()
    print("DB inicializado.")