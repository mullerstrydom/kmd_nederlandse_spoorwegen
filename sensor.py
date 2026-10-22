"""Sensor platform for the KMd Nederlandse Spoorwegen integration."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor entities from a config entry."""
    async_add_entities([KmdNederlandseSpoorwegenSensor()])


class KmdNederlandseSpoorwegenSensor(SensorEntity):
    """Representation of a KMd Nederlandse Spoorwegen sensor."""

    _attr_name = "KMd Nederlandse Spoorwegen"
    _attr_unique_id = "kmd_nederlandse_spoorwegen"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return None

