"""Conservative adaptive first-order thermal model.

The model estimates a local temperature drift from observed temperature changes.
It is deliberately not used to override safety limits or to infer HVAC thermal
power from electrical power.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class ThermalModel:
    """Online first-order model with bounded drift estimate."""

    drift_c_per_hour: float = 0.0
    confidence: float = 0.0
    last_temperature_c: float | None = None
    last_updated: datetime | None = None
    sample_count: int = 0

    def update(self, temperature_c: float, now: datetime) -> None:
        """Update observed drift with a bounded exponentially weighted estimate."""
        if self.last_temperature_c is not None and self.last_updated is not None:
            hours = (now - self.last_updated).total_seconds() / 3600
            if 0.02 <= hours <= 2.0:
                observed = (temperature_c - self.last_temperature_c) / hours
                observed = max(-5.0, min(5.0, observed))
                alpha = 0.15
                self.drift_c_per_hour = (
                    alpha * observed + (1 - alpha) * self.drift_c_per_hour
                )
                self.sample_count += 1
                self.confidence = min(0.95, self.sample_count / 40)
        self.last_temperature_c = temperature_c
        self.last_updated = now

    def predict(self, horizon_hours: float) -> float | None:
        """Return a naive drift projection; None until a temperature is known."""
        if self.last_temperature_c is None:
            return None
        horizon = max(0.0, min(6.0, horizon_hours))
        return self.last_temperature_c + self.drift_c_per_hour * horizon
