import logging
from typing import Any

from albatross.models.metrics import Metrics
from albatross.serializers.camera import CameraSerializer
from albatross.serializers.lens import LensSerializer

log = logging.getLogger(__name__)


class MetricsSerializer:
    @staticmethod
    def from_dict(data: dict[str, Any]) -> Metrics:
        """
        Deserializes a dictionary to a Metrics object
        """
        return Metrics(
            highest_possible_focal_length=data["highest_possible_focal_length"],
            shortest_focal_length=data["shortest_focal_length"],
            lowest_possible_focal_length=data["lowest_possible_focal_length"],
            longest_focal_length=data["longest_focal_length"],
            zoom_focal_lengths_inbetween_min_max=data[
                "zoom_focal_lengths_inbetween_min_max"
            ],
            average_focal_length=data["average_focal_length"],
            mode_focal_length=data["mode_focal_length"],
            instances_aperture_at_widest=data["instances_aperture_at_widest"],
            total_images=data["total_images"],
            instances_high_iso=data["instances_high_iso"],
            instances_exceeds_reciprocal=data["instances_exceeds_reciprocal"],
            lenses=[LensSerializer.from_dict(lens) for lens in data["lenses"]],
            zooms=[LensSerializer.from_dict(lens) for lens in data["zooms"]],
            primes=[LensSerializer.from_dict(lens) for lens in data["primes"]],
            instances_aperture=data["instances_aperture"],
            instances_focal_length=data["instances_focal_length"],
            instances_focal_length_zooms=data["instances_focal_length_zooms"],
            instances_focal_length_primes=data["instances_focal_length_primes"],
            instances_iso=data["instances_iso"],
            instances_shutter_speed=data["instances_shutter_speed"],
            cameras=[CameraSerializer.from_dict(camera) for camera in data["cameras"]],
            camera_frequency=data["camera_frequency_tracking"],
            lens_frequency=data["lens_frequency_tracking"],
            focal_range=data["focal_range"],
        )

    @staticmethod
    def to_dict(metrics: Metrics) -> dict[str, Any]:
        """
        Serializes a Metrics object to json
        """
        return {
            "total_images": metrics.total_images,
            "lenses": [LensSerializer.to_dict(lens) for lens in metrics.lenses],
            "zooms": [LensSerializer.to_dict(lens) for lens in metrics.zooms],
            "primes": [LensSerializer.to_dict(lens) for lens in metrics.primes],
            "cameras": [CameraSerializer.to_dict(camera) for camera in metrics.cameras],
            "highest_possible_focal_length": metrics.highest_possible_focal_length,
            "shortest_focal_length": metrics.shortest_focal_length,
            "lowest_possible_focal_length": metrics.lowest_possible_focal_length,
            "longest_focal_length": metrics.longest_focal_length,
            "zoom_focal_lengths_inbetween_min_max": metrics.zoom_focal_lengths_inbetween_min_max,  # noqa: E501
            "average_focal_length": metrics.average_focal_length,
            "mode_focal_length": metrics.mode_focal_length,
            "instances_aperture_at_widest": metrics.instances_aperture_at_widest,
            "instances_high_iso": metrics.instances_high_iso,
            "instances_exceeds_reciprocal": metrics.instances_exceeds_reciprocal,
            "instances_aperture": metrics.instances_aperture,
            "instances_focal_length": metrics.instances_focal_length,
            "instances_focal_length_zooms": metrics.instances_focal_length_zooms,
            "instances_focal_length_primes": metrics.instances_focal_length_primes,
            "instances_iso": metrics.instances_iso,
            "instances_shutter_speed": metrics.instances_shutter_speed,
            "camera_frequency_tracking": metrics.camera_frequency,
            "lens_frequency_tracking": metrics.lens_frequency,
            "focal_range": metrics.focal_range,
        }
