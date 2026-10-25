from datetime import datetime, timedelta

from custom_components.foxcat_heatbuilding.engine.thermal_model import ThermalModel


def test_model_learns_drift():
    model = ThermalModel()
    start = datetime(2026, 1, 1, 12, 0)
    model.update(20.0, start)
    model.update(21.0, start + timedelta(hours=1))
    assert model.drift_c_per_hour > 0
    assert model.predict(1) is not None


def test_model_does_not_update_on_unreasonable_interval():
    model = ThermalModel()
    start = datetime(2026, 1, 1, 12, 0)
    model.update(20.0, start)
    model.update(25.0, start + timedelta(hours=8))
    assert model.drift_c_per_hour == 0.0
