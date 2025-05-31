import uuid
from typing import Any
from unittest.mock import Mock, patch

import pytest

from albatross.models.lens import Lens
from albatross.repository.base_repository import AlbatrossRepository
from albatross.serializers.lens import LensSerializer
from albatross.services.lens import LensService


def test_serialize_given_lens_object_when_serialized_then_returns_json_string() -> None:
    # Given a valid lens
    id = uuid.uuid4()
    lens = Lens(
        brand="Canon",
        model="EF 24-70mm f/2.8L II USM",
        focal_length_min=24.0,
        focal_length_max=70.0,
        largest_aperture_at_minimum_focal_length=2.8,
        largest_aperture_at_maximum_focal_length=2.8,
        prime=False,
        id=id,
    )

    # When we serialise it
    serialized_lens = LensSerializer.serialize(lens)

    # Then it looks as we expect
    expected_json = (
        '{"id": '
        f'"{id}", '
        '"brand": "Canon", '
        '"model": "EF 24-70mm f/2.8L II USM", "model_url_encoded": '
        '"EF_24_70mm_f_2_8L_II_USM", "focal_length_min": 24.0, '
        '"focal_length_max": 70.0, '
        '"largest_aperture_at_minimum_focal_length": 2.8, '
        '"largest_aperture_at_maximum_focal_length": 2.8, "prime": false, '
        '"mount": null, "crop_factor": null, "mpb_model_id": null, '
        '"price": null, "formatted_price": null, "image_link": null, '
        '"model_url_segment": null, "mpb_model": null}'
    )

    assert serialized_lens == expected_json


def test_deserialize_given_json_string_when_deserialized_then_returns_lens_object() -> (
    None
):
    # Given a JSON string
    json_data = (
        '{"brand": "Canon", "model": "EF 24-70mm f/2.8L II USM", '
        '"focal_length_min": 24.0, "focal_length_max": 70.0, '
        '"largest_aperture_at_minimum_focal_length": 2.8, '
        '"largest_aperture_at_maximum_focal_length": 2.8, '
        '"prime": false, "mount": null}'
    )

    # When the JSON string is deserialized
    lens = LensSerializer.deserialize(json_data)

    # Then the lens object should be initialized with the correct values
    assert lens.brand == "Canon"
    assert lens.model == "EF 24-70mm f/2.8L II USM"
    assert lens.focal_length_min == 24.0
    assert lens.focal_length_max == 70.0
    assert lens.largest_aperture_at_minimum_focal_length == 2.8
    assert lens.largest_aperture_at_maximum_focal_length == 2.8
    assert lens.prime is False
    assert lens.mount is None


@pytest.mark.parametrize(
    "model, brand, expected_focal_length_min, expected_focal_length_max, expected_aperture_min, expected_aperture_max",  # noqa: E501
    [
        ("Canon EF 24-70mm f/2.8L II USM", "Canon", 24.0, 70.0, 2.8, 2.8),
        ("Canon EF 50mm f/1.8 STM", "Canon", 50.0, 50.0, 1.8, 1.8),
        ("Nikon 24-70mm f/2.8G", "Nikon", 24.0, 70.0, 2.8, 2.8),
        ("Sony 70-200mm f2.8-4 OSS", "Sony", 70.0, 200.0, 2.8, 4.0),
        ("Sigma 85mm f1.2 DG HSM Art", "Sigma", 85.0, 85.0, 1.2, 1.2),
        ("Tamron 17-35mm f/2.8-4 Di OSD", "Tarmon", 17.0, 35.0, 2.8, 4.0),
    ],
)
def test_from_model_name_given_valid_model_name_when_parsed_then_returns_lens_object(
    model: str,
    brand: str,
    expected_focal_length_min: float,
    expected_focal_length_max: float,
    expected_aperture_min: float,
    expected_aperture_max: float,
    repository: AlbatrossRepository,
) -> None:
    # Given a valid lens model name
    # When I parse the model name
    lens = LensService.from_model_name(
        model=model, brand=brand, mount=None, db_enabled=False, repo=repository
    )

    # Then the lens object should be initialized with the correct values
    assert lens is not None
    assert lens.brand == brand
    assert lens.model == model
    assert lens.focal_length_min == expected_focal_length_min
    assert lens.focal_length_max == expected_focal_length_max
    assert lens.largest_aperture_at_minimum_focal_length == expected_aperture_min
    assert lens.largest_aperture_at_maximum_focal_length == expected_aperture_max


