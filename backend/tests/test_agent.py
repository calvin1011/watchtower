"""Tests for the Claude competitive intelligence agent."""

import json
from unittest.mock import MagicMock, patch

import pytest

from agent import IntelAnalysis, analyze_scraped_data


def test_intel_analysis_model():
    """IntelAnalysis validates required fields and types."""
    analysis = IntelAnalysis(
        summary="AppFolio launched AI maintenance feature",
        threat_level="MEDIUM",
        threat_reason="Adjacent to HappyCo's Joy AI differentiator",
        happyco_response="Highlight 2.7-day turn and 5.5M units scale.",
        signal_type="PRODUCT_LAUNCH",
        confidence=0.85,
        source_url="https://example.com",
    )
    assert analysis.threat_level == "MEDIUM"
    assert analysis.confidence == 0.85
    assert analysis.source_url == "https://example.com"


def test_intel_analysis_source_url_optional():
    """IntelAnalysis allows source_url to be None."""
    analysis = IntelAnalysis(
        summary="Buildium hiring engineers",
        threat_level="LOW",
        threat_reason="General hiring signal",
        happyco_response="Monitor.",
        signal_type="HIRING_SIGNAL",
        confidence=0.6,
        source_url=None,
    )
    assert analysis.source_url is None


def test_analyze_empty_items_returns_empty_list():
    """Empty input returns empty list without calling API."""
    with patch("agent.Anthropic") as mock_client:
        result = analyze_scraped_data([], "AppFolio")
        mock_client.assert_not_called()
        assert result == []


def test_analyze_scraped_data_parses_json_response():
    """analyze_scraped_data parses Claude JSON and returns IntelAnalysis list."""
    mock_response = MagicMock()
    mock_response.content = [
        MagicMock(
            text=json.dumps(
                [
                    {
                        "summary": "AppFolio announced AI maintenance",
                        "threat_level": "MEDIUM",
                        "threat_reason": "Competes with Joy AI",
                        "happyco_response": "Emphasize 5.5M units",
                        "signal_type": "PRODUCT_LAUNCH",
                        "confidence": 0.8,
                        "source_url": "https://appfolio.com/blog",
                    }
                ]
            )
        )
    ]

    mock_client_instance = MagicMock()
    mock_client_instance.messages.create.return_value = mock_response

    with patch("agent.Anthropic", return_value=mock_client_instance), patch(
        "agent.settings", MagicMock(anthropic_api_key="test-key")
    ):
        items = [
            {
                "title": "AppFolio AI",
                "url": "https://appfolio.com/blog",
                "snippet": "New AI maintenance feature",
                "date": "2024-01-15",
            }
        ]
        result = analyze_scraped_data(items, "AppFolio")

    assert len(result) == 1
    assert result[0].summary == "AppFolio announced AI maintenance"
    assert result[0].threat_level == "MEDIUM"
    assert result[0].signal_type == "PRODUCT_LAUNCH"
    assert result[0].confidence == 0.8


def test_analyze_merges_source_url_from_items():
    """source_url from scraped items is used when agent omits it."""
    mock_response = MagicMock()
    mock_response.content = [
        MagicMock(
            text=json.dumps(
                [
                    {
                        "summary": "Competitor blog post",
                        "threat_level": "LOW",
                        "threat_reason": "Minor",
                        "happyco_response": "Monitor",
                        "signal_type": "MARKETING_SHIFT",
                        "confidence": 0.7,
                    }
                ]
            )
        )
    ]

    mock_client_instance = MagicMock()
    mock_client_instance.messages.create.return_value = mock_response

    with patch("agent.Anthropic", return_value=mock_client_instance), patch(
        "agent.settings", MagicMock(anthropic_api_key="test-key")
    ):
        items = [{"title": "Post", "url": "https://example.com/post", "snippet": "..."}]
        result = analyze_scraped_data(items, "Buildium")

    assert result[0].source_url == "https://example.com/post"


def test_analyze_raises_without_api_key():
    """analyze_scraped_data raises when ANTHROPIC_API_KEY is missing."""
    with patch("agent.settings", MagicMock(anthropic_api_key=None)):
        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY is required"):
            analyze_scraped_data(
                [{"title": "x", "snippet": "y"}],
                "AppFolio",
            )
