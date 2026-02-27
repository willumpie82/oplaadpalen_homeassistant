"""Tests for Oplaadpalen coordinator."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.oplaadpalen.coordinator import OplaadpalenCoordinator


@pytest.mark.asyncio
async def test_coordinator_update_success(mock_hass, mock_session, sample_wms_response, sample_detail_response):
    """Test successful coordinator update."""
    coordinator = OplaadpalenCoordinator(
        hass=mock_hass,
        session=mock_session,
        latitude=52.37403,
        longitude=4.88969,
        radius=5.0,
        update_interval=300,
    )
    
    # Mock API responses
    wms_resp = AsyncMock()
    wms_resp.status = 200
    wms_resp.json = AsyncMock(return_value=sample_wms_response)
    
    detail_resp = AsyncMock()
    detail_resp.status = 200
    detail_resp.json = AsyncMock(return_value=sample_detail_response)
    
    mock_session.get = AsyncMock(side_effect=[wms_resp, detail_resp])
    
    data = await coordinator._async_update_data()
    
    assert data is not None
    assert "stations" in data
    assert len(data["stations"]) == 1
    assert data["stations"][0]["address"] == "Jacob Cnodestraat 23"


@pytest.mark.asyncio
async def test_coordinator_update_error(mock_hass, mock_session):
    """Test coordinator update with error."""
    coordinator = OplaadpalenCoordinator(
        hass=mock_hass,
        session=mock_session,
        latitude=52.37403,
        longitude=4.88969,
        radius=5.0,
        update_interval=300,
    )
    
    mock_session.get = AsyncMock(side_effect=Exception("API Error"))
    
    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()


def test_coordinator_initialization(mock_hass, mock_session):
    """Test coordinator initialization."""
    coordinator = OplaadpalenCoordinator(
        hass=mock_hass,
        session=mock_session,
        latitude=52.37403,
        longitude=4.88969,
        radius=5.0,
        update_interval=300,
    )
    
    assert coordinator.latitude == 52.37403
    assert coordinator.longitude == 4.88969
    assert coordinator.radius == 5.0


def test_coordinator_default_interval(mock_hass, mock_session):
    """Test coordinator with default update interval."""
    coordinator = OplaadpalenCoordinator(
        hass=mock_hass,
        session=mock_session,
        latitude=52.37403,
        longitude=4.88969,
        radius=5.0,
    )
    
    # Default should be 300 seconds
    from datetime import timedelta
    assert coordinator.update_interval == timedelta(seconds=300)
