import json
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    DOMAIN, CONF_ROOM_NAME, CONF_CLIMATE_ENTITY, CONF_ROOM_TEMP_ENTITY,
    CONF_OUTDOOR_TEMP_ENTITY, CONF_LENGTH, CONF_WIDTH, CONF_HEIGHT,
    CONF_SURFACE_OVERRIDE, CONF_AIRFLOW_MAX, CONF_POWER_NOMINAL,
    CONF_POWER_MIN, CONF_POWER_MAX, CONF_HEAT_CAPACITY, CONF_HEAT_LOSS,
    CONF_FAN_FLOW_MAP, CONF_POWER_CURVE, CONF_POWER_CURVE_ENABLED, DEFAULTS,
)


class FoxcatHeatingConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            await self.async_set_unique_id(
                f"{user_input[CONF_ROOM_NAME].strip().lower()}_{user_input[CONF_CLIMATE_ENTITY]}"
            )
            self._abort_if_unique_id_configured()
            user_input[CONF_FAN_FLOW_MAP] = {}
            user_input[CONF_POWER_CURVE] = DEFAULTS[CONF_POWER_CURVE]
            user_input[CONF_POWER_CURVE_ENABLED] = False
            return self.async_create_entry(
                title=f"FoxCat Heating — {user_input[CONF_ROOM_NAME]}",
                data=user_input,
            )

        schema = vol.Schema({
            vol.Required(CONF_ROOM_NAME, default="Salon"): str,
            vol.Required(CONF_CLIMATE_ENTITY): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="climate")
            ),
            vol.Required(CONF_ROOM_TEMP_ENTITY): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor")
            ),
            vol.Required(CONF_OUTDOOR_TEMP_ENTITY): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor")
            ),
            vol.Required(CONF_LENGTH, default=DEFAULTS[CONF_LENGTH]): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=100)),
            vol.Required(CONF_WIDTH, default=DEFAULTS[CONF_WIDTH]): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=100)),
            vol.Required(CONF_HEIGHT, default=DEFAULTS[CONF_HEIGHT]): vol.All(vol.Coerce(float), vol.Range(min=1.0, max=10)),
            vol.Optional(CONF_SURFACE_OVERRIDE, default=0.0): vol.All(vol.Coerce(float), vol.Range(min=0, max=1000)),
            vol.Required(CONF_AIRFLOW_MAX, default=DEFAULTS[CONF_AIRFLOW_MAX]): vol.All(vol.Coerce(float), vol.Range(min=10, max=10000)),
            vol.Required(CONF_POWER_NOMINAL, default=DEFAULTS[CONF_POWER_NOMINAL]): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=100)),
            vol.Required(CONF_POWER_MIN, default=DEFAULTS[CONF_POWER_MIN]): vol.All(vol.Coerce(float), vol.Range(min=0, max=100)),
            vol.Required(CONF_POWER_MAX, default=DEFAULTS[CONF_POWER_MAX]): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=100)),
            vol.Required(CONF_HEAT_CAPACITY, default=DEFAULTS[CONF_HEAT_CAPACITY]): vol.All(vol.Coerce(float), vol.Range(min=0.001, max=10)),
            vol.Required(CONF_HEAT_LOSS, default=DEFAULTS[CONF_HEAT_LOSS]): vol.All(vol.Coerce(float), vol.Range(min=0, max=10)),
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return FoxcatHeatingOptionsFlow(config_entry)


class FoxcatHeatingOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            # Optional JSON maps let advanced users override the inferred fan curve
            # and add outdoor-temperature capacity correction points.
            try:
                fan_map = json.loads(user_input.pop("fan_flow_map_json") or "{}")
                curve = json.loads(user_input.pop("outdoor_power_curve_json") or json.dumps(DEFAULTS[CONF_POWER_CURVE]))
                if not isinstance(fan_map, dict) or not isinstance(curve, dict):
                    raise ValueError("JSON maps must be objects")
                user_input[CONF_FAN_FLOW_MAP] = fan_map
                user_input[CONF_POWER_CURVE] = curve
            except (ValueError, TypeError, json.JSONDecodeError):
                return self.async_show_form(step_id="init", data_schema=self._schema(user_input), errors={"base": "invalid_json"})
            return self.async_create_entry(title="", data=user_input)

        current = {**self.config_entry.data, **self.config_entry.options}
        return self.async_show_form(step_id="init", data_schema=self._schema(current))

    def _schema(self, current):
        return vol.Schema({
            vol.Required(CONF_ROOM_NAME, default=current.get(CONF_ROOM_NAME, "Pièce")): str,
            vol.Required(CONF_LENGTH, default=current.get(CONF_LENGTH, DEFAULTS[CONF_LENGTH])): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=100)),
            vol.Required(CONF_WIDTH, default=current.get(CONF_WIDTH, DEFAULTS[CONF_WIDTH])): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=100)),
            vol.Required(CONF_HEIGHT, default=current.get(CONF_HEIGHT, DEFAULTS[CONF_HEIGHT])): vol.All(vol.Coerce(float), vol.Range(min=1, max=10)),
            vol.Optional(CONF_SURFACE_OVERRIDE, default=current.get(CONF_SURFACE_OVERRIDE, 0.0)): vol.All(vol.Coerce(float), vol.Range(min=0, max=1000)),
            vol.Required(CONF_AIRFLOW_MAX, default=current.get(CONF_AIRFLOW_MAX, DEFAULTS[CONF_AIRFLOW_MAX])): vol.All(vol.Coerce(float), vol.Range(min=10, max=10000)),
            vol.Required(CONF_POWER_NOMINAL, default=current.get(CONF_POWER_NOMINAL, DEFAULTS[CONF_POWER_NOMINAL])): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=100)),
            vol.Required(CONF_POWER_MIN, default=current.get(CONF_POWER_MIN, DEFAULTS[CONF_POWER_MIN])): vol.All(vol.Coerce(float), vol.Range(min=0, max=100)),
            vol.Required(CONF_POWER_MAX, default=current.get(CONF_POWER_MAX, DEFAULTS[CONF_POWER_MAX])): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=100)),
            vol.Required(CONF_HEAT_CAPACITY, default=current.get(CONF_HEAT_CAPACITY, DEFAULTS[CONF_HEAT_CAPACITY])): vol.All(vol.Coerce(float), vol.Range(min=0.001, max=10)),
            vol.Required(CONF_HEAT_LOSS, default=current.get(CONF_HEAT_LOSS, DEFAULTS[CONF_HEAT_LOSS])): vol.All(vol.Coerce(float), vol.Range(min=0, max=10)),
            vol.Required(CONF_POWER_CURVE_ENABLED, default=current.get(CONF_POWER_CURVE_ENABLED, False)): bool,
            vol.Required("fan_flow_map_json", default=json.dumps(current.get(CONF_FAN_FLOW_MAP, {}), ensure_ascii=False)): str,
            vol.Required("outdoor_power_curve_json", default=json.dumps(current.get(CONF_POWER_CURVE, DEFAULTS[CONF_POWER_CURVE]), ensure_ascii=False)): str,
        })
