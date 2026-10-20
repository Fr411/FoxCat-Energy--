DOMAIN = "foxcat_heating"
PLATFORMS = ["sensor"]

CONF_ROOM_NAME = "room_name"
CONF_CLIMATE_ENTITY = "climate_entity"
CONF_ROOM_TEMP_ENTITY = "room_temp_entity"
CONF_OUTDOOR_TEMP_ENTITY = "outdoor_temp_entity"
CONF_LENGTH = "length_m"
CONF_WIDTH = "width_m"
CONF_HEIGHT = "height_m"
CONF_SURFACE_OVERRIDE = "surface_override_m2"
CONF_AIRFLOW_MAX = "airflow_max_m3h"
CONF_POWER_NOMINAL = "power_nominal_kw"
CONF_POWER_MIN = "power_min_kw"
CONF_POWER_MAX = "power_max_kw"
CONF_HEAT_CAPACITY = "effective_capacity_kwh_k"
CONF_HEAT_LOSS = "heat_loss_kw_k"
CONF_FAN_FLOW_MAP = "fan_flow_map"
CONF_POWER_CURVE = "outdoor_power_curve"
CONF_POWER_CURVE_ENABLED = "use_outdoor_power_curve"

DEFAULTS = {
    CONF_LENGTH: 10.0,
    CONF_WIDTH: 6.0,
    CONF_HEIGHT: 2.65,
    CONF_SURFACE_OVERRIDE: 0.0,
    CONF_AIRFLOW_MAX: 610.0,
    CONF_POWER_NOMINAL: 3.2,
    CONF_POWER_MIN: 0.9,
    CONF_POWER_MAX: 4.7,
    CONF_HEAT_CAPACITY: 0.12,
    CONF_HEAT_LOSS: 0.0008,
    CONF_FAN_FLOW_MAP: {},
    # Points are outdoor °C -> available heating capacity fraction.
    CONF_POWER_CURVE: {"-15": 0.55, "-7": 0.70, "2": 0.88, "7": 1.0, "12": 1.0},
    CONF_POWER_CURVE_ENABLED: False,
}
