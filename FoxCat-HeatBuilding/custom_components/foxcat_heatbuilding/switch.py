"""Control switches."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DATA_COORDINATOR


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    async_add_entities([FoxCatAutomaticControlSwitch(coordinator, entry)])


class FoxCatAutomaticControlSwitch(CoordinatorEntity, SwitchEntity):
    _attr_has_entity_name = True
    _attr_name = "Autoriser le moteur automatique"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_automatic_control"

    @property
    def is_on(self):
        return self.coordinator.automatic_enabled

    async def async_turn_on(self, **kwargs):
        # Safe initial release: this flag does not execute physical commands.
        self.coordinator.set_automatic(True)

    async def async_turn_off(self, **kwargs):
        self.coordinator.set_automatic(False)
