from typing import Any
from unittest.mock import Mock, patch

import pytest

from albatross.config import MountType
from albatross.enums.enums import CameraType, SensorSize
from albatross.models.camera import Camera
from albatross.services.camera import CameraService
from albatross.repository.base_repository import AlbatrossRepository


@pytest.mark.parametrize(
    "exif, expected_make, expected_model, expected_crop_factor, expected_sensor_size, expected_camera_type",  # noqa: E501
    [
        (
            {
                "Make": "Canon",
                "Model": "EOS 5D",
                "FocalLength": 50,
                "FocalLengthIn35mmFilm": 50,
            },
            "canon",
            "eos 5d",
            1,
            SensorSize.FULL_FRAME,
            CameraType.DSLR,
        ),
        (
            {
                "Make": "Sony",
                "Model": "ILCE-6400",
                "FocalLength": 50,
                "FocalLengthIn35mmFilm": 75,
            },
            "sony",
            "a6400",
            1.5,
            SensorSize.APSC,
            CameraType.MIRRORLESS,
        ),
        (
            {
                "Make": "Nikon",
                "Model": "Coolpix P900",
                "FocalLength": 10,
                "FocalLengthIn35mmFilm": 56,
            },
            "nikon",
            "coolpix p900",
            5.6,
            SensorSize.ONE_OVER_TWO_POINT_THREE,
            CameraType.COMPACT,
        ),
        (
            {
                "Make": "Fujifilm",
                "Model": "GFX 100",
                "FocalLength": 50,
                "FocalLengthIn35mmFilm": 39.5,
            },
            "fujifilm",
            "gfx 100",
            0.79,
            SensorSize.MEDIUM_FORMAT,
            CameraType.MIRRORLESS,
        ),
        (
            {
                "Make": "Nikon",
                "Model": "1 J4",
                "FocalLength": 10,
                "FocalLengthIn35mmFilm": 27,
            },
            "nikon",
            "1 j4",
            2.7,
            SensorSize.ONE_INCH,
            CameraType.MIRRORLESS,
        ),
        # Canon EOS M series
        (
            {
                "Make": "Canon",
                "Model": "EOS M50",
                "FocalLength": 10,
                "FocalLengthIn35mmFilm": 16,
            },
            "canon",
            "eos m50",
            1.6,
            SensorSize.CANON_APSC,
            CameraType.MIRRORLESS,
        ),
        # Pentax q
        (
            {
                "Make": "Pentax",
                "Model": "Q",
                "FocalLength": 10,
                "FocalLengthIn35mmFilm": 56,
            },
            "pentax",
            "q",
            5.6,
            SensorSize.ONE_OVER_TWO_POINT_THREE,
            CameraType.MIRRORLESS,
        ),
        # Canon EOS full-frame DSLRs
        (
            {
                "Make": "Canon",
                "Model": "EOS 5D Mark II",
                "FocalLength": 50,
                "FocalLengthIn35mmFilm": 50,
            },
            "canon",
            "eos 5d mark ii",
            1,
            SensorSize.FULL_FRAME,
            CameraType.DSLR,
        ),
        (
            {
                "Make": "Canon",
                "Model": "EOS-6D_Mark IV",
                "FocalLength": 35,
                "FocalLengthIn35mmFilm": 35,
            },
            "canon",
            "eos-6d_mark iv",
            1,
            SensorSize.FULL_FRAME,
            CameraType.DSLR,
        ),
        (
            {
                "Make": "Canon",
                "Model": "EOS 1Ds",
                "FocalLength": 85,
                "FocalLengthIn35mmFilm": 85,
            },
            "canon",
            "eos 1ds",
            1,
            SensorSize.FULL_FRAME,
            CameraType.DSLR,
        ),
        (
            {
                "Make": "Canon",
                "Model": "EOS 1D X Mark III",
                "FocalLength": 70,
                "FocalLengthIn35mmFilm": 70,
            },
            "canon",
            "eos 1d x mark iii",
            1,
            SensorSize.FULL_FRAME,
            CameraType.DSLR,
        ),
        # Canon APS-C DSLR (should NOT match full-frame regex)
        (
            {
                "Make": "Canon",
                "Model": "EOS 90D",
                "FocalLength": 50,
                "FocalLengthIn35mmFilm": 80,
            },
            "canon",
            "eos 90d",
            1.6,
            SensorSize.CANON_APSC,
            CameraType.DSLR,
        ),
        # Canon mirrorless full-frame (should not match DSLR regex)
        (
            {
                "Make": "Canon",
                "Model": "EOS R5",
                "FocalLength": 35,
                "FocalLengthIn35mmFilm": 35,
            },
            "canon",
            "eos r5",
            1,
            SensorSize.FULL_FRAME,
            CameraType.MIRRORLESS,
        ),
        # Canon with weird formatting and lowercase brand
        (
            {
                "Make": "canon",
                "Model": "eos_5d_mark_iii",
                "FocalLength": 24,
                "FocalLengthIn35mmFilm": 24,
            },
            "canon",
            "eos_5d_mark_iii",
            1,
            SensorSize.FULL_FRAME,
            CameraType.DSLR,
        ),
    ],
)
@patch("albatross.services.search.query.requests.get")
def test_initializes_with_valid_exif(
    mock_search_requests_get: Any,
    exif: dict[str, str],
    expected_make: str,
    expected_model: str,
    expected_crop_factor: float,
    expected_sensor_size: SensorSize,
    expected_camera_type: CameraType,
    search_requests_get_response: str,
    repository: AlbatrossRepository,
) -> None:
    mock_search_requests_get.return_value = search_requests_get_response
    # When I create a Camera object
    camera: Camera = CameraService.from_exif(exif, db_enabled=False, repo=repository)

    # Then the Camera object should be initialized with the correct values
    assert camera.brand == expected_make
    assert camera.model == expected_model
    assert camera.crop_factor == expected_crop_factor
    assert camera.sensor_size == expected_sensor_size
    assert camera.type == expected_camera_type


