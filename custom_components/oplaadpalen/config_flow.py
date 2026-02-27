"""Config flow for Oplaadpalen integration."""
import logging
from typing import Any

import voluptuous as vol
from geopy.geocoders import Nominatim
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .api import OplaadpalenAPI
from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

CONF_LATITUDE = "latitude"
CONF_LONGITUDE = "longitude"
CONF_ADDRESS = "address"
CONF_RADIUS = "radius"
CONF_UPDATE_INTERVAL = "update_interval"


class OplaadpalenConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Oplaadpalen."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        super().__init__()
        self.no_stations_context: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        info_description: str | None = None

        if user_input is not None:
            # Validate coordinates
            latitude = user_input.get(CONF_LATITUDE)
            longitude = user_input.get(CONF_LONGITUDE)
            address = user_input.get(CONF_ADDRESS)

            # If address provided, try to geocode
            if address:
                try:
                    geolocator = Nominatim(user_agent="homeassistant_oplaadpalen")
                    location = await self.hass.async_add_executor_job(
                        geolocator.geocode, address
                    )
                    if location:
                        latitude = location.latitude
                        longitude = location.longitude
                    else:
                        errors["base"] = "geocoding_failed"
                except Exception as e:
                    _LOGGER.error("Geocoding failed: %s", e)
                    errors["base"] = "geocoding_failed"

            if not errors:
                try:
                    if latitude is None or longitude is None:
                        errors["base"] = "invalid_coords"
                    else:
                        latitude = float(latitude)
                        longitude = float(longitude)

                        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
                            errors["base"] = "invalid_coords"
                except (ValueError, TypeError):
                    errors["base"] = "invalid_coords"

            # Validate radius
            if not errors:
                try:
                    radius = float(user_input.get(CONF_RADIUS, 5.0))
                    if radius < 0.1 or radius > 100:
                        errors["base"] = "invalid_radius"
                except (ValueError, TypeError):
                    errors["base"] = "invalid_radius"

            if not errors:
                await self.async_set_unique_id(
                    f"oplaadpalen_{latitude}_{longitude}"
                )
                self._abort_if_unique_id_configured()

                # Check if stations are found at the given location
                stations_found = True
                try:
                    session = async_get_clientsession(self.hass)
                    api = OplaadpalenAPI(session)
                    stations = await api.get_charging_stations(
                        latitude=latitude,
                        longitude=longitude,
                        radius_km=float(user_input.get(CONF_RADIUS, 5.0)),
                    )
                    stations_found = len(stations) > 0
                    _LOGGER.info(
                        "Station search: %.4f, %.4f, radius %.1f km → found %d stations",
                        latitude,
                        longitude,
                        float(user_input.get(CONF_RADIUS, 5.0)),
                        len(stations),
                    )
                    
                    if not stations_found:
                        _LOGGER.warning(
                            "No charging stations found at coordinates %.4f, %.4f with radius %.1f km",
                            latitude,
                            longitude,
                            float(user_input.get(CONF_RADIUS, 5.0)),
                        )
                except Exception as e:
                    _LOGGER.warning("Could not verify stations availability: %s", e)
                    # Don't fail setup, continue anyway

                # If no stations found, show confirmation step
                if not stations_found:
                    self.no_stations_context = {
                        CONF_NAME: user_input.get(CONF_NAME),
                        CONF_LATITUDE: latitude,
                        CONF_LONGITUDE: longitude,
                        CONF_RADIUS: float(user_input.get(CONF_RADIUS, 5.0)),
                        CONF_UPDATE_INTERVAL: int(user_input.get(CONF_UPDATE_INTERVAL, 300)),
                    }
                    return await self.async_step_no_stations()

                return self.async_create_entry(
                    title=user_input.get(CONF_NAME, f"Oplaadpalen {latitude}, {longitude}"),
                    data={
                        CONF_NAME: user_input.get(CONF_NAME),
                        CONF_LATITUDE: latitude,
                        CONF_LONGITUDE: longitude,
                        CONF_RADIUS: float(user_input.get(CONF_RADIUS, 5.0)),
                        CONF_UPDATE_INTERVAL: int(
                            user_input.get(CONF_UPDATE_INTERVAL, 300)
                        ),
                    },
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_NAME): str,
                vol.Optional(CONF_ADDRESS): str,
                vol.Optional(CONF_LATITUDE): str,
                vol.Optional(CONF_LONGITUDE): str,
                vol.Optional(CONF_RADIUS, default=5.0): vol.Coerce(float),
                vol.Optional(CONF_UPDATE_INTERVAL, default=300): vol.Coerce(int),
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def async_step_no_stations(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle confirmation when no stations are found."""
        if user_input is not None:
            return self.async_create_entry(
                title=self.no_stations_context.get(
                    CONF_NAME,
                    f"Oplaadpalen {self.no_stations_context.get(CONF_LATITUDE)}, {self.no_stations_context.get(CONF_LONGITUDE)}",
                ),
                data=self.no_stations_context,
            )

        lat = self.no_stations_context.get(CONF_LATITUDE)
        lon = self.no_stations_context.get(CONF_LONGITUDE)
        radius = self.no_stations_context.get(CONF_RADIUS, 5.0)

        return self.async_show_form(
            step_id="no_stations",
            description_placeholders={
                "latitude": f"{lat:.4f}",
                "longitude": f"{lon:.4f}",
                "radius": str(radius),
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this config entry."""
        return OplaadpalenOptionsFlow()


class OplaadpalenOptionsFlow(config_entries.OptionsFlow):
    """Handle options for Oplaadpalen."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_RADIUS,
                        default=self.config_entry.data.get(CONF_RADIUS, 5.0),
                    ): vol.Coerce(float),
                    vol.Optional(
                        CONF_UPDATE_INTERVAL,
                        default=self.config_entry.data.get(CONF_UPDATE_INTERVAL, 300),
                    ): vol.Coerce(int),
                }
            ),
        )
