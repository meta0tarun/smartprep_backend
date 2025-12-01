# app/chunker.py
from typing import List

def chunk_text(text: str, max_chars: int = 1500) -> List[str]:
    # simple sentence-based chunker: split on paragraphs and aggregate
    if not text:
        return []
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""
    for p in paragraphs:
        if len(current) + len(p) + 1 <= max_chars:
            current = (current + "\n\n" + p).strip()
        else:
            if current:
                chunks.append(current)
            current = p
    if current:
        chunks.append(current)
    # fallback: if still empty, split on max_chars segments
    out = []
    for c in chunks:
        if len(c) <= max_chars:
            out.append(c)
        else:
            for i in range(0, len(c), max_chars):
                out.append(c[i:i+max_chars])
    return out
