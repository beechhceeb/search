from typing import Any

from albatross.models.metrics import Metrics


def test_instantiate_metrics_model(metrics_primitive: dict[str, Any]) -> None:
    # Given the correct params
    # When I instantiate the Metrics object
    metrics = Metrics(**metrics_primitive)

    # Then the Metrics object should be instantiated
    assert metrics is not None

    # And the Metrics object should be initialised with the correct values
    assert metrics.lenses == metrics_primitive["lenses"]
    assert metrics.cameras == metrics_primitive["cameras"]
    assert (
        metrics.highest_possible_focal_length
        == metrics_primitive["highest_possible_focal_length"]
    )
    assert (
        metrics.lowest_possible_focal_length
        == metrics_primitive["lowest_possible_focal_length"]
    )
    assert (
        metrics.zoom_focal_lengths_inbetween_min_max
        == metrics_primitive["zoom_focal_lengths_inbetween_min_max"]
    )
    assert metrics.average_focal_length == metrics_primitive["average_focal_length"]
    assert metrics.mode_focal_length == metrics_primitive["mode_focal_length"]
    assert (
        metrics.instances_aperture_at_widest
        == metrics_primitive["instances_aperture_at_widest"]
    )
    assert metrics.total_images == metrics_primitive["total_images"]
    assert metrics.instances_high_iso == metrics_primitive["instances_high_iso"]
    assert (
        metrics.instances_exceeds_reciprocal
        == metrics_primitive["instances_exceeds_reciprocal"]
    )
    assert metrics.zooms == metrics_primitive["zooms"]
    assert metrics.primes == metrics_primitive["primes"]
    assert metrics.instances_aperture == metrics_primitive["instances_aperture"]
    assert metrics.instances_focal_length == metrics_primitive["instances_focal_length"]
    assert metrics.instances_iso == metrics_primitive["instances_iso"]
    assert (
        metrics.instances_shutter_speed == metrics_primitive["instances_shutter_speed"]
    )
