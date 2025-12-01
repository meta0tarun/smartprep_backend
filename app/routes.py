# app/routes.py
import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from .db import get_db
from .models import Upload as UploadModel, Analysis as AnalysisModel
from .ocr_utils import file_to_text
from .chunker import chunk_text
from .llm_client import call_llm_for_topics
from .aggregator import aggregate_topics
from .config import Config
from typing import List
import shutil
import uuid
import pathlib
import json

router = APIRouter()

# ensure upload dir exists
pathlib.Path(Config.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

@router.get("/health")
async def health():
    return JSONResponse({"status": "ok"})

def allowed_upload_size(file: UploadFile):
    # check size if needed (UploadFile doesn't expose size without reading)
    return

@router.post("/analyze-llm")
async def analyze_llm(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Accepts single file. Returns JSON:
    { "analysis_id": "<uuid>", "topicsMap": {...}, "summary": "...", "raw": {...} }
    """

    # save uploaded file to disk
    try:
        uid = str(uuid.uuid4())
        filename = f"{uid}_{file.filename}"
        dst = str(pathlib.Path(Config.UPLOAD_DIR) / filename)
        with open(dst, "wb") as out_f:
            content = await file.read()
            out_f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed saving upload: {e}")

    try:
        # OCR -> text pages
        pages = file_to_text(dst)
        # chunk and call LLM per file
        chunks = []
        for p in pages:
            chunks.extend(chunk_text(p))
        # If no chunks, create a minimal chunk
        if not chunks:
            chunks = [""]
        # call LLM
        llm_resp = call_llm_for_topics(chunks)
        topics_map = llm_resp.get("topics_map", {})
        summary = llm_resp.get("summary", "")
        raw = llm_resp.get("raw", {})
    except Exception as e:
        # return a helpful 500 with trace in detail for dev
        raise HTTPException(status_code=500, detail=str(e))

    # persist upload metadata + analysis
    try:
        upload = UploadModel(filename=file.filename, content_type=file.content_type, size_bytes=len(content), storage_path=dst)
        db.add(upload)
        db.commit()
        db.refresh(upload)

        analysis = AnalysisModel(upload_ids=[upload.id], summary=summary, raw_response=raw, topics_map=topics_map, status="done")
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
    except Exception as e:
        # If DB fails, return result but warn
        return JSONResponse(status_code=200, content={"analysis_id": None, "topicsMap": topics_map, "summary": summary, "raw": raw, "warning": f"DB save failed: {e}"})

    return JSONResponse({"analysis_id": analysis.id, "topicsMap": topics_map, "summary": summary, "raw": raw})

@router.post("/analyze-llm-batch")
async def analyze_llm_batch(files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    """
    Accepts multiple files in form 'files': file1, files: file2, ...
    Aggregates topics across files and returns combined map.
    """
    saved_uploads = []
    per_file_topics = []
    raw_agg = {"per_file": []}
    for file in files:
        try:
            uid = str(uuid.uuid4())
            filename = f"{uid}_{file.filename}"
            dst = str(pathlib.Path(Config.UPLOAD_DIR) / filename)
            with open(dst, "wb") as out_f:
                content = await file.read()
                out_f.write(content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed saving upload {file.filename}: {e}")

        # OCR + LLM per file
        try:
            pages = file_to_text(dst)
            chunks = []
            for p in pages:
                chunks.extend(chunk_text(p))
            if not chunks:
                chunks = [""]
            llm_resp = call_llm_for_topics(chunks)
            topics_map = llm_resp.get("topics_map", {})
            per_file_topics.append(topics_map)
            raw_agg["per_file"].append({"filename": file.filename, "raw": llm_resp.get("raw")})
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Processing error for {file.filename}: {e}")

        # save upload row
        try:
            upload = UploadModel(filename=file.filename, content_type=file.content_type, size_bytes=len(content), storage_path=dst)
            db.add(upload)
            db.commit()
            db.refresh(upload)
            saved_uploads.append(upload.id)
        except Exception as e:
            # continue but record warning
            saved_uploads.append(None)

    # aggregate
    combined = aggregate_topics(per_file_topics)

    # store analysis
    try:
        analysis = AnalysisModel(upload_ids=saved_uploads, summary="Batch analysis", raw_response=raw_agg, topics_map=combined, status="done")
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
    except Exception as e:
        return JSONResponse(status_code=200, content={"analysis_id": None, "topicsMap": combined, "summary": "", "raw": raw_agg, "warning": f"DB save failed: {e}"})

    return JSONResponse({"analysis_id": analysis.id, "topicsMap": combined, "summary": "", "raw": raw_agg})
