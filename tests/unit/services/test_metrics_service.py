from typing import Any

import pytest

from albatross.models.camera import Camera
from albatross.models.image_exif import ImageExif
from albatross.models.lens import Lens
from albatross.models.metrics import Metrics
from albatross.serializers.camera import CameraSerializer
from albatross.serializers.lens import LensSerializer
from albatross.serializers.metrics import MetricsSerializer
from albatross.services.metrics import MetricsService


def test_from_exif_given_valid_exif_data_when_parsed_then_returns_metrics_object(
    camera: Camera, lens: Lens, prime_lens: Lens
) -> None:
    # Given valid exif data
    exif_data = [
        ImageExif(
            lens=lens,
            camera=camera,
            aperture=2.8,
            iso=100,
            shutter_speed=1 / 125,
            focal_length=24.0,
            filename="test.jpg",
        ),
        ImageExif(
            lens=lens,
            camera=camera,
            aperture=2.8,
            iso=100,
            shutter_speed=1 / 125,
            focal_length=24.0,
            filename="test.jpg",
        ),
        ImageExif(
            lens=lens,
            camera=camera,
            aperture=2.8,
            iso=100,
            shutter_speed=1 / 125,
            focal_length=70.0,
            filename="test.jpg",
        ),
        ImageExif(
            lens=lens,
            camera=camera,
            aperture=2.8,
            iso=100,
            shutter_speed=1 / 125,
            focal_length=35.0,
            filename="test.jpg",
        ),
        ImageExif(
            lens=prime_lens,
            camera=camera,
            aperture=1.8,
            iso=9000,
            shutter_speed=1 / 2,
            focal_length=50.0,
            filename="test2.jpg",
        ),
    ]

    # When parsed
    metrics = MetricsService.from_exif(exif_data)

    # Then metrics object should be returned
    assert metrics is not None
    assert metrics.total_images == 5
    assert len(metrics.lenses) == 2
    assert len(metrics.cameras) == 1
    assert metrics.average_focal_length == pytest.approx(40.6)
    assert metrics.mode_focal_length == 24.0
    assert len(metrics.instances_high_iso) == 1
    assert len(metrics.instances_exceeds_reciprocal) == 1
    assert len(metrics.highest_possible_focal_length) == 1
    assert len(metrics.lowest_possible_focal_length) == 2


def test_from_exif_given_empty_exif_data_when_parsed_then_raises_value_error() -> None:
    # Given empty exif data
    exif_data: list[ImageExif] = []

    # When we try to serialize it / Then an error should be raised
    with pytest.raises(ValueError) as e:
        MetricsService.from_exif(exif_data)
    assert str(e.value) == "No images to process"


def test_exceeds_reciprocal_given_shutter_speed_less_than_reciprocal_when_checked_then_returns_true() -> (  # noqa: E501
    None
):  # noqa: E501
    # Given a shutter speed less than the reciprocal of the focal length
    shutter_speed = 1 / 30
    focal_length = 50.0

    # When checked
    result = MetricsService.exceeds_reciprocal(shutter_speed, focal_length)

    # Then it should return True
    assert result is True


def test_exceeds_reciprocal_given_shutter_speed_greater_than_reciprocal_when_checked_then_returns_false() -> (  # noqa: E501
    None
):  # noqa: E501
    # Given a shutter speed greater than the reciprocal of the focal length
    shutter_speed = 1 / 100
    focal_length = 50.0

    # When checked
    result = MetricsService.exceeds_reciprocal(shutter_speed, focal_length)

    # Then it should return False
    assert result is False


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


def test_from_exif_with_valid_data(image_exif: ImageExif) -> None:
    # Given valid EXIF data
    exif_data_list = [image_exif]

    # When calling from_exif
    metrics = MetricsService.from_exif(exif_data_list)

    # Then it should return a Metrics object with calculated attributes
    assert metrics.total_images == 1
    assert metrics.average_focal_length == 50.0


def test_from_exif_with_empty_data() -> None:
    # Given empty EXIF data
    exif_data: list[ImageExif] = []

    # When calling from_exif
    # Then it should raise a ValueError
    with pytest.raises(ValueError) as exc_info:
        MetricsService.from_exif(exif_data)
    assert str(exc_info.value) == "No images to process"


def test_calculate_focal_range(lenses: list[Lens]) -> None:
    # Given a list of lenses with focal lengths
    # When calling calculate_focal_range
    focal_range = MetricsService.calculate_focal_range(lenses)

    # Then it should return the correct range
    assert focal_range == range(24, 200)


def test_calculate_focal_range_with_empty_lenses() -> None:
    # Given an empty list of lenses
    lenses: list[Lens] = []

    # When calling calculate_focal_range
    # Then it should raise a ValueError
    with pytest.raises(ValueError) as exc_info:
        MetricsService.calculate_focal_range(lenses)
    assert str(exc_info.value) == "No lenses to process"