@pytest.mark.parametrize(
    "model_name, expected_camera_type",
    [
        ("leica q3 43", CameraType.MIRRORLESS),
        ("zv-e10m2", CameraType.MIRRORLESS),
        ("gfx100rf", CameraType.MIRRORLESS),
        ("sigma bf", CameraType.MIRRORLESS),
        ("a7cr", CameraType.MIRRORLESS),
        ("dc-gh7", CameraType.MIRRORLESS),
        ("ilce-1m2", CameraType.MIRRORLESS),
        ("ilce-7rm5", CameraType.MIRRORLESS),
        ("canon eos r7", CameraType.MIRRORLESS),
        ("x2d 100c", CameraType.MIRRORLESS),
        ("slt-a99v", CameraType.MIRRORLESS),
        ("x-pro2", CameraType.MIRRORLESS),
        ("dc-s1rm2", CameraType.MIRRORLESS),
        ("canon eos-1d x", CameraType.DSLR),
        ("pixel 9a", CameraType.PHONE),
        ("nikon z 8", CameraType.MIRRORLESS),
        ("dc-s9", CameraType.MIRRORLESS),
        ("nikon z5_2", CameraType.MIRRORLESS),
        ("x-m5", CameraType.MIRRORLESS),
        ("canon eos r5m2", CameraType.MIRRORLESS),
        ("om-3", CameraType.MIRRORLESS),
        ("a059", CameraType.MIRRORLESS),
        ("canon powershot v1", CameraType.COMPACT),
        ("nikon z50_2", CameraType.MIRRORLESS),
        ("x-t5", CameraType.MIRRORLESS),
        ("nikon z6_3", CameraType.MIRRORLESS),
    ],
)
def test_multiple_camera_model_names_with_no_brand(
    model_name: str, expected_camera_type: CameraType
) -> None:
    # GIVEN a camera model with a known type and no brand
    brand = "unknown"

    # WHEN we classify it
    camera_type: CameraType = CameraService.classify_camera(brand, model_name)

    # THEN we get the expected type back
    assert camera_type == expected_camera_type


