"""Tests for route filtering and look-ahead behavior."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import patch

from kmd_nederlandse_spoorwegen.api import KmdNederlandseSpoorwegenApiClient


class TestRouteFiltering:
    """Test route- and time-based filtering."""

    def test_async_get_departures_filters_by_destination_and_time_window(self):
        """Trips should only include the configured destination station within the look-ahead window."""
        now = datetime.now()
        valid_departure = SimpleNamespace(
            key="1",
            destination="Utrecht Centraal",
            departure_time_planned=now + timedelta(minutes=20),
            departure_time_actual=now + timedelta(minutes=20),
            departure_platform="3",
            delay=0,
            departure_status="on_time",
            train_type="Intercity",
            cancelled=False,
        )
        wrong_destination = SimpleNamespace(
            key="2",
            destination="Rotterdam Centraal",
            departure_time_planned=now + timedelta(minutes=25),
            departure_time_actual=now + timedelta(minutes=25),
            departure_platform="4",
            delay=0,
            departure_status="on_time",
            train_type="Intercity",
            cancelled=False,
        )
        too_late = SimpleNamespace(
            key="3",
            destination="Utrecht Centraal",
            departure_time_planned=now + timedelta(hours=5),
            departure_time_actual=now + timedelta(hours=5),
            departure_platform="5",
            delay=0,
            departure_status="on_time",
            train_type="Intercity",
            cancelled=False,
        )

        with patch("kmd_nederlandse_spoorwegen.api.NSAPI") as mock_nsapi:
            mock_nsapi.return_value.get_departures.return_value = [
                valid_departure,
                wrong_destination,
                too_late,
            ]
            client = KmdNederlandseSpoorwegenApiClient("test-key")

            result = asyncio.run(
                client.async_get_departures(
                    "Amsterdam Bijlmer Arena",
                    limit=25,
                    destination_station="Utrecht Centraal",
                    lookahead_hours=3,
                )
            )

        assert result["station"] == "Amsterdam Bijlmer Arena"
        assert result["destination_station"] == "Utrecht Centraal"
        assert len(result["departures"]) == 1
        assert result["departures"][0]["destination"] == "Utrecht Centraal"

