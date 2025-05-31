from unittest.mock import MagicMock, Mock, patch

import pytest

from albatross.controller import (
    analyse_extracted_data,
    handle_uploaded_exif,
)
from albatross.models.image_exif import ImageExif
from albatross.models.metrics import Metrics
from albatross.models.recommendations import Recommendations
from albatross.models.results import Results
from albatross.repository.base_repository import AlbatrossRepository
from albatross.services.metrics import MetricsService
from albatross.services.recommendation import RecommendationService
from fixtures import repository


@pytest.fixture
def mock_config() -> MagicMock:  # type: ignore
    with patch("albatross.config") as mock_config:
        mock_config.LOCAL_STORAGE_DIR = "/mock/dir"
        mock_config.SUPPORTED_FILETYPES = ["jpg", "jpeg"]
        yield mock_config


def test_analyse_extracted_data(
    image_exif: ImageExif, repository: AlbatrossRepository
) -> None:
    # Given a list of mock exif data
    mock_exif_data: list[ImageExif] = [image_exif, image_exif]
    mock_metrics: Metrics = MetricsService.from_exif(mock_exif_data)
    mock_results: Results = Results.build(mock_metrics)
    mock_recommendations: Recommendations = RecommendationService.build(
        mock_results, repo=repository
    )

    with (
        patch(
            "albatross.services.metrics.MetricsService.from_exif",
            return_value=mock_metrics,
        ),
        patch(
            "albatross.services.recommendation.RecommendationService.build",
            return_value=mock_recommendations,
        ),
    ):
        # When we call analyse_extracted_data
        result: Recommendations = analyse_extracted_data(
            mock_exif_data, repo=repository, call_llm=False
        )

        # Then we expect the results to be returned
        assert mock_recommendations == result


@pytest.fixture
def raw_exif_json() -> dict[str, list[dict[str, str]]]:
    return {
        "exifData": [
            {"Tag1": "Value1", "Tag2": "Value2"},
            {"Tag3": "Value3", "Tag4": "Value4"},
        ]
    }


@pytest.fixture
def mapped_exif_data() -> list[dict[str, str]]:
    return [
        {"MappedTag1": "MappedValue1", "MappedTag2": "MappedValue2"},
        {"MappedTag3": "MappedValue3", "MappedTag4": "MappedValue4"},
    ]


@pytest.fixture
def mock_image_exif() -> ImageExif:
    return MagicMock(spec=ImageExif)


@pytest.fixture
def mock_recommendations() -> Recommendations:
    return MagicMock(spec=Recommendations)


@patch("albatross.controller.EXIF_WHITELIST", new=["Tag1", "Tag2", "Tag3", "Tag4"])
@patch("albatross.controller.ImageExifService.from_exif")
@patch("albatross.controller.analyse_extracted_data")
def test_handle_uploaded_exif(
    mock_analyse_extracted_data: MagicMock,
    mock_from_exif: MagicMock,
    raw_exif_json: dict[str, list[dict[str, str]]],
    mapped_exif_data: list[dict[str, str]],
    mock_image_exif: ImageExif,
    mock_recommendations: Recommendations,
) -> None:
    # Given: Mock dependencies
    mock_from_exif.return_value = mock_image_exif
    mock_analyse_extracted_data.return_value = mock_recommendations

    # When: Call the function
    result = handle_uploaded_exif(raw_exif_json, repo=repository)

    # Then: Assert the behavior
    mock_from_exif.assert_called()
    assert mock_from_exif.call_count == len(mapped_exif_data)
    mock_analyse_extracted_data.assert_called_once_with(
        [mock_image_exif] * len(mapped_exif_data),
        call_llm=True,
        repo=repository,
    )
    assert result == mock_recommendations


@patch("albatross.controller.EXIF_WHITELIST", new=["Tag1", "Tag2", "Tag3", "Tag4"])
@patch("albatross.controller.ImageExifService.from_exif")
@patch("albatross.controller.analyse_extracted_data")
def test_handle_uploaded_exif_mocked(
    mock_analyse_extracted_data: Mock,
    mock_from_exif: Mock,
    repository: AlbatrossRepository,
) -> None:
    # Given: Mocked dependencies and input data
    raw_exif_json = {
        "exifData": [
            {"Tag1": "Value1", "Tag2": "Value2"},
            {"Tag3": "Value3", "Tag4": "Value4"},
        ]
    }
    mock_image_exif = MagicMock(spec=ImageExif)
    mock_recommendations = MagicMock(spec=Recommendations)

    mock_from_exif.side_effect = [mock_image_exif, mock_image_exif]
    mock_analyse_extracted_data.return_value = mock_recommendations

    # When: The function is called
    result = handle_uploaded_exif(raw_exif_json, repo=repository)

    # Then: Assert the expected behavior
    assert mock_from_exif.call_count == len(raw_exif_json["exifData"])
    mock_from_exif.assert_any_call(
        {"Tag1": "Value1", "Tag2": "Value2"}, filename="", repo=repository
    )
    mock_from_exif.assert_any_call(
        {"Tag3": "Value3", "Tag4": "Value4"}, filename="", repo=repository
    )
    mock_analyse_extracted_data.assert_called_once_with(
        [mock_image_exif, mock_image_exif],
        call_llm=True,
        repo=repository,
    )
    assert result == mock_recommendations
