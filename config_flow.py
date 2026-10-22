"""Config flow for the KMd Nederlandse Spoorwegen integration."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries

from .const import (
    CONF_MAX_DEPARTURES,
    CONF_STATION,
    CONF_SUBSCRIPTION_KEY,
    DEFAULT_MAX_DEPARTURES,
    DEFAULT_STATION,
    DOMAIN,
)


class KmdNederlandseSpoorwegenConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for KMd Nederlandse Spoorwegen."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_STATION],
                data={
                    CONF_SUBSCRIPTION_KEY: user_input[CONF_SUBSCRIPTION_KEY],
                    CONF_STATION: user_input[CONF_STATION],
                    CONF_MAX_DEPARTURES: user_input.get(CONF_MAX_DEPARTURES, DEFAULT_MAX_DEPARTURES),
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_SUBSCRIPTION_KEY): str,
                    vol.Required(CONF_STATION, default=DEFAULT_STATION): str,
                    vol.Optional(CONF_MAX_DEPARTURES, default=DEFAULT_MAX_DEPARTURES): int,
                }
            ),
        )
