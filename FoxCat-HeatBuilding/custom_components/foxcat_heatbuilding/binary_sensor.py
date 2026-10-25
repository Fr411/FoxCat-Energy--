"""Binary sensors."""
from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DATA_COORDINATOR


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    async_add_entities([
        FoxCatPresenceBinarySensor(coordinator, entry),
        FoxCatDataValidBinarySensor(coordinator, entry),
    ])


class FoxCatPresenceBinarySensor(CoordinatorEntity, BinarySensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Présence globale"
    _attr_device_class = BinarySensorDeviceClass.OCCUPANCY

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_presence_binary"

    @property
    def is_on(self):
        return (self.coordinator.data or {}).get("presence") is True


class FoxCatDataValidBinarySensor(CoordinatorEntity, BinarySensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Données de base disponibles"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_data_valid"

    @property
    def is_on(self):
        data = self.coordinator.data or {}
        return bool(data.get("updated_at")) and not data.get("errors")
