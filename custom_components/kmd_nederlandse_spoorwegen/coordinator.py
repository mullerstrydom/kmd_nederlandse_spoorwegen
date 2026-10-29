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
    CONF_DESTINATION_STATION_CODE,
    CONF_LOOKAHEAD_HOURS,
    CONF_MAX_DEPARTURES,
    CONF_STATION,
    CONF_STATION_CODE,
    CONF_SUBSCRIPTION_KEY,
    CONF_UPDATE_INTERVAL,
    DEFAULT_LOOKAHEAD_HOURS,
    DEFAULT_MAX_DEPARTURES,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class KmdNederlandseSpoorwegenCoordinator(DataUpdateCoordinator[dict]):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        update_interval_minutes = config_entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=update_interval_minutes),
        )
        self.config_entry = config_entry
        self.api = KmdNederlandseSpoorwegenApiClient(
            config_entry.data[CONF_SUBSCRIPTION_KEY],
        )
        self.station = config_entry.data.get(CONF_STATION_CODE, config_entry.data[CONF_STATION])
        self.station_name = config_entry.data.get(CONF_STATION, self.station)
        self.destination_station_code = config_entry.data.get(
            CONF_DESTINATION_STATION_CODE,
            config_entry.data.get(CONF_DESTINATION_STATION),
        )
        self.destination_station = self.destination_station_code
        self.destination_station_name = config_entry.data.get(
            CONF_DESTINATION_STATION,
            self.destination_station_code,
        )
        self.max_departures = config_entry.data.get(CONF_MAX_DEPARTURES, DEFAULT_MAX_DEPARTURES)
        self.lookahead_hours = config_entry.data.get(CONF_LOOKAHEAD_HOURS, DEFAULT_LOOKAHEAD_HOURS)

    async def _async_update_data(self) -> dict:
        """Fetch data from the API."""
        return await self.api.async_get_departures(
            self.station,
            self.max_departures,
            destination_station=self.destination_station_code,
            lookahead_hours=self.lookahead_hours,
        )
