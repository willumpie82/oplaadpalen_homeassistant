"""API Client for Oplaadpalen.nl."""
import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)

WMS_URL = "https://www.oplaadpalen.nl/wms"
DETAIL_API_URL = "https://www.oplaadpalen.nl/api/map/location"


class OplaadpalenAPI:
    """API client for Oplaadpalen.nl WMS and Detail APIs."""

    def __init__(self, session: aiohttp.ClientSession):
        """Initialize the API client."""
        self.session = session

    async def get_charging_stations(
        self, latitude: float, longitude: float, radius_km: float = 5.0
    ) -> list[dict[str, Any]]:
        """Get charging stations near the given coordinates from WMS API."""
        # Calculate bounding box (rough approximation)
        # 1 degree latitude ≈ 111 km
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

        try:
            async with self.session.get(WMS_URL, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    features = data.get("features", [])
                    
                    # Fetch detailed information for each station
                    stations_with_details = []
                    for feature in features:
                        external_ref = feature.get("properties", {}).get("external_reference")
                        if external_ref:
                            details = await self.get_station_details_by_reference(external_ref)
                            if details:
                                stations_with_details.append(details)
                    
                    return stations_with_details
                else:
                    _LOGGER.error("API error: HTTP %s", resp.status)
                    return []
        except aiohttp.ClientError as err:
            _LOGGER.error("API request failed: %s", err)
            return []
        except Exception as err:
            _LOGGER.error("Unexpected error: %s", err)
            return []

    async def get_station_details_by_reference(
        self, external_reference: str
    ) -> dict[str, Any] | None:
        """Get detailed information about a charging station by its external reference."""
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
                        _LOGGER.warning("API returned status code: %s", data.get("status_code"))
                        return None
                else:
                    _LOGGER.error("Detail API error: HTTP %s", resp.status)
                    return None
        except aiohttp.ClientError as err:
            _LOGGER.error("Detail API request failed: %s", err)
            return None
        except Exception as err:
            _LOGGER.error("Failed to get station details: %s", err)
            return None