@patch("albatross.services.search.query.requests.get")
def test_from_exif_given_valid_exif_data_when_parsed_then_returns_lens_object(
    mock_requests_get: Mock,
    repository: AlbatrossRepository,
) -> None:
    # Given
    exif_data = {
        "LensModel": "EF 24-70mm f/2.8L II USM",
        "LensMake": "Canon",
        "LensSpecification": [24.0, 70.0, 2.8, 2.8],
    }

    # When
    lens = LensService.from_exif(
        exif_data, mount=None, crop_factor=2, db_enabled=False, repo=repository
    )

    # Then
    assert lens is not None
    assert lens.brand == "Canon"
    assert lens.model == "EF 24-70mm f/2.8L II USM"
    assert lens.focal_length_min == 48.0
    assert lens.focal_length_max == 140.0
    assert lens.largest_aperture_at_minimum_focal_length == 2.8
    assert lens.largest_aperture_at_maximum_focal_length == 2.8


@patch("albatross.services.search.query.requests.get")
def test_from_exif_given_valid_exif_with_rational_spec_values(
    mock_requests_get: Mock,
    repository: AlbatrossRepository,
) -> None:
    # Given
    exif_data = {
        "LensModel": "EF 24-70mm f/2.8L II USM",
        "LensMake": "Canon",
        "LensSpecification": [[24.0, 1], [70.0, 1], [2.8, 1], [2.8, 1]],
    }

    # When
    lens = LensService.from_exif(
        exif_data, mount=None, crop_factor=2, db_enabled=False, repo=repository
    )

    # Then
    assert lens is not None
    assert lens.brand == "Canon"
    assert lens.model == "EF 24-70mm f/2.8L II USM"
    assert lens.focal_length_min == 48.0
    assert lens.focal_length_max == 140.0
    assert lens.largest_aperture_at_minimum_focal_length == 2.8
    assert lens.largest_aperture_at_maximum_focal_length == 2.8


def test_get_aperture_values_from_model_name_raises_error_when_no_values_found() -> (
    None
):
    # Given a lens model name with no aperture values
    model = "Canon EF 24-70mm"

    # When I attempt to parse the aperture values
    with pytest.raises(ValueError) as e:
        LensService.get_aperture_values_from_model_name(model)

    # Then a ValueError should be raised
    assert str(e.value) == "No aperture values found in the model name."


def test_get_focal_length_values_from_model_name_raises_error_when_no_values_found() -> (  # noqa: E501
    None
):
    # Given a lens model name with no focal length values
    model = "Canon EF"

    # When I attempt to parse the focal length values
    with pytest.raises(ValueError) as e:
        LensService.get_focal_length_values_from_model_name(model)

    # Then a ValueError should be raised
    assert str(e.value) == "No focal length values found in the model name."


def test_from_exif_when_no_lens_specification_in_exif(
    repository: AlbatrossRepository,
) -> None:
    # Given
    exif_data = {
        "LensModel": "EF 24-70mm f/2.8L II USM",
        "LensMake": "Canon",
    }

    # When
    lens = LensService.from_exif(exif_data, db_enabled=False, repo=repository)

    # Then
    assert lens is not None
    assert lens.brand == "Canon"
    assert lens.model == "EF 24-70mm f/2.8L II USM"
    assert lens.focal_length_min == 24.0
    assert lens.focal_length_max == 70.0
    assert lens.largest_aperture_at_minimum_focal_length == 2.8
    assert lens.largest_aperture_at_maximum_focal_length == 2.8


def test_from_exif_with_empty_exif_raises_exception(
    repository: AlbatrossRepository,
) -> None:
    # Given an empty EXIF data
    exif_data: dict[str, Any] = {}

    # When I attempt to parse the lens data
    with pytest.raises(ValueError) as e:
        LensService.from_exif(exif_data, repo=repository)

    # Then a ValueError should be raised
    assert str(e.value) == "No lens data found in the EXIF metadata."


def test_from_exif_given_unknown_brand_when_called_then_returns_unknown_brand(
    repository: AlbatrossRepository,
) -> None:
    # Given: EXIF data with no brand
    exif_data = {"LensModel": "Test Model 50mm f/1.8"}

    # When: Calling from_exif
    result = LensService.from_exif(exif_data, db_enabled=False, repo=repository)

    # Then: The brand should be "Unknown Brand"
    assert result.brand == "Unknown Brand"


