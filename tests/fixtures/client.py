from typing import Any

import pytest

from app import create_app


@pytest.fixture
def app() -> Any:
    """Fixture to create the Flask app for testing."""
    return create_app()


@pytest.fixture
def client(app: Any) -> Any:
    """Fixture to create a test client for the Flask app."""
    return app.test_client()
