"""Constants for the KMd Nederlandse Spoorwegen integration."""

from __future__ import annotations

DOMAIN = "kmd_nederlandse_spoorwegen"
PLATFORMS = ["sensor"]
DEFAULT_NAME = "KMd Nederlandse Spoorwegen"

CONF_SUBSCRIPTION_KEY = "subscription_key"
CONF_STATION = "station"
CONF_MAX_DEPARTURES = "max_departures"

DEFAULT_STATION = "Utrecht Centraal"
DEFAULT_MAX_DEPARTURES = 5
