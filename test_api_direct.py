#!/usr/bin/env python3
"""Test the oplaadpalen-py API directly"""
import asyncio
from oplaadpalen_py import OplaadpalenClient
import aiohttp

async def test():
    print("🔍 Testing oplaadpalen-py API with Amsterdam coordinates...")
    async with aiohttp.ClientSession() as session:
        client = OplaadpalenClient(session)
        
        try:
            # Test with Amsterdam coordinates from the warning
            result = await client.get_charging_stations(
                latitude=52.3771,
                longitude=4.8980,
                radius=5.0  # 5 km
            )
            print(f"✅ API returned: {len(result)} stations")
            
            if result:
                print(f"\nFirst 3 stations:")
                for i, station in enumerate(result[:3], 1):
                    print(f"  {i}. {station}")
            else:
                print("\n❌ API returned empty list - likely an API issue")
                    
        except Exception as e:
            print(f"❌ Error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

asyncio.run(test())