@patch("albatross.services.search.query.requests.get")
def test_initializes_with_unknown_sensor_size(
    patch_requests_get: Mock, repository: AlbatrossRepository
) -> None:
    # Given an exif dictionary with unknown sensor size
    exif = {
        "Make": "Unknown",
        "Model": "Unknown",
        "FocalLength": 50,
        "FocalLengthIn35mmFilm": 50,
    }

    # When I create a Camera object
    camera: Camera = CameraService.from_exif(exif, db_enabled=False, repo=repository)

    # Then the Camera object should be initialized with the correct values
    assert camera.sensor_size == SensorSize.FULL_FRAME


def test_initializes_with_crop_sensor_size(crop_sensor_camera: Camera) -> None:
    # When I create a Camera object
    camera: Camera = crop_sensor_camera

    # Then the Camera object should be initialized with the correct values
    assert camera.sensor_size == SensorSize.CANON_APSC


@patch("albatross.services.search.query.requests.get")
def test_calculates_crop_factor_from_sensor_size(
    mock_requests_get: Mock, repository: AlbatrossRepository
) -> None:
    # Given an exif dictionary with crop factor
    exif = {
        "Make": "Sony",
        "Model": "Alpha",
        "FocalLength": 50,
        "FocalLengthIn35mmFilm": 75,
    }

    # When I create a Camera object
    camera: Camera = CameraService.from_exif(exif, db_enabled=False, repo=repository)

    # Then the Camera object should be initialized with the correct values
    assert camera.crop_factor == 1.5


@patch("albatross.services.search.query.requests.get")
def test_assigns_mount_based_on_brand_and_type(
    mock_requests_get: Mock, repository: AlbatrossRepository
) -> None:
    # Given a valid exif dictionary
    exif = {
        "Make": "Nikon",
        "Model": "D850",
        "FocalLength": 50,
        "FocalLengthIn35mmFilm": 50,
    }

    # When I create a Camera object
    camera: Camera = CameraService.from_exif(exif, db_enabled=False, repo=repository)

    # Then the Camera object should be initialized with the correct values
    assert camera.mount.value == MountType.F.value


def test_from_exif_given_existing_camera_when_called_then_returns_camera(
    repository: AlbatrossRepository, camera: Camera
) -> None:
    # Given: A camera exists in the database
    repository.persist(camera)
    exif_data = {"Model": camera.model, "Make": camera.brand}

    # When: Calling from_exif
    result = CameraService.from_exif(exif_data, repo=repository)

    # Then: The existing camera is returned
    assert result.brand == camera.brand
    assert result.model == camera.model
    assert result.crop_factor == camera.crop_factor
    assert result.sensor_size == camera.sensor_size
    assert result.type == camera.type
    assert result.mount == camera.mount
    assert result.ibis == camera.ibis
    assert result.model_url_encoded == camera.model_url_encoded


@patch("albatross.services.search.query.requests.get")
def test_from_exif_given_unknown_brand_when_called_then_returns_unknown_brand(
    mock_requests_get: Mock,
    repository: AlbatrossRepository,
) -> None:
    # Given: EXIF data with no brand
    exif_data = {"Model": "Test Model"}

    # When: Calling from_exif
    result = CameraService.from_exif(exif_data, db_enabled=False, repo=repository)

    # Then: The brand should be "Unknown Brand"
    assert result.brand == "unknown brand"


def test_classify_camera_given_model_patterns_when_called_then_returns_correct_type() -> (  # noqa: E501
    None
):
    # Given: Various camera models
    assert CameraService.classify_camera("canon", "eos 5d") == CameraType.DSLR
    assert CameraService.classify_camera("sony", "a7") == CameraType.MIRRORLESS
    assert CameraService.classify_camera("nikon", "coolpix") == CameraType.COMPACT
    assert CameraService.classify_camera("unknown", "unknown") == CameraType.UNKNOWN
    assert CameraService.classify_camera("gopro", "hero") == CameraType.ACTION
    assert CameraService.classify_camera("dji", "hero") == CameraType.DRONE


def test_map_sony_internal_to_public_model_given_internal_model_when_called_then_returns_public_model() -> (  # noqa: E501
    None
):
    # Given: A Sony internal model
    internal_model = "ilce-7m3"

    # When: Mapping to public model
    public_model = CameraService.map_sony_internal_to_public_model(internal_model)

    # Then: The public model should be returned
    assert public_model == "A7 III"  # Example mapping


