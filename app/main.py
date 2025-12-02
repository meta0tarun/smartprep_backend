# app/main.py
import logging
from fastapi import FastAPI
from .routes import router
from .config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

def create_app():
    app = FastAPI(title="SmartPrep Backend (MVP - No DB)")
    app.include_router(router)
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=Config.HOST, port=Config.PORT, reload=True)
