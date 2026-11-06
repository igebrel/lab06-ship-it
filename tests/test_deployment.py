from pathlib import Path

import gradio
import sklearn

from predict import MODEL_INFO


def test_sklearn_version_matches_model():
    """Verify that the installed scikit-learn version matches the model."""
    saved_version = MODEL_INFO["sklearn_version"]
    installed_version = sklearn.__version__

    assert installed_version == saved_version


def test_requirements_sklearn_version_matches_model():
    """Verify requirements.txt pins the saved model's sklearn version."""
    requirements_path = Path(__file__).resolve().parents[1] / "requirements.txt"

    requirements = requirements_path.read_text(encoding="utf-8")

    expected_version = MODEL_INFO["sklearn_version"]

    assert f"scikit-learn=={expected_version}" in requirements


def test_gradio_not_in_core_requirements():
    """Check that Gradio is excluded from core model dependencies."""
    requirements_path = Path(__file__).resolve().parents[1] / "requirements.txt"

    requirements = requirements_path.read_text(encoding="utf-8").splitlines()

    assert not any(line.strip().lower().startswith("gradio") for line in requirements)


def test_readme_gradio_version_matches_installed():
    """Verify Hugging Face uses the installed Gradio version."""
    readme_path = Path(__file__).resolve().parents[1] / "README.md"

    readme = readme_path.read_text(encoding="utf-8")

    expected_version = gradio.__version__

    assert f"sdk_version: {expected_version}" in readme


def test_readme_app_file_exists():
    """Verify that the Hugging Face application entry point exists."""
    project_root = Path(__file__).resolve().parents[1]
    readme = (project_root / "README.md").read_text(encoding="utf-8")

    app_file = None

    for line in readme.splitlines():
        if line.startswith("app_file:"):
            app_file = line.split(":", 1)[1].strip()
            break

    assert app_file is not None, "README.md must define app_file"
    assert (project_root / app_file).is_file(), (
        f"Application file does not exist: {app_file}"
    )
