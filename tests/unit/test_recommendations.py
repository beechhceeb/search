import json
from unittest.mock import Mock, patch

import pytest

from albatross.models.camera import Camera
from albatross.models.lens import Lens
from albatross.models.metrics import Metrics
from albatross.models.recommendations import Recommendations
from albatross.models.results import Results
from albatross.serializers.recommendations import RecommendationsSerializer
from albatross.services.recommendation import RecommendationService
from albatross.repository.base_repository import AlbatrossRepository


def test_build(results: Results, repository: AlbatrossRepository) -> None:
    # When: Building recommendations
    from albatross.services.recommendation import RecommendationService

    recommendations = RecommendationService.build(
        results, repo=repository, db_enabled=False
    )

    # Then: Verify the recommendations object
    assert recommendations.primary_camera.model == "a7 iii"
    assert recommendations.current_widest_aperture == 1.8
    assert recommendations.favourite_focal_length == 35
    assert (
        recommendations.recommended_aperture == 1.4
    )  # Assuming next smallest aperture is 1.4


def test_lenses_contains_primes_at_given_focal_length(results: Results) -> None:
    # When: Checking if lenses contain primes at given focal length
    from albatross.services.recommendation import RecommendationService

    result = RecommendationService.lenses_contains_primes_at_given_focal_length(
        50, results.metrics.lenses
    )

    # Then: Verify the result
    assert result is True


def test_metrics_contains_no_fast_lenses(results: Results) -> None:
    # When: Checking if metrics contain no fast lenses
    from albatross.services.recommendation import RecommendationService

    result = RecommendationService.metrics_contains_no_fast_lenses(
        results.metrics.lenses, 50
    )

    # Then: Verify the result
    assert result is False


def test_get_next_smallest_aperture_value() -> None:
    # When: Getting next smallest aperture value
    from albatross.services.recommendation import RecommendationService

    result: float = RecommendationService.get_next_smallest_aperture_value(1.8)

    # Then: Verify the result
    assert result == 1.4  # Assuming next smallest aperture is 1.4


def test_get_next_small_aperture_value_with_irregular_aperture() -> None:
    # When: Getting next smallest aperture value with irregular aperture
    from albatross.services.recommendation import RecommendationService

    result: float = RecommendationService.get_next_smallest_aperture_value(1.7)

    # Then: Verify the result
    assert result == 1.4  # Assuming next smallest aperture is 1.4


def test_build_recommended_focal_length_by_gaps(results: Results) -> None:
    # When: Building recommended focal length by gaps
    from albatross.services.recommendation import RecommendationService

    result = RecommendationService.build_recommended_focal_length_by_gaps(
        results.metrics.focal_range,
        35,
        results.metrics.lenses,
        results.focal_length.percentage_taken_at_lowest_value,
        results.focal_length.percentage_taken_at_highest_value,
    )

    # Then: Verify the result
    assert result == 35


def test_build_recommended_focal_length_by_gaps_wide_angle(results: Results) -> None:
    # Given: A focal range that includes wide-angle focal lengths and high percentage
    # at lowest value
    results.focal_length.focal_range = range(35, 200)
    results.focal_length.percentage_taken_at_lowest_value = 35

    # When: Building recommended focal length by gaps
    from albatross.services.recommendation import RecommendationService

    result = RecommendationService.build_recommended_focal_length_by_gaps(
        results.focal_length.focal_range,
        50,
        results.metrics.lenses,
        results.focal_length.percentage_taken_at_lowest_value,
        results.focal_length.percentage_taken_at_highest_value,
    )

    # Then: Verify the result
    assert result == 28


