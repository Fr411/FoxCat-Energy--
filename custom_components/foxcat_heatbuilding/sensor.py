"""Sensor entities."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.const import UnitOfTemperature, UnitOfPower
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DATA_COORDINATOR


SENSORS = {
    "presence": ("Présence globale", None, None),
    "outdoor_temperature_c": ("Température extérieure", SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS),
    "solar_power_w": ("Puissance solaire", SensorDeviceClass.POWER, UnitOfPower.WATT),
    "grid_power_w": ("Puissance réseau", SensorDeviceClass.POWER, UnitOfPower.WATT),
    "electricity_price": ("Prix électricité", None, None),
    "profile": ("Profil thermique", None, None),
}


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    async_add_entities([FoxCatDiagnosticSensor(coordinator, entry, key, label, device_class, unit)
                        for key, (label, device_class, unit) in SENSORS.items()])


class FoxCatDiagnosticSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, key, label, device_class, unit):
        super().__init__(coordinator)
        self.key = key
        self._attr_name = label
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = unit
        self._attr_suggested_object_id = f"foxcat_heatbuilding_{key}"

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        if self.key == "presence":
            value = data.get("presence")
            return "présent" if value is True else "absent" if value is False else "inconnu"
        if self.key == "profile":
            return data.get("profile")
        return data.get(self.key)

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data or {}
        return {
            "updated_at": data.get("updated_at").isoformat() if data.get("updated_at") else None,
            "automatic_enabled": data.get("automatic_enabled", False),
            "zone_count": len(data.get("zones", {})),
            "errors": data.get("errors", []),
        }
