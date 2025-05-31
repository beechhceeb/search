import json

from albatross.models.exif_collections import (
    ISO,
    Aperture,
    FocalLength,
    Illuminance,
    ShutterSpeed,
)
from albatross.models.metrics import Metrics
from albatross.models.results import Results
from albatross.serializers.exif_collections import (
    ApertureSerializer,
    ExposureSerializer,
    FocalLengthSerializer,
    ISOSerializer,
    ShutterSpeedSerializer,
)
from albatross.serializers.results import ResultsSerializer


def test_to_json_given_results_object_when_serialized_then_returns_correct_json(
    metrics: Metrics,
    focal_length: FocalLength,
    aperture: Aperture,
    iso: ISO,
    shutter_speed: ShutterSpeed,
    exposure: Illuminance,
) -> None:
    # Given a Results object
    results = Results(
        metrics=metrics,
        focal_length=focal_length,
        aperture=aperture,
        iso=iso,
        shutter_speed=shutter_speed,
        exposure=exposure,
    )
    serializer = ResultsSerializer()

    # When calling to_json
    json_result = serializer.to_json(results)

    # Then it should return a JSON string with the correct data
    data = json.loads(json_result)
    assert data["metrics"]["total_images"] == metrics.total_images
    assert data["metrics"]["focal_range"] == (
        f"{metrics.focal_range.start} - {metrics.focal_range.stop}"
    )
    assert data["focal_length"] == FocalLengthSerializer().to_dict(focal_length)
    assert data["aperture"] == ApertureSerializer().to_dict(aperture)
    assert data["iso"] == ISOSerializer().to_dict(iso)
    assert data["shutter_speed"] == ShutterSpeedSerializer().to_dict(shutter_speed)
    assert data["exposure"] == ExposureSerializer().to_dict(exposure)
