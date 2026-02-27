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

DOMAIN: Final = "oplaadpalen"
PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR]

UPDATE_INTERVAL_DEFAULT = 300  # 5 minutes


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Oplaadpalen from a config entry."""
    _LOGGER.info("Setting up Oplaadpalen entry: %s", entry.entry_id)
    
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
