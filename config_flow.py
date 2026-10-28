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

    async def async_step_user(self, user_input=None):
        """Collect the API key and continue to the station selection step."""
        errors = {}

        if user_input is not None:
            if all(key in user_input for key in (CONF_STATION, CONF_DESTINATION_STATION)):
                station_name = user_input[CONF_STATION]
                destination_name = user_input[CONF_DESTINATION_STATION]
                station_code = station_name
                destination_station_code = destination_name

                subscription_key = user_input.get(CONF_SUBSCRIPTION_KEY)
                if subscription_key:
                    try:
                        station_map = await asyncio.to_thread(self._station_map, subscription_key)
                    except Exception:  # pragma: no cover - exercised in real HA runtime
                        station_map = {}
                    station_code = station_map.get(station_name, station_name)
                    destination_station_code = station_map.get(destination_name, destination_name)

                return self.async_create_entry(
                    title=f"{station_name} → {destination_name}",
                    data={
                        CONF_SUBSCRIPTION_KEY: subscription_key or self._subscription_key,
                        CONF_STATION: station_name,
                        CONF_STATION_CODE: station_code,
                        CONF_DESTINATION_STATION: destination_name,
                        CONF_DESTINATION_STATION_CODE: destination_station_code,
                        CONF_MAX_DEPARTURES: user_input.get(CONF_MAX_DEPARTURES, DEFAULT_MAX_DEPARTURES),
                        CONF_LOOKAHEAD_HOURS: user_input.get(
                            CONF_LOOKAHEAD_HOURS,
                            DEFAULT_LOOKAHEAD_HOURS,
                        ),
                    },
                )

            self._subscription_key = user_input[CONF_SUBSCRIPTION_KEY]
            try:
                station_map = await asyncio.to_thread(self._station_map, self._subscription_key)
            except Exception:  # pragma: no cover - exercised in real HA runtime
                errors["base"] = "cannot_connect"
            else:
                if not station_map:
                    errors["base"] = "cannot_connect"
                else:
                    return await self.async_step_station_selection(station_map=station_map)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_SUBSCRIPTION_KEY): str}),
            errors=errors,
        )

    async def async_step_station_selection(self, user_input=None, station_map=None):
        """Show the station and destination selection form and save the NS station codes."""
        if self._subscription_key is None:
            return await self.async_step_user()

        if station_map is None and user_input is None:
            station_map = await asyncio.to_thread(self._station_map, self._subscription_key)

        if user_input is not None:
            if station_map is None:
                station_map = await asyncio.to_thread(self._station_map, self._subscription_key)

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

        if station_map is None:
            station_map = await asyncio.to_thread(self._station_map, self._subscription_key)

        station_options = list(station_map.keys())

        default_station = (
            DEFAULT_STATION if DEFAULT_STATION in station_options else station_options[0]
        )
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
