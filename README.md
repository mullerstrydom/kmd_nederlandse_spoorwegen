# KMd Nederlandse Spoorwegen

Custom Home Assistant integration for the Dutch rail departures API.

## Requirements

- A valid Nederlandse Spoorwegen (NS) API subscription key
- A station name such as `Utrecht Centraal`

## Setup

1. Copy this folder into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.
3. Add the integration via the UI.
4. Enter:
   - Subscription key
   - Station
   - Max departures

## Example config flow values

- Subscription key: `YOUR_NS_API_KEY`
- Station: `Utrecht Centraal`
- Max departures: `5`

## Run unit tests

```bash
python -m pytest tests/test_api.py -q
```

## Notes

This integration uses the official `ns-api` Python package.
