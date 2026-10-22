"""Sensor platform for the KMd Nederlandse Spoorwegen integration."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import KmdNederlandseSpoorwegenCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor entities from a config entry."""
    coordinator: KmdNederlandseSpoorwegenCoordinator = hass.data["kmd_nederlandse_spoorwegen"][config_entry.entry_id]
    entities = [
        DepartureInfoSensor(coordinator, departure)
        for departure in coordinator.data.get("departures", [])
    ]
    async_add_entities(entities)


class DepartureInfoSensor(SensorEntity):
    """Representation of a departure sensor."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: KmdNederlandseSpoorwegenCoordinator, departure: dict) -> None:
        self.coordinator = coordinator
        self.departure = departure
        self._attr_unique_id = (
            f"{coordinator.station}_{departure.get('route', 'unknown')}_"
            f"{departure.get('departure_time', 'unknown')}"
        )
        self._attr_name = f"{departure.get('route', 'Train')} {departure.get('departure_time', '')}"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.departure.get("status", "unknown")

    @property
    def extra_state_attributes(self):
        """Return extra attributes for the sensor."""
        return {
            "destination": self.departure.get("destination"),
            "platform": self.departure.get("platform"),
            "delay": self.departure.get("delay"),
            "departure_time": self.departure.get("departure_time"),
            "actual_departure_time": self.departure.get("actual_departure_time"),
            "train": self.departure.get("train"),
            "cancelled": self.departure.get("cancelled"),
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success
