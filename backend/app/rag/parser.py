from __future__ import annotations

from pathlib import Path

import fitz


def _clean_text(text: str) -> str:
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines)


def extract_pdf_pages(file_path: str | Path) -> list[dict]:
    document = fitz.open(file_path)
    pages: list[dict] = []
    try:
        for page_index, page in enumerate(document, start=1):
            raw_text = page.get_text("text")
            cleaned = _clean_text(raw_text)
            pages.append(
                {
                    "page_number": page_index,
                    "text": cleaned,
                }
            )
    finally:
        document.close()
    return pages
