"""Client for fetching Dutch rail departure data via the NS API library."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from homeassistant.exceptions import HomeAssistantError
from ns_api import NSAPI

_LOGGER = logging.getLogger(__name__)


class KmdNederlandseSpoorwegenApiError(HomeAssistantError):
    """Raised when the Dutch rail API returns an error."""


class KmdNederlandseSpoorwegenApiClient:
    """Wrapper around the official NS API Python package."""

    def __init__(self, subscription_key: str) -> None:
        self._client = NSAPI(subscription_key)

    async def _fetch_departures(self, station: str, limit: int) -> list[Any]:
        """Fetch raw departure data and wrap transport-level errors."""
        _LOGGER.debug("Fetching departures for station=%s limit=%s", station, limit)
        try:
            result = await asyncio.to_thread(
                self._client.get_departures,
                station=station,
                max_journeys=str(limit),
            )
            _LOGGER.debug("Raw departures response for %s: %s", station, result)
            return result
        except KeyError as err:  # pragma: no cover - defensive guard
            if err.args and err.args[0] == "payload":
                _LOGGER.warning(
                    "NS API returned a response without a 'payload' key for station %s; treating as empty result",
                    station,
                )
                return []
            _LOGGER.exception("Unhandled KeyError fetching departures for station %s", station)
            raise KmdNederlandseSpoorwegenApiError(
                f"Failed to fetch departures for station {station}: {err}"
            ) from err
        except TypeError as err:  # pragma: no cover - defensive guard
            _LOGGER.exception("TypeError fetching departures for station %s", station)
            raise KmdNederlandseSpoorwegenApiError(
                f"TypeError while fetching departures for station {station}: {err}"
            ) from err
        except Exception as err:  # pragma: no cover - defensive guard
            _LOGGER.exception("Unexpected exception fetching departures for station %s", station)
            raise KmdNederlandseSpoorwegenApiError(
                f"Failed to fetch departures for station {station}: {err}"
            ) from err

    async def async_get_departures(
        self,
        station: str,
        limit: int = 25,
        destination_station: str | None = None,
        lookahead_hours: int = 3,
    ) -> dict[str, Any]:
        """Fetch departure data for a station, optionally filtered by destination and time window."""
        departures = await self._fetch_departures(station, limit)

        if not departures:
            return {"station": station, "departures": []}

        if not isinstance(departures, list):
            return {"station": station, "departures": []}

        now = datetime.now(timezone.utc)
        cutoff = now + timedelta(hours=lookahead_hours)

        normalized = []
        for departure in departures:
            if departure is None:
                continue

            departure_time = self._safe_get(departure, "departure_time_planned")
            if departure_time is not None:
                if isinstance(departure_time, str):
                    try:
                        departure_time = datetime.fromisoformat(departure_time.replace("Z", "+00:00"))
                    except ValueError:
                        departure_time = None
                elif not hasattr(departure_time, "tzinfo") or departure_time.tzinfo is None:
                    departure_time = departure_time.replace(tzinfo=timezone.utc)
                else:
                    departure_time = departure_time.astimezone(timezone.utc)

                if departure_time is not None:
                    if departure_time < now:
                        continue
                    if departure_time > cutoff:
                        continue

            destination = self._safe_get(departure, "destination")
            if destination_station and destination_station.lower() not in str(destination).lower():
                continue

            normalized.append(
                {
                    "key": self._safe_get(departure, "key"),
                    "route": destination,
                    "destination": destination,
                    "departure_time": departure_time,
                    "actual_departure_time": self._safe_get(departure, "departure_time_actual"),
                    "platform": self._safe_get(departure, "departure_platform"),
                    "delay": self._safe_get(departure, "delay", 0),
                    "status": self._safe_get(departure, "departure_status", "unknown"),
                    "train": self._safe_get(departure, "train_type"),
                    "cancelled": self._safe_get(departure, "cancelled", False),
                }
            )

        return {"station": station, "destination_station": destination_station, "departures": normalized}

    @staticmethod
    def _safe_get(value: Any, attr: str, default: Any = None) -> Any:
        """Safely read a value from a departure object or mapping."""
        if value is None:
            return default

        if isinstance(value, dict):
            return value.get(attr, default)

        return getattr(value, attr, default)
