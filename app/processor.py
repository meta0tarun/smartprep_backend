# app/processor.py
import os
import logging
from typing import List
from .config import Config

logger = logging.getLogger("app.processor")
logger.setLevel(logging.INFO)

# PDF extraction (pdfminer)
def _extract_text_from_pdf(path: str) -> str:
    try:
        from pdfminer.high_level import extract_text
        return extract_text(path) or ""
    except Exception as e:
        logger.warning("PDF extraction failed: %s", e)
        return ""

# Image OCR (pytesseract + PIL)
def _extract_text_from_image(path: str) -> str:
    try:
        from PIL import Image
        import pytesseract
        img = Image.open(path)
        text = pytesseract.image_to_string(img)
        return text or ""
    except Exception as e:
        logger.warning("Image OCR failed: %s", e)
        return ""

def extract_text_from_file(path: str) -> str:
    path = str(path)
    ext = os.path.splitext(path)[1].lower()
    if ext in (".pdf",):
        return _extract_text_from_pdf(path)
    elif ext in (".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"):
        return _extract_text_from_image(path)
    else:
        # Attempt PDF extraction first, otherwise return empty
        return _extract_text_from_pdf(path) or _extract_text_from_image(path) or ""

def basic_topic_heuristic(text: str, max_topics: int = 6):
    """
    Very small heuristic to pick top words/phrases as topics if LLM isn't used.
    This is only a fallback.
    """
    if not text:
        return {}
    import re
    words = re.findall(r"[A-Za-z]{3,}", text)
    freq = {}
    for w in words:
        k = w.lower()
        freq[k] = freq.get(k, 0) + 1
    # take top N words which are not stopwords
    stop = set(["the","and","for","with","this","that","are","from","which","between","using","use"])
    items = [(k, v) for k, v in freq.items() if k not in stop]
    items.sort(key=lambda x: x[1], reverse=True)
    top = dict(items[:max_topics])
    return top
