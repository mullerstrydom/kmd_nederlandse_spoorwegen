"""Tests for the config flow validation."""

from __future__ import annotations

import asyncio

from kmd_nederlandse_spoorwegen.config_flow import KmdNederlandseSpoorwegenConfigFlow
from kmd_nederlandse_spoorwegen.const import (
    CONF_DESTINATION_STATION,
    CONF_LOOKAHEAD_HOURS,
    CONF_MAX_DEPARTURES,
    CONF_STATION,
    CONF_SUBSCRIPTION_KEY,
    DEFAULT_DESTINATION_STATION,
    DEFAULT_LOOKAHEAD_HOURS,
    DEFAULT_MAX_DEPARTURES,
    DEFAULT_STATION,
)


class TestKmdNederlandseSpoorwegenConfigFlow:
    """Test config flow behavior."""

    def test_user_step_creates_entry_with_valid_input(self):
        """Valid user input should create an entry with the expected data."""
        flow = KmdNederlandseSpoorwegenConfigFlow()
        flow.async_create_entry = lambda title, data: {"title": title, "data": data}

        result = asyncio.run(flow.async_step_user({
            CONF_SUBSCRIPTION_KEY: "abc123",
            CONF_STATION: "Utrecht Centraal",
            CONF_DESTINATION_STATION: "Amsterdam Centraal",
            CONF_MAX_DEPARTURES: 8,
            CONF_LOOKAHEAD_HOURS: 2,
        }))

        assert result["title"] == "Utrecht Centraal → Amsterdam Centraal"
        assert result["data"][CONF_SUBSCRIPTION_KEY] == "abc123"
        assert result["data"][CONF_STATION] == "Utrecht Centraal"
        assert result["data"][CONF_DESTINATION_STATION] == "Amsterdam Centraal"
        assert result["data"][CONF_MAX_DEPARTURES] == 8
        assert result["data"][CONF_LOOKAHEAD_HOURS] == 2

    def test_user_step_uses_defaults_when_values_are_missing(self):
        """The form should populate default values for station and max departures."""
        flow = KmdNederlandseSpoorwegenConfigFlow()
        result = asyncio.run(flow.async_step_user())

        assert result["type"] == "form"
        assert result["step_id"] == "user"

        schema = result["data_schema"]
        schema_keys = list(schema.schema.keys())
        required = [key.schema for key in schema_keys if hasattr(key, "schema")]

        assert CONF_SUBSCRIPTION_KEY in required
        assert CONF_STATION in required
        assert CONF_DESTINATION_STATION in required
        assert CONF_MAX_DEPARTURES in required
        assert CONF_LOOKAHEAD_HOURS in required

        station_key = next(key for key in schema_keys if getattr(key, "schema", None) == CONF_STATION)
        dest_key = next(key for key in schema_keys if getattr(key, "schema", None) == CONF_DESTINATION_STATION)
        max_key = next(key for key in schema_keys if getattr(key, "schema", None) == CONF_MAX_DEPARTURES)
        lookahead_key = next(key for key in schema_keys if getattr(key, "schema", None) == CONF_LOOKAHEAD_HOURS)

        assert station_key.default() == DEFAULT_STATION
        assert dest_key.default() == DEFAULT_DESTINATION_STATION
        assert max_key.default() == DEFAULT_MAX_DEPARTURES
        assert lookahead_key.default() == DEFAULT_LOOKAHEAD_HOURS
