from typing import Any

import pytest


@pytest.fixture
def exif_data() -> dict[str, Any]:
    return {
        "ExifVersion": "0230",
        "ExposureTime": [1, 100],
        "ApertureValue": 2.8,
        "ISOSpeedRatings": 100,
        "FocalLength": 50.0,
        "Make": "Nikon",
        "Model": "D850",
        "FocalLengthIn35mmFilm": 50,
        "LensModel": "50mm f/1.8",
        "LensMake": "Nikon",
        "XResolution": 300,
        "YResolution": 300,
    }


@pytest.fixture
def filename() -> str:
    return "test_image.jpg"
