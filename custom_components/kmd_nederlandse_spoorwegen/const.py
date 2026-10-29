"""Constants for the KMd Nederlandse Spoorwegen integration."""

from __future__ import annotations

DOMAIN = "kmd_nederlandse_spoorwegen"
PLATFORMS = ["sensor"]
DEFAULT_NAME = "KMd Nederlandse Spoorwegen"

CONF_SUBSCRIPTION_KEY = "subscription_key"
CONF_STATION = "station"
CONF_STATION_CODE = "station_code"
CONF_DESTINATION_STATION = "destination_station"
CONF_DESTINATION_STATION_CODE = "destination_station_code"
CONF_MAX_DEPARTURES = "max_departures"
CONF_LOOKAHEAD_HOURS = "lookahead_hours"
CONF_UPDATE_INTERVAL = "update_interval_minutes"

DEFAULT_STATION = "Amsterdam Bijlmer Arena"
DEFAULT_DESTINATION_STATION = "Utrecht Centraal"
DEFAULT_MAX_DEPARTURES = 10
DEFAULT_LOOKAHEAD_HOURS = 3
DEFAULT_UPDATE_INTERVAL = 30
