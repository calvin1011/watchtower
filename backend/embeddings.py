"""OpenAI embeddings for semantic search. Uses text-embedding-3-small (1536 dims)."""

from openai import OpenAI

from config import settings

EMBEDDING_MODEL = "text-embedding-3-small"


def get_embedding(text: str) -> list[float] | None:
    """
    Generate embedding for text using OpenAI.

    Returns 1536-dim vector, or None if API key missing or request fails.
    """
    api_key = settings.openai_api_key
    if not api_key:
        return None

    text = (text or "").strip()
    if not text:
        return None

    try:
        client = OpenAI(api_key=api_key)
        resp = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text[:8000],  # limit input length
        )
        return resp.data[0].embedding
    except Exception:
        return None
