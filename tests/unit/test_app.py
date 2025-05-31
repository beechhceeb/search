import json
from typing import Any
from unittest.mock import Mock, patch
from uuid import UUID


from albatross.config import EXIF_WHITELIST
from albatross.models.recommendations import Recommendations
from albatross.repository.base_repository import AlbatrossRepository


def test_index_route(client: Any) -> None:
    # Given: The Flask app is running
    # When: Sending a GET request to the index route
    response = client.get("/")

    # Then: The response should be 200 OK and contain the expected content
    assert response.status_code == 200


def test_recall_route(client: Any) -> None:
    # Given: A valid recommendations_id
    recommendations_id = "123e4567-e89b-12d3-a456-426614174000"

    # When: Sending a GET request to the recall route
    response = client.get(f"/{recommendations_id}")

    # Then: The response should be 200 OK and contain the recommendations_id
    assert response.status_code == 200
    assert recommendations_id.encode() in response.data


def test_process_exif_route(
    client: Any, exif_data: dict[str, Any], repository: AlbatrossRepository
) -> None:
    # FIXME: really stretching the definition of a unit test with this one
    #  most of my unit tests are really integration tests
    # Given: Valid EXIF data

    # When: Sending a POST request to the process-exif route
    response = client.post("/process-exif", json={"exifData": [exif_data]})

    # Then: The response should be 200 OK and contain the expected JSON keys
    assert response.status_code == 200


@patch("app.handle_uploaded_exif")
def test_process_exif_route_with_llm_response(
    mock_handle_exif: Mock,
    client: Any,
    recommendations_with_llm_response: Recommendations,
) -> None:
    # Given a recommendations object, with an llm response
    mock_handle_exif.return_value = recommendations_with_llm_response
    # When: Sending a POST request to the process-exif route
    response = client.post("/process-exif", json={"exifData": [{}]})

    # Then: The response should be 200 OK
    assert response.status_code == 200


def test_health_check_route(client: Any) -> None:
    # Given: The Flask app is running
    # When: Sending a GET request to the health check route
    response = client.get("/healthz")

    # Then: The response should be 200 OK
    assert response.status_code == 200


def test_get_recalled_recommendations_route(
    client: Any,
    repository: AlbatrossRepository,
    recommendations_without_llm_response: Recommendations,
) -> None:
    # Given: we persist a recommendations object in the database
    recommendations_id: UUID = repository.persist(recommendations_without_llm_response)

    # When: Sending a GET request to the recall route with that recommendations_id
    response = client.get(f"/recall/{recommendations_id}")

    # Then: The response should be 200 OK
    assert response.status_code == 200


def test_get_recalled_recommendations_route_when_recommendations_not_found(
    client: Any,
) -> None:
    # Given: A non-existent recommendations_id
    recommendations_id = "123e4567-e89b-12d3-a456-426614174000"

    # When: Sending a GET request to the recall route
    response = client.get(f"/recall/{recommendations_id}")

    # Then: The response should be 200
    assert response.status_code == 200


def test_test_badges_route(client: Any) -> None:
    # Given: The Flask app is running
    # When: Sending a GET request to the test-badges route
    response = client.get("/test-badges")

    # Then: The response should be 200 OK and contain badges
    assert response.status_code == 200


def test_get_exif_whitelist(client: Any) -> None:
    # Given: The Flask app is running
    # When: Sending a GET request to the /exif-whitelist route
    response = client.get("/exif-whitelist")

    # Then: The response should be 200 OK and contain the expected content
    assert response.status_code == 200
    assert EXIF_WHITELIST == json.loads(response.data)


def test_swagger(client: Any) -> None:
    # Given: The Flask app is running
    # When: Sending a GET request to the /swagger.json route
    response = client.get("/swagger")

    # Then: The response should be 200 OK and contain the expected content
    assert response.status_code == 200
    assert "swagger" in response.text
