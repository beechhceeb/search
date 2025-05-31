from typing import Any
from unittest.mock import Mock, patch

from albatross.models.image_exif import ImageExif
from albatross.repository.base_repository import AlbatrossRepository
from albatross.services.image_exif import ImageExifService
from albatross.services.lens import LensService


@patch("albatross.services.search.query.requests.get")
def test_exif_serializer_from_exif(
    mock_requests_get: Mock,
    exif_data: dict[str, Any],
    filename: str,
    repository: AlbatrossRepository,
) -> None:
    # Given exif_data, filename, camera, lens
    # When from_exif is called with exif_data and filename
    result = ImageExifService.from_exif(
        exif_data, filename, db_enabled=False, repo=repository
    )

    # Then an ExifData object is returned
    assert isinstance(result, ImageExif)

    # And the ExifData object has the correct attributes
    assert result.filename == filename
    assert result.iso == 100
    assert result.shutter_speed == 0.01
    assert result.aperture == 2.8
    assert result.focal_length == 50.0
    assert result.exif_version == "0230"


@patch("albatross.services.search.query.requests.get")
@patch("albatross.services.image_exif.LensService.from_exif")
def test_from_exif_when_lens_serializer_from_exif_raises_value_error(
    mock_lens_serializer: LensService,
    mock_requests_get: Mock,
    exif_data: dict[str, Any],
    filename: str,
    repository: AlbatrossRepository,
) -> None:
    # Given the lens serializer raises a ValueError
    mock_lens_serializer.side_effect = ValueError("No lens set")

    # When from_exif is called with exif_data and filename
    result = ImageExifService.from_exif(
        exif_data, filename, db_enabled=False, repo=repository
    )

    # Then an ExifData object is returned
    assert isinstance(result, ImageExif)

    # And the ExifData object has the correct attributes
    assert result.filename == filename
    assert result.iso == 100
    assert result.shutter_speed == 0.01
    assert result.aperture == 2.8
    assert result.focal_length == 50.0
