# Oplaadpalen.nl Integration for Home Assistant

[![hacs][hacs-badge]][hacs-url]
[![GitHub Release][releases-badge]][releases-url]

A Home Assistant custom integration that monitors available charging equipment (EVSEs) at nearby EV charging stations from oplaadpalen.nl.

## Project Structure

This project consists of two main components:

1. **oplaadpalen_py/** - Standalone Python library for the Oplaadpalen API
   - Pure Python client with no Home Assistant dependencies
   - Can be installed from PyPI as `oplaadpalen-py`
   - Comprehensive test coverage
   - Reusable across different projects

2. **custom_components/oplaadpalen/** - Home Assistant integration
   - Uses the `oplaadpalen_py` library for API calls
   - Provides binary sensors for EVSE availability
   - Configuration via Home Assistant UI

## Current Status

✅ **Integration is fully functional** (v0.1.8)
- Code tested and working correctly
- Library published to PyPI
- Verified working in 's-Hertogenbosch area

⚠️ **Important - WMS Data Coverage Limitation**

The oplaadpalen.nl WMS API has **sparse geographic coverage**. This means:
- ✅ Some areas have excellent data (verified: 's-Hertogenbosch, Arnhem region)  
- ❌ Other areas have no public WMS data (e.g., Amsterdam, Rotterdam)
- ✅ Your location may work - **test it first** (see below)

This is an **external API limitation**, not a code issue.

## Features

- 🔌 Monitor EVSE (charging point) availability at nearby stations
- 📍 Configure by coordinates or address
- 🔄 Automatic updates at configurable intervals
- 🏠 Create multiple devices for different locations
- ⚡ Binary sensors for each EVSE's availability status
- 📊 Detailed station information (address, operator, connector types, power)

## Installation

### Installation from HACS (Recommended)

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

## Testing WMS Coverage for Your Location

Before setting up the integration, check if your location has WMS data:

### Quick Test (curl)

Replace `LAT` and `LON` with your coordinates:

```bash
curl "https://www.oplaadpalen.nl/wms?REQUEST=GetFeatureInfo&SERVICE=WMS&SRS=EPSG:4326&VERSION=1.1.1&INFO_FORMAT=application/json&BBOX=LON-0.01,LAT-0.01,LON+0.01,LAT+0.01&HEIGHT=500&WIDTH=500&LAYERS=eco:rta_and_clusters&QUERY_LAYERS=eco:rta_and_clusters&X=250&Y=250" | python -m json.tool
```

**Interpreting results:**

```json
// ✅ GOOD - Location has data
{"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {"external_reference": "400b80f85597c2dc211ef83e942010aa"}}]}

// ❌ BAD - No stations in WMS
{"type": "FeatureCollection", "features": []}
```

### Tested Working Locations

✅ **Verified WMS Coverage:**
- 's-Hertogenbosch (51.6890, 5.2670) - **1+ stations** (Jacob Cnodestraat 23 area)
- Amsterdam - **Singel area (52.3737, 4.8885) - 1+ stations** - Coverage is **neighborhood-specific**, not city-wide
  - Singel 250: 2 EVSEs (EQUANS operator, 11kW)
  - Dam area (52.3733, 4.8939): ❌ No coverage nearby

⚠️ **Neighborhood-Level Coverage Variation:**
- WMS coverage varies **by neighborhood**, not by city
- Same city can have both covered and uncovered areas (sometimes just 400m apart)
- Always test your **exact address**

❌ **Known to lack WMS data (areas tested):**
- Amsterdam Dam area (52.3733, 4.8939) - 0 stations
- Rotterdam - 0 stations (untested in detail)

### Examples

**Working: 's-Hertogenbosch (Jacob Cnodestraat 23)**
```bash
curl "https://www.oplaadpalen.nl/wms?REQUEST=GetFeatureInfo&SERVICE=WMS&SRS=EPSG:4326&VERSION=1.1.1&INFO_FORMAT=application/json&BBOX=5.2670,51.6890,5.2770,51.6990&HEIGHT=500&WIDTH=500&LAYERS=eco:rta_and_clusters&QUERY_LAYERS=eco:rta_and_clusters&X=250&Y=250" | python -m json.tool
# Result: 1 station found ✅
```

**Working: Amsterdam (Singel 214/250)**
```bash
curl "https://www.oplaadpalen.nl/wms?REQUEST=GetFeatureInfo&SERVICE=WMS&SRS=EPSG:4326&VERSION=1.1.1&INFO_FORMAT=application/json&BBOX=4.8785,52.3637,4.8985,52.3837&HEIGHT=500&WIDTH=500&LAYERS=eco:rta_and_clusters&QUERY_LAYERS=eco:rta_and_clusters&X=250&Y=250" | python -m json.tool
# Result: 1 station found ✅ (Singel 250, EQUANS operator)
```

**No coverage: Amsterdam (Dam area ~400m away)**
```bash
curl "https://www.oplaadpalen.nl/wms?REQUEST=GetFeatureInfo&SERVICE=WMS&SRS=EPSG:4326&VERSION=1.1.1&INFO_FORMAT=application/json&BBOX=4.878,52.363,4.898,52.383&HEIGHT=500&WIDTH=500&LAYERS=eco:rta_and_clusters&QUERY_LAYERS=eco:rta_and_clusters&X=250&Y=250" | python -m json.tool
# Result: 0 features ❌ (neighborhood without coverage)
```

---

### Development

The `oplaadpalen_py` library is the core of this project and can be developed independently:

```bash
cd oplaadpalen_py

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest test_client.py -v --cov=. --cov-report=html

# Build package
python setup.py sdist bdist_wheel
```

### Running Tests

The integration includes a comprehensive test suite. To run tests locally:

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all integration tests
pytest tests/

# Run library tests
cd oplaadpalen_py
pytest test_client.py -v

# Run with coverage
pytest tests/ --cov=custom_components/oplaadpalen --cov-report=html

# Or use the test script
python run_tests.py
```

See [tests/README.md](tests/README.md) and [oplaadpalen_py/README.md](oplaadpalen_py/README.md) for more details on testing.

---

<!-- Badge Links -->
[hacs-badge]: https://img.shields.io/badge/HACS-Custom-41BDF5?logo=homeassistantcommunity
[hacs-url]: https://my.home-assistant.io/redirect/repository/?owner=willumpie82&repository=oplaadpalen_homeassistant&category=integration
[releases-badge]: https://img.shields.io/github/release/willumpie82/oplaadpalen_homeassistant?label=Release
[releases-url]: https://github.com/willumpie82/oplaadpalen_homeassistant/releases
