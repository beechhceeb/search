import json
import logging
from typing import Any

from albatross.enums.enums import MountType
from albatross.models.lens import Lens

log = logging.getLogger(__name__)


class LensSerializer:
    @staticmethod
    def serialize(lens: Lens) -> str:
        """Serializes the Lens object to JSON."""
        lens_dict = {
            key: value
            for key, value in lens.__dict__.items()
            if not key.startswith("_sa_")
        }
        lens_dict["id"] = str(lens_dict["id"])
        return json.dumps(lens_dict)

    @staticmethod
    def deserialize(data: str) -> Lens:
        """Deserializes the JSON string to a Lens object."""
        lens_data = json.loads(data)
        return Lens(
            brand=lens_data["brand"],
            model=lens_data["model"],
            focal_length_min=lens_data["focal_length_min"],
            focal_length_max=lens_data["focal_length_max"],
            largest_aperture_at_minimum_focal_length=lens_data[
                "largest_aperture_at_minimum_focal_length"
            ],
            largest_aperture_at_maximum_focal_length=lens_data[
                "largest_aperture_at_maximum_focal_length"
            ],
            mount=lens_data.get("mount"),
            prime=lens_data["prime"],
        )

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Lens:
        """
        Deserializes a dictionary to a Lens object.
        """
        return Lens(
            brand=data["brand"],
            model=data["model"],
            focal_length_min=data["focal_length_min"],
            focal_length_max=data["focal_length_max"],
            largest_aperture_at_minimum_focal_length=data[
                "largest_aperture_at_minimum_focal_length"
            ],
            largest_aperture_at_maximum_focal_length=data[
                "largest_aperture_at_maximum_focal_length"
            ],
            mount=MountType(data.get("mount", "").lower()),
            prime=data["prime"],
        )

    @staticmethod
    def to_dict(lens: Lens) -> dict[str, Any]:
        """
        Serializes a Lens object to json
        """
        return {
            "brand": lens.brand,
            "model": lens.model,
            "focal_length_min": lens.focal_length_min,
            "focal_length_max": lens.focal_length_max,
            "largest_aperture_at_minimum_focal_length": lens.largest_aperture_at_minimum_focal_length,  # noqa: E501
            "largest_aperture_at_maximum_focal_length": lens.largest_aperture_at_maximum_focal_length,  # noqa: E501
            "mount": lens.mount.name if lens.mount else None,
            "prime": lens.prime,
        }