def test_get_camera_mount_given_unknown_values_when_called_then_returns_unknown_mount() -> (  # noqa: E501
    None
):
    # Given: Unknown brand, sensor size, and camera type
    mount = CameraService.get_camera_mount(
        "unknown", SensorSize.UNKNOWN, CameraType.UNKNOWN
    )

    # Then: The mount should be unknown
    assert mount == MountType.UNKNOWN


def test_calculate_sensor_size_given_crop_factor_when_called_then_returns_correct_sensor_size() -> (  # noqa: E501
    None
):
    # Given: Various crop factors
    assert CameraService.calculate_sensor_size(1) == SensorSize.FULL_FRAME
    assert CameraService.calculate_sensor_size(1.5) == SensorSize.APSC
    assert CameraService.calculate_sensor_size(2) == SensorSize.FOUR_THIRDS


def test_get_camera_crop_factor_without_focal_length_35mm() -> None:
    # Given: A camera object without focal length in 35mm film equivalent
    # When: Calling get_camera_crop_factor
    crop_factor = CameraService.get_camera_crop_factor(
        focal_length=20.0,
        focal_length_35mm=None,
        brand="olympus",
        camera_type=CameraType.DSLR,
    )

    # Then: The crop factor should be calculated correctly
    assert crop_factor == 2.0


def test_get_camera_crop_factor_returns_none_when_not_enough_data() -> None:
    # Given: A camera object without enough data
    # When: Calling get_camera_crop_factor
    crop_factor = CameraService.get_camera_crop_factor(
        focal_length=20.0,
        focal_length_35mm=None,
        brand="canon",
        camera_type=CameraType.DSLR,
    )

    # Then: The crop factor should be None
    assert crop_factor is None


def test_attempt_to_get_crop_factor_from_brand_when_no_matching_brand_returns_none() -> (  # noqa: E501
    None
):  # noqa: E501
    # Given: A camera object with an unknown brand
    # When: Calling get_camera_crop_factor
    crop_factor = CameraService.get_camera_crop_factor(
        focal_length=20.0,
        focal_length_35mm=None,
        brand="unknown_brand",
        camera_type=CameraType.DSLR,
    )

    # Then: The crop factor should be None
    assert crop_factor is None


def test_attempt_to_get_crop_factor_from_brand_when_one_brand() -> None:
    # Given: A camera object with an unknown brand
    # When: Calling get_camera_crop_factor
    crop_factor = CameraService.attempt_to_get_crop_factor_from_brand(
        brand="olympus",
        camera_type=CameraType.DSLR,
    )

    # Then: The crop factor should be None
    assert crop_factor == 2


def test_get_possible_sensor_sizes_from_brand_and_type() -> None:
    # Given: A brand and camera type
    brand = "canon"
    camera_type = CameraType.DSLR

    # When: Calling get_possible_sensor_sizes_from_brand_and_type
    sensor_sizes = CameraService.get_possible_sensor_sizes_from_brand_and_type(
        brand, camera_type
    )

    # Then: The sensor sizes should match the expected values
    assert sensor_sizes == [SensorSize.CANON_APSC, SensorSize.FULL_FRAME]


def test_get_possible_sensor_sizes_from_brand_and_type_with_unknown_brand() -> None:
    # Given: An unknown brand and camera type
    brand = "unknown_brand"
    camera_type = CameraType.DSLR

    # When: Calling get_possible_sensor_sizes_from_brand_and_type
    sensor_sizes = CameraService.get_possible_sensor_sizes_from_brand_and_type(
        brand, camera_type
    )

    # Then: The sensor sizes should be unknown
    assert sensor_sizes == [SensorSize.UNKNOWN]


def test_get_possible_sensor_sizes_from_brand_and_type_with_type_without_mount() -> (
    None
):
    # Given: A brand and camera type that doesn't have a mount
    brand = "canon"
    camera_type = CameraType.ACTION

    # When: Calling get_possible_sensor_sizes_from_brand_and_type
    sensor_sizes = CameraService.get_possible_sensor_sizes_from_brand_and_type(
        brand, camera_type
    )

    # Then: The sensor sizes should be unknown
    assert sensor_sizes == [SensorSize.UNKNOWN]
