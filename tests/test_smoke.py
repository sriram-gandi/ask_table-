"""Basic repository smoke tests."""


def test_project_imports_as_expected() -> None:
    """Keep CI meaningful even before the full integration suite is added."""
    from app.agents.state import AnalysisState

    assert AnalysisState is not None