def test_build_recommended_focal_length_by_gaps_telephoto(results: Results) -> None:
    # Given: A focal range that includes telephoto focal lengths and high percentage at
    # highest value
    results.focal_length.focal_range = range(85, 200)
    results.focal_length.percentage_taken_at_highest_value = 35

    # When: Building recommended focal length by gaps
    from albatross.services.recommendation import RecommendationService

    result = RecommendationService.build_recommended_focal_length_by_gaps(
        results.focal_length.focal_range,
        50,
        results.metrics.lenses,
        results.focal_length.percentage_taken_at_lowest_value,
        results.focal_length.percentage_taken_at_highest_value,
    )

    # Then: Verify the result
    assert result == 135


def test_build_recommended_aperture_by_gaps_no_change(results: Results) -> None:
    # Given: percentage_wide_open and percentage_high_iso are below the limits
    percentage_wide_open = 20
    percentage_high_iso = 20
    current_widest_aperture = 2.8

    # When: Building recommended aperture by gaps
    from albatross.services.recommendation import RecommendationService

    result = RecommendationService.build_recommended_aperture_by_gaps(
        current_widest_aperture,
        percentage_wide_open,
        percentage_high_iso,
    )

    # Then: Verify the result
    assert result == current_widest_aperture


def test_build_recommended_focal_length_by_gaps_normal(results: Results) -> None:
    # Given: A focal range that includes normal focal lengths
    results.focal_length.focal_range = range(40, 60)

    # When: Building recommended focal length by gaps
    from albatross.services.recommendation import RecommendationService

    result = RecommendationService.build_recommended_focal_length_by_gaps(
        results.focal_length.focal_range,
        50,
        results.metrics.lenses,
        results.focal_length.percentage_taken_at_lowest_value,
        results.focal_length.percentage_taken_at_highest_value,
    )

    # Then: Verify the result
    assert result == 50


def test_build_recommended_focal_length_by_gaps_no_recommendation(
    results: Results,
) -> None:
    # Given: A focal range that does not match any specific recommendation criteria
    results.focal_length.focal_range = range(70, 85)
    results.focal_length.percentage_taken_at_lowest_value = 10
    results.focal_length.percentage_taken_at_highest_value = 10

    # When: Building recommended focal length by gaps
    from albatross.services.recommendation import RecommendationService

    result = RecommendationService.build_recommended_focal_length_by_gaps(
        results.focal_length.focal_range,
        50,
        results.metrics.lenses,
        results.focal_length.percentage_taken_at_lowest_value,
        results.focal_length.percentage_taken_at_highest_value,
    )

    # Then: Verify the result
    assert result is None


def test_build_recommended_aperture_by_gaps(results: Results) -> None:
    # When: Building recommended aperture by gaps
    from albatross.services.recommendation import RecommendationService

    result = RecommendationService.build_recommended_aperture_by_gaps(
        1.8,
        results.aperture.percentage_taken_at_lowest_value,
        results.iso.percentage_taken_at_highest_value,
    )

    # Then: Verify the result
    assert result == 1.4  # Assuming next smallest aperture is 1.4


def test_recommendations_build_with_camera_data(
    metrics: Metrics,
    camera: Camera,
    results: Results,
    repository: AlbatrossRepository,
) -> None:
    # Given
    metrics.cameras = [
        camera,
        camera,
    ]
    metrics.camera_frequency = {
        "a7 iii": {"frequency": 100},
    }
    results.metrics = metrics

    # When
    from albatross.services.recommendation import RecommendationService

    recommendations = RecommendationService.build(
        results=results,
        repo=repository,
        db_enabled=False,
    )

    # Then
    assert recommendations.primary_camera.model == "a7 iii"


def test_recommendations_build_with_lens_data(
    metrics: Metrics,
    camera: Camera,
    sony_fe_lens: Lens,
    results: Results,
    repository: AlbatrossRepository,
) -> None:
    # Given
    metrics.cameras = [camera]
    metrics.camera_frequency = {"a7 iii": {"frequency": 100}}
    metrics.lenses = [sony_fe_lens]
    metrics.lens_frequency = {sony_fe_lens.model: {"frequency": 100}}
    results.metrics = metrics

    # When
    from albatross.services.recommendation import RecommendationService

    recommendations = RecommendationService.build(
        results=results,
        repo=repository,
        db_enabled=False,
    )

    # Then
    assert recommendations.primary_mount_lenses[0].model == sony_fe_lens.model
    assert recommendations.current_widest_aperture == 2.8


