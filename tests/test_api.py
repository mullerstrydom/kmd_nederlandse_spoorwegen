"""Tests for the Dutch Rail API client."""

from __future__ import annotations

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api import KmdNederlandseSpoorwegenApiClient, KmdNederlandseSpoorwegenApiError


class TestKmdNederlandseSpoorwegenApiClient:
    """Test the API client normalization logic."""

    def test_async_get_departures_normalizes_payload(self):
        """The client should return Home Assistant-friendly departure data."""
        now = datetime.now()
        departure = SimpleNamespace(
            key="123_2026-10-22T08:15:00+00:00",
            destination="Amsterdam Centraal",
            departure_time_planned=now + timedelta(minutes=20),
            departure_time_actual=now + timedelta(minutes=18),
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

    def test_async_get_departures_skips_malformed_entries(self):
        """Malformed departure entries should be skipped instead of crashing the whole result."""
        now = datetime.now()
        valid_departure = SimpleNamespace(
            key="123_2026-10-22T08:15:00+00:00",
            destination="Amsterdam Centraal",
            departure_time_planned=now + timedelta(minutes=20),
            departure_time_actual=now + timedelta(minutes=18),
            departure_platform="3",
            delay=3,
            departure_status="on_time",
            train_type="Intercity",
            cancelled=False,
        )

        malformed_departure = {"destination": "Bad data"}

        with patch("api.NSAPI") as mock_nsapi:
            mock_nsapi.return_value.get_departures.return_value = [
                valid_departure,
                malformed_departure,
                None,
            ]
            client = KmdNederlandseSpoorwegenApiClient("test-key")

            result = asyncio.run(client.async_get_departures("Utrecht Centraal", 5))

        assert len(result["departures"]) == 2
        assert result["departures"][0]["destination"] == "Amsterdam Centraal"
        assert result["departures"][1]["destination"] == "Bad data"

    def test_async_get_departures_raises_type_error_for_transport_failure(self):
        """A TypeError from the underlying transport should be surfaced as the custom API error."""
        with patch("api.NSAPI") as mock_nsapi:
            mock_nsapi.return_value.get_departures.side_effect = TypeError(
                "the JSON object must be str, bytes or bytearray, not NoneType"
            )
            client = KmdNederlandseSpoorwegenApiClient("test-key")

            with pytest.raises(KmdNederlandseSpoorwegenApiError, match="TypeError while fetching departures"):
                asyncio.run(client.async_get_departures("Utrecht Centraal", 5))

    def test_async_get_departures_handles_missing_payload(self):
        """A missing payload in the NS response should be treated as an empty result."""
        with patch("api.NSAPI") as mock_nsapi:
            mock_nsapi.return_value.get_departures.side_effect = KeyError("payload")
            client = KmdNederlandseSpoorwegenApiClient("test-key")

            result = asyncio.run(client.async_get_departures("Maarssen", 5))

        assert result["station"] == "Maarssen"
        assert result["departures"] == []
