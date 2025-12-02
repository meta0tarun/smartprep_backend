# app/routes.py
import os
import uuid
import shutil
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List
from .config import Config
from .processor import extract_text_from_file, basic_topic_heuristic
from .llm_client import call_openrouter

logger = logging.getLogger("app.routes")
logger.setLevel(logging.INFO)

router = APIRouter()

def ensure_upload_dir():
    os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
    return Config.UPLOAD_DIR

@router.get("/health")
async def health():
    return JSONResponse({"status": "ok"})

def _save_upload(upload: UploadFile) -> str:
    updir = ensure_upload_dir()
    fname = f"{uuid.uuid4().hex}_{upload.filename}"
    dest = os.path.join(updir, fname)
    with open(dest, "wb") as f:
        shutil.copyfileobj(upload.file, f)
    upload.file.close()
    return dest

@router.post("/analyze-llm")
async def analyze_llm(file: UploadFile = File(...)):
    """
    Accepts a single file in form field 'file'
    """
    try:
        path = _save_upload(file)
        text = extract_text_from_file(path)
        if not text:
            # fallback message
            text = f"[no text extracted from {file.filename}]"
        # If DEMO_MODE, LLM client returns stub
        llm_resp = call_openrouter(text)
        # If LLM returned no topics, use fallback heuristic
        topics = llm_resp.get("topicsMap") or basic_topic_heuristic(text)
        return JSONResponse({
            "analysis_id": None,
            "topicsMap": topics,
            "summary": llm_resp.get("summary"),
            "raw": llm_resp.get("raw"),
        })
    except Exception as e:
        logger.exception("Processing error for %s", getattr(file, "filename", "unknown"))
        raise HTTPException(status_code=500, detail=f"Processing error for {getattr(file, 'filename', 'unknown')}: {e}")

@router.post("/analyze-llm-batch")
async def analyze_llm_batch(files: List[UploadFile] = File(...)):
    """
    Accepts multiple files in form field 'files'
    """
    saved = []
    combined_text = []
    try:
        for f in files:
            p = _save_upload(f)
            saved.append(p)
            txt = extract_text_from_file(p)
            if txt:
                combined_text.append(txt)
        joined = "\n\n".join(combined_text)
        if not joined:
            joined = "[no text extracted from uploaded files]"
        llm_resp = call_openrouter(joined)
        topics = llm_resp.get("topicsMap") or basic_topic_heuristic(joined)
        return JSONResponse({
            "analysis_id": None,
            "topicsMap": topics,
            "summary": llm_resp.get("summary"),
            "raw": llm_resp.get("raw"),
        })
    except Exception as e:
        logger.exception("Processing error for batch")
        raise HTTPException(status_code=500, detail=f"Processing error: {e}")
