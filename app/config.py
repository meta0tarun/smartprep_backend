import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))

    DATABASE_URL = os.getenv("DATABASE_URL")  # MUST be set in Render

    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "mistral/mistral-7b-instruct")

    OPENROUTER_API_URL = os.getenv(
        "OPENROUTER_API_URL",
        "https://api.openrouter.ai/v1/chat/completions"
    )

    DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() in ("1", "true", "yes")

    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/tmp/uploads")
    MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))

    @staticmethod
    def validate():
        if not Config.DATABASE_URL:
            raise RuntimeError("Missing DATABASE_URL")
        if not Config.OPENROUTER_API_KEY and not Config.DEMO_MODE:
            raise RuntimeError("Missing OPENROUTER_API_KEY while DEMO_MODE=false")
