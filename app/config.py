# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))

    # LLM / OpenRouter
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")  # no default, keep secret
    OPENROUTER_API_URL = os.getenv(
        "OPENROUTER_API_URL",
        "https://api.openrouter.ai/v1/chat/completions"
    )
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "mistral/mistral-7b-instruct")

    # Demo mode: skip LLM and return fast stub results
    DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() in ("1", "true", "yes")

    # Uploads
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/tmp/uploads")
    MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))

    @staticmethod
    def validate():
        # For MVP, we allow missing OPENROUTER_API_KEY if DEMO_MODE is true.
        if not Config.DEMO_MODE and not Config.OPENROUTER_API_KEY:
            raise RuntimeError("OPENROUTER_API_KEY is not set and DEMO_MODE is false.")
