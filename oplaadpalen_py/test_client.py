"""Tests for Oplaadpalen Python Client Library."""
import pytest
from unittest.mock import AsyncMock, MagicMock
import aiohttp

from oplaadpalen_py import OplaadpalenClient


@pytest.fixture
def mock_session():
    """Create a mock aiohttp session."""
    session = AsyncMock(spec=aiohttp.ClientSession)
    return session


@pytest.fixture
def sample_wms_response():
    """Sample WMS API response."""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "external_reference": "ref_123"
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
            "address": "Test Street 1",
            "city": "Amsterdam",
            "postal_code": "1000 AA",
            "country": "NLD",
            "evses": [
                {
                    "status": "AVAILABLE",
                    "connectors": [
                        {
                            "standard": "IEC_62196_T2",
                            "format": "SOCKET",
                            "max_power": 11000
                        }
                    ]
                }
            ],
            "operator": {
                "name": "Test Operator",
                "website": "http://test.nl"
            },
            "access_type": "Public",
            "support_phone_number": "+31123456789"
        }
    }


@pytest.mark.asyncio
async def test_get_charging_stations_success(mock_session, sample_wms_response, sample_detail_response):
    """Test successful charging station retrieval."""
    client = OplaadpalenClient(mock_session)
    
    # Mock responses
    wms_resp = AsyncMock()
    wms_resp.status = 200
    wms_resp.json = AsyncMock(return_value=sample_wms_response)
    
    detail_resp = AsyncMock()
    detail_resp.status = 200
    detail_resp.json = AsyncMock(return_value=sample_detail_response)
    
    mock_session.get = AsyncMock(side_effect=[wms_resp, detail_resp])
    
    result = await client.get_charging_stations(52.37403, 4.88969, 5.0)
    
    assert len(result) == 1
    assert result[0]["address"] == "Test Street 1"
    assert result[0]["city"] == "Amsterdam"
    assert result[0]["external_reference"] == "ref_123"


@pytest.mark.asyncio
async def test_get_charging_stations_invalid_latitude(mock_session):
    """Test with invalid latitude."""
    client = OplaadpalenClient(mock_session)
    
    with pytest.raises(ValueError, match="Latitude must be between"):
        await client.get_charging_stations(91.0, 4.88969, 5.0)


@pytest.mark.asyncio
async def test_get_charging_stations_invalid_longitude(mock_session):
    """Test with invalid longitude."""
    client = OplaadpalenClient(mock_session)
    
    with pytest.raises(ValueError, match="Longitude must be between"):
        await client.get_charging_stations(52.37403, 181.0, 5.0)


@pytest.mark.asyncio
async def test_get_charging_stations_invalid_radius(mock_session):
    """Test with invalid radius."""
    client = OplaadpalenClient(mock_session)
    
    with pytest.raises(ValueError, match="Radius must be between"):
        await client.get_charging_stations(52.37403, 4.88969, 150.0)


@pytest.mark.asyncio
async def test_get_charging_stations_api_error(mock_session):
    """Test handling of API error."""
    client = OplaadpalenClient(mock_session)
    
    resp = AsyncMock()
    resp.status = 500
    mock_session.get = AsyncMock(return_value=resp)
    
    result = await client.get_charging_stations(52.37403, 4.88969, 5.0)
    
    assert result == []


@pytest.mark.asyncio
async def test_get_charging_stations_network_error(mock_session):
    """Test handling of network error."""
    client = OplaadpalenClient(mock_session)
    
    mock_session.get = AsyncMock(side_effect=aiohttp.ClientError("Network error"))
    
    result = await client.get_charging_stations(52.37403, 4.88969, 5.0)
    
    assert result == []


@pytest.mark.asyncio
async def test_get_station_details_success(mock_session, sample_detail_response):
    """Test successful station detail retrieval."""
    client = OplaadpalenClient(mock_session)
    
    resp = AsyncMock()
    resp.status = 200
    resp.json = AsyncMock(return_value=sample_detail_response)
    
    mock_session.get = AsyncMock(return_value=resp)
    
    result = await client.get_station_details("ref_123")
    
    assert result is not None
    assert result["address"] == "Test Street 1"
    assert result["external_reference"] == "ref_123"


