
---
title: QuickBite Late Order Check
emoji: 🚚
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 6.31.0
python_version: 3.11
app_file: app.py
pinned: false
short_description: Predict late deliveries and voucher decisions.
---

# QuickBite Late Order Check

This application predicts the probability that a QuickBite
food delivery order will arrive late.

It uses a trained machine learning model and a saved
decision threshold to determine whether a customer
should receive a $4 voucher.


## How to Run Locally

Use Python 3.11. Clone the repository and install the local application and test
requirements (core requirements alone do not include Gradio).

```bash
git clone https://github.com/igebrel/lab06-ship-it.git
cd lab06-ship-it
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

On Windows, activate with `.venv\Scripts\activate` instead. Alternatively:

```bash
conda env create -f environment.yml
conda activate lab06-ship-it
```

Launch the application:

```bash
python app.py
```

Open the local URL printed in the terminal, usually http://127.0.0.1:7860.
The instructor's reload command is also supported:

```bash
gradio app.py
```

The existing Lab 05 pipeline is loaded from `models/late_orders.joblib`;
no training is needed. Only load trusted joblib artifacts.

## Deployment Status

Hugging Face deployment is postponed until the GitHub repository is finalized.
No public Space URL has been verified for this revision. The existing Space
settings block is retained for later deployment. Local execution is supported;
GitHub hosts the source, not a running Gradio application. An exemption based
on all members being unable to create a Space has not been verified.

## Team

| Member | Actual contribution |
|---|---|
| Ibrahim Gebrel | Initial repository implementation: saved model integration, prediction and validation logic, Gradio interface, automated tests, environment configuration, and documentation. |
| Muharrem Kaya (`matthewkaya`) | Reviewed saved model/metadata consistency; pinned direct dependencies; shared categorical choices between validation and UI; added boundary, validation, model consistency and UI error tests; corrected local-run instructions, deployment status, verification and team documentation. |

Other member names and contributions have not been confirmed and are not
attributed here. The team must confirm the complete roster before submission.

## Requirements Review

The supplied assignment PDF is **AIGC 5005 Midterm Project: Predict No-Shows**
(Maple Physio), not the QuickBite Lab 06 handout. Its separate training, classes,
and dataset requirements have not been substituted for this Lab 06 project.
Full Lab 06 rubric compliance remains unverified until the correct handout is
available. The available Lab 06 announcement provides this provisional checklist:

| Requirement | Evidence / status |
|---|---|
| Existing Lab 05 pipeline and metadata | Saved artifacts retained; feature order and threshold checked by tests. |
| Matching inputs, validation and optional preparation warning | Eight metadata features; numeric/category checks and missing-value tests. |
| Local Gradio application | `app.py`; launch commands above. |
| Required quality checks | Commands and observed results in Tests below. |
| Reproducible direct dependencies | Pinned requirements, Python 3.11 Conda environment; transitive dependencies are not locked. |
| Member contributions | Confirmed contributions above; complete roster and each member's participation unverified. |
| Public Space or confirmed exemption | Pending separate deployment work; neither verified. |

## Decisions

### Input Features

The QuickBite model uses eight input features to estimate
the probability of a late food delivery.

| Feature | Valid Values | Description |
|---|---|---|
| distance_km | 0.1–30 | Delivery distance in kilometres |
| items | 1–20 | Number of items in the order |
| hour | 10–22 | Order hour in 24-hour format |
| prep_minutes | 1–60 or blank | Restaurant preparation time |
| courier_months | 0–120 | Courier experience in months |
| weather | clear, rain, snow | Weather conditions |
| day_type | weekday, weekend | Type of day |
| vehicle | bike, scooter, car | Courier transportation |

### Voucher Decision Rule

The application uses a decision threshold of 0.30,
which was selected during Lab 05 model evaluation.

- If the predicted late-delivery probability is
  greater than or equal to 0.30, issue a $4 voucher.
- If the probability is below 0.30, do not issue a voucher.

The application displays the predicted probability,
the voucher decision, and the decision threshold.

### Missing Preparation Time

Preparation time is optional. When this field is left
blank, the saved machine learning pipeline handles
the missing value through its preprocessing procedure.

The application also displays a warning informing
the user that the preparation time was not provided.



## Result

### Model Evaluation

Results below are transcribed from `models/model_info.json`. The Lab 05
training data and evaluation script are not included, so the metrics cannot be
independently recomputed here. Artifact consistency checks do not establish
that the original evaluation avoided leakage.

The QuickBite application uses the trained machine learning
pipeline developed in Lab 05.

The saved model was evaluated using a 25% test split
and a decision threshold of 0.30.

| Evaluation Metric | Result |
|---|---:|
| Precision | 0.4907 |
| Recall | 0.4530 |
| F1-score | 0.4711 |
| ROC-AUC | 0.7962 |
| Decision threshold | 0.30 |

### Confusion Matrix

| | Predicted On Time | Predicted Late |
|---|---:|---:|
| Actual On Time | 578 | 55 |
| Actual Late | 64 | 53 |

### Business Cost Comparison

The Lab 05 evaluation compared three voucher strategies
using the assignment's business cost assumptions.

| Strategy | Estimated Cost |
|---|---:|
| Flag nobody | $1,755 |
| Flag everybody | $3,000 |
| Use the trained model | $1,392 |

The trained model reduced the estimated business cost
by $363 compared with flagging nobody.

This represents approximately 20.7% cost savings
under the Lab 05 evaluation assumptions.

These results are based on the held-out test dataset.
They do not guarantee the same performance or savings
for future real-world deliveries.


## Limitations

The QuickBite application demonstrates how machine learning
can support food delivery decisions. However, several
limitations should be considered.

1. **Dataset limitations:** The model was developed using
   synthetic delivery data. Its performance may differ
   when applied to real customer orders.

2. **Prediction uncertainty:** The predicted probability
   represents an estimate, not a guarantee that an order
   will arrive late.

3. **Limited input features:** The model uses eight features.
   Other factors, such as traffic congestion, restaurant
   workload, and unexpected road closures, are not directly
   included.

4. **Missing preparation time:** When preparation time is
   unavailable, the saved preprocessing pipeline handles
   the missing value. This may affect prediction accuracy.

5. **Decision threshold:** The 0.30 threshold was selected
   using Lab 05 evaluation assumptions. Different business
   costs or operating conditions may require a new threshold.

6. **Real-world validation:** The application is an academic
   prototype. Additional testing, monitoring, and validation
   would be necessary before using it in a production
   delivery service.


## Tests

The QuickBite application includes automated tests
using pytest and code-quality checks using Ruff.

### Prediction Tests

The prediction tests verify:

- Predicted probabilities are between 0 and 1.
- High-risk orders trigger a $4 voucher.
- Low-risk orders do not trigger a voucher.
- Higher-risk orders produce higher late-delivery probabilities.
- The saved model's decision threshold is used.
- Missing preparation time is handled correctly.
- Invalid numerical inputs are rejected.
- Invalid categorical inputs are rejected.

### Deployment Tests

The deployment tests verify:

- The installed scikit-learn version matches the saved model.
- The scikit-learn version in requirements.txt matches the model.
- Gradio is excluded from the core requirements.txt file.

### Run the Tests

```bash
python -m pytest -v
python -m ruff format --check .
python -m ruff check .
```

### Verified Results

- 38 automated pytest test cases passed.
- Ruff code-quality checks passed.
- Python formatting was verified using Ruff.

Checks used the existing Python 3.11 environment, not a newly installed Conda
environment. A clean source export was also checked using those dependencies.

These tests help confirm that the application behaves
consistently and that its dependencies are configured
correctly.



## References

Gradio. (n.d.). *Gradio documentation*.
https://www.gradio.app/docs

Hugging Face. (n.d.). *Spaces overview*.
https://huggingface.co/docs/hub/spaces-overview

Hugging Face. (n.d.). *Gradio Spaces*.
https://huggingface.co/docs/hub/spaces-sdks-gradio

pytest. (n.d.). *pytest documentation*.
https://docs.pytest.org/

Ruff. (n.d.). *Ruff documentation*.
https://docs.astral.sh/ruff/

Scikit-learn developers. (n.d.). *Scikit-learn user guide*.
https://scikit-learn.org/stable/user_guide.html