def test_build_recommended_focal_length_by_gaps_prime(sony_fe_lens: Lens) -> None:
    # Given
    current_focal_range = range(24, 70)
    preferred_focal_length = 50
    owned_lenses = [sony_fe_lens]
    percentage_taken_at_lowest_value = 10
    percentage_taken_at_highest_value = 10

    # When
    from albatross.services.recommendation import RecommendationService

    result = RecommendationService.build_recommended_focal_length_by_gaps(
        current_focal_range=current_focal_range,
        preferred_focal_length=preferred_focal_length,
        owned_lenses=owned_lenses,
        percentage_taken_at_lowest_value=percentage_taken_at_lowest_value,
        percentage_taken_at_highest_value=percentage_taken_at_highest_value,
    )

    # Then
    assert result == 50


def test_build_recommended_focal_length_by_gaps_no_prime(results: Results) -> None:
    # Given: A preferred focal length without a prime lens
    results.focal_length.focal_range = range(24, 70)
    results.metrics.lenses = []
    preferred_focal_length = 50

    # When: Building recommended focal length by gaps
    result = RecommendationService.build_recommended_focal_length_by_gaps(
        current_focal_range=results.focal_length.focal_range,
        preferred_focal_length=preferred_focal_length,
        owned_lenses=results.metrics.lenses,
        percentage_taken_at_lowest_value=10,
        percentage_taken_at_highest_value=10,
    )

    # Then: Verify the result
    assert result == 50


def test_build_recommended_aperture_by_gaps_high_iso(results: Results) -> None:
    # Given: High ISO usage and wide-open aperture usage
    current_widest_aperture = 2.8
    percentage_wide_open = 40
    percentage_high_iso = 50

    # When: Building recommended aperture by gaps
    result = RecommendationService.build_recommended_aperture_by_gaps(
        current_widest_aperture=current_widest_aperture,
        percentage_wide_open=percentage_wide_open,
        percentage_high_iso=percentage_high_iso,
    )

    # Then: Verify the result
    assert result < current_widest_aperture


@patch("albatross.services.recommendation.GeminiService.__init__", return_value=None)
@patch(
    "albatross.services.recommendation.GeminiService.build_recommendations",
    return_value=("Lens Rec", "Camera Rec"),
)
def test_get_llm_recommendations_gemini(
    mock_build_recommendations: Mock,
    mock_init: Mock,
    results: Results,
    camera: Camera,
    lens: Lens,
    recommendations_without_llm_response: Recommendations,
) -> None:
    # Given: LLM is enabled and Gemini is the selected product
    with (
        patch("albatross.services.recommendation.LLM_ENABLED", True),
        patch("albatross.services.recommendation.LLM_PRODUCT", "gemini"),
    ):
        # When: Getting LLM recommendations
        lens_rec, camera_rec = RecommendationService.get_llm_recommendations(
            recommendations_without_llm_response
        )

    # Then: Verify the LLM recommendations
    assert lens_rec == "Lens Rec"
    assert camera_rec == "Camera Rec"


def test_to_json(results: Results, camera: Camera) -> None:
    # Given: A Recommendations object
    recommendations = Recommendations(
        primary_camera=camera,
        primary_mount_lenses=[],
        current_widest_aperture=2.8,
        favourite_focal_length=50,
        recommended_aperture=2.8,
        recommended_focal_length=50,
        recommendation_statement=["Test statement"],
        results=results,
    )

    # When: Serializing to JSON
    json_data = RecommendationsSerializer.to_json(recommendations)

    # Then: Verify the JSON structure
    assert '"current_widest_aperture": 2.8' in json_data
    assert '"favourite_focal_length": 50' in json_data


