# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))

    # Do NOT hardcode secrets here. Must be set in Render env.
    DATABASE_URL = os.getenv("DATABASE_URL")

    # OpenRouter / LLM
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    # full endpoint your code will call — override in Render if different
    OPENROUTER_API_URL = os.getenv(
        "OPENROUTER_API_URL",
        "https://api.openrouter.ai/v1/chat/completions"
    )
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "mistral/mistral-7b-instruct")

    DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() in ("1", "true", "yes")

    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/tmp/uploads")
    MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))

    @staticmethod
    def validate():
        if not Config.DATABASE_URL:
            raise RuntimeError("DATABASE_URL is not set.")
        if not Config.OPENROUTER_API_KEY and not Config.DEMO_MODE:
            raise RuntimeError("OPENROUTER_API_KEY not set and DEMO_MODE is false.")
