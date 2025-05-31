import pytest

from albatross.models.camera import Camera
from albatross.models.exif_collections import Illuminance
from albatross.models.image_exif import ImageExif
from albatross.models.lens import Lens
from albatross.models.results import ISO, Aperture, FocalLength, ShutterSpeed


@pytest.fixture
def iso() -> ISO:
    instances = [100, 200, 400, 600, 800, 6400]
    return ISO(
        instances=instances,
    )


@pytest.fixture
def shutter_speed() -> ShutterSpeed:
    instances = [1 / 60, 1 / 80, 1 / 80, 1 / 1000, 1 / 1000]
    exceeds_reciprocal = [1 / 60]
    return ShutterSpeed(
        instances=instances,
        exceeds_reciprocal=exceeds_reciprocal,
    )


@pytest.fixture
def aperture() -> Aperture:
    instances = [1.8, 2.8, 2.8, 4, 5.6, 8]
    instances_wide_open = [2.8, 2.8, 1.8]
    return Aperture(
        instances=instances,
        instances_wide_open=instances_wide_open,
    )


@pytest.fixture
def focal_length() -> FocalLength:
    instances_focal_length = [24, 35, 35, 35, 100, 150, 200]
    return FocalLength(
        instances=instances_focal_length,
        instances_min=[24.0],
        instances_max=[200.0],
        instances_zooms=[24.0, 35.0, 35.0, 35.0],
        instances_primes=[100.0, 150.0, 200.0],
    )


@pytest.fixture
def exposure() -> Illuminance:
    instances = [0.0, 5.0, 7.0, 11.0, 4.0, 1.0, 2.0]
    instances_exposure_in_dark = [0.0, 5.0, 4.0, 1.0, 2.0]
    return Illuminance(
        instances=instances,
        instances_in_dark=instances_exposure_in_dark,
    )


@pytest.fixture
def image_exif(camera: Camera, lens: Lens, filename: str) -> ImageExif:
    return ImageExif(
        camera=camera,
        lens=lens,
        filename=filename,
        aperture=2.8,
        iso=100,
        shutter_speed=1 / 100,
        focal_length=50.0,
        exposure=1.0,
    )