def test_from_json(recommendations_without_llm_response: Recommendations) -> None:
    # Given: A JSON string representing a Recommendations object
    json_string: str = RecommendationsSerializer.to_json(
        recommendations_without_llm_response
    )

    # When: Deserializing from JSON
    actual = RecommendationsSerializer.from_json(json_string)

    # Then: Verify the Recommendations object
    assert (
        actual.current_widest_aperture
        == recommendations_without_llm_response.current_widest_aperture
    )
    assert (
        actual.favourite_focal_length
        == recommendations_without_llm_response.favourite_focal_length
    )


def test_get_from_persisted_id(
    repository: AlbatrossRepository,
    recommendations_without_llm_response: Recommendations,
) -> None:
    # Given: A persisted recommendation ID
    repository.get_recommendation = Mock(
        return_value=recommendations_without_llm_response
    )

    # When: Retrieving the recommendation
    recommendation = RecommendationService.get_from_persisted_id(
        recommendations_without_llm_response.id,
        repo=repository,
    )

    # Then: Verify the recommendation retrieval
    assert recommendation


def test_strip_dict_of_verbose_keys(results: Results, camera: Camera) -> None:
    # Given: A dictionary with verbose keys
    data = {
        "key1": "value1",
        "instances": "value2",
        "nested": {"key2": "value3", "total_images": "value4"},
    }

    # When: Stripping verbose keys
    stripped_data = RecommendationsSerializer.strip_dict_of_verbose_keys(
        ["instances", "total_images"], data
    )

    # Then: Verify the stripped dictionary
    assert "instances" not in stripped_data
    assert "total_images" not in stripped_data["nested"]


@patch(
    "albatross.services.recommendation.RecommendationService.get_llm_recommendations"
)
def test_recommendations_get_llm_recommendations_raises_not_implemented_when_llm_disabled(  # noqa: E501
    mock_get_llm_recommendations: Mock,
    recommendations_without_llm_response: Recommendations,
) -> None:
    # Given: LLM is disabled
    with patch("albatross.services.recommendation.LLM_ENABLED", False):
        # And the mocked method raises and exception
        mock_get_llm_recommendations.side_effect = NotImplementedError(
            "LLM is not enabled"
        )
        # When: Getting LLM recommendations
        Recommendations(
            primary_camera=recommendations_without_llm_response.primary_camera,
            primary_mount_lenses=recommendations_without_llm_response.primary_mount_lenses,
            current_widest_aperture=recommendations_without_llm_response.current_widest_aperture,
            favourite_focal_length=recommendations_without_llm_response.favourite_focal_length,
            recommended_aperture=recommendations_without_llm_response.recommended_aperture,
            recommended_focal_length=recommendations_without_llm_response.recommended_focal_length,
            recommendation_statement=recommendations_without_llm_response.recommendation_statement,
            results=recommendations_without_llm_response.results,
        )
        # Then: Verify the exception was raised
        with pytest.raises(NotImplementedError):
            RecommendationService.get_llm_recommendations(
                recommendations_without_llm_response
            )


def test_from_json_handles_focal_ranges(
    recommendations_without_llm_response: Recommendations,
) -> None:
    # Given: A JSON string representing a Recommendations object with focal ranges
    recommendations_without_llm_response.focal_length = Mock()
    recommendations_without_llm_response.results.metrics.focal_range = range(24, 70)
    json_string: str = RecommendationsSerializer.to_json(
        recommendations_without_llm_response
    )

    # When: Deserializing from JSON
    actual = RecommendationsSerializer.from_json(json_string)

    # Then: Verify the focal ranges are handled correctly
    assert actual.results.metrics.focal_range == range(24, 70)


