from typing import Any

import pytest

from albatross.models.camera import Camera
from albatross.models.lens import Lens
from albatross.models.metrics import Metrics
from albatross.models.results import FocalLength


@pytest.fixture
def metrics_primitive(
    lenses: list[Lens], prime_lens: Lens, camera: Camera, focal_length: FocalLength
) -> dict[str, Any]:
    lens_frequency = {}
    camera_frequency = {}

    for lens in lenses:
        lens_frequency[lens.model] = {"frequency": 1, "percentage_of_all": 33}

    camera_frequency[camera.model] = {"frequency": 1, "percentage_of_all": 100}

    return {
        "highest_possible_focal_length": [200],
        "lowest_possible_focal_length": [24],
        "zoom_focal_lengths_inbetween_min_max": [100],
        "average_focal_length": 100,
        "mode_focal_length": 100,
        "instances_aperture_at_widest": [1.8],
        "total_images": 3,
        "instances_high_iso": [6400],
        "instances_exceeds_reciprocal": [1 / 60],
        "lenses": lenses,
        "zooms": [prime_lens],
        "primes": [],
        "instances_aperture": [1.8, 2.8, 2.8, 4.0, 5.6, 8.0],
        "instances_focal_length": focal_length.instances,
        "instances_focal_length_zooms": focal_length.instances_zooms,
        "instances_focal_length_primes": focal_length.instances_primes,
        "instances_iso": [100, 200, 400, 400, 800, 6400],
        "instances_shutter_speed": [1 / 60, 1 / 80, 1 / 80, 1 / 80, 1 / 1000, 1 / 1000],
        "cameras": [camera],
        "longest_focal_length": 200,
        "shortest_focal_length": 24,
        "lens_frequency": lens_frequency,
        "camera_frequency": camera_frequency,
        "focal_range": range(24, 200),
    }


@pytest.fixture
def metrics(metrics_primitive: dict[str, Any]) -> Metrics:
    return Metrics(**metrics_primitive)
