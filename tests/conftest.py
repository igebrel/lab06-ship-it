import pytest


@pytest.fixture
def valid_order():
    """Provide a valid delivery order for automated tests."""
    return {
        "distance_km": 5.0,
        "items": 3,
        "hour": 18,
        "prep_minutes": 20,
        "courier_months": 12,
        "weather": "clear",
        "day_type": "weekday",
        "vehicle": "bike",
    }
