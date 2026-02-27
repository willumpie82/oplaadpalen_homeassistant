#!/usr/bin/env python3
"""Test the integration flow: geocoding + API call"""
import asyncio
from geopy.geocoders import Nominatim
from oplaadpalen_py import OplaadpalenClient
import aiohttp

async def test():
    print("=" * 60)
    print("🔍 Testing Integration Flow")
    print("=" * 60)
    
    # Step 1: Test geocoding
    print("\n1️⃣ Geocoding 'Dam 1'...")
    try:
        geolocator = Nominatim(user_agent="homeassistant")
        location = geolocator.geocode("Dam 1")
        if location:
            print(f"✅ Geocoded to: ({location.latitude}, {location.longitude})")
            lat, lon = location.latitude, location.longitude
        else:
            print("❌ Geocoding failed - no results")
            return
    except Exception as e:
        print(f"❌ Geocoding error: {e}")
        return
    
    # Step 2: Test API
    print(f"\n2️⃣ Calling API with 5km radius...")
    async with aiohttp.ClientSession() as session:
        client = OplaadpalenClient(session)
        try:
            result = await client.get_charging_stations(
                latitude=lat,
                longitude=lon,
                radius=5000
            )
            print(f"✅ API returned: {len(result)} stations")
            
            if result:
                print(f"\n📍 First 3 stations:")
                for i, station in enumerate(result[:3], 1):
                    print(f"   {i}. {station}")
            else:
                print("\n❌ No stations with 5km - trying 10km...")
                result = await client.get_charging_stations(
                    latitude=lat,
                    longitude=lon,
                    radius=10000
                )
                print(f"   With 10km radius: {len(result)} stations")
                
                if not result:
                    print("\n⚠️  Still no stations. Possible causes:")
                    print("   1. oplaadpalen.nl API is down")
                    print("   2. No stations exist near Amsterdam")
                    print("   3. API format changed")
                
        except Exception as e:
            print(f"❌ API error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

asyncio.run(test())
