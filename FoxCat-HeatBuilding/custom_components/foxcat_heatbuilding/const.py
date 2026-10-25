"""Constants for FoxCat HeatBuilding."""
from __future__ import annotations

DOMAIN = "foxcat_heatbuilding"
PLATFORMS = ["sensor", "binary_sensor", "switch", "number", "select"]

CONF_NAME = "name"
CONF_ZONES = "zones"
CONF_PERSON_ENTITIES = "person_entities"
CONF_OUTDOOR_TEMPERATURE = "outdoor_temperature_entity"
CONF_SOLAR_POWER = "solar_power_entity"
CONF_GRID_POWER = "grid_power_entity"
CONF_PRICE = "electricity_price_entity"
CONF_WEATHER = "weather_entity"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_AUTO_CONTROL = "automatic_control"

DEFAULT_NAME = "FoxCat HeatBuilding"
DEFAULT_SCAN_INTERVAL = 60
MIN_SCAN_INTERVAL = 15
MAX_SCAN_INTERVAL = 600

DATA_COORDINATOR = "coordinator"
DATA_CONFIG = "config"

ATTR_ZONE_ID = "zone_id"
ATTR_REASON = "reason"
ATTR_CONFIDENCE = "confidence"
ATTR_TARGET_TEMPERATURE = "target_temperature_c"
ATTR_ACTION = "action"

PROFILE_COMFORT = "comfort"
PROFILE_ECO = "eco"
PROFILE_SOLAR = "solar"
PROFILE_OPTIONS = [PROFILE_COMFORT, PROFILE_ECO, PROFILE_SOLAR]

ACTION_HOLD = "HOLD"
ACTION_PREHEAT = "PREHEAT"
ACTION_PRECOOL = "PRECOOL"
ACTION_REDUCE = "REDUCE"
ACTION_RESTORE_COMFORT = "RESTORE_COMFORT"
ACTION_NO_ACTION = "NO_ACTION"
