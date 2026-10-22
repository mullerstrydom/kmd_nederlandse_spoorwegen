"""Data coordinator for the KMd Nederlandse Spoorwegen integration."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import KmdNederlandseSpoorwegenApiClient
from .const import (
    CONF_DESTINATION_STATION,
    CONF_LOOKAHEAD_HOURS,
    CONF_MAX_DEPARTURES,
    CONF_STATION,
    CONF_SUBSCRIPTION_KEY,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class KmdNederlandseSpoorwegenCoordinator(DataUpdateCoordinator[dict]):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=5),
        )
        self.config_entry = config_entry
        self.api = KmdNederlandseSpoorwegenApiClient(
            config_entry.data[CONF_SUBSCRIPTION_KEY],
        )
        self.station = config_entry.data[CONF_STATION]
        self.destination_station = config_entry.data.get(CONF_DESTINATION_STATION)
        self.max_departures = config_entry.data.get(CONF_MAX_DEPARTURES, 25)
        self.lookahead_hours = config_entry.data.get(CONF_LOOKAHEAD_HOURS, 3)

    async def _async_update_data(self) -> dict:
        """Fetch data from the API."""
        return await self.api.async_get_departures(
            self.station,
            self.max_departures,
            destination_station=self.destination_station,
            lookahead_hours=self.lookahead_hours,
        )
