"""Oplaadpalen API Client - No external dependencies (only aiohttp)."""
import logging
from typing import Any, Optional

import aiohttp

_LOGGER = logging.getLogger(__name__)

WMS_URL = "https://www.oplaadpalen.nl/wms"
DETAIL_API_URL = "https://www.oplaadpalen.nl/api/map/location"


class OplaadpalenClient:
    """Python client for Oplaadpalen.nl API."""

    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        """Initialize the client.
        
        Args:
            session: Optional aiohttp ClientSession. If not provided, a new one will be created.
        """
        self.session = session
        self._own_session = False

    async def __aenter__(self):
        """Async context manager entry."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
            self._own_session = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._own_session and self.session:
            await self.session.close()

    async def get_charging_stations(
        self, latitude: float, longitude: float, radius_km: float = 5.0
    ) -> list[dict[str, Any]]:
        """Get charging stations near the given coordinates.
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            radius_km: Search radius in kilometers (default: 5.0)
            
        Returns:
            List of station dictionaries with detailed information
            
        Raises:
            ValueError: If coordinates or radius are invalid
            aiohttp.ClientError: If API request fails
        """
        # Validate inputs
        if not (-90 <= latitude <= 90):
            raise ValueError(f"Latitude must be between -90 and 90, got {latitude}")
        if not (-180 <= longitude <= 180):
            raise ValueError(f"Longitude must be between -180 and 180, got {longitude}")
        if radius_km < 0.1 or radius_km > 100:
            raise ValueError(f"Radius must be between 0.1 and 100 km, got {radius_km}")

        # Calculate bounding box
        lat_offset = radius_km / 111.0
        lon_offset = radius_km / (111.0 * (0.7 + 0.3 * abs(latitude) / 90))

        bbox = f"{longitude - lon_offset},{latitude - lat_offset},{longitude + lon_offset},{latitude + lat_offset}"

        params = {
            "REQUEST": "GetFeatureInfo",
            "SERVICE": "WMS",
            "SRS": "EPSG:4326",
            "VERSION": "1.1.1",
            "INFO_FORMAT": "application/json",
            "BBOX": bbox,
            "HEIGHT": "500",
            "WIDTH": "500",
            "LAYERS": "eco:rta_and_clusters",
            "QUERY_LAYERS": "eco:rta_and_clusters",
            "X": "250",
            "Y": "250",
        }

        if self.session is None:
            raise RuntimeError("No session available. Use as async context manager or provide session.")

        try:
            async with self.session.get(WMS_URL, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    features = data.get("features", [])
                    _LOGGER.info(f"WMS API returned {len(features)} features")
                    
                    # Fetch detailed information for each station
                    stations_with_details = []
                    for feature in features:
                        external_ref = feature.get("properties", {}).get("external_reference")
                        if external_ref:
                            details = await self.get_station_details(external_ref)
                            if details:
                                stations_with_details.append(details)
                            else:
                                _LOGGER.info(f"No details for reference {external_ref}")
                    
                    _LOGGER.info(f"Returning {len(stations_with_details)} stations with details")
                    return stations_with_details
                else:
                    _LOGGER.error("WMS API error: HTTP %s", resp.status)
                    return []
        except aiohttp.ClientError as err:
            _LOGGER.error("WMS API request failed: %s", err)
            return []
        except Exception as err:
            _LOGGER.error("Unexpected error fetching stations: %s", err)
            return []

    async def get_station_details(self, external_reference: str) -> Optional[dict[str, Any]]:
        """Get detailed information about a charging station.
        
        Args:
            external_reference: Station external reference ID
            
        Returns:
            Station data dictionary or None if request fails
            
        Raises:
            aiohttp.ClientError: If API request fails
        """
        if not external_reference:
            raise ValueError("external_reference cannot be empty")

        if self.session is None:
            raise RuntimeError("No session available. Use as async context manager or provide session.")

        try:
            url = f"{DETAIL_API_URL}/{external_reference}"
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("status_code") == 1000 and "data" in data:
                        return {
                            "external_reference": external_reference,
                            **data["data"]
                        }
                    else:
                        _LOGGER.warning(
                            "Detail API returned status code: %s for reference %s",
                            data.get("status_code"),
                            external_reference
                        )
                        return None
                else:
                    _LOGGER.error("Detail API error for %s: HTTP %s", external_reference, resp.status)
                    return None
        except aiohttp.ClientError as err:
            _LOGGER.error("Detail API request failed for %s: %s", external_reference, err)
            return None
        except Exception as err:
            _LOGGER.error("Unexpected error fetching station details: %s", err)
            return None
