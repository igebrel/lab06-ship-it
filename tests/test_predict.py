import pytest

from predict import predict_order


def test_probability_is_between_zero_and_one(valid_order):
    """Check that the model returns a valid probability."""
    result = predict_order(valid_order)

    probability = result["late_probability"]

    assert 0.0 <= probability <= 1.0


def test_high_risk_order_issues_voucher(valid_order):
    """Check that a high-risk order receives a $4 voucher."""
    order = valid_order.copy()

    order.update(
        {
            "distance_km": 8.0,
            "items": 4,
            "hour": 18,
            "prep_minutes": 25,
            "courier_months": 12,
            "weather": "rain",
            "day_type": "weekday",
            "vehicle": "bike",
        }
    )

    result = predict_order(order)

    assert result["late_probability"] >= result["threshold"]
    assert result["issue_voucher"] is True
    assert result["voucher_amount"] == 4.0


def test_low_risk_order_does_not_issue_voucher(valid_order):
    """Check that a low-risk order does not receive a voucher."""
    order = valid_order.copy()

    order.update(
        {
            "distance_km": 1.0,
            "items": 1,
            "hour": 14,
            "prep_minutes": 5,
            "courier_months": 60,
            "weather": "clear",
            "day_type": "weekday",
            "vehicle": "car",
        }
    )

    result = predict_order(order)

    assert result["late_probability"] < result["threshold"]
    assert result["issue_voucher"] is False
    assert result["voucher_amount"] == 0.0


def test_harder_order_has_higher_late_probability(valid_order):
    """Check that a harder delivery has greater predicted late risk."""
    easy_order = valid_order.copy()
    easy_order.update(
        {
            "distance_km": 1.0,
            "items": 1,
            "hour": 14,
            "prep_minutes": 5,
            "courier_months": 60,
            "weather": "clear",
            "day_type": "weekday",
            "vehicle": "car",
        }
    )

    hard_order = valid_order.copy()
    hard_order.update(
        {
            "distance_km": 8.0,
            "items": 4,
            "hour": 18,
            "prep_minutes": 25,
            "courier_months": 12,
            "weather": "rain",
            "day_type": "weekday",
            "vehicle": "bike",
        }
    )

    easy_result = predict_order(easy_order)
    hard_result = predict_order(hard_order)

    assert hard_result["late_probability"] > easy_result["late_probability"]


def test_prediction_uses_saved_threshold(valid_order):
    """Check that predictions use the threshold saved in model metadata."""
    from predict import THRESHOLD

    result = predict_order(valid_order)

    assert result["threshold"] == THRESHOLD
    assert result["threshold"] == 0.30

    expected_decision = result["late_probability"] >= THRESHOLD

    assert result["issue_voucher"] == expected_decision


def test_missing_preparation_time(valid_order):
    """Check that missing preparation time is handled correctly."""
    order = valid_order.copy()
    order["prep_minutes"] = None

    result = predict_order(order)

    assert 0.0 <= result["late_probability"] <= 1.0
    assert len(result["warnings"]) > 0

    warning_text = " ".join(result["warnings"]).lower()

    assert "prep_minutes" in warning_text


@pytest.mark.parametrize(
    "feature, invalid_value",
    [
        ("distance_km", 50),
        ("items", 25),
        ("hour", 25),
        ("prep_minutes", 75),
        ("courier_months", 150),
    ],
)
def test_invalid_numeric_inputs(valid_order, feature, invalid_value):
    """Check that invalid numeric inputs are rejected."""
    order = valid_order.copy()
    order[feature] = invalid_value

    with pytest.raises(ValueError, match=feature):
        predict_order(order)


@pytest.mark.parametrize(
    "feature, invalid_value",
    [
        ("weather", "storm"),
        ("weather", "Snow"),
        ("day_type", "holiday"),
        ("vehicle", "helicopter"),
    ],
)
def test_invalid_categorical_inputs(valid_order, feature, invalid_value):
    """Check that unsupported categories are rejected."""
    order = valid_order.copy()
    order[feature] = invalid_value

    with pytest.raises(ValueError, match=feature):
        predict_order(order)


@pytest.mark.parametrize("offset, expected", [(-1e-9, False), (0, True), (1e-9, True)])
def test_threshold_boundary(offset, expected):
    from predict import THRESHOLD, voucher_decision

    assert voucher_decision(THRESHOLD + offset) is expected


@pytest.mark.parametrize(
    "feature, value",
    [
        ("distance_km", None),
        ("distance_km", float("nan")),
        ("distance_km", float("inf")),
        ("distance_km", True),
        ("items", 1.5),
        ("hour", 18.5),
        ("weather", None),
        ("vehicle", "Car"),
    ],
)
def test_invalid_missing_and_nonfinite_inputs(valid_order, feature, value):
    valid_order[feature] = value
    with pytest.raises(ValueError, match=feature):
        predict_order(valid_order)


@pytest.mark.parametrize("missing", [None, "", "  "])
def test_optional_preparation_variants(valid_order, missing):
    valid_order["prep_minutes"] = missing
    result = predict_order(valid_order)
    assert 0 <= result["late_probability"] <= 1
    assert "prep_minutes" in result["warnings"][0]


def test_saved_pipeline_matches_metadata():
    from predict import FEATURE_COLUMNS, MODEL, THRESHOLD

    assert list(MODEL.feature_names_in_) == FEATURE_COLUMNS
    assert list(MODEL.classes_) == [0, 1]
    assert 0 <= THRESHOLD <= 1
