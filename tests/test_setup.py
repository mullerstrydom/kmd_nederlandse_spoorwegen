"""Smoke tests for config entry setup and unload."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.kmd_nederlandse_spoorwegen import async_setup_entry, async_unload_entry
from custom_components.kmd_nederlandse_spoorwegen.const import (
    CONF_DESTINATION_STATION,
    CONF_DESTINATION_STATION_CODE,
    CONF_LOOKAHEAD_HOURS,
    CONF_MAX_DEPARTURES,
    CONF_STATION,
    CONF_STATION_CODE,
    CONF_SUBSCRIPTION_KEY,
    DEFAULT_DESTINATION_STATION,
    DEFAULT_LOOKAHEAD_HOURS,
    DEFAULT_MAX_DEPARTURES,
    DEFAULT_STATION,
)
from custom_components.kmd_nederlandse_spoorwegen import DOMAIN


class TestSetupSmoke:
    """Verify the config entry sets up and unloads cleanly."""

    def test_async_setup_entry_stores_coordinator_and_forwards_sensor_platform(self):
        """A valid config entry should initialize the coordinator and start the sensor platform."""
        hass = MagicMock()
        hass.data = {}
        hass.config_entries = MagicMock()
        hass.config_entries.async_forward_entry_setups = AsyncMock()

        entry = MagicMock()
        entry.entry_id = "test-entry"
        entry.version = 2
        entry.data = {
            CONF_SUBSCRIPTION_KEY: "abc123",
            CONF_STATION: "Utrecht Centraal",
            CONF_STATION_CODE: "UT",
            CONF_DESTINATION_STATION: "Amsterdam Centraal",
            CONF_DESTINATION_STATION_CODE: "ASD",
            CONF_MAX_DEPARTURES: 5,
        }

        coordinator = MagicMock()
        coordinator.async_config_entry_first_refresh = AsyncMock()

        with patch("custom_components.kmd_nederlandse_spoorwegen.KmdNederlandseSpoorwegenCoordinator", return_value=coordinator) as mock_coordinator:
            result = asyncio.run(async_setup_entry(hass, entry))

        assert result is True
        mock_coordinator.assert_called_once_with(hass, entry)
        coordinator.async_config_entry_first_refresh.assert_awaited_once()
        assert hass.data[DOMAIN][entry.entry_id] is coordinator
        hass.config_entries.async_forward_entry_setups.assert_awaited_once_with(entry, ["sensor"])

    def test_async_setup_entry_migrates_legacy_station_name_config(self):
        """Old entries with station names only should be upgraded with station codes."""
        hass = MagicMock()
        hass.data = {}
        hass.config_entries = MagicMock()
        hass.config_entries.async_forward_entry_setups = AsyncMock()
        hass.config_entries.async_update_entry = MagicMock()
        hass.async_add_executor_job = AsyncMock(return_value={"Utrecht Centraal": "UT", "Amsterdam Centraal": "ASD"})

        entry = MagicMock()
        entry.entry_id = "legacy-entry"
        entry.version = 1
        entry.data = {
            CONF_SUBSCRIPTION_KEY: "abc123",
            CONF_STATION: "Utrecht Centraal",
            CONF_DESTINATION_STATION: "Amsterdam Centraal",
        }

        coordinator = MagicMock()
        coordinator.async_config_entry_first_refresh = AsyncMock()

        with patch("custom_components.kmd_nederlandse_spoorwegen.KmdNederlandseSpoorwegenCoordinator", return_value=coordinator):
            result = asyncio.run(async_setup_entry(hass, entry))

        assert result is True
        hass.config_entries.async_update_entry.assert_called_once()
        updated_data = hass.config_entries.async_update_entry.call_args.kwargs["data"]
        assert updated_data[CONF_STATION_CODE] == "UT"
        assert updated_data[CONF_DESTINATION_STATION_CODE] == "ASD"

    def test_async_unload_entry_removes_coordinator_and_unloads_platforms(self):
        """Unloading should clear the coordinator data and unload the sensor platform."""
        hass = MagicMock()
        hass.data = {DOMAIN: {"test-entry": object()}}
        hass.config_entries = MagicMock()
        hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)

        entry = MagicMock()
        entry.entry_id = "test-entry"

        result = asyncio.run(async_unload_entry(hass, entry))

        assert result is True
        hass.config_entries.async_unload_platforms.assert_awaited_once_with(entry, ["sensor"])
        assert hass.data[DOMAIN] == {}
