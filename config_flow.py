"""Config flow for the KMd Nederlandse Spoorwegen integration."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries

from .const import DOMAIN


class KmdNederlandseSpoorwegenConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for KMd Nederlandse Spoorwegen."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(
                title="KMd Nederlandse Spoorwegen",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("username"): str,
                    vol.Optional("password"): str,
                }
            ),
        )

