#!/bin/bash
# Debug HA integration loading

echo "=== Checking integration folder structure ==="
find custom_components/oplaadpalen -type f -name "*.py" | head -20

echo ""
echo "=== Checking manifest.json syntax ==="
python3 -m json.tool custom_components/oplaadpalen/manifest.json

echo ""
echo "=== Checking imports by testing library install ==="
python3 << 'PYEOF'
import sys
try:
    print("✅ Checking geopy...")
    import geopy
    print(f"   geopy version: {geopy.__version__}")
except ImportError as e:
    print(f"❌ geopy not installed: {e}")

try:
    print("✅ Checking oplaadpalen_py...")
    from oplaadpalen_py import OplaadpalenClient
    print(f"   oplaadpalen_py imported successfully")
except ImportError as e:
    print(f"❌ oplaadpalen_py not installed: {e}")

try:
    print("✅ Checking homeassistant...")
    from homeassistant import config_entries
    print(f"   homeassistant available")
except ImportError as e:
    print(f"   (homeassistant not in this env - normal)") 

PYEOF

echo ""
echo "=== Checking for Python syntax errors ==="
python3 -m py_compile custom_components/oplaadpalen/__init__.py && echo "✅ __init__.py" || echo "❌ __init__.py"
python3 -m py_compile custom_components/oplaadpalen/config_flow.py && echo "✅ config_flow.py" || echo "❌ config_flow.py"
python3 -m py_compile custom_components/oplaadpalen/binary_sensor.py && echo "✅ binary_sensor.py" || echo "❌ binary_sensor.py"
python3 -m py_compile custom_components/oplaadpalen/coordinator.py && echo "✅ coordinator.py" || echo "❌ coordinator.py"
python3 -m py_compile custom_components/oplaadpalen/api.py && echo "✅ api.py" || echo "❌ api.py"

echo ""
echo "=== Git status ==="
git log --oneline -3
