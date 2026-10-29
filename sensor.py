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
    async_add_entities(
        [
            NextDepartureSensor(coordinator),
            UpcomingDeparturesSensor(coordinator),
        ]
    )


class RouteDepartureSensorBase(SensorEntity):
    """Base class for route-related departure sensors."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: KmdNederlandseSpoorwegenCoordinator) -> None:
        self.coordinator = coordinator

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @property
    def _departures(self) -> list[dict]:
        """Return the departure list from the coordinator."""
        return self.coordinator.data.get("departures", [])


class NextDepartureSensor(RouteDepartureSensorBase):
    """Sensor that exposes the next departure time for the configured route."""

    def __init__(self, coordinator: KmdNederlandseSpoorwegenCoordinator) -> None:
        super().__init__(coordinator)
        route_suffix = (
            f"_{coordinator.destination_station_name or coordinator.destination_station}"
            if coordinator.destination_station
            else ""
        )
        self._attr_unique_id = f"{coordinator.station}{route_suffix}_next_departure"
        self._attr_name = (
            f"{coordinator.station_name} → {coordinator.destination_station_name} next departure"
            if coordinator.destination_station_name
            else f"{coordinator.station_name} next departure"
        )

    @property
    def native_value(self):
        """Return the next departure time."""
        for departure in self._departures:
            if departure.get("departure_time") is not None:
                return departure.get("departure_time")
        return None

    @property
    def extra_state_attributes(self):
        """Return details for the next departure."""
        departures = self._departures
        next_departure = next(
            (item for item in departures if item.get("departure_time") is not None),
            {},
        )
        return {
            "origin": self.coordinator.station,
            "destination": self.coordinator.destination_station or next_departure.get("destination"),
            "next_departure": next_departure,
            "platform": next_departure.get("platform"),
            "delay": next_departure.get("delay"),
            "train": next_departure.get("train"),
            "status": next_departure.get("status"),
            "lookahead_hours": self.coordinator.lookahead_hours,
            "route_filter": self.coordinator.destination_station,
        }


class UpcomingDeparturesSensor(RouteDepartureSensorBase):
    """Sensor that exposes the list of upcoming departures for the configured route."""

    def __init__(self, coordinator: KmdNederlandseSpoorwegenCoordinator) -> None:
        super().__init__(coordinator)
        route_suffix = (
            f"_{coordinator.destination_station_name or coordinator.destination_station}"
            if coordinator.destination_station
            else ""
        )
        self._attr_unique_id = f"{coordinator.station}{route_suffix}_upcoming_departures"
        self._attr_name = (
            f"{coordinator.station_name} → {coordinator.destination_station_name} departures"
            if coordinator.destination_station_name
            else f"{coordinator.station_name} departures"
        )

    @property
    def native_value(self):
        """Return the number of upcoming departures."""
        return len(self._departures)

    @property
    def extra_state_attributes(self):
        """Return the complete list of upcoming departures."""
        return {
            "origin": self.coordinator.station,
            "destination": self.coordinator.destination_station,
            "departures": self._departures,
            "lookahead_hours": self.coordinator.lookahead_hours,
            "route_filter": self.coordinator.destination_station,
        }
