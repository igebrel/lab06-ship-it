import gradio as gr
import pytest

from app import run_prediction


def test_app_valid_order(valid_order):
    probability, decision, warning = run_prediction(**valid_order)
    assert probability.endswith("%")
    assert decision in ("Issue $4 voucher", "No voucher required")
    assert warning == "No warnings."


def test_app_invalid_order_shows_field_error(valid_order):
    valid_order["distance_km"] = -1
    with pytest.raises(gr.Error, match="distance_km"):
        run_prediction(**valid_order)


def test_app_missing_preparation_shows_warning(valid_order):
    valid_order["prep_minutes"] = None
    assert "prep_minutes" in run_prediction(**valid_order)[2]
