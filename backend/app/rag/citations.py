from __future__ import annotations


def build_citations(source_ids: list[str], retrieved_chunks: list[dict]) -> list[dict]:
    indexed = {chunk["source_id"]: chunk for chunk in retrieved_chunks}
    citations: list[dict] = []
    for source_id in source_ids:
        chunk = indexed.get(source_id)
        if not chunk:
            continue
        citations.append(
            {
                "chunk_id": chunk["chunk_id"],
                "file_name": chunk["file_name"],
                "page_number": chunk["page_number"],
                "quote": chunk["content"][:320],
                "score": chunk.get("score"),
            }
        )
    return citations
