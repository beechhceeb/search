from typing import Any

import pytest

from albatross.config import MountType
from albatross.models.lens import Lens


@pytest.fixture
def lens_primitive() -> dict[str, Any]:
    return {
        "brand": "Canon",
        "model": "EF 24-70mm f/2.8L II USM",
        "focal_length_min": 24.0,
        "focal_length_max": 70.0,
        "largest_aperture_at_minimum_focal_length": 2.8,
        "largest_aperture_at_maximum_focal_length": 2.8,
        "prime": False,
        "mount": MountType.EF,
    }


@pytest.fixture
def lens(lens_primitive: dict[str, Any]) -> Lens:
    lens = Lens(
        brand=lens_primitive["brand"],
        model=lens_primitive["model"],
        focal_length_min=lens_primitive["focal_length_min"],
        focal_length_max=lens_primitive["focal_length_max"],
        largest_aperture_at_minimum_focal_length=lens_primitive[
            "largest_aperture_at_minimum_focal_length"
        ],
        largest_aperture_at_maximum_focal_length=lens_primitive[
            "largest_aperture_at_maximum_focal_length"
        ],
        prime=lens_primitive["prime"],
        mount=lens_primitive["mount"],
    )
    return lens


@pytest.fixture
def sony_fe_lens() -> Lens:
    return Lens(
        brand="Sony",
        model="FE 24-70mm f/2.8 GM",
        focal_length_min=24.0,
        focal_length_max=70.0,
        largest_aperture_at_minimum_focal_length=2.8,
        largest_aperture_at_maximum_focal_length=2.8,
        prime=False,
        mount=MountType.FE,
    )


@pytest.fixture
def lenses() -> list[Lens]:
    lenses: list[Lens] = [
        Lens(
            brand="Canon",
            model="EF 24-70mm f/2.8L II USM",
            focal_length_min=24.0,
            focal_length_max=70.0,
            largest_aperture_at_minimum_focal_length=2.8,
            largest_aperture_at_maximum_focal_length=2.8,
            prime=False,
            mount=MountType.EF,
        ),
        Lens(
            brand="Canon",
            model="EF 70-200mm f/2.8L IS III USM",
            focal_length_min=70.0,
            focal_length_max=200.0,
            largest_aperture_at_minimum_focal_length=2.8,
            largest_aperture_at_maximum_focal_length=2.8,
            prime=False,
            mount=MountType.EF,
        ),
        Lens(
            brand="Canon",
            model="EF 50mm f/1.8",
            focal_length_min=50.0,
            focal_length_max=50.0,
            largest_aperture_at_minimum_focal_length=1.8,
            largest_aperture_at_maximum_focal_length=1.8,
            prime=True,
            mount=MountType.EF,
        ),
    ]
    return lenses


@pytest.fixture
def prime_lens(lens_primitive: dict[str, Any]) -> Lens:
    lens = Lens(
        brand=lens_primitive["brand"],
        model="EF 50mm f/1.8",
        focal_length_min=50,
        focal_length_max=50,
        largest_aperture_at_minimum_focal_length=1.8,
        largest_aperture_at_maximum_focal_length=1.8,
        prime=True,
        mount=lens_primitive["mount"],
    )
    return lens
