"""API Client for Oplaadpalen.nl - Wrapper around oplaadpalen_py library."""
import logging
from typing import Any

from aiohttp import ClientSession
from oplaadpalen_py import OplaadpalenClient

_LOGGER = logging.getLogger(__name__)


class OplaadpalenAPI:
    """Wrapper around OplaadpalenClient for Home Assistant integration."""

    def __init__(self, session: ClientSession):
        """Initialize the API client using the oplaadpalen_py library."""
        self.client = OplaadpalenClient(session)

    async def get_charging_stations(
        self, latitude: float, longitude: float, radius_km: float = 5.0
    ) -> list[dict[str, Any]]:
        """Get charging stations near the given coordinates.
        
        Uses the oplaadpalen_py library which handles WMS and Detail API calls.
        """
        try:
            _LOGGER.debug(
                "Fetching stations: lat=%.4f lon=%.4f radius=%.1f km",
                latitude, longitude, radius_km
            )
            result = await self.client.get_charging_stations(latitude, longitude, radius_km)
            _LOGGER.debug("Fetched %d charging stations", len(result))
            return result
        except Exception as err:
            _LOGGER.error("Failed to fetch charging stations: %s", err)
            return []

    async def get_station_details_by_reference(
        self, external_reference: str
    ) -> dict[str, Any] | None:
        """Get detailed information about a charging station by its external reference."""
        try:
            return await self.client.get_station_details(external_reference)
        except Exception as err:
            _LOGGER.error("Failed to get station details: %s", err)
            return None
