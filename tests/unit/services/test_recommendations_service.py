from albatross.models.recommendations import Recommendations
from albatross.serializers.recommendations import RecommendationsSerializer


def test_to_json_abridged_given_valid_recommendations_when_serialized_then_correct_json(
    recommendations_without_llm_response: Recommendations,
) -> None:
    # Given: A valid Recommendations object
    # When: Serializing to abridged JSON
    abridged_json = RecommendationsSerializer.to_json_abridged(
        recommendations_without_llm_response
    )

    # Then: The JSON should not contain verbose keys and should be correctly formatted
    assert "instances" not in abridged_json
    assert "total_images" not in abridged_json
    assert "zoom_focal_lengths_inbetween_min_max" not in abridged_json
    assert "possible_focal_length" not in abridged_json
    assert "primes" not in abridged_json
    assert "zooms" not in abridged_json
    assert "primary_camera" in abridged_json
    assert "primary_mount_lenses" in abridged_json
    assert "current_widest_aperture" in abridged_json
    assert "favourite_focal_length" in abridged_json
    assert "focal_range" in abridged_json
    assert "recommended_aperture" in abridged_json
    assert "recommended_focal_length" in abridged_json
    assert "recommendation_statement" in abridged_json
    assert "results" in abridged_json
