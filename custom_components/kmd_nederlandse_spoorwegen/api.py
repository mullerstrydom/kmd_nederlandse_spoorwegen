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

        if not departures or not isinstance(departures, list):
            return {"station": station, "departures": []}

        now = datetime.now(timezone.utc)
        cutoff = now + timedelta(hours=lookahead_hours)

        normalized = []
        for departure in departures:
            normalized_departure = self._normalize_departure(
                departure,
                now=now,
                cutoff=cutoff,
                destination_station=destination_station,
            )
            if normalized_departure is not None:
                normalized.append(normalized_departure)

        return {"station": station, "destination_station": destination_station, "departures": normalized}

    def _normalize_departure(
        self,
        departure: Any,
        *,
        now: datetime,
        cutoff: datetime,
        destination_station: str | None,
    ) -> dict[str, Any] | None:
        """Convert a raw departure payload into a compact, Home Assistant-friendly dictionary."""
        if departure is None:
            return None

        departure_time = self._first_present(departure, "plannedDateTime", "departure_time_planned")
        actual_departure_time = self._first_present(departure, "actualDateTime", "departure_time_actual")
        planned_track = self._first_present(departure, "plannedTrack", "departure_platform")
        actual_track = self._first_present(departure, "actualTrack", "departure_platform")
        product = self._safe_get(departure, "product", {}) or {}
        route_stations = self._safe_get(departure, "routeStations", []) or []
        destination = self._first_present(departure, "direction", "destination")

        if destination is None and route_stations and isinstance(route_stations[-1], dict):
            destination = route_stations[-1].get("mediumName")

        departure_time = self._normalize_datetime(departure_time)
        actual_departure_time = self._normalize_datetime(actual_departure_time)

        if departure_time is not None:
            if departure_time < now or departure_time > cutoff:
                return None

        # if destination_station and destination_station.lower() not in str(destination or "").lower():
        #     return None

        return {
            "key": self._safe_get(departure, "name") or self._safe_get(departure, "key"),
            "route": destination,
            "destination": destination,
            "direction": self._safe_get(departure, "direction") or destination,
            "departure_time": departure_time,
            "actual_departure_time": actual_departure_time,
            "planned_departure_time": departure_time,
            "platform": actual_track or planned_track or self._safe_get(departure, "departure_platform"),
            "planned_platform": planned_track or self._safe_get(departure, "departure_platform"),
            "actual_platform": actual_track or self._safe_get(departure, "departure_platform"),
            "delay": self._safe_get(departure, "delay", 0),
            "status": self._safe_get(departure, "departureStatus")
            or self._safe_get(departure, "departure_status", "unknown"),
            "train": (
                product.get("shortCategoryName")
                or product.get("longCategoryName")
                or self._safe_get(departure, "train_type")
                or self._safe_get(departure, "trainCategory")
            ),
            "train_number": product.get("number"),
            "train_category": product.get("categoryCode") or self._safe_get(departure, "trainCategory"),
            "cancelled": self._safe_get(departure, "cancelled", False),
            "route_stations": route_stations,
            "messages": self._safe_get(departure, "messages", []),
            "product": product,
            "planned_track": planned_track,
            "actual_track": actual_track,
            "name": self._safe_get(departure, "name"),
        }

    @staticmethod
    def _first_present(value: Any, *keys: str) -> Any:
        """Return the first non-None field from a list of candidate keys."""
        for key in keys:
            candidate = value.get(key) if isinstance(value, dict) else getattr(value, key, None)
            if candidate is not None:
                return candidate
        return None

    @staticmethod
    def _safe_get(value: Any, attr: str, default: Any = None) -> Any:
        """Safely read a value from a departure object or mapping."""
        if value is None:
            return default

        if isinstance(value, dict):
            return value.get(attr, default)

        return getattr(value, attr, default)


    @staticmethod
    def _normalize_datetime(value: Any) -> datetime | None:
        """Normalize an ISO-8601 string or datetime object to a timezone-aware UTC datetime."""
        if value is None:
            return None

        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                return None

        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)

        return value.astimezone(timezone.utc)

