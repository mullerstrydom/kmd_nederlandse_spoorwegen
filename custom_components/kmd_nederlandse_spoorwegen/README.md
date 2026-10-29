# KMd Nederlandse Spoorwegen

Custom Home Assistant integration for the Dutch rail departures API.

## Requirements

- A valid Nederlandse Spoorwegen (NS) API subscription key
- An origin station and optional destination station

## Setup

1. Copy this folder into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.
3. Add the integration via the UI.
4. Enter:
   - Subscription key
   - Origin station
   - Destination station
   - Max departures
   - Look ahead hours

## Example config flow values

- Subscription key: `YOUR_NS_API_KEY`
- Origin station: `Amsterdam Bijlmer Arena`
- Destination station: `Utrecht Centraal`
- Max departures: `25`
- Look ahead hours: `3`

This will show trains leaving from Amsterdam Bijlmer Arena for Utrecht Centraal in the next 3 hours.

The integration creates two sensors per config entry:
- `next_departure`: the next departure time for that route/station
- `upcoming_departures`: the list of departures within the configured look-ahead window

These are ideal for dashboard cards like:
- a single sensor card for the next departure time
- a list card or markdown card for all upcoming departures for that route

## Run unit tests

```bash
python -m pytest tests/test_api.py tests/test_coordinator.py tests/test_config_flow.py tests/test_setup.py tests/test_route_filtering.py -q
```

## Notes

This integration uses the official `ns-api` Python package and filters trips by destination and a configurable time window.
