import json
from typing import Any

from albatross.models.results import Results
from albatross.serializers.exif_collections import (
    ApertureSerializer,
    ExposureSerializer,
    FocalLengthSerializer,
    ISOSerializer,
    ShutterSpeedSerializer,
)
from albatross.serializers.metrics import MetricsSerializer


class ResultsSerializer:
    """
    Serializes a Results object to json
    """

    def to_dict(self, results: Results) -> dict[str, Any]:
        """
        Serializes a Results object to json
        """
        focal_length_serializer = FocalLengthSerializer()
        aperture_serializer = ApertureSerializer()
        iso_serializer = ISOSerializer()
        shutter_speed_serializer = ShutterSpeedSerializer()
        exposure_serializer = ExposureSerializer()
        metrics_serializer = MetricsSerializer()
        return {
            "focal_length": focal_length_serializer.to_dict(results.focal_length),
            "aperture": aperture_serializer.to_dict(results.aperture),
            "iso": iso_serializer.to_dict(results.iso),
            "shutter_speed": shutter_speed_serializer.to_dict(results.shutter_speed),
            "exposure": exposure_serializer.to_dict(results.exposure),
            "metrics": metrics_serializer.to_dict(results.metrics),
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Results:
        """
        Deserializes a dictionary to a Results object
        """
        focal_length = FocalLengthSerializer.from_dict(data["focal_length"])
        aperture = ApertureSerializer.from_dict(data["aperture"])
        iso = ISOSerializer.from_dict(data["iso"])
        shutter_speed = ShutterSpeedSerializer.from_dict(data["shutter_speed"])
        exposure = ExposureSerializer.from_dict(data["exposure"])
        metrics = MetricsSerializer.from_dict(data["metrics"])

        return Results(
            metrics=metrics,
            focal_length=focal_length,
            aperture=aperture,
            iso=iso,
            exposure=exposure,
            shutter_speed=shutter_speed,
        )

    def to_json(self, results: Results) -> str:
        """
        Serializes a Results object to json
        """
        data = self.to_dict(results)
        data["metrics"]["focal_range"] = (
            f"{data['metrics']['focal_range'].start} - "
            f"{data['metrics']['focal_range'].stop}"
        )
        return json.dumps(data)

    @staticmethod
    def from_json(json_string: str) -> Results:
        """Deserialize a Results object from a JSON string."""
        data: dict[str, Any] = json.loads(json_string)
        if data["metrics"]["focal_range"]:
            start, stop = map(
                int,
                data["metrics"]["focal_range"].split(" - "),
            )
            data["metrics"]["focal_range"] = range(start, stop)
        return ResultsSerializer.from_dict(data)
