"""Prediction and validation logic for the QuickBite late-order checker."""

import json
import math
from pathlib import Path

import joblib
import pandas as pd

MODEL_DIR = Path(__file__).resolve().parent / "models"
MODEL_PATH = MODEL_DIR / "late_orders.joblib"
METADATA_PATH = MODEL_DIR / "model_info.json"

# Load both saved artifacts once when this module is imported.
with METADATA_PATH.open("r", encoding="utf-8") as file:
    MODEL_INFO = json.load(file)

MODEL = joblib.load(MODEL_PATH)

FEATURE_COLUMNS = MODEL_INFO["feature_columns"]
THRESHOLD = float(MODEL_INFO["threshold"])
VOUCHER_COST = 4.0

NUMERIC_RANGES = {
    "distance_km": (0.1, 30),
    "items": (1, 20),
    "hour": (10, 22),
    "prep_minutes": (1, 60),
    "courier_months": (0, 120),
}

INTEGER_FEATURES = {"items", "hour"}

CATEGORY_CHOICES = {
    "weather": ("clear", "rain", "snow"),
    "day_type": ("weekday", "weekend"),
    "vehicle": ("bike", "scooter", "car"),
}


def validate_order(order: dict) -> tuple[dict, list[str]]:
    """Validate an order and return cleaned values and warnings."""
    if not isinstance(order, dict):
        raise ValueError("Order information must be a dictionary.")

    cleaned = {}
    warnings = []

    for feature in FEATURE_COLUMNS:
        if feature not in NUMERIC_RANGES and feature not in CATEGORY_CHOICES:
            raise ValueError(f"Unsupported model feature: {feature}")

        value = order.get(feature)

        if feature == "prep_minutes" and (
            value is None or (isinstance(value, str) and not value.strip())
        ):
            cleaned[feature] = float("nan")
            warnings.append(
                "prep_minutes was left blank. "
                "The model will estimate it using the training-data median."
            )
            continue

        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValueError(f"{feature} is required.")

        if feature in CATEGORY_CHOICES:
            if not isinstance(value, str) or value not in CATEGORY_CHOICES[feature]:
                choices = ", ".join(CATEGORY_CHOICES[feature])
                raise ValueError(
                    f"{feature} must be one of: {choices}. "
                    "Use the exact lowercase spelling."
                )
            cleaned[feature] = value
            continue

        if isinstance(value, bool):
            raise ValueError(f"{feature} must be a number.")

        try:
            number = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{feature} must be a number.") from exc

        if not math.isfinite(number):
            raise ValueError(f"{feature} must be a finite number.")

        minimum, maximum = NUMERIC_RANGES[feature]
        if not minimum <= number <= maximum:
            raise ValueError(f"{feature} must be between {minimum} and {maximum}.")

        if feature in INTEGER_FEATURES:
            if not number.is_integer():
                raise ValueError(f"{feature} must be a whole number.")
            cleaned[feature] = int(number)
        else:
            cleaned[feature] = number

    return cleaned, warnings


def voucher_decision(probability: float, threshold: float | None = None) -> bool:
    """Return True when the order qualifies for a $4 voucher."""
    if threshold is None:
        threshold = THRESHOLD

    if not math.isfinite(probability) or not 0 <= probability <= 1:
        raise ValueError("Probability must be between 0 and 1.")

    if not math.isfinite(threshold) or not 0 <= threshold <= 1:
        raise ValueError("Threshold must be between 0 and 1.")

    return probability >= threshold


def predict_order(order: dict) -> dict:
    """Score an order and return the probability and voucher decision."""
    cleaned, warnings = validate_order(order)

    # Preserve the exact feature order used during model training.
    frame = pd.DataFrame([cleaned], columns=FEATURE_COLUMNS)
    probability = float(MODEL.predict_proba(frame)[0, 1])
    issue_voucher = voucher_decision(probability)

    return {
        "late_probability": probability,
        "on_time_probability": 1.0 - probability,
        "threshold": THRESHOLD,
        "issue_voucher": issue_voucher,
        "voucher_amount": VOUCHER_COST if issue_voucher else 0.0,
        "warnings": warnings,
    }
