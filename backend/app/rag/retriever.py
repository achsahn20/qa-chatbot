from __future__ import annotations

import re

from app.config import get_settings
from app.rag.embeddings import get_embedding_service
from app.rag.vector_store import get_vector_store


TOKEN_PATTERN = re.compile(r"\b[\w-]+\b")


def _keyword_overlap_score(question: str, content: str) -> float:
    question_terms = set(TOKEN_PATTERN.findall(question.lower()))
    content_terms = set(TOKEN_PATTERN.findall(content.lower()))
    if not question_terms or not content_terms:
        return 0.0
    overlap = len(question_terms & content_terms)
    return overlap / max(1, min(len(question_terms), 8))


def retrieve_chunks(question: str, owner_id: str, document_ids: list[str] | None = None, top_k: int | None = None) -> list[dict]:
    settings = get_settings()
    embedder = get_embedding_service()
    vector_store = get_vector_store()

    query_embedding = embedder.embed_text(question)
    top_k_value = top_k or settings.default_top_k
    raw = vector_store.query(query_embedding=query_embedding, owner_id=owner_id, document_ids=document_ids, top_k=top_k_value)

    ids = raw.get("ids", [[]])[0]
    documents = raw.get("documents", [[]])[0]
    metadatas = raw.get("metadatas", [[]])[0]
    distances = raw.get("distances", [[]])[0]

    results: list[dict] = []
    for vector_id, content, metadata, distance in zip(ids, documents, metadatas, distances, strict=False):
        semantic_score = 1.0 - float(distance)
        lexical_score = _keyword_overlap_score(question, content)
        score = max(semantic_score, lexical_score)
        threshold = 0.12 if settings.embedding_provider == "hash" else settings.similarity_threshold
        if score < threshold:
            continue
        results.append(
            {
                "vector_id": vector_id,
                "chunk_id": metadata["chunk_id"],
                "document_id": metadata["document_id"],
                "file_name": metadata["file_name"],
                "page_number": metadata["page_number"],
                "section_title": metadata.get("section_title"),
                "content": content,
                "source_id": metadata["source_id"],
                "score": round(score, 4),
                "semantic_score": round(semantic_score, 4),
                "lexical_score": round(lexical_score, 4),
            }
        )

    results.sort(key=lambda item: item["score"], reverse=True)
    return results[: settings.max_context_chunks]
