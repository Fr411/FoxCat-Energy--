"""Safety validation for proposed commands."""
from __future__ import annotations

from dataclasses import dataclass

from ..models import ZoneDecision, ZoneSnapshot


@dataclass(frozen=True)
class SafetyResult:
    allowed: bool
    reason: str


def validate_decision(
    decision: ZoneDecision,
    snapshot: ZoneSnapshot,
    *,
    automatic_enabled: bool,
    explicitly_authorized: bool,
    min_setpoint_c: float,
    max_setpoint_c: float,
    max_delta_c: float,
    last_command_age_s: float | None,
    min_command_interval_s: int = 900,
) -> SafetyResult:
    """Fail closed: reject unless every required condition is met."""
    if not automatic_enabled:
        return SafetyResult(False, "Pilotage automatique désactivé.")
    if not explicitly_authorized:
        return SafetyResult(False, "Zone non autorisée explicitement.")
    if not snapshot.available:
        return SafetyResult(False, "Équipement ou mesure indisponible.")
    if decision.target_temperature_c is None:
        return SafetyResult(False, "Aucune consigne proposée.")
    if not min_setpoint_c <= decision.target_temperature_c <= max_setpoint_c:
        return SafetyResult(False, "Consigne hors des limites configurées.")
    if snapshot.current_setpoint_c is not None:
        if abs(decision.target_temperature_c - snapshot.current_setpoint_c) > max_delta_c:
            return SafetyResult(False, "Variation de consigne supérieure à la limite.")
    if last_command_age_s is not None and last_command_age_s < min_command_interval_s:
        return SafetyResult(False, "Temporisation minimale entre commandes non écoulée.")
    return SafetyResult(True, "Commande validée.")
