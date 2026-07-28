from __future__ import annotations

import hashlib
import math
import re
from typing import Protocol

import numpy as np

from app.config import get_settings

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - optional dependency path
    OpenAI = None


TOKEN_PATTERN = re.compile(r"\b[\w-]+\b")


class EmbeddingService(Protocol):
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        ...

    def embed_text(self, text: str) -> list[float]:
        ...


class HashEmbeddingService:
    def __init__(self, dimension: int) -> None:
        self.dimension = dimension

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_text(text) for text in texts]

    def embed_text(self, text: str) -> list[float]:
        vector = np.zeros(self.dimension, dtype=np.float32)
        tokens = TOKEN_PATTERN.findall(text.lower())
        if not tokens:
            return vector.tolist()

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            bucket = int.from_bytes(digest[:4], "big") % self.dimension
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[bucket] += sign

        norm = math.sqrt(float(np.dot(vector, vector)))
        if norm > 0:
            vector = vector / norm
        return vector.tolist()


class OpenAIEmbeddingService:
    def __init__(self, api_key: str, model: str) -> None:
        if OpenAI is None:
            raise RuntimeError("OpenAI package is not installed.")
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(model=self.model, input=texts)
        return [item.embedding for item in response.data]

    def embed_text(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]


def get_embedding_service() -> EmbeddingService:
    settings = get_settings()
    if settings.embedding_provider == "openai" and settings.openai_api_key:
        return OpenAIEmbeddingService(api_key=settings.openai_api_key, model=settings.embedding_model)
    return HashEmbeddingService(dimension=settings.embedding_dimension)
