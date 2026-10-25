from custom_components.foxcat_heatbuilding.engine.safety import validate_decision
from custom_components.foxcat_heatbuilding.models import ZoneDecision, ZoneSnapshot


def _snapshot():
    return ZoneSnapshot("salon", 20.0, 20.0, "climate.salon", True, True)


def test_safety_fails_closed_when_automatic_disabled():
    decision = ZoneDecision("salon", "PREHEAT", 21.0, "test", 0.5)
    result = validate_decision(
        decision, _snapshot(), automatic_enabled=False,
        explicitly_authorized=True, min_setpoint_c=17, max_setpoint_c=24,
        max_delta_c=1, last_command_age_s=None,
    )
    assert not result.allowed


def test_safety_rejects_large_delta():
    decision = ZoneDecision("salon", "PREHEAT", 23.0, "test", 0.5)
    result = validate_decision(
        decision, _snapshot(), automatic_enabled=True,
        explicitly_authorized=True, min_setpoint_c=17, max_setpoint_c=24,
        max_delta_c=1, last_command_age_s=None,
    )
    assert not result.allowed
