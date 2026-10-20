from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature, UnitOfTime, UnitOfPower, UnitOfVolume
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN, PLATFORMS, CONF_ROOM_NAME, CONF_CLIMATE_ENTITY, CONF_ROOM_TEMP_ENTITY,
    CONF_OUTDOOR_TEMP_ENTITY, CONF_LENGTH, CONF_WIDTH, CONF_HEIGHT,
    CONF_SURFACE_OVERRIDE, CONF_AIRFLOW_MAX, CONF_POWER_NOMINAL,
    CONF_POWER_MIN, CONF_POWER_MAX, CONF_HEAT_CAPACITY, CONF_HEAT_LOSS,
    CONF_FAN_FLOW_MAP, CONF_POWER_CURVE, CONF_POWER_CURVE_ENABLED,
)


def _num(value):
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (TypeError, ValueError):
        return None


def _normalise(text: str) -> str:
    return str(text).strip().lower().replace("_", " ").replace("-", " ")


def _fan_data(climate_state, max_airflow: float, overrides: dict) -> tuple[float | None, str, list]:
    attrs = climate_state.attributes if climate_state else {}
    modes = attrs.get("fan_modes") or []
    active = attrs.get("fan_mode")
    # Auto is not a measurable fan step. Unknown modes remain visible but are
    # not silently treated as a known physical airflow.
    usable = [str(m) for m in modes if _normalise(m) not in ("auto", "automatic", "off", "on")]
    if active is None:
        return None, "unknown", usable
    active_key = str(active)
    if active_key in overrides:
        val = _num(overrides[active_key])
        return (val, "configured", usable) if val is not None and val > 0 else (None, "invalid_override", usable)
    if not usable:
        return None, "no_fan_modes", usable
    if active_key not in usable:
        return None, "automatic_or_unlisted", usable
    # User-requested approximation: maximum airflow divided into N equal
    # steps; the lowest usable step is 1/N and the highest is max airflow.
    index = usable.index(active_key) + 1
    return max_airflow * index / len(usable), "linear_estimate", usable


def _curve_factor(outdoor_temp: float, curve: dict) -> float:
    points = []
    for key, value in (curve or {}).items():
        x, y = _num(key), _num(value)
        if x is not None and y is not None and 0 < y <= 1.5:
            points.append((x, y))
    points.sort()
    if not points:
        return 1.0
    if outdoor_temp <= points[0][0]:
        return points[0][1]
    if outdoor_temp >= points[-1][0]:
        return points[-1][1]
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if x0 <= outdoor_temp <= x1:
            if x1 == x0:
                return y0
            return y0 + (y1 - y0) * (outdoor_temp - x0) / (x1 - x0)
    return 1.0


@dataclass
class HeatingSnapshot:
    values: dict[str, Any]


class FoxcatHeatingCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, config: dict):
        super().__init__(hass, logger=None, name=f"FoxCat Heating {config.get(CONF_ROOM_NAME, 'room')}", update_interval=None)
        self.config = config
        self.entry = entry

    async def _async_update_data(self):
        return self._calculate()

    def _calculate(self):
        c = self.config
        room_name = c.get(CONF_ROOM_NAME, "Pièce")
        climate_id = c.get(CONF_CLIMATE_ENTITY)
        room_temp_id = c.get(CONF_ROOM_TEMP_ENTITY)
        outdoor_id = c.get(CONF_OUTDOOR_TEMP_ENTITY)
        climate = self.hass.states.get(climate_id) if climate_id else None
        room_state = self.hass.states.get(room_temp_id) if room_temp_id else None
        outdoor_state = self.hass.states.get(outdoor_id) if outdoor_id else None

        room_temp = _num(room_state.state) if room_state and room_state.state not in ("unknown", "unavailable") else None
        outdoor_temp = _num(outdoor_state.state) if outdoor_state and outdoor_state.state not in ("unknown", "unavailable") else None
        target = _num(climate.attributes.get("temperature")) if climate else None
        hvac_mode = climate.state if climate else "unknown"
        fan_mode = climate.attributes.get("fan_mode") if climate else None
        modes = climate.attributes.get("fan_modes", []) if climate else []
        area = _num(c.get(CONF_SURFACE_OVERRIDE)) or (_num(c.get(CONF_LENGTH)) or 0) * (_num(c.get(CONF_WIDTH)) or 0)
        height = _num(c.get(CONF_HEIGHT)) or 0
        volume = area * height
        max_airflow = _num(c.get(CONF_AIRFLOW_MAX)) or 0
        airflow, airflow_source, fan_modes = _fan_data(climate, max_airflow, c.get(CONF_FAN_FLOW_MAP, {}))

        p_nom = _num(c.get(CONF_POWER_NOMINAL)) or 0
        p_min = _num(c.get(CONF_POWER_MIN)) or 0
        p_max = _num(c.get(CONF_POWER_MAX)) or p_nom
        p_max = max(0, p_max)
        p_min = max(0, p_min)

        # Airflow correction is deliberately conservative and configurable
        # through per-mode airflow overrides. It is NOT treated as a direct
        # linear thermal-capacity law.
        airflow_factor = min(1.0, airflow / max_airflow) if airflow is not None and max_airflow > 0 else None
        outdoor_factor = _curve_factor(outdoor_temp, c.get(CONF_POWER_CURVE, {})) if outdoor_temp is not None and c.get(CONF_POWER_CURVE_ENABLED) else 1.0
        power_available = min(p_max, p_nom * outdoor_factor)
        if airflow_factor is not None:
            # Only apply a weak fan-flow penalty when below max flow; never
            # scale thermal output linearly with airflow.
            power_available *= (0.70 + 0.30 * airflow_factor)
        if hvac_mode != "heat":
            power_available = 0.0

        capacity = max(0, _num(c.get(CONF_HEAT_CAPACITY)) or 0)
        heat_loss = max(0, _num(c.get(CONF_HEAT_LOSS)) or 0)
        if room_temp is not None and outdoor_temp is not None:
            mean_delta = ((room_temp + target) / 2 - outdoor_temp) if target is not None else (room_temp - outdoor_temp)
            losses = max(0, heat_loss * mean_delta)
        else:
            losses = None
        net_power = max(0, power_available - losses) if losses is not None else None
        delta = max(0, target - room_temp) if target is not None and room_temp is not None else None
        energy = capacity * delta if delta is not None else None
        minutes = (60 * energy / net_power) if energy is not None and net_power is not None and net_power > 0 else (0.0 if delta == 0 else None)

        if delta is None or target is None or room_temp is None:
            status = "Données de température indisponibles"
        elif delta == 0:
            status = "Consigne atteinte"
        elif hvac_mode != "heat":
            status = "Climatisation non en mode chauffage"
        elif net_power is None:
            status = "Déperditions non calculables"
        elif net_power <= 0:
            status = "Puissance nette insuffisante"
        elif airflow is None:
            status = "Temps estimé — vitesse ventilateur inconnue"
        else:
            status = "Estimation simplifiée"

        return {
            "room_name": room_name, "area": round(area, 2), "volume": round(volume, 2),
            "room_temp": room_temp, "target_temp": target, "outdoor_temp": outdoor_temp,
            "delta": round(delta, 2) if delta is not None else None,
            "hvac_mode": hvac_mode, "fan_mode": fan_mode, "fan_modes": fan_modes,
            "airflow": round(airflow, 1) if airflow is not None else None,
            "airflow_source": airflow_source, "airflow_factor": round(airflow_factor, 3) if airflow_factor is not None else None,
            "power_nominal": p_nom, "power_min": p_min, "power_max": p_max,
            "power_available": round(power_available, 3), "outdoor_factor": round(outdoor_factor, 3),
            "heat_losses": round(losses, 3) if losses is not None else None,
            "net_power": round(net_power, 3) if net_power is not None else None,
            "capacity": capacity, "energy": round(energy, 3) if energy is not None else None,
            "minutes": round(minutes, 1) if minutes is not None and math.isfinite(minutes) else None,
            "status": status,
        }


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    config = {**entry.data, **entry.options}
    coordinator = FoxcatHeatingCoordinator(hass, entry, config)

    @callback
    def refresh(_event=None):
        coordinator.async_set_updated_data(coordinator._calculate())

    # Trigger updates from relevant entity state changes.
    from homeassistant.helpers.event import async_track_state_change_event
    tracked = [config.get(CONF_CLIMATE_ENTITY), config.get(CONF_ROOM_TEMP_ENTITY), config.get(CONF_OUTDOOR_TEMP_ENTITY)]
    unsub = async_track_state_change_event(hass, [x for x in tracked if x], refresh)
    entry.async_on_unload(unsub)

    coordinator.data = coordinator._calculate()
    async_add_entities([
        FoxcatHeatingSensor(coordinator, entry, "minutes", "Temps de chauffe estimé", "min", "mdi:timer-thermometer"),
        FoxcatHeatingSensor(coordinator, entry, "airflow", "Débit de ventilation estimé", "m³/h", "mdi:fan"),
        FoxcatHeatingSensor(coordinator, entry, "power_available", "Puissance thermique estimée", "kW", "mdi:heat-pump"),
        FoxcatHeatingSensor(coordinator, entry, "net_power", "Puissance nette estimée", "kW", "mdi:flash"),
        FoxcatHeatingSensor(coordinator, entry, "energy", "Énergie thermique estimée nécessaire", "kWh", "mdi:lightning-bolt"),
        FoxcatHeatingSensor(coordinator, entry, "heat_losses", "Déperditions thermiques estimées", "kW", "mdi:home-thermometer"),
        FoxcatHeatingSensor(coordinator, entry, "area", "Surface configurée", "m²", "mdi:floor-plan"),
        FoxcatHeatingSensor(coordinator, entry, "volume", "Volume configuré", "m³", "mdi:cube-outline"),
        FoxcatHeatingSensor(coordinator, entry, "delta", "Écart à la consigne", "°C", "mdi:thermometer"),
        FoxcatHeatingSensor(coordinator, entry, "status", "État du calcul", None, "mdi:information-outline"),
    ], update_before_add=False)


