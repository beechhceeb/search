import json
import logging
from typing import Any

from albatross.models.recommendations import Recommendations
from albatross.serializers.camera import CameraSerializer
from albatross.serializers.lens import LensSerializer
from albatross.serializers.results import ResultsSerializer
from albatross.utils import make_dictionary_serializable

log = logging.getLogger(__name__)


class RecommendationsSerializer:
    @staticmethod
    def to_dict(recommendations: Recommendations) -> dict[str, Any]:
        """
        Serializes a Recommendations object to json
        """

        results_serializer = ResultsSerializer()
        lens_serializer = LensSerializer()
        camera_serializer = CameraSerializer()
        return {
            "primary_camera": camera_serializer.to_dict(recommendations.primary_camera),
            "primary_mount_lenses": [
                lens_serializer.to_dict(lens)
                for lens in recommendations.primary_mount_lenses
            ],
            "current_widest_aperture": recommendations.current_widest_aperture,
            "favourite_focal_length": recommendations.favourite_focal_length,
            "recommended_aperture": recommendations.recommended_aperture,
            "recommended_focal_length": recommendations.recommended_focal_length,
            "recommendation_statement": recommendations.recommendation_statement,
            "results": (
                results_serializer.to_dict(recommendations.results)
                if getattr(recommendations, "results", None) is not None
                else None
            ),
        }

    @staticmethod
    def to_json(recommendations: "Recommendations") -> str:
        """
        Serializes a Recommendations object to json
        """
        self_dict = RecommendationsSerializer.to_dict(recommendations)

        self_dict = make_dictionary_serializable(self_dict)

        try:
            return json.dumps(self_dict)
        except Exception as e:
            log.error(f"Error serializing Recommendations object: {e}")
            raise

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Recommendations":
        """
        Deserializes a Recommendations object from a dict
        """
        results_serializer = ResultsSerializer()
        lens_serializer = LensSerializer()
        camera_serializer = CameraSerializer()

        primary_camera = camera_serializer.from_dict(data["primary_camera"])
        primary_mount_lenses = [
            lens_serializer.from_dict(lens) for lens in data["primary_mount_lenses"]
        ]
        current_widest_aperture = data["current_widest_aperture"]
        favourite_focal_length = data["favourite_focal_length"]
        recommended_aperture = data["recommended_aperture"]
        recommended_focal_length = data["recommended_focal_length"]
        recommendation_statement = data["recommendation_statement"]
        results = results_serializer.from_dict(data["results"])

        return Recommendations(
            primary_camera=primary_camera,
            primary_mount_lenses=primary_mount_lenses,
            current_widest_aperture=current_widest_aperture,
            favourite_focal_length=favourite_focal_length,
            recommended_aperture=recommended_aperture,
            recommended_focal_length=recommended_focal_length,
            recommendation_statement=recommendation_statement,
            results=results,
        )

    @staticmethod
    def from_json(json_string: str) -> "Recommendations":
        """
        Deserializes a Recommendations object from json
        """
        data: dict[str, Any] = json.loads(json_string)
        # Convert the focal_range string back to a range object
        if data["results"]["metrics"]["focal_range"]:  # pragma: no branch
            start, stop = map(
                int,
                [
                    data["results"]["metrics"]["focal_range"][0],
                    data["results"]["metrics"]["focal_range"][-1] + 1,
                ],
            )
            data["results"]["metrics"]["focal_range"] = range(start, stop)

        return RecommendationsSerializer.from_dict(data)

    @staticmethod
    def to_json_abridged(recommendations: Recommendations) -> str:
        """
        Serializes a Recommendations object to json without the instances
        """
        recommendations_dict = RecommendationsSerializer.to_dict(recommendations)
        abridged_dict: dict[str, Any] = (
            RecommendationsSerializer.strip_dict_of_verbose_keys(
                [
                    "instances",
                    "total_images",
                    "zoom_focal_lengths_inbetween_min_max",
                    "possible_focal_length",
                ],
                recommendations_dict,
            )
        )
        # Also dump the results.metrics.cameras, results.metrics.lenses,
        # results.metrics.primes, results.metrics.zooms
        abridged_dict["results"]["metrics"].pop("cameras", None)
        abridged_dict["results"]["metrics"].pop("lenses", None)
        abridged_dict["results"]["metrics"].pop("primes", None)
        abridged_dict["results"]["metrics"].pop("zooms", None)

        if abridged_dict["results"]["metrics"]["focal_range"]:
            abridged_dict["results"]["metrics"]["focal_range"] = str(
                abridged_dict["results"]["metrics"]["focal_range"]
            )
        else:
            abridged_dict["results"]["metrics"]["focal_range"] = None

        return json.dumps(abridged_dict)

    @staticmethod
    def strip_dict_of_verbose_keys(
        verbose_keys: list[str], _dict: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Strips a dict of verbose keys. searches through the dict and sub dicts
        """
        return_dict: dict[str, Any] = {}
        for key in _dict.keys():
            if not any([v for v in verbose_keys if v in key]):
                if isinstance(_dict[key], dict):
                    return_dict[key] = (
                        RecommendationsSerializer.strip_dict_of_verbose_keys(
                            verbose_keys, _dict[key]
                        )
                    )
                else:
                    return_dict[key] = _dict[key]
        return return_dict
