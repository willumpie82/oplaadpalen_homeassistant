"""Pytest configuration and fixtures for Oplaadpalen tests."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiohttp import ClientSession


@pytest.fixture
def mock_session():
    """Create a mock aiohttp session."""
    session = AsyncMock(spec=ClientSession)
    return session


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = MagicMock()
    hass.async_add_executor_job = AsyncMock()
    hass.data = {}
    hass.helpers = MagicMock()
    hass.helpers.aiohttp_client = MagicMock()
    hass.helpers.aiohttp_client.async_get_clientsession = AsyncMock(return_value=AsyncMock(spec=ClientSession))
    return hass


@pytest.fixture
def sample_wms_response():
    """Sample WMS API response with external references."""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "external_reference": "400b80f85597c2dc211ef83e942010aa"
                }
            }
        ]
    }


@pytest.fixture
def sample_detail_response():
    """Sample detail API response."""
    return {
        "status_code": 1000,
        "status_message": "OK",
        "data": {
            "address": "Jacob Cnodestraat 23",
            "city": "'s-Hertogenbosch",
            "postal_code": "5223 HS",
            "country": "NLD",
            "evses": [
                {
                    "status": "AVAILABLE",
                    "connectors": [
                        {
                            "standard": "IEC_62196_T2",
                            "format": "SOCKET",
                            "pricing_id": "4f2bcd8f14b29279e534e8d7f4bff3da",
                            "max_power": 11000
                        }
                    ]
                },
                {
                    "status": "OCCUPIED",
                    "connectors": [
                        {
                            "standard": "IEC_62196_T2",
                            "format": "SOCKET",
                            "pricing_id": "4f2bcd8f14b29279e534e8d7f4bff3da",
                            "max_power": 11000
                        }
                    ]
                }
            ],
            "operator": {
                "name": "Vattenfall InCharge",
                "website": "http://vattenfall.nl"
            },
            "access_type": "Public",
            "support_phone_number": "+(31)-(88)-3637991"
        }
    }


@pytest.fixture
def sample_station_data(sample_detail_response):
    """Sample station data after processing."""
    data = sample_detail_response["data"]
    return {
        "external_reference": "400b80f85597c2dc211ef83e942010aa",
        **data
    }