class FoxcatHeatingSensor(SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, key, name, unit, icon):
        self.coordinator = coordinator
        self.entry = entry
        self.key = key
        self._attr_name = name
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"FoxCat Heating — {coordinator.config.get(CONF_ROOM_NAME, 'Pièce')}",
            manufacturer="FoxCat",
            model="Estimation thermique",
            sw_version="1.0.0",
        )
        self._attr_state_class = SensorStateClass.MEASUREMENT if unit else None
        if key == "minutes":
            self._attr_native_unit_of_measurement = UnitOfTime.MINUTES
        if key == "power_available" or key == "net_power" or key == "heat_losses":
            self._attr_native_unit_of_measurement = "kW"
        if key == "status":
            self._attr_entity_category = None

    @property
    def native_value(self):
        value = self.coordinator.data.get(self.key, {}) if self.coordinator.data else None
        if self.key == "status":
            return value
        return value

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data or {}
        if self.key == "status":
            return dict(data)
        return {
            "room": data.get("room_name"),
            "temperature_actuelle": data.get("room_temp"),
            "consigne": data.get("target_temp"),
            "temperature_exterieure": data.get("outdoor_temp"),
            "mode_hvac": data.get("hvac_mode"),
            "vitesse_ventilation": data.get("fan_mode"),
            "vitesses_disponibles": data.get("fan_modes"),
            "source_debit": data.get("airflow_source"),
            "facteur_puissance_exterieure": data.get("outdoor_factor"),
            "etat_calcul": data.get("status"),
        }
