"""Config flow for FoxCat HeatBuilding."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    DOMAIN, DEFAULT_NAME, CONF_NAME, CONF_ZONES, CONF_PERSON_ENTITIES,
    CONF_OUTDOOR_TEMPERATURE, CONF_SOLAR_POWER, CONF_GRID_POWER,
    CONF_PRICE, CONF_WEATHER, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL, MAX_SCAN_INTERVAL,
)


def _schema(defaults: dict | None = None) -> vol.Schema:
    defaults = defaults or {}
    return vol.Schema({
        vol.Required(CONF_NAME, default=defaults.get(CONF_NAME, DEFAULT_NAME)): str,
        vol.Required(CONF_ZONES, default=defaults.get(CONF_ZONES, "salon")): str,
        vol.Optional(CONF_PERSON_ENTITIES, default=defaults.get(CONF_PERSON_ENTITIES, "")): str,
        vol.Optional(CONF_OUTDOOR_TEMPERATURE, default=defaults.get(CONF_OUTDOOR_TEMPERATURE, "")): str,
        vol.Optional(CONF_SOLAR_POWER, default=defaults.get(CONF_SOLAR_POWER, "")): str,
        vol.Optional(CONF_GRID_POWER, default=defaults.get(CONF_GRID_POWER, "")): str,
        vol.Optional(CONF_PRICE, default=defaults.get(CONF_PRICE, "")): str,
        vol.Optional(CONF_WEATHER, default=defaults.get(CONF_WEATHER, "")): str,
        vol.Required(CONF_SCAN_INTERVAL, default=defaults.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)):
            vol.All(int, vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL)),
    })


def _parse_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


class FoxCatHeatBuildingConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Set up a building and initial zone registry."""
        errors = {}
        if user_input is not None:
            name = user_input[CONF_NAME].strip()
            if not name:
                errors["base"] = "invalid_name"
            else:
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_id_configured()
                data = dict(user_input)
                data[CONF_NAME] = name
                data[CONF_ZONES] = _parse_csv(user_input[CONF_ZONES]) or ["salon"]
                data[CONF_PERSON_ENTITIES] = _parse_csv(user_input.get(CONF_PERSON_ENTITIES, ""))
                for key in (
                    CONF_OUTDOOR_TEMPERATURE, CONF_SOLAR_POWER, CONF_GRID_POWER,
                    CONF_PRICE, CONF_WEATHER,
                ):
                    data[key] = user_input.get(key, "").strip() or None
                return self.async_create_entry(title=name, data=data)
        return self.async_show_form(step_id="user", data_schema=_schema(), errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return FoxCatHeatBuildingOptionsFlow(config_entry)


class FoxCatHeatBuildingOptionsFlow(config_entries.OptionsFlow):
    """Options flow for non-structural settings."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        current = {**self.config_entry.data, **self.config_entry.options}
        if user_input is not None:
            data = dict(user_input)
            data[CONF_ZONES] = _parse_csv(data[CONF_ZONES]) or ["salon"]
            data[CONF_PERSON_ENTITIES] = _parse_csv(data.get(CONF_PERSON_ENTITIES, ""))
            for key in (CONF_OUTDOOR_TEMPERATURE, CONF_SOLAR_POWER, CONF_GRID_POWER, CONF_PRICE, CONF_WEATHER):
                data[key] = data.get(key, "").strip() or None
            return self.async_create_entry(title="", data=data)
        display = dict(current)
        display[CONF_ZONES] = ", ".join(current.get(CONF_ZONES, []))
        display[CONF_PERSON_ENTITIES] = ", ".join(current.get(CONF_PERSON_ENTITIES, []))
        for key in (CONF_OUTDOOR_TEMPERATURE, CONF_SOLAR_POWER, CONF_GRID_POWER, CONF_PRICE, CONF_WEATHER):
            display[key] = current.get(key) or ""
        return self.async_show_form(step_id="init", data_schema=_schema(display))
