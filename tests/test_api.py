"""Tests for Oplaadpalen API client."""
import pytest
from unittest.mock import AsyncMock, patch
from aiohttp import ClientError

from custom_components.oplaadpalen.api import OplaadpalenAPI


@pytest.mark.asyncio
async def test_get_charging_stations_success(mock_session, sample_wms_response, sample_detail_response):
    """Test successful charging station retrieval."""
    api = OplaadpalenAPI(mock_session)
    
    # Mock WMS response
    wms_resp = AsyncMock()
    wms_resp.status = 200
    wms_resp.json = AsyncMock(return_value=sample_wms_response)
    
    # Mock detail API response
    detail_resp = AsyncMock()
    detail_resp.status = 200
    detail_resp.json = AsyncMock(return_value=sample_detail_response)
    
    mock_session.get = AsyncMock(side_effect=[wms_resp, detail_resp])
    
    result = await api.get_charging_stations(52.37403, 4.88969, 5.0)
    
    assert len(result) == 1
    assert result[0]["address"] == "Jacob Cnodestraat 23"
    assert result[0]["external_reference"] == "400b80f85597c2dc211ef83e942010aa"
    assert len(result[0]["evses"]) == 2


@pytest.mark.asyncio
async def test_get_charging_stations_wms_error(mock_session):
    """Test handling of WMS API error."""
    api = OplaadpalenAPI(mock_session)
    
    resp = AsyncMock()
    resp.status = 500
    mock_session.get = AsyncMock(return_value=resp)
    
    result = await api.get_charging_stations(52.37403, 4.88969, 5.0)
    
    assert result == []


@pytest.mark.asyncio
async def test_get_charging_stations_network_error(mock_session):
    """Test handling of network error."""
    api = OplaadpalenAPI(mock_session)
    
    mock_session.get = AsyncMock(side_effect=ClientError("Network error"))
    
    result = await api.get_charging_stations(52.37403, 4.88969, 5.0)
    
    assert result == []


@pytest.mark.asyncio
async def test_get_station_details_by_reference_success(mock_session, sample_detail_response):
    """Test successful station detail retrieval."""
    api = OplaadpalenAPI(mock_session)
    
    resp = AsyncMock()
    resp.status = 200
    resp.json = AsyncMock(return_value=sample_detail_response)
    
    mock_session.get = AsyncMock(return_value=resp)
    
    result = await api.get_station_details_by_reference("400b80f85597c2dc211ef83e942010aa")
    
    assert result is not None
    assert result["address"] == "Jacob Cnodestraat 23"
    assert result["external_reference"] == "400b80f85597c2dc211ef83e942010aa"


@pytest.mark.asyncio
async def test_get_station_details_by_reference_failure(mock_session):
    """Test failed station detail retrieval."""
    api = OplaadpalenAPI(mock_session)
    
    resp = AsyncMock()
    resp.status = 404
    mock_session.get = AsyncMock(return_value=resp)
    
    result = await api.get_station_details_by_reference("invalid_ref")
    
    assert result is None


@pytest.mark.asyncio
async def test_get_station_details_by_reference_invalid_status(mock_session):
    """Test handling of invalid status code in response."""
    api = OplaadpalenAPI(mock_session)
    
    resp = AsyncMock()
    resp.status = 200
    resp.json = AsyncMock(return_value={"status_code": 2000, "status_message": "Error"})
    
    mock_session.get = AsyncMock(return_value=resp)
    
    result = await api.get_station_details_by_reference("400b80f85597c2dc211ef83e942010aa")
    
    assert result is None


@pytest.mark.asyncio
async def test_bounding_box_calculation(mock_session):
    """Test that bounding box is calculated correctly."""
    api = OplaadpalenAPI(mock_session)
    
    resp = AsyncMock()
    resp.status = 200
    resp.json = AsyncMock(return_value={"features": []})
    
    mock_session.get = AsyncMock(return_value=resp)
    
    await api.get_charging_stations(50.0, 10.0, 5.0)
    
    # Verify get was called
    assert mock_session.get.called
    
    # Get the call args
    call_args = mock_session.get.call_args
    params = call_args.kwargs.get('params')
    
    assert params is not None
    assert 'BBOX' in params
    # BBOX format: minlon,minlat,maxlon,maxlat
    bbox_parts = params['BBOX'].split(',')
    assert len(bbox_parts) == 4
