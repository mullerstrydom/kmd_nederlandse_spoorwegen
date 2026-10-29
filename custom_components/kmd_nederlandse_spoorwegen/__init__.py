"""The KMd Nederlandse Spoorwegen integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from ns_api import NSAPI

from .const import (
    CONF_DESTINATION_STATION,
    CONF_DESTINATION_STATION_CODE,
    CONF_STATION,
    CONF_STATION_CODE,
    CONF_SUBSCRIPTION_KEY,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import KmdNederlandseSpoorwegenCoordinator


def _station_code_map(subscription_key: str) -> dict[str, str]:
    """Return a mapping of station names to NS station codes."""
    station_map: dict[str, str] = {}
    for station in NSAPI(subscription_key).get_stations():
        code = getattr(station, "code", None)
        long_name = getattr(station, "names", {}).get("long")
        if code and long_name:
            station_map[long_name] = code
    return dict(sorted(station_map.items()))


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate older config entries to include station codes."""
    if config_entry.version == 1:
        data = {**config_entry.data}
        subscription_key = data.get(CONF_SUBSCRIPTION_KEY)
        station_name = data.get(CONF_STATION)
        destination_name = data.get(CONF_DESTINATION_STATION)
        station_map: dict[str, str] = {}

        if subscription_key:
            try:
                station_map = await hass.async_add_executor_job(_station_code_map, subscription_key)
            except Exception:  # pragma: no cover - runtime/network dependent
                station_map = {}

        if station_name and CONF_STATION_CODE not in data:
            data[CONF_STATION_CODE] = station_map.get(station_name, station_name)
        if destination_name and CONF_DESTINATION_STATION_CODE not in data:
            data[CONF_DESTINATION_STATION_CODE] = station_map.get(destination_name, destination_name)

        hass.config_entries.async_update_entry(config_entry, data=data, version=2)
        return True

    return False


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the component from YAML."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up KMd Nederlandse Spoorwegen from a config entry."""
    await async_migrate_entry(hass, entry)
    coordinator = KmdNederlandseSpoorwegenCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
