"""Centralized actuator boundary.

No physical command is executed in beta.1. Future actuator methods must call
Home Assistant services only after explicit zone authorization and safety checks.
"""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.core import HomeAssistant


@dataclass(frozen=True)
class ActuationResult:
    executed: bool
    reason: str


class Actuator:
    """Single boundary for all physical commands."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass

    async def async_apply(self, decision, safety_result) -> ActuationResult:
        """Fail closed in this release; never command a device."""
        if not safety_result.allowed:
            return ActuationResult(False, safety_result.reason)
        return ActuationResult(
            False,
            "Exécution physique non implémentée dans beta.1; aucune commande envoyée.",
        )
