# app/ocr_utils.py
import os
from typing import List
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
from .config import Config
import tempfile

# Convert an uploaded file (path) to list of plain text pages
def file_to_text(file_path: str) -> List[str]:
    """
    Supports images and PDF.
    Returns list of page-level text strings.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext in (".pdf",):
        # use pdf2image (requires poppler)
        images = convert_from_path(file_path, dpi=200)
        texts = []
        for im in images:
            texts.append(image_to_text(im))
        return texts
    else:
        # treat as image
        with Image.open(file_path) as im:
            return [image_to_text(im)]

def image_to_text(image: Image.Image) -> str:
    # you can set tesseract_cmd if not in PATH
    # pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
    text = pytesseract.image_to_string(image, lang='eng')
    return text or ""
