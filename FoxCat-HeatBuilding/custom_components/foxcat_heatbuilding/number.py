"""Configurable optimization parameters."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DATA_COORDINATOR


PARAMETERS = [
    ("solar_delta", "Écart maximal consigne solaire", 0.0, 2.0, 0.1, 1.0, "°C"),
    ("eco_delta", "Réduction de consigne éco", 0.0, 3.0, 0.1, 1.0, "°C"),
]


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    async_add_entities([FoxCatParameterNumber(coordinator, entry, *param) for param in PARAMETERS])


class FoxCatParameterNumber(CoordinatorEntity, NumberEntity):
    _attr_has_entity_name = True
    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator, entry, key, name, minimum, maximum, step, initial, unit):
        super().__init__(coordinator)
        self.key = key
        self._value = initial
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_native_min_value = minimum
        self._attr_native_max_value = maximum
        self._attr_native_step = step
        self._attr_native_unit_of_measurement = unit

    @property
    def native_value(self):
        return self._value

    async def async_set_native_value(self, value: float):
        self._value = float(value)
        self.async_write_ha_state()
