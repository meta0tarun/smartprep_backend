# app/main.py
import uvicorn
from fastapi import FastAPI
from .routes import router
from .config import Config

app = FastAPI(title="SmartPrep Backend")

app.include_router(router)

@app.on_event("startup")
async def startup_event():
    # create upload dir
    import pathlib
    pathlib.Path(Config.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=Config.HOST, port=Config.PORT, reload=True)
