"""Presence aggregation helpers."""
from __future__ import annotations

from homeassistant.core import HomeAssistant


def any_person_home(hass: HomeAssistant, person_entities: list[str]) -> bool | None:
    """Return True if any person is home, False if all known away, None if unknown."""
    if not person_entities:
        return None
    states = [hass.states.get(entity_id) for entity_id in person_entities]
    if any(state is None or state.state in ("unknown", "unavailable") for state in states):
        known_home = any(state is not None and state.state == "home" for state in states)
        return True if known_home else None
    return any(state.state == "home" for state in states)
