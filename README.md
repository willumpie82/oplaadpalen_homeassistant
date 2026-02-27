# Oplaadpalen.nl Integration for Home Assistant

[![hacs][hacs-badge]][hacs-url]
[![GitHub Release][releases-badge]][releases-url]

A Home Assistant custom integration that monitors available charging equipment (EVSEs) at nearby EV charging stations from oplaadpalen.nl.

## Features

- 🔌 Monitor EVSE (charging point) availability at nearby stations
- 📍 Configure by coordinates or address
- 🔄 Automatic updates at configurable intervals
- 🏠 Create multiple devices for different locations
- ⚡ Binary sensors for each EVSE's availability status
- 📊 Detailed station information (address, operator, connector types, power)

## Installation

### HACS Installation (Recommended)

1. Open Home Assistant and go to: **HACS → Integrations**
2. Click the **⋯** (three dots) menu → **Custom repositories**
3. Add this repository URL:
   ```
   https://github.com/willumpie82/oplaadpalen_homeassistant
   ```
4. Select Category: **Integration**
5. Click "Create"
6. Find "Oplaadpalen.nl" in HACS and click **Install**
7. **Restart Home Assistant**

### Manual Installation

1. Clone this repository into your `custom_components` directory:
   ```bash
   git clone https://github.com/willumpie82/oplaadpalen_homeassistant.git ~/.homeassistant/custom_components/oplaadpalen
   ```

2. Restart Home Assistant

3. Go to Settings → Devices & Services → Create Integration and search for "Oplaadpalen"

## Configuration

The integration can be configured via the Home Assistant UI:

1. Go to Settings → Devices & Services → Create Integration
2. Search for "Oplaadpalen.nl"
3. Enter your device name and either:
   - Coordinates (latitude/longitude)
   - An address (which will be geocoded to coordinates)
4. Set the search radius in km
5. Set the update interval in seconds

### Example Configuration

- **Device Name**: My EV Charger Monitor
- **Address**: Amsterdam, Netherlands
- **Search Radius**: 5 km
- **Update Interval**: 300 seconds (5 minutes)

## Sensors

For each EVSE (charging point) found at nearby stations, the integration creates a binary sensor:

- `binary_sensor.<device_name>_<station>_evse_<n>` - Indicates if an EVSE is AVAILABLE

### Example Sensors

- `binary_sensor.my_ev_charger_monitor_evse_0`
- `binary_sensor.my_ev_charger_monitor_evse_1`

### Sensor Attributes

Each EVSE sensor includes detailed attributes:

- **status** - Current EVSE status (AVAILABLE, OCCUPIED, etc.)
- **address** - Full address of the charging station
- **city** - City name
- **postal_code** - Postal code
- **country** - Country code
- **operator** - Charging station operator name
- **access_type** - Public/Private access
- **connector_standard** - Connector type (e.g., IEC_62196_T2)
- **connector_format** - Socket or Cable format
- **max_power** - Maximum power in watts
- **support_phone** - Support phone number

## API

The integration uses two oplaadpalen.nl APIs:

1. **WMS API** - Finds stations near coordinates
   - Endpoint: `https://www.oplaadpalen.nl/wms`
   - Returns: Feature collection with external references

2. **Detail API** - Gets station and EVSE information
   - Endpoint: `https://www.oplaadpalen.nl/api/map/location/{external_reference}`
   - Returns: Complete station data including EVSEs and connector information

## Usage

You can use the binary sensors in automations and templates:

```yaml
automation:
  - alias: Notify when charger available
    trigger:
      platform: state
      entity_id: binary_sensor.my_ev_charger_monitor_evse_0
      to: 'on'
    action:
      service: notify.mobile_app_iphone
      data:
        message: "Charging port available!"
```

## Requirements

- Home Assistant 2023.12 or later
- geopy >= 2.3.0 (for address geocoding)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

### No sensors appear

- Check that coordinates are correct
- Verify there are charging stations within the search radius
- Check the Home Assistant logs for errors

### Update failures

- Verify internet connection
- Check if oplaadpalen.nl API is accessible
- Reduce the search radius if the request times out

## Support

For issues or feature requests, please visit: https://github.com/willumpie82/oplaadpalen_homeassistant/issues

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

<!-- Badge Links -->
[hacs-badge]: https://img.shields.io/badge/HACS-Custom-41BDF5?logo=homeassistantcommunity
[hacs-url]: https://my.home-assistant.io/redirect/repository/?owner=willumpie82&repository=oplaadpalen_homeassistant&category=integration
[releases-badge]: https://img.shields.io/github/release/willumpie82/oplaadpalen_homeassistant?label=Release
[releases-url]: https://github.com/willumpie82/oplaadpalen_homeassistant/releases
