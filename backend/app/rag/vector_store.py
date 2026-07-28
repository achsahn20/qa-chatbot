from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any

import numpy as np

from app.config import get_settings


class PersistentVectorStore:
    def __init__(self) -> None:
        settings = get_settings()
        self.file_path = Path(settings.chroma_persist_directory) / "vector_store.json"
        if not self.file_path.exists():
            self._write([])

    def _read(self) -> list[dict[str, Any]]:
        if not self.file_path.exists():
            return []
        with self.file_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _write(self, payload: list[dict[str, Any]]) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with self.file_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle)

    def upsert_chunks(
        self,
        chunk_ids: list[str],
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, Any]],
    ) -> None:
        existing = {item["id"]: item for item in self._read()}
        for chunk_id, document, embedding, metadata in zip(chunk_ids, documents, embeddings, metadatas, strict=False):
            existing[chunk_id] = {
                "id": chunk_id,
                "document": document,
                "embedding": embedding,
                "metadata": metadata,
            }
        self._write(list(existing.values()))

    def delete_by_document(self, document_id: str) -> None:
        filtered = [item for item in self._read() if item["metadata"].get("document_id") != document_id]
        self._write(filtered)

    def query(
        self,
        query_embedding: list[float],
        owner_id: str,
        document_ids: list[str] | None,
        top_k: int,
    ) -> dict[str, Any]:
        query_vector = np.array(query_embedding, dtype=np.float32)
        matches: list[tuple[float, dict[str, Any]]] = []
        for item in self._read():
            metadata = item["metadata"]
            if metadata.get("owner_id") != owner_id:
                continue
            if document_ids and metadata.get("document_id") not in document_ids:
                continue
            vector = np.array(item["embedding"], dtype=np.float32)
            denominator = float(np.linalg.norm(query_vector) * np.linalg.norm(vector))
            similarity = float(np.dot(query_vector, vector) / denominator) if denominator else 0.0
            matches.append((similarity, item))

        matches.sort(key=lambda pair: pair[0], reverse=True)
        top_matches = matches[:top_k]

        return {
            "ids": [[item["id"] for _, item in top_matches]],
            "documents": [[item["document"] for _, item in top_matches]],
            "metadatas": [[item["metadata"] for _, item in top_matches]],
            "distances": [[1.0 - score for score, _ in top_matches]],
        }

    def stats(self) -> dict[str, Any]:
        return {"count": len(self._read())}


@lru_cache
def get_vector_store() -> PersistentVectorStore:
    return PersistentVectorStore()
