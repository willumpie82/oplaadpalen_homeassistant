"""Oplaadpalen.nl integration for Home Assistant."""
import asyncio
import logging
from typing import Final

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

# Check for required dependencies
try:
    import geopy
    import oplaadpalen_py
except ImportError as err:
    raise ImportError(
        "oplaadpalen integration requires 'geopy' and 'oplaadpalen-py' packages. "
        "These should be installed automatically, but they're missing. "
        "Try uninstalling and reinstalling the integration, or install them manually via pip: "
        "pip install geopy>=2.3.0 oplaadpalen-py>=0.1.0"
    ) from err

_LOGGER: logging.Logger = logging.getLogger(__name__)

# Log that the module was imported
_LOGGER.warning("🚀 OPLAADPALEN MODULE IMPORTED - Version 0.1.14")

DOMAIN: Final = "oplaadpalen"
PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR]

UPDATE_INTERVAL_DEFAULT = 300  # 5 minutes


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Oplaadpalen from a config entry."""
    _LOGGER.warning("⚡ ASYNC_SETUP_ENTRY CALLED - Entry: %s", entry.entry_id)
    
    hass.data.setdefault(DOMAIN, {})
    
    # Store the entry
    hass.data[DOMAIN][entry.entry_id] = entry.data
    
    # Setup platforms
    try:
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    except Exception as e:
        _LOGGER.error("Failed to setup platforms for entry %s: %s", entry.entry_id, e, exc_info=True)
        return False
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok
