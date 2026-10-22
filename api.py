"""Client for fetching Dutch rail departure data via the NS API library."""

from __future__ import annotations

from typing import Any

from homeassistant.exceptions import HomeAssistantError
from ns_api import NSAPI


class KmdNederlandseSpoorwegenApiError(HomeAssistantError):
    """Raised when the Dutch rail API returns an error."""


class KmdNederlandseSpoorwegenApiClient:
    """Wrapper around the official NS API Python package."""

    def __init__(self, subscription_key: str) -> None:
        self._client = NSAPI(subscription_key)

    async def async_get_departures(self, station: str, limit: int = 5) -> dict[str, Any]:
        """Fetch departure data for a station."""
        try:
            departures = self._client.get_departures(station=station, max_journeys=str(limit))
        except Exception as err:  # pragma: no cover - defensive guard
            raise KmdNederlandseSpoorwegenApiError(
                f"Failed to fetch departures for station {station}: {err}"
            ) from err

        if not departures:
            return {"station": station, "departures": []}

        if not isinstance(departures, list):
            return {"station": station, "departures": []}

        normalized = []
        for departure in departures:
            if departure is None:
                continue

            normalized.append(
                {
                    "key": self._safe_get(departure, "key"),
                    "route": self._safe_get(departure, "destination"),
                    "destination": self._safe_get(departure, "destination"),
                    "departure_time": self._safe_get(departure, "departure_time_planned"),
                    "actual_departure_time": self._safe_get(departure, "departure_time_actual"),
                    "platform": self._safe_get(departure, "departure_platform"),
                    "delay": self._safe_get(departure, "delay", 0),
                    "status": self._safe_get(departure, "departure_status", "unknown"),
                    "train": self._safe_get(departure, "train_type"),
                    "cancelled": self._safe_get(departure, "cancelled", False),
                }
            )

        return {"station": station, "departures": normalized}

    @staticmethod
    def _safe_get(value: Any, attr: str, default: Any = None) -> Any:
        """Safely read a value from a departure object or mapping."""
        if value is None:
            return default

        if isinstance(value, dict):
            return value.get(attr, default)

        return getattr(value, attr, default)
