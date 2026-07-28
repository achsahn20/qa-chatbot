from __future__ import annotations

from dataclasses import dataclass
import json
import re

from app.config import get_settings
from app.rag.prompts import SYSTEM_PROMPT, build_context_blocks, build_user_prompt

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - optional dependency path
    OpenAI = None


@dataclass(slots=True)
class GeneratedAnswer:
    answer: str
    source_ids: list[str]
    insufficient_context: bool
    model_name: str


class FallbackAnswerGenerator:
    def generate(self, question: str, chunks: list[dict], conversation_summary: str = "") -> GeneratedAnswer:
        if not chunks:
            return GeneratedAnswer(
                answer="I could not find this in the uploaded documents.",
                source_ids=[],
                insufficient_context=True,
                model_name="fallback-extractive",
            )

        query_terms = set(re.findall(r"\b[\w-]+\b", question.lower()))
        selected_sentences: list[str] = []
        selected_ids: list[str] = []

        for chunk in chunks[:3]:
            sentences = re.split(r"(?<=[.!?])\s+", chunk["content"])
            best_sentences = [sentence.strip() for sentence in sentences if query_terms & set(re.findall(r"\b[\w-]+\b", sentence.lower()))]
            if not best_sentences and sentences:
                best_sentences = [sentences[0].strip()]
            for sentence in best_sentences[:2]:
                if sentence and sentence not in selected_sentences:
                    selected_sentences.append(sentence)
            if chunk["source_id"] not in selected_ids:
                selected_ids.append(chunk["source_id"])

        if not selected_sentences:
            return GeneratedAnswer(
                answer="I could not find this in the uploaded documents.",
                source_ids=[],
                insufficient_context=True,
                model_name="fallback-extractive",
            )

        answer = "Based on the uploaded documents, " + " ".join(selected_sentences)
        return GeneratedAnswer(
            answer=answer,
            source_ids=selected_ids,
            insufficient_context=False,
            model_name="fallback-extractive",
        )


class OpenAIAnswerGenerator:
    def __init__(self, api_key: str, model: str) -> None:
        if OpenAI is None:
            raise RuntimeError("OpenAI package is not installed.")
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate(self, question: str, chunks: list[dict], conversation_summary: str = "") -> GeneratedAnswer:
        if not chunks:
            return GeneratedAnswer(
                answer="I could not find this in the uploaded documents.",
                source_ids=[],
                insufficient_context=True,
                model_name=self.model,
            )

        context_blocks = build_context_blocks(chunks)
        response = self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(question, context_blocks, conversation_summary)},
            ],
        )
        content = response.choices[0].message.content or "{}"
        payload = json.loads(content)
        return GeneratedAnswer(
            answer=payload.get("answer", "I could not find this in the uploaded documents."),
            source_ids=payload.get("source_ids", []),
            insufficient_context=payload.get("insufficient_context", False),
            model_name=self.model,
        )


def get_answer_generator() -> FallbackAnswerGenerator | OpenAIAnswerGenerator:
    settings = get_settings()
    if settings.llm_provider == "openai" and settings.openai_api_key:
        return OpenAIAnswerGenerator(api_key=settings.openai_api_key, model=settings.llm_model)
    return FallbackAnswerGenerator()
