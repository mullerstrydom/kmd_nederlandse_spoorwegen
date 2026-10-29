# KMd Nederlandse Spoorwegen

Custom Home Assistant integration for Dutch rail departures using the Nederlandse Spoorwegen API.

## Features

- Monitor departures from a chosen station
- Optionally filter by destination station
- Show the next departure and upcoming departures
- Configure route settings from the Home Assistant UI

## Requirements

- Home Assistant 2024.10.0 or newer
- A valid Nederlandse Spoorwegen API subscription key

## Installation

### HACS

1. Add this repository as a custom repository in HACS.
2. Search for "KMd Nederlandse Spoorwegen".
3. Install the integration.
4. Restart Home Assistant.

### Manual

1. Copy the `custom_components/kmd_nederlandse_spoorwegen` folder into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.
3. Add the integration from Settings > Devices & Services > Add Integration.

## Configuration

When setting up the integration, provide:

- Subscription key
- Origin station
- Destination station
- Max departures
- Look-ahead hours

## Example

A typical configuration could be:

- Origin station: `Amsterdam Bijlmer Arena`
- Destination station: `Utrecht Centraal`
- Max departures: `25`
- Look-ahead hours: `3`

This will show departures from Amsterdam Bijlmer Arena to Utrecht Centraal in the next 3 hours.

## Dashboard card example

This integration exposes sensor entities such as `sensor.<route>_next_departure` and `sensor.<route>_upcoming_departures`.

A clean markdown dashboard card using a table layout can look like this:

```yaml
type: markdown
content: |
  ## Amsterdam Bijlmer Arena → Utrecht Centraal

  | Time | Destination | Platform | Delay |
  |------|-------------|----------|-------|
  {% set items = state_attr('sensor.amsterdam_bijlmer_arena_to_utrecht_centraal_upcoming_departures', 'value') %}
  {% if items %}
  {% for item in items[:5] %}
  | {{ item.time }} | {{ item.destination }} | {{ item.platform or '-' }} | {{ item.delay or 'On time' }} |
  {% endfor %}
  {% else %}
  | - | No departures found | - | - |
  {% endif %}
```

If your entity IDs differ, use the actual names created by the integration when you configure it.

## Development

To run the tests locally:

```bash
python -m pytest tests -q
```

## Notes

This integration uses the official `ns-api` Python package and filters trains by destination and time window.
