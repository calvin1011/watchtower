"""Tests for OpenAI embeddings."""

from unittest.mock import MagicMock, patch

import pytest

from embeddings import get_embedding


def test_get_embedding_returns_none_without_api_key():
    """get_embedding returns None when OPENAI_API_KEY is missing."""
    with patch("embeddings.settings", MagicMock(openai_api_key=None)):
        assert get_embedding("test text") is None


def test_get_embedding_returns_none_for_empty_text():
    """get_embedding returns None for empty or whitespace-only text."""
    with patch("embeddings.settings", MagicMock(openai_api_key="sk-test")):
        assert get_embedding("") is None
        assert get_embedding("   ") is None


def test_get_embedding_returns_vector():
    """get_embedding returns 1536-dim vector from OpenAI."""
    fake_embedding = [0.1] * 1536
    mock_response = MagicMock()
    mock_response.data = [MagicMock(embedding=fake_embedding)]

    mock_client = MagicMock()
    mock_client.embeddings.create.return_value = mock_response

    with (
        patch("embeddings.settings", MagicMock(openai_api_key="sk-test")),
        patch("embeddings.OpenAI", return_value=mock_client),
    ):
        result = get_embedding("AppFolio launched AI feature")
    assert result == fake_embedding
    assert len(result) == 1536
    mock_client.embeddings.create.assert_called_once()
    call_kwargs = mock_client.embeddings.create.call_args[1]
    assert call_kwargs["input"] == "AppFolio launched AI feature"
    assert call_kwargs["model"] == "text-embedding-3-small"


def test_get_embedding_returns_none_on_api_error():
    """get_embedding returns None when API raises."""
    with (
        patch("embeddings.settings", MagicMock(openai_api_key="sk-test")),
        patch("embeddings.OpenAI") as mock_openai,
    ):
        mock_openai.return_value.embeddings.create.side_effect = Exception("API error")
        assert get_embedding("test") is None
