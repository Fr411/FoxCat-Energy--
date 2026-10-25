"""Data coordinator for FoxCat HeatBuilding."""
from __future__ import annotations

from datetime import datetime
import logging

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN, CONF_NAME, CONF_ZONES, CONF_PERSON_ENTITIES, CONF_OUTDOOR_TEMPERATURE,
    CONF_SOLAR_POWER, CONF_GRID_POWER, CONF_PRICE, CONF_WEATHER, CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL, PROFILE_COMFORT, ACTION_NO_ACTION,
)
from .engine.thermal_model import ThermalModel
from .engine.presence import any_person_home
from .engine.decision import decide_zone
from .models import ZoneSnapshot

_LOGGER = logging.getLogger(__name__)


def _float_state(hass: HomeAssistant, entity_id: str | None) -> float | None:
    if not entity_id:
        return None
    state = hass.states.get(entity_id)
    if state is None or state.state in ("unknown", "unavailable"):
        return None
    try:
        return float(state.state)
    except (ValueError, TypeError):
        return None


class FoxCatHeatBuildingCoordinator(DataUpdateCoordinator):
    """Collect data and calculate proposed decisions."""

    def __init__(self, hass: HomeAssistant, entry):
        self.hass = hass
        self.entry = entry
        self.config = {**entry.data, **entry.options}
        interval = int(self.config.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=__import__("datetime").timedelta(seconds=max(15, min(600, interval))),
        )
        self.models: dict[str, ThermalModel] = {}
        self.profile = PROFILE_COMFORT
        self.automatic_enabled = False
        self.authorized_zones: set[str] = set()
        self.last_decisions: dict[str, dict] = {}
        self.last_command_time: dict[str, datetime] = {}

    async def _async_update_data(self):
        now = dt_util.utcnow()
        zones = self.config.get(CONF_ZONES, ["salon"])
        if isinstance(zones, str):
            zones = [zones]
        persons = self.config.get(CONF_PERSON_ENTITIES, [])
        if isinstance(persons, str):
            persons = [persons]
        presence = any_person_home(self.hass, persons)
        outdoor = _float_state(self.hass, self.config.get(CONF_OUTDOOR_TEMPERATURE))
        solar = _float_state(self.hass, self.config.get(CONF_SOLAR_POWER))
        grid = _float_state(self.hass, self.config.get(CONF_GRID_POWER))
        price = _float_state(self.hass, self.config.get(CONF_PRICE))
        weather_entity = self.config.get(CONF_WEATHER)
        weather_state = self.hass.states.get(weather_entity) if weather_entity else None

        zone_data = {}
        for raw_zone in zones:
            zone_id = str(raw_zone).strip().lower().replace(" ", "_")
            # Zone sensors and climate entities are configured later in the zone options.
            # The first version never discovers/pilots devices implicitly.
            model = self.models.setdefault(zone_id, ThermalModel())
            snapshot = ZoneSnapshot(
                zone_id=zone_id,
                temperature_c=None,
                current_setpoint_c=None,
                climate_entity=None,
                occupied=presence is True,
                available=False,
            )
            decision = decide_zone(
                snapshot, self.profile, max(0.0, -grid) if grid is not None else None,
                solar_delta_max_c=1.0, eco_delta_c=1.0,
                model_confidence=model.confidence,
            )
            zone_data[zone_id] = {
                "snapshot": snapshot,
                "decision": decision,
                "model": model,
            }

        return {
            "updated_at": now,
            "name": self.config.get(CONF_NAME, "FoxCat HeatBuilding"),
            "presence": presence,
            "outdoor_temperature_c": outdoor,
            "solar_power_w": solar,
            "grid_power_w": grid,
            "electricity_price": price,
            "weather_state": weather_state.state if weather_state else None,
            "zones": zone_data,
            "automatic_enabled": self.automatic_enabled,
            "profile": self.profile,
            "last_decisions": self.last_decisions,
            "errors": [],
        }

    @callback
    def set_profile(self, profile: str) -> None:
        self.profile = profile
        self.async_set_updated_data(self.data)

    @callback
    def set_automatic(self, enabled: bool) -> None:
        # Enabling this switch only enables the engine flag. It does not yet
        # authorize zones or execute any HVAC command.
        self.automatic_enabled = enabled
        self.async_set_updated_data(self.data)
