# How to Add Stations Manually (WMS Coverage Workaround)

If your location doesn't have WMS data, you can manually add charging stations using their external reference IDs.

## Quick Start

### Step 1: Find Your Station's External Reference

If you know a station's URL from oplaadpalen.nl:
```
https://www.oplaadpalen.nl/en/station/400b80f85597c2dc211ef83e942010aa
                                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                        This is the external_reference
```

Or use curl to find it:
```bash
# This queries WMS for your coordinates
curl "https://www.oplaadpalen.nl/wms?REQUEST=GetFeatureInfo&SERVICE=WMS&SRS=EPSG:4326&VERSION=1.1.1&INFO_FORMAT=application/json&BBOX=5.2670,51.6890,5.2770,51.6990&HEIGHT=500&WIDTH=500&LAYERS=eco:rta_and_clusters&QUERY_LAYERS=eco:rta_and_clusters&X=250&Y=250" | grep -o '"external_reference":"[^"]*"'

# Result: "external_reference":"400b80f85597c2dc211ef83e942010aa"
```

### Step 2: Get Station Details

```bash
curl "https://www.oplaadpalen.nl/api/map/location/400b80f85597c2dc211ef83e942010aa" | python -m json.tool
```

Response example:
```json
{
  "status_code": 1000,
  "data": {
    "external_reference": "400b80f85597c2dc211ef83e942010aa",
    "address": "Jacob Cnodestraat 23",
    "city": "'s-Hertogenbosch",
    "latitude": 51.6890,
    "longitude": 5.2670,
    "operator": "Vattenfall InCharge",
    "connectors": ["IEC_62196_T2", "IEC_62196_T2"],
    "power": [22.0, 22.0],
    "evses": [
      {"status": 0, "power": 22.0, "connector": "IEC_62196_T2"},
      {"status": 0, "power": 22.0, "connector": "IEC_62196_T2"}
    ]
  }
}
```

### Step 3: Configure in Home Assistant

**Option A: Through Integration Settings** (if implemented in future version)

1. Create integration as usual
2. After setup, add external reference in integration options
3. Integration will fetch station details automatically

**Option B: Current Workaround** (v0.1.8)

Edit the integration's `const.py` file:

```python
# custom_components/oplaadpalen/const.py

# Add this section for manual stations
MANUAL_STATIONS = {
    "jacob-cnodestraat-23": {
        "external_reference": "400b80f85597c2dc211ef83e942010aa",
        "name": "Jacob Cnodestraat 23",
        "address": "Jacob Cnodestraat 23, 's-Hertogenbosch"
    }
}
```

Then modify `binary_sensor.py` to create sensors for these stations in addition to WMS-discovered ones.

---

## Script: Bulk Find Stations

```bash
#!/bin/bash
# find_nearby_stations.sh - Find all stations in an area

LAT=$1
LON=$2
RADIUS=${3:-0.05}  # degrees (≈ 5km)

MIN_LAT=$(echo "$LAT - $RADIUS" | bc)
MAX_LAT=$(echo "$LAT + $RADIUS" | bc)
MIN_LON=$(echo "$LON - $RADIUS" | bc)
MAX_LON=$(echo "$LON + $RADIUS" | bc)

echo "Searching for stations: Lat $MIN_LAT-$MAX_LAT, Lon $MIN_LON-$MAX_LON"

curl -s "https://www.oplaadpalen.nl/wms?REQUEST=GetFeatureInfo&SERVICE=WMS&SRS=EPSG:4326&VERSION=1.1.1&INFO_FORMAT=application/json&BBOX=$MIN_LON,$MIN_LAT,$MAX_LON,$MAX_LAT&HEIGHT=500&WIDTH=500&LAYERS=eco:rta_and_clusters&QUERY_LAYERS=eco:rta_and_clusters&X=250&Y=250" | \
python3 -c "
import sys, json
data = json.load(sys.stdin)
for feature in data.get('features', []):
    ref = feature['properties'].get('external_reference', 'unknown')
    print(f'Found station: {ref}')
    # Fetch details
    import urllib.request
    try:
        url = f'https://www.oplaadpalen.nl/api/map/location/{ref}'
        with urllib.request.urlopen(url) as f:
            detail = json.load(f)
            if detail['status_code'] == 1000:
                data = detail['data']
                print(f\"  Address: {data.get('address', 'N/A')}\")
                print(f\"  City: {data.get('city', 'N/A')}\")
                print(f\"  Power: {data.get('power', [])} kW\")
                print(f\"  Operator: {data.get('operator', 'N/A')}\")
                print()
    except Exception as e:
        print(f'  (Could not fetch details: {e})\n')
"
```

Usage:
```bash
chmod +x find_nearby_stations.sh
./find_nearby_stations.sh 51.6890 5.2670  # Your coordinates
```

---

## Supported External References

These are validated station references that work:

| Location | External Reference | Address | EVSE Count | Operator |
|----------|-------------------|---------|-----------|----------|
| Amsterdam - Singel | 4000263c1ad824e7211e897ae42010a8 | Singel 250, Amsterdam | 2 | EQUANS |
| 's-Hertogenbosch | 400b80f85597c2dc211ef83e942010aa | Jacob Cnodestraat 23 | 2 | Vattenfall InCharge |

Add more as you discover them!

---

## Troubleshooting Manual Add

### Station returns 404 / empty response
- Reference ID may be incorrect
- Station may be offline
- Double-check against oplaadpalen.nl website

### Integration doesn't use manual stations
- Feature not yet implemented in v0.1.8
- You'll need to modify `config_flow.py` and `binary_sensor.py`
- Or wait for integration enhancement

### Need automated discovery?

Consider using EAFO (European Alternative Fuels Observatory) API:
```bash
# EAFO has much better coverage
curl "https://data.eafo.eu/api/v1/stations?" \
  --data-urlencode 'longitude=5.267' \
  --data-urlencode 'latitude=51.689' \
  --data-urlencode 'distance=10'  # km
```

---

## Next Steps

1. ✅ Find your station's external reference
2. ✅ Test it with the Detail API
3. ⏳ Wait for manual station config feature
4. Or: ✅ Implement it yourself (see code modification option above)

---

**Questions?** Check the main [README.md](README.md) or [INTEGRATION_STATUS.md](INTEGRATION_STATUS.md)
