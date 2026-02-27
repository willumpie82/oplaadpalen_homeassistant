# Oplaadpalen.nl Python Library

A lightweight Python client library for the Oplaadpalen.nl EV charging stations API.

## Features

- 🔌 Query charging stations near coordinates
- 📍 Automatic geographic bounding box calculation
- ⚡ Async/await support with aiohttp
- 🛡️ Comprehensive error handling and validation
- 📦 Zero external dependencies (only aiohttp)
- ✅ Full test coverage
- 🚀 Ready for production use

## Installation

```bash
pip install oplaadpalen-py
```

Or from source:

```bash
git clone https://github.com/willumpie82/oplaadpalen_homeassistant
cd oplaadpalen_homeassistant/oplaadpalen_py
pip install -e .
```

## Quick Start

### Basic Usage

```python
import aiohttp
from oplaadpalen_py import OplaadpalenClient

async def main():
    async with aiohttp.ClientSession() as session:
        async with OplaadpalenClient(session) as client:
            # Get charging stations near Amsterdam (5 km radius)
            stations = await client.get_charging_stations(
                latitude=52.37403,
                longitude=4.88969,
                radius_km=5.0
            )
            
            for station in stations:
                print(f"Station: {station['address']}")
                print(f"City: {station['city']}")
                print(f"Operator: {station['operator']['name']}")
                print(f"EVSEs: {len(station['evses'])}")
                print()
```

### Context Manager Usage

The client can be used as an async context manager:

```python
from oplaadpalen_py import OplaadpalenClient

async def main():
    # Client creates and manages its own session
    async with OplaadpalenClient() as client:
        stations = await client.get_charging_stations(52.37403, 4.88969)
```

## API Reference

### OplaadpalenClient

#### `get_charging_stations(latitude, longitude, radius_km=5.0)`

Query charging stations near the specified coordinates.

**Parameters:**
- `latitude` (float): Center latitude (-90 to 90)
- `longitude` (float): Center longitude (-180 to 180)
- `radius_km` (float): Search radius in kilometers (0.1 to 100, default: 5.0)

**Returns:**
- `list[dict]`: List of station dictionaries

**Raises:**
- `ValueError`: If coordinates or radius are invalid
- `aiohttp.ClientError`: If API request fails

**Station Data Structure:**

```python
{
    "external_reference": "400b80f85597c2dc211ef83e942010aa",
    "address": "Jacob Cnodestraat 23",
    "city": "'s-Hertogenbosch",
    "postal_code": "5223 HS",
    "country": "NLD",
    "evses": [
        {
            "status": "AVAILABLE",
            "connectors": [
                {
                    "standard": "IEC_62196_T2",
                    "format": "SOCKET",
                    "max_power": 11000
                }
            ]
        }
    ],
    "operator": {
        "name": "Vattenfall InCharge",
        "website": "http://vattenfall.nl"
    },
    "access_type": "Public",
    "support_phone_number": "+(31)-(88)-3637991"
}
```

#### `get_station_details(external_reference)`

Get detailed information about a specific charging station by its external reference.

**Parameters:**
- `external_reference` (str): Station external reference ID

**Returns:**
- `dict | None`: Station data dictionary or None if request fails

## Running Tests

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=oplaadpalen_py --cov-report=html
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Usage in Home Assistant

This library is used by the Oplaadpalen Home Assistant integration:

```python
from oplaadpalen_py import OplaadpalenClient

# In the Home Assistant integration
client = OplaadpalenClient(hass_session)
stations = await client.get_charging_stations(lat, lon, radius)
```

See the [Home Assistant integration](https://github.com/willumpie82/oplaadpalen_homeassistant) for more details.
