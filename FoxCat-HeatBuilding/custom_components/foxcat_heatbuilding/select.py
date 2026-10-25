"""Thermal profile selector."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DATA_COORDINATOR, PROFILE_OPTIONS


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    async_add_entities([FoxCatProfileSelect(coordinator, entry)])


class FoxCatProfileSelect(CoordinatorEntity, SelectEntity):
    _attr_has_entity_name = True
    _attr_name = "Profil thermique"
    _attr_options = PROFILE_OPTIONS

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_profile"

    @property
    def current_option(self):
        return self.coordinator.profile

    async def async_select_option(self, option: str):
        if option not in PROFILE_OPTIONS:
            return
        self.coordinator.set_profile(option)
