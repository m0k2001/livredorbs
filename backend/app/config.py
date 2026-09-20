import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Persistent data directory (for SQLite DB)
DATA_DIR = Path(os.getenv("DATA_DIR", str(BASE_DIR)))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "livredor.db"

# Persistent media uploads directory
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", str(BASE_DIR / "uploads")))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Built frontend directory (for production Docker serving)
FRONTEND_DIST_DIR = Path(os.getenv("FRONTEND_DIST", str(BASE_DIR.parent / "frontend" / "dist")))

# Secret token required in the API submission
SECRET_SUBMIT_TOKEN = os.getenv("SUBMIT_TOKEN", "retraitebs-7x8k2q")

# Secret URL slug for guest submission access (/souvenir-v7k9x4p)
CLIENT_SECRET_SLUG = os.getenv("CLIENT_SECRET_SLUG", "souvenir-v7k9x4p")

# Admin password for moderation
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "beatrice2026")

# Team password for colleagues photo upload
TEAM_PASSWORD = os.getenv("TEAM_PASSWORD", "vetalians2026")

# Doctor name for branding
HONORED_PERSON = os.getenv("HONORED_PERSON", "Dr Béatrice Sarda")

# API Documentation toggle (Swagger / Redoc) - disabled by default in production
ENABLE_DOCS = os.getenv("ENABLE_DOCS", "false").strip().lower() in ("true", "1", "yes")

# Allowed CORS origins
DEFAULT_ORIGINS = "https://retraitebs.vetalians.fr,http://localhost:5173,http://localhost:8000,http://127.0.0.1:5173,http://127.0.0.1:8000"
raw_origins = os.getenv("ALLOWED_ORIGINS", DEFAULT_ORIGINS)
ALLOWED_ORIGINS = [orig.strip() for orig in raw_origins.split(",") if orig.strip()]
if "*" in ALLOWED_ORIGINS:
    ALLOWED_ORIGINS = ["*"]

