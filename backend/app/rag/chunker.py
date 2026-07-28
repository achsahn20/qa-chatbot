from __future__ import annotations

from dataclasses import dataclass
import re

from app.config import get_settings


@dataclass(slots=True)
class ChunkPayload:
    chunk_index: int
    page_number: int
    content: str
    section_title: str | None
    char_start: int
    char_end: int
    token_count: int


def estimate_tokens(text: str) -> int:
    return max(1, int(len(text.split()) * 1.3))


def detect_section_title(text: str) -> str | None:
    first_line = text.splitlines()[0].strip() if text.splitlines() else ""
    if not first_line:
        return None
    if len(first_line) <= 120 and (first_line.istitle() or first_line.isupper()):
        return first_line
    return None


def _paragraph_units(text: str) -> list[str]:
    units = [segment.strip() for segment in re.split(r"\n{2,}", text) if segment.strip()]
    if units:
        return units
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def chunk_pages(
    pages: list[dict],
    chunk_size_chars: int | None = None,
    chunk_overlap_chars: int | None = None,
) -> list[ChunkPayload]:
    settings = get_settings()
    chunk_size = chunk_size_chars or settings.chunk_size_chars
    overlap = chunk_overlap_chars or settings.chunk_overlap_chars
    results: list[ChunkPayload] = []
    chunk_index = 0

    for page in pages:
        page_text = page["text"]
        if not page_text:
            continue
        units = _paragraph_units(page_text)
        current = ""
        current_start = 0

        for unit in units:
            candidate = f"{current}\n\n{unit}".strip() if current else unit
            if len(candidate) <= chunk_size:
                if not current:
                    current_start = page_text.find(unit)
                current = candidate
                continue

            if current:
                start = current_start
                end = start + len(current)
                results.append(
                    ChunkPayload(
                        chunk_index=chunk_index,
                        page_number=page["page_number"],
                        content=current,
                        section_title=detect_section_title(current),
                        char_start=start,
                        char_end=end,
                        token_count=estimate_tokens(current),
                    )
                )
                chunk_index += 1

                overlap_text = current[-overlap:] if overlap < len(current) else current
                current = f"{overlap_text}\n\n{unit}".strip()
                current_start = max(0, end - len(overlap_text))
            else:
                for idx in range(0, len(unit), max(1, chunk_size - overlap)):
                    part = unit[idx : idx + chunk_size]
                    results.append(
                        ChunkPayload(
                            chunk_index=chunk_index,
                            page_number=page["page_number"],
                            content=part,
                            section_title=detect_section_title(part),
                            char_start=idx,
                            char_end=idx + len(part),
                            token_count=estimate_tokens(part),
                        )
                    )
                    chunk_index += 1
                current = ""

        if current:
            start = current_start
            end = start + len(current)
            results.append(
                ChunkPayload(
                    chunk_index=chunk_index,
                    page_number=page["page_number"],
                    content=current,
                    section_title=detect_section_title(current),
                    char_start=start,
                    char_end=end,
                    token_count=estimate_tokens(current),
                )
            )
            chunk_index += 1

    return results
