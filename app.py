import gradio as gr

from predict import FEATURE_COLUMNS, THRESHOLD, predict_order


def run_prediction(
    distance_km,
    items,
    hour,
    prep_minutes,
    courier_months,
    weather,
    day_type,
    vehicle,
):
    """Validate an order and display its predicted late-delivery risk."""
    values = {
        "distance_km": distance_km,
        "items": items,
        "hour": hour,
        "prep_minutes": prep_minutes,
        "courier_months": courier_months,
        "weather": weather,
        "day_type": day_type,
        "vehicle": vehicle,
    }

    order = {feature: values[feature] for feature in FEATURE_COLUMNS}

    try:
        result = predict_order(order)
    except (ValueError, TypeError) as error:
        raise gr.Error(str(error)) from error

    probability = f"{result['late_probability']:.2%}"

    decision = "Issue $4 voucher" if result["issue_voucher"] else "No voucher required"

    warnings = result.get("warnings", [])
    warning_message = (
        "**Warning:** " + "\n\n".join(warnings) if warnings else "No warnings."
    )

    return probability, decision, warning_message


with gr.Blocks(title="QuickBite Late Order Check") as demo:
    gr.Markdown("# 🚚 QuickBite Late Order Check")

    gr.Markdown(
        "### AI-Powered Late Delivery Prediction\n"
        "Enter the delivery details to estimate the probability "
        "of a late arrival and determine whether a $4 voucher "
        "should be issued."
    )

    gr.Markdown(f"**Decision threshold:** {THRESHOLD:.0%} late-delivery probability")

    gr.Markdown("### 📦 Delivery Order Details")

    with gr.Row():
        distance_km = gr.Number(
            label="Delivery Distance (km)",
            value=5.0,
            minimum=0.1,
            maximum=30.0,
            step=0.1,
            info="Allowed range: 0.1–30 km",
        )

        items = gr.Number(
            label="Number of Items",
            value=3,
            minimum=1,
            maximum=20,
            step=1,
            precision=0,
            info="Allowed range: 1–20 items",
        )

    with gr.Row():
        hour = gr.Number(
            label="Order Hour (24-hour format)",
            value=18,
            minimum=10,
            maximum=22,
            step=1,
            precision=0,
            info="Allowed range: 10–22",
        )

        prep_minutes = gr.Number(
            label="Preparation Time (minutes)",
            value=20,
            minimum=1,
            maximum=60,
            step=1,
            info="Allowed range: 1–60 minutes. Optional: leave blank.",
        )

    courier_months = gr.Number(
        label="Courier Experience (months)",
        value=12,
        minimum=0,
        maximum=120,
        step=1,
        info="Allowed range: 0–120 months",
    )

    with gr.Row():
        weather = gr.Dropdown(
            choices=["clear", "rain", "snow"],
            label="Weather Conditions",
            value="clear",
            info="Select the weather conditions for the delivery.",
        )

        day_type = gr.Dropdown(
            choices=["weekday", "weekend"],
            label="Day Type",
            value="weekday",
            info="Select whether the order is on a weekday or weekend.",
        )

        vehicle = gr.Dropdown(
            choices=["bike", "scooter", "car"],
            label="Delivery Vehicle Type",
            value="bike",
            info="Select the vehicle used for the delivery.",
        )

    gr.Markdown("### 🔍 Late Delivery Prediction")

    predict_button = gr.Button(
        value="Predict Late Delivery",
        variant="primary",
    )

    gr.Markdown("### 📊 Prediction Results")

    late_probability_output = gr.Textbox(
        label="Late Delivery Probability",
        interactive=False,
    )

    voucher_decision_output = gr.Textbox(
        label="Voucher Decision",
        interactive=False,
    )

    warning_output = gr.Markdown()

    predict_button.click(
        fn=run_prediction,
        inputs=[
            distance_km,
            items,
            hour,
            prep_minutes,
            courier_months,
            weather,
            day_type,
            vehicle,
        ],
        outputs=[
            late_probability_output,
            voucher_decision_output,
            warning_output,
        ],
    )


if __name__ == "__main__":
    demo.launch()
