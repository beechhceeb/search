from typing import Any

from albatross.models.metrics import Metrics
from albatross.serializers.camera import CameraSerializer
from albatross.serializers.lens import LensSerializer
from albatross.serializers.metrics import MetricsSerializer


def test_from_dict(metrics_primitive: dict[str, Any]) -> None:
    # Given a dictionary with valid metrics data
    # When calling from_dict
    metrics_primitive["lenses"] = [
        LensSerializer.to_dict(lens) for lens in metrics_primitive["lenses"]
    ]
    metrics_primitive["zooms"] = [
        LensSerializer.to_dict(camera) for camera in metrics_primitive["zooms"]
    ]
    metrics_primitive["primes"] = [
        LensSerializer.to_dict(camera) for camera in metrics_primitive["primes"]
    ]
    metrics_primitive["cameras"] = [
        CameraSerializer.to_dict(camera) for camera in metrics_primitive["cameras"]
    ]
    metrics_primitive["camera_frequency_tracking"] = {}
    metrics_primitive["lens_frequency_tracking"] = {}

    metrics = MetricsSerializer.from_dict(metrics_primitive)

    # Then it should return a Metrics object with the correct attributes
    assert isinstance(metrics, Metrics)
    assert metrics.total_images == metrics_primitive["total_images"]
    assert metrics.average_focal_length == 100


def test_to_dict(metrics: Metrics) -> None:
    # Given a Metrics object
    # When calling to_dict
    result = MetricsSerializer.to_dict(metrics)

    # Then it should return a dictionary with the correct data
    assert result["total_images"] == 3
    assert result["average_focal_length"] == 100
