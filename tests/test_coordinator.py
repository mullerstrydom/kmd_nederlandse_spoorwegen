"""Tests for the coordinator behavior."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from kmd_nederlandse_spoorwegen.coordinator import KmdNederlandseSpoorwegenCoordinator
from kmd_nederlandse_spoorwegen.const import (
    CONF_MAX_DEPARTURES,
    CONF_STATION,
    CONF_SUBSCRIPTION_KEY,
)


class TestKmdNederlandseSpoorwegenCoordinator:
    """Test coordinator behavior."""

    def test_coordinator_fetches_departures_using_station_config(self):
        """The coordinator should use the config entry station and max departures values."""
        entry = MagicMock()
        entry.data = {
            CONF_SUBSCRIPTION_KEY: "test-key",
            CONF_STATION: "Utrecht Centraal",
            CONF_MAX_DEPARTURES: 7,
        }

        with patch("kmd_nederlandse_spoorwegen.coordinator.DataUpdateCoordinator.__init__", return_value=None):
            with patch("kmd_nederlandse_spoorwegen.coordinator.KmdNederlandseSpoorwegenApiClient") as mock_api_cls:
                mock_api = mock_api_cls.return_value
                mock_api.async_get_departures = AsyncMock(
                    return_value={"station": "Utrecht Centraal", "departures": []}
                )

                coordinator = KmdNederlandseSpoorwegenCoordinator(MagicMock(), entry)
                result = asyncio.run(coordinator._async_update_data())

        assert result == {"station": "Utrecht Centraal", "departures": []}
        mock_api.async_get_departures.assert_awaited_once_with("Utrecht Centraal", 7)

    def test_coordinator_uses_default_max_departures(self):
        """The coordinator should fall back to the default max departures value."""
        entry = MagicMock()
        entry.data = {
            CONF_SUBSCRIPTION_KEY: "test-key",
            CONF_STATION: "Amsterdam Centraal",
        }

        with patch("kmd_nederlandse_spoorwegen.coordinator.DataUpdateCoordinator.__init__", return_value=None):
            with patch("kmd_nederlandse_spoorwegen.coordinator.KmdNederlandseSpoorwegenApiClient") as mock_api_cls:
                mock_api = mock_api_cls.return_value
                mock_api.async_get_departures = AsyncMock(
                    return_value={"station": "Amsterdam Centraal", "departures": []}
                )

                coordinator = KmdNederlandseSpoorwegenCoordinator(MagicMock(), entry)
                asyncio.run(coordinator._async_update_data())

        mock_api.async_get_departures.assert_awaited_once_with("Amsterdam Centraal", 5)
