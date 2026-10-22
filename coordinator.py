"""Data coordinator for the KMd Nederlandse Spoorwegen integration."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN


class KmdNederlandseSpoorwegenCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, config_entry) -> None:
        super().__init__(
            hass,
            logger=__import__("logging").getLogger(__name__),
            name=DOMAIN,
            update_interval=timedelta(minutes=5),
        )
        self.config_entry = config_entry

    async def _async_update_data(self):
        """Fetch data from the API."""
        return {}

