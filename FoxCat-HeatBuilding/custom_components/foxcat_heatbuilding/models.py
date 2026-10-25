"""Typed internal models."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ZoneSnapshot:
    zone_id: str
    temperature_c: float | None
    current_setpoint_c: float | None
    climate_entity: str | None
    occupied: bool
    available: bool
    hvac_mode: str | None = None
    attributes: dict[str, Any] | None = None


@dataclass(frozen=True)
class ZoneDecision:
    zone_id: str
    action: str
    target_temperature_c: float | None
    reason: str
    confidence: float
    eligible_for_execution: bool = False
