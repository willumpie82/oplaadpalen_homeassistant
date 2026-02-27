"""Binary sensor platform for Oplaadpalen integration."""
import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN
from .config_flow import CONF_LATITUDE, CONF_LONGITUDE, CONF_RADIUS, CONF_UPDATE_INTERVAL
from .coordinator import OplaadpalenCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up binary sensors for Oplaadpalen."""
    try:
        coordinator = OplaadpalenCoordinator(
            hass,
            async_get_clientsession(hass),
            latitude=entry.data[CONF_LATITUDE],
            longitude=entry.data[CONF_LONGITUDE],
            radius=entry.data.get(CONF_RADIUS, 5.0),
            update_interval=entry.data.get(CONF_UPDATE_INTERVAL, 300),
        )
        
        await coordinator.async_config_entry_first_refresh()
        
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][entry.entry_id] = coordinator
        
        entities = []
        
        if coordinator.data and "stations" in coordinator.data:
            stations = coordinator.data["stations"]
            if stations:
                for station_idx, station in enumerate(stations):
                    station_name = station.get("address", f"Station {station_idx}")
                    city = station.get("city", "")
                    if city:
                        station_name = f"{station_name}, {city}"
                    
                    evses = station.get("evses", [])
                    
                    for evse_idx, evse in enumerate(evses):
                        status = evse.get("status", "UNKNOWN")
                        
                        connectors = evse.get("connectors", [])
                        connector_info = ""
                        if connectors:
                            connector_types = [c.get("standard", "Unknown") for c in connectors]
                            power = connectors[0].get("max_power", 0)
                            connector_info = f" ({', '.join(connector_types)}, {power}W)"
                        
                        entities.append(
                            OplaadpalenEVSESensor(
                                coordinator,
                                entry.entry_id,
                                station_idx=station_idx,
                                evse_idx=evse_idx,
                                station_name=station_name,
                                evse_num=evse_idx + 1,
                                connector_info=connector_info,
                                status=status,
                                station_data=station,
                                evse_data=evse,
                            )
                        )
            else:
                _LOGGER.info("⏳ No stations found yet for entry %s. Coordinator will retry on next update.", entry.entry_id)
        else:
            _LOGGER.info("⏳ Waiting for first data refresh for entry %s", entry.entry_id)
            
    except Exception as err:
        _LOGGER.error("Failed to set up binary_sensor: %s", err, exc_info=True)
        async_add_entities([], update_before_add=True)
        return
    
    async_add_entities(entities, update_before_add=True)


class OplaadpalenEVSESensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for individual EVSE (charging point)."""

    _attr_device_class = BinarySensorDeviceClass.PLUG

    def __init__(
        self,
        coordinator: OplaadpalenCoordinator,
        entry_id: str,
        station_idx: int,
        evse_idx: int,
        station_name: str,
        evse_num: int,
        connector_info: str,
        status: str,
        station_data: dict[str, Any],
        evse_data: dict[str, Any],
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entry_id = entry_id
        self.station_idx = station_idx
        self.evse_idx = evse_idx
        self.station_name = station_name
        self.evse_num = evse_num
        self.connector_info = connector_info
        self.initial_status = status
        self.station_data = station_data
        self.evse_data = evse_data

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        external_ref = self.station_data.get("external_reference", "unknown")
        return f"oplaadpalen_{self.entry_id}_{external_ref}_evse_{self.evse_idx}"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self.station_name} - EVSE {self.evse_num}{self.connector_info}"

    @property
    def is_on(self) -> bool | None:
        """Return true if EVSE is available."""
        try:
            if self.coordinator.data and "stations" in self.coordinator.data:
                stations = self.coordinator.data["stations"]
                if self.station_idx < len(stations):
                    station = stations[self.station_idx]
                    evses = station.get("evses", [])
                    
                    if self.evse_idx < len(evses):
                        evse = evses[self.evse_idx]
                        status = evse.get("status", "UNKNOWN")
                        return status == "AVAILABLE"
            return None
        except (IndexError, KeyError, TypeError):
            return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        try:
            if self.coordinator.data and "stations" in self.coordinator.data:
                stations = self.coordinator.data["stations"]
                if self.station_idx < len(stations):
                    station = stations[self.station_idx]
                    evses = station.get("evses", [])
                    
                    if self.evse_idx < len(evses):
                        evse = evses[self.evse_idx]
                        connectors = evse.get("connectors", [])
                        
                        attrs = {
                            "status": evse.get("status", "UNKNOWN"),
                            "address": station.get("address", "Unknown"),
                            "city": station.get("city", "Unknown"),
                            "postal_code": station.get("postal_code", ""),
                            "country": station.get("country", ""),
                            "operator": station.get("operator", {}).get("name", "Unknown"),
                            "access_type": station.get("access_type", "Unknown"),
                        }
                        
                        if connectors:
                            connector = connectors[0]
                            attrs.update({
                                "connector_standard": connector.get("standard", "Unknown"),
                                "connector_format": connector.get("format", "Unknown"),
                                "max_power": connector.get("max_power", 0),
                            })
                        
                        if station.get("support_phone_number"):
                            attrs["support_phone"] = station.get("support_phone_number")
                        
                        return attrs
            
            return {}
        except (IndexError, KeyError, TypeError):
            return {}