def test_from_exif_given_zero_lens_model_when_called_then_raises_value_error(
    repository: AlbatrossRepository,
) -> None:
    # Given: EXIF data with "0.0 mm f/0.0" lens model
    exif_data = {"LensModel": "0.0 mm f/0.0"}

    # When/Then: Calling from_exif should raise a ValueError
    with pytest.raises(ValueError, match="No lens data found in the EXIF metadata."):
        LensService.from_exif(exif_data, repo=repository)


def test_from_exif_given_model_with_brand_in_name_when_called_then_derives_brand(
    repository: AlbatrossRepository,
) -> None:
    # Given: EXIF data with a model containing a brand name
    exif_data = {"LensModel": "Canon EF 50mm f/1.8"}

    # When: Calling from_exif
    result = LensService.from_exif(exif_data, db_enabled=False, repo=repository)

    # Then: The brand should be derived from the model name
    assert result.brand == "canon"


@patch("albatross.services.search.query.requests.get")
def test_from_exif_given_lens_specification_when_called_then_parses_correctly(
    mock_requests_get: Mock,
    repository: AlbatrossRepository,
) -> None:
    # Given: EXIF data with LensSpecification
    exif_data = {
        "LensModel": "Test Model",
        "LensSpecification": [24, 70, 2.8, 4.0],
    }

    # When: Calling from_exif
    result = LensService.from_exif(exif_data, db_enabled=False, repo=repository)

    # Then: The focal lengths and apertures should be parsed correctly
    assert result.focal_length_min == 24
    assert result.focal_length_max == 70
    assert result.largest_aperture_at_minimum_focal_length == 2.8
    assert result.largest_aperture_at_maximum_focal_length == 4.0


@patch("albatross.services.search.query.requests.get")
def test_from_exif_given_zero_division_in_lens_specification_when_called_then_logs_warning(  # noqa: E501
    mock_requests_get: Mock,
    repository: AlbatrossRepository,
    caplog: pytest.LogCaptureFixture,
) -> None:
    # Given: EXIF data with LensSpecification causing ZeroDivisionError
    exif_data = {
        "LensModel": "Test Model",
        "LensSpecification": [[0, 0], [0, 0], [0, 0], [0, 0]],
    }

    # When: Calling from_exif
    result = LensService.from_exif(exif_data, db_enabled=False, repo=repository)

    # Then: A warning should be logged, and all values should be 0.0
    assert "Division by zero error in lens data" in caplog.text
    assert result.focal_length_min == 0.0
    assert result.focal_length_max == 0.0


@patch("albatross.services.search.query.requests.get")
def test_from_exif_given_invalid_focal_length_when_called_then_returns_none(
    mock_requests_get: Mock,
    repository: AlbatrossRepository,
) -> None:
    # Given: EXIF data with invalid focal length
    exif_data = {
        "LensModel": "Test Model",
        "LensSpecification": [float("nan"), float("nan"), 2.8, 4.0],
    }

    # When: Calling from_exif
    result = LensService.from_exif(exif_data, db_enabled=False, repo=repository)

    # Then: Focal lengths should be None
    assert result.focal_length_min is None
    assert result.focal_length_max is None


@patch("albatross.services.search.query.requests.get")
def test_from_exif_given_prime_lens_when_called_then_sets_prime_true(
    mock_requests_get: Mock,
    repository: AlbatrossRepository,
) -> None:
    # Given: EXIF data for a prime lens
    exif_data = {
        "LensModel": "Test Model",
        "LensSpecification": [50, 50, 1.8, 1.8],
    }

    # When: Calling from_exif
    result = LensService.from_exif(exif_data, db_enabled=False, repo=repository)

    # Then: The lens should be marked as prime
    assert result.prime is True


def test_from_exif_given_missing_lens_specification_when_called_then_falls_back_to_model_name(  # noqa: E501
    repository: AlbatrossRepository,
) -> None:  # noqa: E501
    # Given: EXIF data with no LensSpecification
    exif_data = {"LensModel": "Canon EF 50mm f/1.8"}

    # When: Calling from_exif
    result = LensService.from_exif(exif_data, db_enabled=False, repo=repository)

    # Then: The lens should be created using from_model_name
    assert result.model == "Canon EF 50mm f/1.8"


