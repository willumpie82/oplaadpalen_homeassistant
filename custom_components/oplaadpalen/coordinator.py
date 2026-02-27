"""Coordinator for Oplaadpalen integration."""
import logging
from datetime import timedelta
from typing import Any

from aiohttp import ClientSession

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import OplaadpalenAPI

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL_DEFAULT = 300  # 5 minutes


class OplaadpalenCoordinator(DataUpdateCoordinator):
    """Coordinator for Oplaadpalen data updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        session: ClientSession,
        latitude: float,
        longitude: float,
        radius: float = 5.0,
        update_interval: int = UPDATE_INTERVAL_DEFAULT,
    ):
        """Initialize the coordinator."""
        self.api = OplaadpalenAPI(session)
        self.latitude = latitude
        self.longitude = longitude
        self.radius = radius

        super().__init__(
            hass,
            _LOGGER,
            name="Oplaadpalen",
            update_interval=timedelta(seconds=update_interval),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        try:
            stations = await self.api.get_charging_stations(
                self.latitude, self.longitude, self.radius
            )
            return {
                "stations": stations,
                "count": len(stations),
                "latitude": self.latitude,
                "longitude": self.longitude,
            }
        except Exception as err:
            raise UpdateFailed(f"Failed to fetch Oplaadpalen data: {err}") from err
