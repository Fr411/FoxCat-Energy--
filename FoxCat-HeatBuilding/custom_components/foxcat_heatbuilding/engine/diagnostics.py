"""Diagnostic helpers."""
from __future__ import annotations


def summarize_entity(hass, entity_id: str | None) -> dict:
    if not entity_id:
        return {"entity_id": None, "valid": False, "reason": "non_configured"}
    state = hass.states.get(entity_id)
    if state is None:
        return {"entity_id": entity_id, "valid": False, "reason": "missing"}
    if state.state in ("unknown", "unavailable"):
        return {"entity_id": entity_id, "valid": False, "reason": state.state}
    return {"entity_id": entity_id, "valid": True, "state": state.state}
