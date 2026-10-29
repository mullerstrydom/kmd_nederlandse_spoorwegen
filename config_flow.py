"""Config flow for the KMd Nederlandse Spoorwegen integration."""

from __future__ import annotations

import asyncio

import voluptuous as vol
from homeassistant import config_entries
from ns_api import NSAPI

from .const import (
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
    DOMAIN,
)


class KmdNederlandseSpoorwegenConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for the KMd Nederlandse Spoorwegen integration."""

    VERSION = 2

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._subscription_key: str | None = None

    @staticmethod
    def _station_map(subscription_key: str) -> dict[str, str]:
        """Return a mapping of station display names to NS station codes."""
        station_map: dict[str, str] = {}
        for station in NSAPI(subscription_key).get_stations():
            code = getattr(station, "code", None)
            long_name = getattr(station, "names", {}).get("long")
            if code and long_name:
                station_map[long_name] = code
        return dict(sorted(station_map.items()))

    @staticmethod
    def _has_station_selection_input(user_input: dict) -> bool:
        """Return True when a submitted form already includes the station fields."""
        return all(key in user_input for key in (CONF_STATION, CONF_DESTINATION_STATION))

    async def _async_get_station_map_for_key(self, subscription_key: str | None) -> dict[str, str]:
        """Fetch the station mapping for a subscription key and return an empty map on failure."""
        if not subscription_key:
            return {}

        try:
            return await asyncio.to_thread(self._station_map, subscription_key)
        except Exception:  # pragma: no cover - exercised in real HA runtime
            return {}

    async def async_step_user(self, user_input=None):
        """Collect the API key and continue to the station selection step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({vol.Required(CONF_SUBSCRIPTION_KEY): str}),
            )

        if self._has_station_selection_input(user_input):
            return await self._async_create_entry_from_form(user_input)

        self._subscription_key = user_input[CONF_SUBSCRIPTION_KEY]
        return await self._async_continue_after_api_key()

    async def _async_continue_after_api_key(self):
        """Load station options after the API key is entered."""
        station_map = await self._async_get_station_map_for_key(self._subscription_key)
        if not station_map:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({vol.Required(CONF_SUBSCRIPTION_KEY): str}),
                errors={"base": "cannot_connect"},
            )

        return await self.async_step_station_selection(station_map=station_map)

    async def _async_create_entry_from_form(self, user_input):
        """Create an entry directly when the form already includes station values."""
        subscription_key = user_input.get(CONF_SUBSCRIPTION_KEY)
        station_name = user_input[CONF_STATION]
        destination_name = user_input[CONF_DESTINATION_STATION]
        station_map = await self._async_get_station_map_for_key(subscription_key)

        return self.async_create_entry(
            title=f"{station_name} → {destination_name}",
            data={
                CONF_SUBSCRIPTION_KEY: subscription_key or self._subscription_key,
                CONF_STATION: station_name,
                CONF_STATION_CODE: station_map.get(station_name, station_name),
                CONF_DESTINATION_STATION: destination_name,
                CONF_DESTINATION_STATION_CODE: station_map.get(destination_name, destination_name),
                CONF_MAX_DEPARTURES: user_input.get(CONF_MAX_DEPARTURES, DEFAULT_MAX_DEPARTURES),
                CONF_LOOKAHEAD_HOURS: user_input.get(
                    CONF_LOOKAHEAD_HOURS,
                    DEFAULT_LOOKAHEAD_HOURS,
                ),
            },
        )

    async def async_step_station_selection(self, user_input=None, station_map=None):
        """Show the station selection form and save the station codes."""
        if self._subscription_key is None:
            return await self.async_step_user()

        if station_map is None:
            station_map = await self._async_get_station_map_for_key(self._subscription_key)

        if user_input is not None:
            return self._create_entry_from_selection(user_input, station_map)

        return self._show_station_selection_form(station_map)

    def _create_entry_from_selection(self, user_input, station_map):
        """Create config entry data from the chosen station and destination."""
        station_name = user_input[CONF_STATION]
        destination_name = user_input[CONF_DESTINATION_STATION]
        return self.async_create_entry(
            title=f"{station_name} → {destination_name}",
            data={
                CONF_SUBSCRIPTION_KEY: self._subscription_key,
                CONF_STATION: station_name,
                CONF_STATION_CODE: station_map[station_name],
                CONF_DESTINATION_STATION: destination_name,
                CONF_DESTINATION_STATION_CODE: station_map[destination_name],
                CONF_MAX_DEPARTURES: user_input.get(CONF_MAX_DEPARTURES, DEFAULT_MAX_DEPARTURES),
                CONF_LOOKAHEAD_HOURS: user_input.get(
                    CONF_LOOKAHEAD_HOURS,
                    DEFAULT_LOOKAHEAD_HOURS,
                ),
            },
        )

    def _show_station_selection_form(self, station_map):
        """Return the station selection form to the user."""
        station_options = list(station_map.keys())
        default_station = DEFAULT_STATION if DEFAULT_STATION in station_options else station_options[0]
        default_destination = (
            DEFAULT_DESTINATION_STATION
            if DEFAULT_DESTINATION_STATION in station_options
            else station_options[0]
        )

        return self.async_show_form(
            step_id="station_selection",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_STATION, default=default_station): vol.In(station_options),
                    vol.Required(CONF_DESTINATION_STATION, default=default_destination): vol.In(station_options),
                    vol.Optional(CONF_MAX_DEPARTURES, default=DEFAULT_MAX_DEPARTURES): int,
                    vol.Optional(CONF_LOOKAHEAD_HOURS, default=DEFAULT_LOOKAHEAD_HOURS): int,
                }
            ),
        )
