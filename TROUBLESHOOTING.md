# Integration Not Showing - Troubleshooting & Fix

## 🔴 Root Cause Found

**Critical Issue**: Your `strings.json` file had a Python docstring at the top:

```json
"""String resources for Oplaadpalen integration."""
{
  "config": { ... }
```

Home Assistant couldn't parse this as JSON, so the entire config flow failed silently with **no error messages**.

**Status**: ✅ **FIXED** in latest commit

---

## 🔧 What to Do Next

### 1. **Pull Latest Changes**

```bash
cd "/Users/willemoldemans/Documents/PROJECTEN/homeassistant hacs"
git pull origin main
# Should get commit: "fix: Remove Python docstring from strings.json"
```

### 2. **Update Home Assistant**

**Option A - If using local installation:**
```bash
pip install -e ./oplaadpalen_py
# Reinstall integration
cp -r custom_components/oplaadpalen ~/.homeassistant/custom_components/
# Restart HA
```

**Option B - If using Docker:**

Remove old installation and reinstall:

```bash
# Stop Home Assistant
docker-compose stop ha

# Clear old integration cache
docker-compose exec ha rm -rf /config/custom_components/oplaadpalen

# Restart
docker-compose up -d

# Wait 30 seconds for startup
sleep 30

# Check logs
docker-compose logs ha | tail -20 | grep -i oplaadpalen
```

### 3. **Set Up Integration**

1. Go to **Settings → Devices & Services**
2. Click **Create Integration**
3. Search for **Oplaadpalen.nl**
4. Click "Create"
5. Fill in your details:
   - Device Name: `EV Charger Monitor` (or your choice)
   - Address: `Singel 214, 1016 AB, Amsterdam` (or your address)
   - Radius: `5` km
   - Update Interval: `300` seconds

6. You should see:
   - ✅ Geocoding message: Shows coordinates (52.3737, 4.8885)
   - ✅ Station search result: Shows "1 station found" or "No stations found"
   - ✅ If stations found: Config entry created, binary sensors appear
   - ⚠️ If no stations: "No Charging Stations Found" confirmation screen

### 4. **Check for Logs**

Go to **Settings → System → Logs** and search for `oplaadpalen`:

**Expected log messages (in order):**
```
2026-02-27 22:15:30 INFO Fetching stations: lat=52.3737 lon=4.8885 radius=5.0 km
2026-02-27 22:15:31 INFO Fetched 1 charging stations
2026-02-27 22:15:31 INFO [1/1] Getting details for 4000263c1ad824e7211e897ae42010a8
2026-02-27 22:15:32 INFO ✅ Got details for 4000263c1ad824e7211e897ae42010a8
2026-02-27 22:15:32 INFO Station search: 52.3737, 4.8885, radius 5.0 km → found 1 stations
```

---

## 📋 Troubleshooting Checklist

| Check | Expected | If Not | Fix |
|-------|----------|--------|-----|
| Integration appears in config flow | ✅ Yes | Generic error | Restart HA, clear cache |
| Geocoding works | ✅ Shows coordinates | "Geocoding failed" | Check network, try more specific address |
| Station search runs | ✅ Log shows results | No logs appear | Check internet, WMS coverage at coordinates |
| Sensors created | ✅ Devices appear | Empty setup | 0 stations found - test with `test_your_location.py` |
| Sensors show status | ✅ Available/Not Available | Empty/Unknown | Wait for first update (~30 sec) |

---

## 🧪 Pre-Testing (Before Docker Restart)

Test your address works:

```bash
python3 test_your_location.py 52.3737 4.8885
# Expected: ✅ SUCCESS - Found 1 charging station(s)!
```

If that works, the integration should work too.

---

## 📝 What Changed

**Before (broken):**
```json
"""String resources for Oplaadpalen integration."""
{
  "config": { ... }
```

**After (fixed):**
```json
{
  "config": { ... }
}
```

Home Assistant's JSON parser couldn't handle the docstring, causing silent setup failure.

---

## ❓ Still Not Working?

Try these steps:

1. **Clear Docker volume** (⚠️ Destructive):
   ```bash
   docker-compose down -v
   docker-compose up -d
   ```

2. **Check HA logs for Python errors:**
   ```bash
   docker-compose logs ha | grep -i "error\|exception\|traceback" | head -20
   ```

3. **Test integration code directly:**
   ```bash
   python3 << 'EOF'
   import asyncio
   from oplaadpalen_py import OplaadpalenClient
   import aiohttp
   
   async def test():
       async with aiohttp.ClientSession() as session:
           client = OplaadpalenClient(session)
           stations = await client.get_charging_stations(52.3737, 4.8885, 5.0)
           print(f"Found {len(stations)} stations")
           for s in stations:
               print(f"  - {s.get('address', 'Unknown')}, {s.get('city', 'Unknown')}")
   
   asyncio.run(test())
   EOF
   ```

4. **Verify PyPI package versions:**
   ```bash
   pip show geopy oplaadpalen-py
   ```
   - geopy >= 2.3.0
   - oplaadpalen-py >= 0.1.0

---

## Version Info

- **Integration**: v0.1.8 (fixed)
- **Library**: 0.1.0
- **geopy**: 2.3.0+
- **Home Assistant**: 2023.12+

---

**After applying the fix and restarting, the integration should appear and work correctly!**
