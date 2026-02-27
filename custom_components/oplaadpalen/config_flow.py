"""Config flow for Oplaadpalen integration."""
import logging
from typing import Any

import voluptuous as vol
from geopy.geocoders import Nominatim

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

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

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

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
