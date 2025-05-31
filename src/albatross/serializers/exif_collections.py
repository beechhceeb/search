from typing import Any

from albatross.models.exif_collections import (
    ISO,
    Aperture,
    BaseExifAttribute,
    FocalLength,
    Illuminance,
    ShutterSpeed,
)


class ExifCollectionsSerializer:
    """
    Serializes a BaseExifAttribute to json
    """

    def to_dict(self, exif_collections: BaseExifAttribute) -> dict[str, Any]:
        """
        Serializes a BaseExifAttribute to json
        """
        return {
            "total_images": getattr(exif_collections, "total_images", None),
            "instances": getattr(exif_collections, "instances", None),
            "instances_at_highest_value": getattr(
                exif_collections, "instances_at_highest_value", None
            ),
            "instances_at_lowest_value": getattr(
                exif_collections, "instances_at_lowest_value", None
            ),
            "highest_value": getattr(exif_collections, "highest_value", None),
            "percentage_taken_at_highest_value": getattr(
                exif_collections, "percentage_taken_at_highest_value", None
            ),
            "mode_instances_at_highest_value": getattr(
                exif_collections, "mode_instances_at_highest_value", None
            ),
            "lowest_value": getattr(exif_collections, "lowest_value", None),
            "percentage_taken_at_lowest_value": getattr(
                exif_collections, "percentage_taken_at_lowest_value", None
            ),
            "mode_instances_at_lowest_value": getattr(
                exif_collections, "mode_instances_at_lowest_value", None
            ),
            "mean": getattr(exif_collections, "mean", None),
            "mode": getattr(exif_collections, "mode", None),
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> BaseExifAttribute:
        """
        Deserializes a dictionary to a BaseExifAttribute object
        """
        # This method should be implemented in subclasses
        raise NotImplementedError("Subclasses must implement from_dict method")


class FocalLengthSerializer(ExifCollectionsSerializer):
    def to_dict(self, focal_length: FocalLength) -> dict[str, Any]:
        """
        Serializes a FocalLength object to json
        """
        base_exif_data: dict[str, Any] = super(FocalLengthSerializer, self).to_dict(
            focal_length
        )
        return base_exif_data

    @staticmethod
    def from_dict(data: dict[str, Any]) -> FocalLength:
        """
        Deserializes a dictionary to a FocalLength object
        """
        return FocalLength(
            instances=data["instances"],
            instances_max=data["instances_at_highest_value"],
            instances_min=data["instances_at_lowest_value"],
        )


class ApertureSerializer(ExifCollectionsSerializer):
    def to_dict(self, aperture: Aperture) -> dict[str, Any]:
        """
        Serializes an Aperture object to json
        """
        base_exif_data: dict[str, Any] = super(ApertureSerializer, self).to_dict(
            aperture
        )
        return base_exif_data

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Aperture:
        """
        Deserializes a dictionary to an Aperture object
        """
        return Aperture(
            instances=data["instances"],
            instances_wide_open=data["instances_at_highest_value"],
        )


class ISOSerializer(ExifCollectionsSerializer):
    def to_dict(self, iso: ISO) -> dict[str, Any]:
        """
        Serializes an ISO object to json
        """
        base_exif_data: dict[str, Any] = super(ISOSerializer, self).to_dict(iso)
        return base_exif_data

    @staticmethod
    def from_dict(data: dict[str, Any]) -> ISO:
        """
        Deserializes a dictionary to an ISO object
        """
        return ISO(instances=data["instances"])


class ShutterSpeedSerializer(ExifCollectionsSerializer):
    def to_dict(self, shutter_speed: ShutterSpeed) -> dict[str, Any]:
        """
        Serializes a ShutterSpeed object to json
        """
        base_exif_data: dict[str, Any] = super(ShutterSpeedSerializer, self).to_dict(
            shutter_speed
        )
        return base_exif_data

    @staticmethod
    def from_dict(data: dict[str, Any]) -> ShutterSpeed:
        """
        Deserializes a dictionary to a ShutterSpeed object
        """
        return ShutterSpeed(
            instances=data["instances"],
            exceeds_reciprocal=data["instances_at_highest_value"],
        )


class ExposureSerializer(ExifCollectionsSerializer):
    def to_dict(self, exposure: Illuminance) -> dict[str, Any]:
        """
        Serializes a ShutterSpeed object to json
        """
        base_exif_data: dict[str, Any] = super(ExposureSerializer, self).to_dict(
            exposure
        )
        return base_exif_data

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Illuminance:
        """
        Deserializes a dictionary to an Exposure object
        """
        return Illuminance(
            instances=data["instances"],
            instances_in_dark=data["instances_at_lowest_value"],
        )
