# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()  # read .env in local dev if present

class Config:
    # Backend
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))

    # Database (SQLAlchemy DATABASE_URL)
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Anonymous(*_*)-(^_^)@db.ocpldyafbkxuwxkznggj.supabase.co:5432/postgres")  # required in production

    # OpenRouter / LLM
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "mistral/mistral-7b-instruct")

    # Demo mode fallback (if True, LLM calls are stubbed)
    DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() in ("1", "true", "yes")

    # Upload settings
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/tmp/uploads")
    MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))

    # Validate early
    @staticmethod
    def validate():
        if not Config.DATABASE_URL:
            raise RuntimeError("DATABASE_URL is not set. Copy full Postgres connection string from Supabase (Settings → Database → Connection string).")
        # if you want to force LLM keys required, remove the next check and rely on DEMO_MODE
        # if not Config.OPENROUTER_API_KEY and not Config.DEMO_MODE:
        #     raise RuntimeError("OPENROUTER_API_KEY is not set and DEMO_MODE is false.")