@pytest.mark.asyncio
async def test_get_station_details_empty_reference():
    """Test with empty reference."""
    client = OplaadpalenClient(None)
    
    with pytest.raises(ValueError, match="external_reference cannot be empty"):
        await client.get_station_details("")


@pytest.mark.asyncio
async def test_get_station_details_not_found(mock_session):
    """Test when station is not found."""
    client = OplaadpalenClient(mock_session)
    
    resp = AsyncMock()
    resp.status = 404
    mock_session.get = AsyncMock(return_value=resp)
    
    result = await client.get_station_details("invalid_ref")
    
    assert result is None


@pytest.mark.asyncio
async def test_context_manager_creates_session():
    """Test context manager creates own session."""
    async with OplaadpalenClient() as client:
        assert client.session is not None
        assert client._own_session is True


@pytest.mark.asyncio
async def test_no_session_error():
    """Test error when no session available."""
    client = OplaadpalenClient(None)
    
    with pytest.raises(RuntimeError, match="No session available"):
        await client.get_charging_stations(52.37403, 4.88969, 5.0)


@pytest.mark.asyncio
async def test_bounding_box_calculation(mock_session):
    """Test bounding box calculations are made correctly."""
    client = OplaadpalenClient(mock_session)
    
    resp = AsyncMock()
    resp.status = 200
    resp.json = AsyncMock(return_value={"features": []})
    
    mock_session.get = AsyncMock(return_value=resp)
    
    await client.get_charging_stations(50.0, 10.0, 5.0)
    
    # Verify get was called
    assert mock_session.get.called
    
    call_args = mock_session.get.call_args
    params = call_args.kwargs.get('params')
    
    assert params is not None
    assert 'BBOX' in params
    
    # Parse BBOX
    bbox_parts = params['BBOX'].split(',')
    assert len(bbox_parts) == 4
    
    # Verify bounds are reasonable (±0.1 degrees for 5km at equator)
    min_lon, min_lat, max_lon, max_lat = [float(x) for x in bbox_parts]
    assert min_lon < 10.0 < max_lon
    assert min_lat < 50.0 < max_lat


@pytest.mark.asyncio
async def test_invalid_api_response(mock_session):
    """Test handling of invalid API response."""
    client = OplaadpalenClient(mock_session)
    
    resp = AsyncMock()
    resp.status = 200
    resp.json = AsyncMock(return_value={
        "status_code": 2000,
        "status_message": "Error"
    })
    
    mock_session.get = AsyncMock(return_value=resp)
    
    result = await client.get_station_details("ref_123")
    
    assert result is None


@pytest.mark.asyncio
async def test_multiple_stations(mock_session):
    """Test retrieval of multiple stations."""
    client = OplaadpalenClient(mock_session)
    
    wms_response = {
        "features": [
            {
                "properties": {"external_reference": "ref_1"}
            },
            {
                "properties": {"external_reference": "ref_2"}
            }
        ]
    }
    
    detail_response_1 = {
        "status_code": 1000,
        "data": {
            "address": "Station 1",
            "city": "Amsterdam",
            "evses": []
        }
    }
    
    detail_response_2 = {
        "status_code": 1000,
        "data": {
            "address": "Station 2",
            "city": "Rotterdam",
            "evses": []
        }
    }
    
    wms_resp = AsyncMock()
    wms_resp.status = 200
    wms_resp.json = AsyncMock(return_value=wms_response)
    
    detail_resp_1 = AsyncMock()
    detail_resp_1.status = 200
    detail_resp_1.json = AsyncMock(return_value=detail_response_1)
    
    detail_resp_2 = AsyncMock()
    detail_resp_2.status = 200
    detail_resp_2.json = AsyncMock(return_value=detail_response_2)
    
    mock_session.get = AsyncMock(side_effect=[wms_resp, detail_resp_1, detail_resp_2])
    
    result = await client.get_charging_stations(52.37403, 4.88969, 5.0)
    
    assert len(result) == 2
    assert result[0]["address"] == "Station 1"
    assert result[1]["address"] == "Station 2"
