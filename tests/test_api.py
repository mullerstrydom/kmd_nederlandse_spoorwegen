"""Tests for the Dutch Rail API client."""

from __future__ import annotations

import asyncio
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from api import KmdNederlandseSpoorwegenApiClient, KmdNederlandseSpoorwegenApiError


class TestKmdNederlandseSpoorwegenApiClient:
    """Test the API client normalization logic."""

    def test_async_get_departures_normalizes_payload(self):
        """The client should return Home Assistant-friendly departure data."""
        departure = SimpleNamespace(
            key="123_2026-10-22T08:15:00+00:00",
            destination="Amsterdam Centraal",
            departure_time_planned=datetime(2026, 10, 22, 8, 15, 0),
            departure_time_actual=datetime(2026, 10, 22, 8, 18, 0),
            departure_platform="3",
            delay=3,
            departure_status="on_time",
            train_type="Intercity",
            cancelled=False,
        )

        with patch("api.NSAPI") as mock_nsapi:
            mock_nsapi.return_value.get_departures.return_value = [departure]
            client = KmdNederlandseSpoorwegenApiClient("test-key")

            result = asyncio.run(client.async_get_departures("Utrecht Centraal", 5))

        assert result["station"] == "Utrecht Centraal"
        assert len(result["departures"]) == 1
        assert result["departures"][0]["destination"] == "Amsterdam Centraal"
        assert result["departures"][0]["platform"] == "3"
        assert result["departures"][0]["delay"] == 3
        assert result["departures"][0]["train"] == "Intercity"

    def test_async_get_departures_handles_empty_results(self):
        """An empty API result should be normalized to an empty list."""
        with patch("api.NSAPI") as mock_nsapi:
            mock_nsapi.return_value.get_departures.return_value = []
            client = KmdNederlandseSpoorwegenApiClient("test-key")

            result = asyncio.run(client.async_get_departures("Utrecht Centraal", 5))

        assert result["station"] == "Utrecht Centraal"
        assert result["departures"] == []

    def test_async_get_departures_raises_api_error_on_failure(self):
        """A library failure should be wrapped in a custom API error."""
        with patch("api.NSAPI") as mock_nsapi:
            mock_nsapi.return_value.get_departures.side_effect = RuntimeError("API unavailable")
            client = KmdNederlandseSpoorwegenApiClient("test-key")

            with pytest.raises(KmdNederlandseSpoorwegenApiError, match="API unavailable"):
                asyncio.run(client.async_get_departures("Utrecht Centraal", 5))
