# Unit Tests for Oplaadpalen Integration

This directory contains unit tests for the Oplaadpalen Home Assistant integration.

## Test Structure

- **test_api.py** - Tests for the API client (`OplaadpalenAPI`)
  - WMS API communication
  - Detail API communication
  - Error handling and edge cases
  - Bounding box calculations

- **test_config_flow.py** - Tests for the configuration flow
  - Configuration with coordinates
  - Address geocoding
  - Input validation
  - Options flow

- **test_binary_sensor.py** - Tests for the binary sensor platform
  - Sensor creation
  - State updates
  - Attribute handling
  - Error conditions

- **test_coordinator.py** - Tests for the data coordinator
  - Data update lifecycle
  - Error handling
  - Initialization

- **conftest.py** - Shared fixtures and test utilities
  - Mock Home Assistant instance
  - Mock aiohttp session
  - Sample API responses

## Installation

Install test dependencies:

```bash
pip install -r requirements-test.txt
```

## Running Tests

Run all tests:

```bash
pytest tests/
```

Run with verbose output:

```bash
pytest tests/ -v
```

Run with coverage report:

```bash
pytest tests/ --cov=custom_components/oplaadpalen --cov-report=html
```

Run specific test file:

```bash
pytest tests/test_api.py
```

Run specific test:

```bash
pytest tests/test_api.py::test_get_charging_stations_success
```

Using the run script:

```bash
python run_tests.py
```

## Test Coverage

The test suite aims for comprehensive coverage of:

- ✅ API client functionality
- ✅ Configuration validation
- ✅ Binary sensor state management
- ✅ Data coordinator updates
- ✅ Error handling and edge cases

## Adding New Tests

When adding new functionality:

1. Create a corresponding test file or add to existing test
2. Use the fixtures in `conftest.py` for common test data
3. Mock external dependencies (API calls, Home Assistant APIs)
4. Include both success and error cases
5. Run the test suite to ensure all tests pass

Example test structure:

```python
@pytest.mark.asyncio
async def test_new_feature(mock_hass, mock_session):
    """Test description."""
    # Setup
    # Execute
    # Assert
```

## Fixtures

### Common Fixtures (conftest.py)

- `mock_session` - Mock aiohttp ClientSession
- `mock_hass` - Mock Home Assistant instance
- `sample_wms_response` - Sample WMS API response
- `sample_detail_response` - Sample detail API response
- `sample_station_data` - Processed station data

Use these in your tests to maintain consistency and reduce boilerplate.

## CI/CD Integration

These tests can be integrated into GitHub Actions for continuous integration:

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements-test.txt
      - run: pytest tests/ --cov=custom_components/oplaadpalen
```
