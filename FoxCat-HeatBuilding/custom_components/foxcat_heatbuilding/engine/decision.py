"""Deterministic decision logic."""
from __future__ import annotations

from ..const import (
    ACTION_HOLD, ACTION_PREHEAT, ACTION_REDUCE, ACTION_RESTORE_COMFORT,
    ACTION_NO_ACTION, PROFILE_COMFORT, PROFILE_ECO, PROFILE_SOLAR,
)
from ..models import ZoneSnapshot, ZoneDecision


def decide_zone(
    snapshot: ZoneSnapshot,
    profile: str,
    solar_surplus_w: float | None,
    solar_delta_max_c: float,
    eco_delta_c: float,
    model_confidence: float,
) -> ZoneDecision:
    """Generate a proposed target. This function never executes commands."""
    if not snapshot.available or snapshot.temperature_c is None:
        return ZoneDecision(snapshot.zone_id, ACTION_NO_ACTION, None,
                            "Zone ou température indisponible; aucune commande.", 0.0)
    current = snapshot.current_setpoint_c
    if current is None:
        return ZoneDecision(snapshot.zone_id, ACTION_NO_ACTION, None,
                            "Consigne actuelle inconnue; aucune commande.", 0.0)

    if snapshot.occupied:
        if profile == PROFILE_ECO:
            target = current - eco_delta_c
            return ZoneDecision(snapshot.zone_id, ACTION_REDUCE, target,
                                "Profil éco demandé et présence confirmée.", model_confidence)
        if profile == PROFILE_SOLAR and solar_surplus_w is not None and solar_surplus_w >= 800:
            target = current + solar_delta_max_c
            return ZoneDecision(snapshot.zone_id, ACTION_PREHEAT, target,
                                "Surplus solaire mesuré estimé suffisant; proposition de préchauffage.",
                                model_confidence)
        return ZoneDecision(snapshot.zone_id, ACTION_HOLD, current,
                            "Présence détectée; maintien de la consigne.", model_confidence)

    # No presence or unknown presence never means an automatic setback by itself.
    return ZoneDecision(snapshot.zone_id, ACTION_RESTORE_COMFORT, current,
                        "Absence non pilotée automatiquement dans cette version; maintien de la consigne.",
                        model_confidence)
