from app.services.discovery_service import haversine_km, normalize_search_term


def test_normalize_search_term_strips_noise():
    assert normalize_search_term("Raju Tailor!! 560103") == "raju tailor 560103"


def test_haversine_zero_for_same_point():
    assert haversine_km(12.9716, 77.5946, 12.9716, 77.5946) == 0


def test_haversine_returns_positive_distance():
    assert haversine_km(12.9716, 77.5946, 12.9569, 77.7011) > 5
