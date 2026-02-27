"""Tests for Oplaadpalen binary sensor platform."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.oplaadpalen.binary_sensor import (
    OplaadpalenEVSESensor,
)


@pytest.fixture
def mock_coordinator(sample_station_data):
    """Create a mock coordinator."""
    coordinator = MagicMock()
    coordinator.last_update_success = True
    coordinator.data = {
        "stations": [sample_station_data],
        "count": 1,
    }
    return coordinator


@pytest.fixture
def mock_entry_id():
    """Mock entry ID."""
    return "test_entry_123"


def test_evse_sensor_creation(mock_coordinator, sample_station_data, mock_entry_id):
    """Test EVSE sensor creation."""
    sensor = OplaadpalenEVSESensor(
        coordinator=mock_coordinator,
        entry_id=mock_entry_id,
        station_idx=0,
        evse_idx=0,
        station_name="Test Station",
        evse_num=1,
        connector_info=" (IEC_62196_T2, 11000W)",
        status="AVAILABLE",
        station_data=sample_station_data,
        evse_data=sample_station_data["evses"][0],
    )
    
    assert sensor.entry_id == mock_entry_id
    assert sensor.station_idx == 0
    assert sensor.evse_idx == 0


def test_evse_sensor_unique_id(mock_coordinator, sample_station_data, mock_entry_id):
    """Test EVSE sensor unique ID generation."""
    sensor = OplaadpalenEVSESensor(
        coordinator=mock_coordinator,
        entry_id=mock_entry_id,
        station_idx=0,
        evse_idx=0,
        station_name="Test Station",
        evse_num=1,
        connector_info="",
        status="AVAILABLE",
        station_data=sample_station_data,
        evse_data=sample_station_data["evses"][0],
    )
    
    unique_id = sensor.unique_id
    
    assert unique_id is not None
    assert "test_entry_123" in unique_id
    assert "400b80f85597c2dc211ef83e942010aa" in unique_id
    assert "evse_0" in unique_id


def test_evse_sensor_name(mock_coordinator, sample_station_data, mock_entry_id):
    """Test EVSE sensor name."""
    sensor = OplaadpalenEVSESensor(
        coordinator=mock_coordinator,
        entry_id=mock_entry_id,
        station_idx=0,
        evse_idx=0,
        station_name="Jacob Cnodestraat 23, 's-Hertogenbosch",
        evse_num=1,
        connector_info=" (IEC_62196_T2, 11000W)",
        status="AVAILABLE",
        station_data=sample_station_data,
        evse_data=sample_station_data["evses"][0],
    )
    
    name = sensor.name
    
    assert "Jacob Cnodestraat 23" in name
    assert "EVSE 1" in name
    assert "IEC_62196_T2" in name


def test_evse_sensor_is_on_available(mock_coordinator, sample_station_data, mock_entry_id):
    """Test EVSE sensor state when available."""
    sensor = OplaadpalenEVSESensor(
        coordinator=mock_coordinator,
        entry_id=mock_entry_id,
        station_idx=0,
        evse_idx=0,
        station_name="Test Station",
        evse_num=1,
        connector_info="",
        status="AVAILABLE",
        station_data=sample_station_data,
        evse_data=sample_station_data["evses"][0],
    )
    
    # First EVSE is AVAILABLE
    assert sensor.is_on is True


def test_evse_sensor_is_on_occupied(mock_coordinator, sample_station_data, mock_entry_id):
    """Test EVSE sensor state when occupied."""
    sensor = OplaadpalenEVSESensor(
        coordinator=mock_coordinator,
        entry_id=mock_entry_id,
        station_idx=0,
        evse_idx=1,
        station_name="Test Station",
        evse_num=2,
        connector_info="",
        status="OCCUPIED",
        station_data=sample_station_data,
        evse_data=sample_station_data["evses"][1],
    )
    
    # Second EVSE is OCCUPIED
    assert sensor.is_on is False


def test_evse_sensor_available(mock_coordinator, sample_station_data, mock_entry_id):
    """Test EVSE sensor availability."""
    sensor = OplaadpalenEVSESensor(
        coordinator=mock_coordinator,
        entry_id=mock_entry_id,
        station_idx=0,
        evse_idx=0,
        station_name="Test Station",
        evse_num=1,
        connector_info="",
        status="AVAILABLE",
        station_data=sample_station_data,
        evse_data=sample_station_data["evses"][0],
    )
    
    assert sensor.available is True


def test_evse_sensor_unavailable(mock_coordinator, sample_station_data, mock_entry_id):
    """Test EVSE sensor unavailability."""
    mock_coordinator.last_update_success = False
    
    sensor = OplaadpalenEVSESensor(
        coordinator=mock_coordinator,
        entry_id=mock_entry_id,
        station_idx=0,
        evse_idx=0,
        station_name="Test Station",
        evse_num=1,
        connector_info="",
        status="AVAILABLE",
        station_data=sample_station_data,
        evse_data=sample_station_data["evses"][0],
    )
    
    assert sensor.available is False


def test_evse_sensor_extra_attributes(mock_coordinator, sample_station_data, mock_entry_id):
    """Test EVSE sensor extra attributes."""
    sensor = OplaadpalenEVSESensor(
        coordinator=mock_coordinator,
        entry_id=mock_entry_id,
        station_idx=0,
        evse_idx=0,
        station_name="Test Station",
        evse_num=1,
        connector_info="",
        status="AVAILABLE",
        station_data=sample_station_data,
        evse_data=sample_station_data["evses"][0],
    )
    
    attrs = sensor.extra_state_attributes
    
    assert attrs is not None
    assert attrs["status"] == "AVAILABLE"
    assert attrs["address"] == "Jacob Cnodestraat 23"
    assert attrs["city"] == "'s-Hertogenbosch"
    assert attrs["operator"] == "Vattenfall InCharge"
    assert attrs["connector_standard"] == "IEC_62196_T2"
    assert attrs["max_power"] == 11000


def test_evse_sensor_is_on_invalid_index(mock_coordinator, sample_station_data, mock_entry_id):
    """Test EVSE sensor with invalid index."""
    sensor = OplaadpalenEVSESensor(
        coordinator=mock_coordinator,
        entry_id=mock_entry_id,
        station_idx=99,  # Invalid
        evse_idx=0,
        station_name="Test Station",
        evse_num=1,
        connector_info="",
        status="AVAILABLE",
        station_data=sample_station_data,
        evse_data=sample_station_data["evses"][0],
    )
    
    # Should return None when index is invalid
    assert sensor.is_on is None


def test_evse_sensor_is_on_no_data(mock_entry_id):
    """Test EVSE sensor with no coordinator data."""
    mock_coordinator = MagicMock()
    mock_coordinator.last_update_success = True
    mock_coordinator.data = None
    
    sensor = OplaadpalenEVSESensor(
        coordinator=mock_coordinator,
        entry_id=mock_entry_id,
        station_idx=0,
        evse_idx=0,
        station_name="Test Station",
        evse_num=1,
        connector_info="",
        status="AVAILABLE",
        station_data={},
        evse_data={},
    )
    
    # Should return None when no data
    assert sensor.is_on is None