def test_attempt_to_get_brand_from_model_name_given_no_brand_when_called_then_returns_none() -> (  # noqa: E501
    None
):
    # Given: A model name with no recognizable brand
    model_name = "Unknown Lens Model"

    # When: Calling attempt_to_get_brand_from_model_name
    result = LensService.attempt_to_get_brand_from_model_name(model_name)

    # Then: The result should be None
    assert result is None


def test_from_exif_handles_zero_lens_model(
    repository: AlbatrossRepository,
) -> None:
    # Given: EXIF data with "0.0 mm f/0.0" lens model
    exif_data = {"LensModel": "0.0 mm f/0.0"}

    # When/Then: Calling from_exif should raise a ValueError
    with pytest.raises(ValueError, match="No lens data found in the EXIF metadata."):
        LensService.from_exif(exif_data, repo=repository)


def test_from_exif_derives_brand_from_model(
    repository: AlbatrossRepository,
) -> None:
    # Given: EXIF data with unknown brand but recognizable model
    exif_data = {"LensModel": "Canon EF 50mm f/1.8", "LensMake": "Unknown Brand"}

    # When: Calling from_exif
    lens = LensService.from_exif(exif_data, db_enabled=False, repo=repository)

    # Then: The brand should be derived from the model name
    assert lens.brand == "canon"


@patch("albatross.services.search.query.requests.get")
def test_from_exif_parses_lens_specification(
    mock_requests_get: Mock, repository: AlbatrossRepository
) -> None:
    # Given: EXIF data with valid LensSpecification
    exif_data = {
        "LensModel": "Test Model",
        "LensSpecification": [24, 70, 2.8, 4.0],
    }

    # When: Calling from_exif
    lens = LensService.from_exif(exif_data, db_enabled=False, repo=repository)

    # Then: Focal lengths and apertures should be parsed correctly
    assert lens.focal_length_min == 24
    assert lens.focal_length_max == 70
    assert lens.largest_aperture_at_minimum_focal_length == 2.8
    assert lens.largest_aperture_at_maximum_focal_length == 4.0


@patch("albatross.services.search.query.requests.get")
def test_from_exif_handles_zero_division_in_lens_specification(
    mock_requests_get: Mock,
    repository: AlbatrossRepository,
    caplog: pytest.LogCaptureFixture,
) -> None:
    # Given: EXIF data with LensSpecification causing ZeroDivisionError
    exif_data = {
        "LensModel": "Test Model",
        "LensSpecification": [[0, 0], [0, 0], [0, 0], [0, 0]],
    }

    # When: Calling from_exif
    lens = LensService.from_exif(exif_data, db_enabled=False, repo=repository)

    # Then: A warning should be logged, and all values should be 0.0
    assert "Division by zero error in lens data" in caplog.text
    assert lens.focal_length_min == 0.0
    assert lens.focal_length_max == 0.0


@patch("albatross.services.search.query.requests.get")
def test_from_exif_handles_invalid_focal_lengths(
    mock_requests_get: Mock, repository: AlbatrossRepository
) -> None:
    # Given: EXIF data with invalid focal lengths
    exif_data = {
        "LensModel": "Test Model",
        "LensSpecification": [float("nan"), float("nan"), 2.8, 4.0],
    }

    # When: Calling from_exif
    lens = LensService.from_exif(exif_data, db_enabled=False, repo=repository)

    # Then: Focal lengths should be None
    assert lens.focal_length_min is None
    assert lens.focal_length_max is None


@patch("albatross.services.search.query.requests.get")
def test_from_exif_sets_prime_attribute(
    mock_requests_get: Mock, repository: AlbatrossRepository
) -> None:
    # Given: EXIF data for a prime lens
    exif_data = {
        "LensModel": "Test Model",
        "LensSpecification": [50, 50, 1.8, 1.8],
    }

    # When: Calling from_exif
    lens = LensService.from_exif(exif_data, db_enabled=False, repo=repository)

    # Then: The lens should be marked as prime
    assert lens.prime is True


def test_from_exif_falls_back_to_from_model_name(
    repository: AlbatrossRepository,
) -> None:
    # Given: EXIF data with no LensSpecification
    exif_data = {"LensModel": "Canon EF 50mm f/1.8"}

    # When: Calling from_exif
    lens = LensService.from_exif(exif_data, db_enabled=False, repo=repository)

    # Then: The lens should be created using from_model_name
    assert lens.model == "Canon EF 50mm f/1.8"
