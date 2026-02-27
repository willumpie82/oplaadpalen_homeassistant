#!/usr/bin/env python3
"""
Test if your location has WMS data coverage.

Usage:
    python3 test_your_location.py 51.6890 5.2670
    
This will test if the given coordinates (lat, lon) have charging station data
in the oplaadpalen.nl WMS API.
"""

import sys
import json
import urllib.request
import urllib.error

def test_wms_coverage(lat: float, lon: float):
    """Test if coordinates have WMS data."""
    
    # Create bounding box around coordinates
    # 0.01 degrees ≈ ~1 km
    bbox = f"{lon-0.01},{lat-0.01},{lon+0.01},{lat+0.01}"
    
    url = (
        f"https://www.oplaadpalen.nl/wms?"
        f"REQUEST=GetFeatureInfo&"
        f"SERVICE=WMS&"
        f"SRS=EPSG:4326&"
        f"VERSION=1.1.1&"
        f"INFO_FORMAT=application/json&"
        f"BBOX={bbox}&"
        f"HEIGHT=500&"
        f"WIDTH=500&"
        f"LAYERS=eco:rta_and_clusters&"
        f"QUERY_LAYERS=eco:rta_and_clusters&"
        f"X=250&"
        f"Y=250"
    )
    
    print(f"\n📍 Testing WMS coverage for coordinates (Lat: {lat}, Lon: {lon})")
    print(f"🔍 Querying bounding box: {bbox}")
    print(f"🌐 URL: {url[:100]}...")
    
    try:
        # Add proper User-Agent to avoid 403 errors
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (compatible; OplaadpalenTest/1.0)'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
        features = data.get('features', [])
        feature_count = len(features)
        
        print(f"\n✅ Response received: {feature_count} station(s) found\n")
        
        if feature_count == 0:
            print("❌ NO DATA - Your location is not in the WMS coverage area")
            return False
        else:
            print(f"✅ SUCCESS - Found {feature_count} charging station(s)!")
            for i, feature in enumerate(features, 1):
                ref = feature.get('properties', {}).get('external_reference', 'unknown')
                print(f"   [{i}] Reference: {ref}")
            return True
            
    except urllib.error.URLError as e:
        print(f"\n❌ Error fetching data: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"\n❌ Error parsing response: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        print("\n📍 Example - Test 's-Hertogenbosch:")
        print("   python3 test_your_location.py 51.6890 5.2670")
        print("\n📍 Example - Test Amsterdam:")
        print("   python3 test_your_location.py 52.3733 4.8939")
        sys.exit(1)
    
    try:
        lat = float(sys.argv[1])
        lon = float(sys.argv[2])
    except ValueError:
        print(f"❌ Error: Invalid coordinates. Expected floats, got: {sys.argv[1]}, {sys.argv[2]}")
        sys.exit(1)
    
    success = test_wms_coverage(lat, lon)
    
    if success:
        print("\n✨ Your integration should work! Set it up with these coordinates.")
    else:
        print("\n⚠️  Your location may not have WMS coverage yet.")
        print("    Try a nearby location or check the map: https://www.oplaadpalen.nl/")
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
