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

        if departures is None:
            return {"station": station, "departures": []}

        normalized = []
        for departure in departures:
            normalized.append(
                {
                    "key": getattr(departure, "key", None),
                    "route": getattr(departure, "destination", None),
                    "destination": getattr(departure, "destination", None),
                    "departure_time": getattr(departure, "departure_time_planned", None),
                    "actual_departure_time": getattr(departure, "departure_time_actual", None),
                    "platform": getattr(departure, "departure_platform", None),
                    "delay": getattr(departure, "delay", 0),
                    "status": getattr(departure, "departure_status", "unknown"),
                    "train": getattr(departure, "train_type", None),
                    "cancelled": getattr(departure, "cancelled", False),
                }
            )

        return {"station": station, "departures": normalized}
