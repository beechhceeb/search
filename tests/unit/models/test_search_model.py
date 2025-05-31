from requests import Response

from albatross.models.search import SearchResultModel, SearchResponse


def test_search_result_model_init(
    search_requests_get_response: Response,
) -> None:
    """
    Test the SearchResultModel class initialization.
    """
    # Given: A mock response from the search service
    model = SearchResultModel(
        model_name="A7 iii",
        model_id="12345",
        image_link="/media-service/a450727b-b7ae-4c0f-8dde-413e5106ea09",
        model_url_segment="/sony-a7-iii",
        price=12345,
    )

    assert model.model_name == "A7 iii"
    assert model.model_id == "12345"
    assert model.image_link == "/media-service/a450727b-b7ae-4c0f-8dde-413e5106ea09"
    assert model.model_url_segment == "/sony-a7-iii"
    assert model.price == 12345.0


def test_to_dict(
    search_requests_get_response: Response,
) -> None:
    """
    Test the to_dict method of SearchResultModel.
    """
    # Given: A mock response from the search service
    model = SearchResultModel(
        model_name="A7 iii",
        model_id="12345",
        image_link="/media-service/a450727b-b7ae-4c0f-8dde-413e5106ea09",
        model_url_segment="/sony-a7-iii",
        price=12345,
    )

    # When: Convert the model to a dictionary
    result_dict = model.to_dict()

    # Then: Assert the dictionary contains the expected values
    assert result_dict["model_name"] == "A7 iii"
    assert result_dict["model_id"] == "12345"
    assert (
        result_dict["image_link"]
        == "/media-service/a450727b-b7ae-4c0f-8dde-413e5106ea09"
    )
    assert result_dict["model_url_segment"] == "/sony-a7-iii"
    assert result_dict["price"] == 12345.0


def test_from_dict(
    search_requests_get_response: Response,
) -> None:
    """
    Test the from_dict method of SearchResultModel.
    """
    # Given: A dictionary representing a search result
    search_result_input = {
        "model_name": "A7 iii",
        "model_id": "12345",
        "image_link": "/media-service/a450727b-b7ae-4c0f-8dde-413e5106ea09",
        "model_url_segment": "/sony-a7-iii",
        "price": 12345,
    }

    # When: Create a SearchResultModel instance from the dictionary
    model = SearchResultModel.from_dict(search_result_input)

    # Then: Assert the model contains the expected values
    assert model.model_name == "A7 iii"
    assert model.model_id == "12345"
    assert model.image_link == "/media-service/a450727b-b7ae-4c0f-8dde-413e5106ea09"
    assert model.model_url_segment == "/sony-a7-iii"
    assert model.price == 12345.0


def test_search_response_from_json_response() -> None:
    """
    Test the SearchResponse.from_json_response method.
    """
    # Given: A mock JSON response from the search service
    json_response = {
        "results": [
            {
                "model_name": {"values": ["A7 iii"]},
                "model_id": {"values": ["12345"]},
                "model_images": {
                    "values": ["/media-service/a450727b-b7ae-4c0f-8dde-413e5106ea09"]
                },
                "model_url_segment": {"values": ["/sony-a7-iii"]},
            }
        ]
    }

    # When: Creating a SearchResponse from the JSON response
    response = SearchResponse.from_json_response(json_response)

    # Then: The response should contain a SearchResultModel with the correct values
    assert len(response.results) == 1
    model = response.results[0]
    assert model.model_name == "A7 iii"
    assert model.model_id == "12345"
    assert model.image_link == "/media-service/a450727b-b7ae-4c0f-8dde-413e5106ea09"
    assert model.model_url_segment == "/sony-a7-iii"


def test_search_response_from_json_response_with_missing_keys() -> None:
    """
    Test the SearchResponse.from_json_response method with missing keys.
    """
    # Given: A mock JSON response with missing keys
    json_response = {
        "results": [
            {
                "model_name": {"values": ["A7 iii"]},
                "model_id": {"values": ["12345"]},
                # Missing model_images and model_url_segment
            }
        ]
    }

    # When: Creating a SearchResponse from the JSON response
    response = SearchResponse.from_json_response(json_response)

    # Then: The response should contain an empty results list
    assert len(response.results) == 0