def test_to_json_abridged(
    recommendations_without_llm_response: Recommendations,
) -> None:
    # Given: A Recommendations object
    recommendations_without_llm_response.recommendation_statement = ["Test statement"]
    recommendations_without_llm_response.results.metrics.camera_frequency = {
        "a7 iii": {"frequency": 100},
    }

    # When: Serializing to JSON
    json_data = RecommendationsSerializer.to_json_abridged(
        recommendations_without_llm_response
    )

    # Then: Verify the JSON structure
    assert '"recommendation_statement": ["Test statement"]' in json_data
    assert '"camera_frequency_tracking": {"a7 iii": {"frequency": 100}}' in json_data


def test_to_json_abridged_without_focal_range(
    recommendations_without_llm_response: Recommendations,
) -> None:
    # Given: A Recommendations object without focal range
    recommendations_without_llm_response.results.metrics.focal_range = None

    # When: Serializing to JSON
    json_data = RecommendationsSerializer.to_json_abridged(
        recommendations_without_llm_response
    )

    # Then: Verify the JSON structure
    assert '"focal_range": null' in json_data


def test_get_from_persisted_id_id_not_found(
    repository: AlbatrossRepository,
    recommendations_without_llm_response: Recommendations,
) -> None:
    # Given: A persisted recommendation ID that does not exist
    repository.get_recommendation = Mock(return_value=None)

    # When/Then: Retrieving the recommendation raises an error
    with pytest.raises(ValueError):
        RecommendationService.get_from_persisted_id(
            recommendations_without_llm_response.id,
            repo=repository,
        )


@patch("albatross.services.recommendation.RecommendationService.get_from_persisted_id")
@patch(
    "albatross.services.recommendation.RecommendationService.get_llm_recommendations"
)
def test_populate_llm_recommendations_returns_existing(
    mock_get_llm: Mock,
    mock_get_from: Mock,
    recommendations_with_llm_response: Recommendations,
) -> None:
    repo = Mock(spec=AlbatrossRepository)
    mock_get_from.return_value = recommendations_with_llm_response

    result = RecommendationService.populate_llm_recommendations(
        recommendations_with_llm_response.id,
        repo=repo,
    )

    mock_get_from.assert_called_once_with(
        recommendations_with_llm_response.id, repo=repo
    )
    mock_get_llm.assert_not_called()
    repo.persist.assert_not_called()
    assert result is recommendations_with_llm_response


@patch("albatross.services.recommendation.RecommendationService.get_from_persisted_id")
@patch(
    "albatross.services.recommendation.RecommendationService.get_llm_recommendations"
)
def test_populate_llm_recommendations_fetches_and_persists(
    mock_get_llm_recommendations: Mock,
    mock_get_from_persisted_id: Mock,
    recommendations_without_llm_response: Recommendations,
) -> None:
    repo = Mock(spec=AlbatrossRepository)
    mock_get_from_persisted_id.return_value = recommendations_without_llm_response
    mock_get_llm_recommendations.return_value = ([{"l": "1"}], [{"c": "2"}])
    repo.persist.return_value = recommendations_without_llm_response

    result = RecommendationService.populate_llm_recommendations(
        recommendations_without_llm_response.id,
        repo=repo,
    )

    mock_get_from_persisted_id.assert_called_once_with(
        recommendations_without_llm_response.id, repo=repo
    )
    mock_get_llm_recommendations.assert_called_once_with(
        recommendations_without_llm_response.recommendation_statement
    )
    repo.persist.assert_called_once_with(recommendations_without_llm_response)
    assert recommendations_without_llm_response.llm_lens_recommendation == [{"l": "1"}]
    assert recommendations_without_llm_response.llm_camera_recommendation == [
        {"c": "2"}
    ]
    assert result == recommendations_without_llm_response


def test_build_minimized_analysis(camera: Camera, results: Results) -> None:
    # Given: A camera and results object
    analysis_json = RecommendationService.build_minimized_analysis(camera, results)

    # When: Parsing the JSON
    data = json.loads(analysis_json)

    # Then: Verify the structure of the JSON
    assert data["current_gear"]["primary_camera"]["name"] == (
        f"{camera.brand} {camera.model}"
    )
    assert data["analysis_of_pictures"]["metrics"]["focal_range"] != ""
