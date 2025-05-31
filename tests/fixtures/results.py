import pytest

from albatross.models.exif_collections import Illuminance
from albatross.models.metrics import Metrics
from albatross.models.results import ISO, Aperture, FocalLength, Results, ShutterSpeed


@pytest.fixture
def results(
    focal_length: FocalLength,
    aperture: Aperture,
    iso: ISO,
    shutter_speed: ShutterSpeed,
    metrics: Metrics,
    exposure: Illuminance,
) -> Results:
    return Results(
        aperture=aperture,
        focal_length=focal_length,
        iso=iso,
        shutter_speed=shutter_speed,
        metrics=metrics,
        exposure=exposure,
    )
