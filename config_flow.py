"""Config flow for the KMd Nederlandse Spoorwegen integration."""

from __future__ import annotations

import asyncio

import voluptuous as vol
from homeassistant import config_entries
from ns_api import NSAPI

from .const import (
    CONF_DESTINATION_STATION,
    CONF_LOOKAHEAD_HOURS,
    CONF_MAX_DEPARTURES,
    CONF_STATION,
    CONF_SUBSCRIPTION_KEY,
    DEFAULT_DESTINATION_STATION,
    DEFAULT_LOOKAHEAD_HOURS,
    DEFAULT_MAX_DEPARTURES,
    DEFAULT_STATION,
    DOMAIN,
)


class KmdNederlandseSpoorwegenConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for KMd Nederlandse Spoorwegen."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._subscription_key: str | None = None

    @staticmethod
    def _station_options(subscription_key: str) -> list[str]:
        """Fetch and normalize the available station names from the NS API."""
        stations = NSAPI(subscription_key).get_stations()
        names = []
        for station in stations:
            long_name = getattr(station, "names", {}).get("long")
            if long_name:
                names.append(long_name)
            else:
                names.append(str(station))
        return sorted(set(names))

    async def async_step_user(self, user_input=None):
        """Handle the initial step, collecting the subscription key."""
        errors = {}

        if user_input is not None:
            if CONF_STATION in user_input and CONF_DESTINATION_STATION in user_input:
                return self.async_create_entry(
                    title=f"{user_input[CONF_STATION]} → {user_input.get(CONF_DESTINATION_STATION, DEFAULT_DESTINATION_STATION)}",
                    data={
                        CONF_SUBSCRIPTION_KEY: user_input[CONF_SUBSCRIPTION_KEY],
                        CONF_STATION: user_input[CONF_STATION],
                        CONF_DESTINATION_STATION: user_input.get(
                            CONF_DESTINATION_STATION,
                            DEFAULT_DESTINATION_STATION,
                        ),
                        CONF_MAX_DEPARTURES: user_input.get(CONF_MAX_DEPARTURES, DEFAULT_MAX_DEPARTURES),
                        CONF_LOOKAHEAD_HOURS: user_input.get(
                            CONF_LOOKAHEAD_HOURS,
                            DEFAULT_LOOKAHEAD_HOURS,
                        ),
                    },
                )

            self._subscription_key = user_input[CONF_SUBSCRIPTION_KEY]
            try:
                station_options = await asyncio.to_thread(
                    self._station_options,
                    self._subscription_key,
                )
            except Exception:  # pragma: no cover - exercised in real HA runtime
                errors["base"] = "cannot_connect"
            else:
                if not station_options:
                    errors["base"] = "cannot_connect"
                else:
                    return await self.async_step_station_selection()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_SUBSCRIPTION_KEY): str,
            }),
            errors=errors,
        )

    async def async_step_station_selection(self, user_input=None):
        """Choose from the available NS stations and create the config entry."""
        errors = {}

        if self._subscription_key is None:
            return await self.async_step_user()

        station_options = await asyncio.to_thread(
            self._station_options,
            self._subscription_key,
        )

        if user_input is not None:
            return self.async_create_entry(
                title=f"{user_input[CONF_STATION]} → {user_input.get(CONF_DESTINATION_STATION, DEFAULT_DESTINATION_STATION)}",
                data={
                    CONF_SUBSCRIPTION_KEY: self._subscription_key,
                    CONF_STATION: user_input[CONF_STATION],
                    CONF_DESTINATION_STATION: user_input.get(
                        CONF_DESTINATION_STATION,
                        DEFAULT_DESTINATION_STATION,
                    ),
                    CONF_MAX_DEPARTURES: user_input.get(CONF_MAX_DEPARTURES, DEFAULT_MAX_DEPARTURES),
                    CONF_LOOKAHEAD_HOURS: user_input.get(
                        CONF_LOOKAHEAD_HOURS,
                        DEFAULT_LOOKAHEAD_HOURS,
                    ),
                },
            )

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
                    vol.Required(
                        CONF_DESTINATION_STATION,
                        default=default_destination,
                    ): vol.In(station_options),
                    vol.Optional(CONF_MAX_DEPARTURES, default=DEFAULT_MAX_DEPARTURES): int,
                    vol.Optional(CONF_LOOKAHEAD_HOURS, default=DEFAULT_LOOKAHEAD_HOURS): int,
                }
            ),
            errors=errors,
        )