def test_exceeds_reciprocal_returns_true() -> None:
    # Given a shutter speed less than the reciprocal of the focal length
    shutter_speed = 1 / 30
    focal_length = 50.0

    # When calling exceeds_reciprocal
    result = MetricsService.exceeds_reciprocal(shutter_speed, focal_length)

    # Then it should return True
    assert result is True


def test_exceeds_reciprocal_returns_false() -> None:
    # Given a shutter speed greater than the reciprocal of the focal length
    shutter_speed = 1 / 100
    focal_length = 50.0

    # When calling exceeds_reciprocal
    result = MetricsService.exceeds_reciprocal(shutter_speed, focal_length)

    # Then it should return False
    assert result is False


def test_to_dict(metrics: Metrics) -> None:
    # Given a Metrics object
    # When calling to_dict
    result = MetricsSerializer.to_dict(metrics)

    # Then it should return a dictionary with the correct data
    assert result["total_images"] == 3
    assert result["average_focal_length"] == 100


def test_from_exif_filters_unknown_camera_models(image_exif: ImageExif) -> None:
    # Given: EXIF data with some images having unknown camera models
    image_exif.camera.model = "Fake Model"
    exif_data = [image_exif, image_exif]

    # When: Calling from_exif
    metrics = MetricsService.from_exif(exif_data)

    # Then: Images with unknown camera models should be filtered out
    assert metrics.total_images == 2
    assert metrics.cameras[0].model != "unknown model"


def test_from_exif_tracks_lens_frequency(image_exif: ImageExif) -> None:
    # Given: EXIF data with multiple images using the same lens
    exif_data = [image_exif, image_exif]

    # When: Calling from_exif
    metrics = MetricsService.from_exif(exif_data)

    # Then: Lens frequency should be tracked correctly
    assert metrics.lens_frequency[image_exif.lens.model]["frequency"] == 2
    assert metrics.lens_frequency[image_exif.lens.model]["percentage_of_all"] == 100.0


def test_from_exif_tracks_camera_frequency(image_exif: ImageExif) -> None:
    # Given: EXIF data with multiple images using the same camera
    exif_data = [image_exif, image_exif]

    # When: Calling from_exif
    metrics = MetricsService.from_exif(exif_data)

    # Then: Camera frequency should be tracked correctly
    assert metrics.camera_frequency[image_exif.camera.model]["frequency"] == 2
    assert (
        metrics.camera_frequency[image_exif.camera.model]["percentage_of_all"] == 100.0
    )


def test_from_exif_calculates_focal_length_metrics(image_exif: ImageExif) -> None:
    # Given: EXIF data with valid focal lengths
    exif_data = [image_exif]

    # When: Calling from_exif
    metrics = MetricsService.from_exif(exif_data)

    # Then: Focal length metrics should be calculated correctly
    assert (
        metrics.average_focal_length
        == image_exif.focal_length * image_exif.camera.crop_factor
    )
    assert metrics.shortest_focal_length == metrics.longest_focal_length


def test_from_exif_sorts_focal_length_lists(image_exif: ImageExif) -> None:
    # Given: EXIF data with various focal lengths
    exif_data = [image_exif]

    # When: Calling from_exif
    metrics = MetricsService.from_exif(exif_data)

    # Then: Focal length-related lists should be sorted
    assert metrics.highest_possible_focal_length == sorted(
        metrics.highest_possible_focal_length, reverse=True
    )
    assert metrics.lowest_possible_focal_length == sorted(
        metrics.lowest_possible_focal_length
    )


def test_from_exif_calculates_exposure_metrics(image_exif: ImageExif) -> None:
    # Given: EXIF data with valid exposure values
    exif_data = [image_exif]

    # When: Calling from_exif
    metrics = MetricsService.from_exif(exif_data)

    # Then: Exposure metrics should be calculated correctly
    assert (
        metrics.instances_exposure_in_dark == [image_exif.exposure]
        if image_exif.exposure < 7
        else []
    )


def test_from_exif_with_no_exif_data_raises_value_error() -> None:
    # Given: No EXIF data
    exif_data: list[ImageExif] = []

    # When: Calling from_exif
    # Then: It should raise a ValueError
    with pytest.raises(ValueError) as exc_info:
        MetricsService.from_exif(exif_data)
    assert str(exc_info.value) == "No images to process"


def test_from_exif_handles_exception_when_calculate_focal_range_raises_value_error(
    image_exif: ImageExif,
) -> None:
    # Given: EXIF data with valid images, but no lenses
    # so that the calculate_focal_range raises a ValueError
    image_exif.lens = None

    # When: Calling from_exif
    # Then: It should not raise a ValueError
    metrics = MetricsService.from_exif([image_exif])

    # And: metrics are returned
    assert metrics
