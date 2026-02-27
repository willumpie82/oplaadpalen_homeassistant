"""Tests for Oplaadpalen config flow."""
import pytest
from unittest.mock import AsyncMock, patch
from homeassistant.data_entry_flow import FlowResult

from custom_components.oplaadpalen.config_flow import (
    OplaadpalenConfigFlow,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_ADDRESS,
    CONF_RADIUS,
    CONF_UPDATE_INTERVAL,
)


@pytest.mark.asyncio
async def test_config_flow_with_coordinates(mock_hass):
    """Test configuration flow with coordinates."""
    flow = OplaadpalenConfigFlow()
    flow.hass = mock_hass
    
    user_input = {
        "name": "Test Location",
        CONF_LATITUDE: "52.37403",
        CONF_LONGITUDE: "4.88969",
        CONF_RADIUS: 5.0,
        CONF_UPDATE_INTERVAL: 300,
    }
    
    with patch.object(flow, "async_set_unique_id"):
        with patch.object(flow, "_abort_if_unique_id_configured"):
            with patch.object(flow, "async_create_entry") as mock_create:
                mock_create.return_value = FlowResult
                
                result = await flow.async_step_user(user_input)
                
                # Verify create_entry was called
                assert mock_create.called


@pytest.mark.asyncio
async def test_config_flow_with_address(mock_hass):
    """Test configuration flow with address geocoding."""
    flow = OplaadpalenConfigFlow()
    flow.hass = mock_hass
    
    mock_location = AsyncMock()
    mock_location.latitude = 52.37403
    mock_location.longitude = 4.88969
    
    user_input = {
        "name": "Test Location",
        CONF_ADDRESS: "Amsterdam, Netherlands",
        CONF_RADIUS: 5.0,
        CONF_UPDATE_INTERVAL: 300,
    }
    
    with patch("custom_components.oplaadpalen.config_flow.Nominatim") as mock_geo:
        mock_geocoder = AsyncMock()
        mock_geocoder.geocode = AsyncMock(return_value=mock_location)
        mock_geo.return_value = mock_geocoder
        
        with patch.object(flow, "async_set_unique_id"):
            with patch.object(flow, "_abort_if_unique_id_configured"):
                with patch.object(flow, "async_create_entry") as mock_create:
                    mock_create.return_value = FlowResult
                    mock_hass.async_add_executor_job = AsyncMock(return_value=mock_location)
                    
                    result = await flow.async_step_user(user_input)
                    
                    # Verify create_entry was called
                    assert mock_create.called


@pytest.mark.asyncio
async def test_config_flow_invalid_coordinates(mock_hass):
    """Test configuration flow with invalid coordinates."""
    flow = OplaadpalenConfigFlow()
    flow.hass = mock_hass
    
    user_input = {
        "name": "Test Location",
        CONF_LATITUDE: "invalid",
        CONF_LONGITUDE: "4.88969",
        CONF_RADIUS: 5.0,
        CONF_UPDATE_INTERVAL: 300,
    }
    
    result = await flow.async_step_user(user_input)
    
    # Should show form with errors
    assert result["type"] == "form"
    assert "base" in result.get("errors", {})


@pytest.mark.asyncio
async def test_config_flow_invalid_radius(mock_hass):
    """Test configuration flow with invalid radius."""
    flow = OplaadpalenConfigFlow()
    flow.hass = mock_hass
    
    user_input = {
        "name": "Test Location",
        CONF_LATITUDE: "52.37403",
        CONF_LONGITUDE: "4.88969",
        CONF_RADIUS: 150.0,  # Too large
        CONF_UPDATE_INTERVAL: 300,
    }
    
    result = await flow.async_step_user(user_input)
    
    # Should show form with errors
    assert result["type"] == "form"
    assert "base" in result.get("errors", {})


@pytest.mark.asyncio
async def test_config_flow_geocoding_failed(mock_hass):
    """Test configuration flow with failed geocoding."""
    flow = OplaadpalenConfigFlow()
    flow.hass = mock_hass
    
    user_input = {
        "name": "Test Location",
        CONF_ADDRESS: "Invalid Address XYZ",
        CONF_RADIUS: 5.0,
        CONF_UPDATE_INTERVAL: 300,
    }
    
    with patch("custom_components.oplaadpalen.config_flow.Nominatim") as mock_geo:
        mock_geocoder = AsyncMock()
        mock_geocoder.geocode = AsyncMock(return_value=None)
        mock_geo.return_value = mock_geocoder
        mock_hass.async_add_executor_job = AsyncMock(return_value=None)
        
        result = await flow.async_step_user(user_input)
        
        # Should show form with errors
        assert result["type"] == "form"
        assert "base" in result.get("errors", {})


@pytest.mark.asyncio
async def test_config_flow_options(mock_hass):
    """Test configuration flow options."""
    from homeassistant.config_entries import ConfigEntry
    
    config_entry = ConfigEntry(
        version=1,
        domain="oplaadpalen",
        title="Test",
        data={
            CONF_RADIUS: 5.0,
            CONF_UPDATE_INTERVAL: 300,
        },
        source="user",
    )
    
    from custom_components.oplaadpalen.config_flow import OplaadpalenOptionsFlow
    
    flow = OplaadpalenOptionsFlow(config_entry)
    flow.hass = mock_hass
    
    user_input = {
        CONF_RADIUS: 10.0,
        CONF_UPDATE_INTERVAL: 600,
    }
    
    with patch.object(flow, "async_create_entry") as mock_create:
        mock_create.return_value = FlowResult
        
        result = await flow.async_step_init(user_input)
        
        # Verify create_entry was called
        assert mock_create.called
