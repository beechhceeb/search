from typing import Any
from unittest.mock import patch
from uuid import UUID

from flask.testing import FlaskClient

from albatross.repository.base_repository import AlbatrossRepository


def test_process_exif_and_recall_flow(
    client: FlaskClient,
    exif_data: dict[str, object],
    repository: AlbatrossRepository,
) -> None:
    """Ensure EXIF upload persists recommendations and recall retrieves them."""
    with patch("app.repository", repository):
        # POST the EXIF data
        response = client.post("/process-exif", json={"exifData": [exif_data]})
        assert response.status_code == 200

        data = response.get_json()
        assert data is not None
        rec_id = UUID(data["additional_data"]["recommendations_id"])

        # Verify the recommendation was persisted
        result = repository.get_recommendation(rec_id)
        print(f"[test] Result of get_recommendation: {result}")
        assert result is not None

        # Recall the recommendation
        recall_response = client.get(f"/recall/{rec_id}")
        assert recall_response.status_code == 200


def test_llm_recommendations_endpoint(
    client: FlaskClient,
    repository: AlbatrossRepository,
    recommendations_with_llm_response: dict[str, object],
) -> None:
    """Check that the LLM recommendations endpoint renders HTML."""
    with patch("app.repository", repository):
        persisted = repository.persist(recommendations_with_llm_response)

        response = client.get(f"/llm-recommendations/{persisted.id}")
        assert response.status_code == 200
        assert "Recommended Lens Upgrades" in response.get_data(as_text=True)


def test_index_route_returns_main_page(client: FlaskClient) -> None:
    """Ensure the index page renders correctly."""
    response = client.get("/")
    assert response.status_code == 200
    assert "What kind of photographer are you?" in response.get_data(as_text=True)


def test_recall_index_route(client: FlaskClient) -> None:
    """Ensure the index page renders with the provided recommendations id."""
    rec_id = "123e4567-e89b-12d3-a456-426614174000"
    response = client.get(f"/{rec_id}")
    assert response.status_code == 200
    assert rec_id in response.get_data(as_text=True)


def test_clear_lm_cache_endpoint(client: FlaskClient, tmp_path: Any) -> None:
    """Verify that the clear-lm-cache endpoint removes the cache file."""
    fake_cache = tmp_path / "cache.json"
    fake_cache.write_text("{}")
    with patch("app.CACHE_FILE", fake_cache.as_posix()):
        assert fake_cache.exists()
        response = client.delete("/clear-lm-cache")
        assert response.status_code == 200
        assert not fake_cache.exists()


def test_test_badges_endpoint(client: FlaskClient) -> None:
    """Ensure the test-badges endpoint returns badge HTML."""
    response = client.get("/test-badges")
    assert response.status_code == 200
    assert "The Bokeh Master" in response.get_data(as_text=True)
