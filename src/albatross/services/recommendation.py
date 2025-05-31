import json
import logging
import math
import traceback
from typing import TYPE_CHECKING, Any
from uuid import UUID

from albatross.config import (
    BRIGHT_APERTURE_CUTOFF,
    COMMON_FOCAL_LENGTHS,
    COMMON_LENS_MAX_APERTURES,
    HIGH_ISO_LIMIT,
    LLM_ENABLED,
    LLM_PRODUCT,
    NORMAL_FOCAL_RANGE,
    PERCENTAGE_LIMIT_FOR_HIGH_ISO,
    PERCENTAGE_LIMIT_FOR_WIDE_APERTURE,
    TELEPHOTO_FOCAL_RANGE,
    WIDE_ANGLE_FOCAL_RANGE,
)
from albatross.models.camera import Camera
from albatross.models.lens import Lens
from albatross.models.results import Results
from albatross.repository.base_repository import AlbatrossRepository
from albatross.services.llm.gemini import GeminiService
from albatross.utils import get_closest_round_aperture_value

if TYPE_CHECKING:  # pragma: no cover
    from albatross.models.recommendations import Recommendations

log = logging.getLogger(__name__)


class RecommendationService:
    @staticmethod
    def lenses_contains_primes_at_given_focal_length(
        focal_length: int, lenses: list[Lens]
    ) -> bool:
        return any(
            [
                lens
                for lens in lenses
                if lens.prime and lens.focal_length_max == focal_length
            ]
        )

    @staticmethod
    def metrics_contains_no_fast_lenses(
        lenses: list[Lens], preferred_focal_length: int
    ) -> bool:
        return (
            len(
                [
                    lens
                    for lens in lenses
                    if lens.focal_length_min
                    and lens.focal_length_max
                    and preferred_focal_length
                    in range(
                        math.floor(lens.focal_length_min),
                        math.ceil(lens.focal_length_max),
                    )
                    and lens.largest_aperture_at_minimum_focal_length
                    < BRIGHT_APERTURE_CUTOFF
                ]
            )
            == 0
        )

    @staticmethod
    def get_next_smallest_aperture_value(aperture: float) -> float:
        if aperture not in COMMON_LENS_MAX_APERTURES:
            aperture = get_closest_round_aperture_value(
                aperture, COMMON_LENS_MAX_APERTURES
            )

        try:
            return float(
                COMMON_LENS_MAX_APERTURES[COMMON_LENS_MAX_APERTURES.index(aperture) - 1]
            )
        except IndexError:  # pragma: no cover
            return aperture

    @staticmethod
    def build_recommended_focal_length_by_gaps(
        current_focal_range: range,
        preferred_focal_length: int | None,
        owned_lenses: list[Lens],
        percentage_taken_at_lowest_value: float,
        percentage_taken_at_highest_value: float,
    ) -> int | None:
        if (
            preferred_focal_length
            and not RecommendationService.lenses_contains_primes_at_given_focal_length(
                preferred_focal_length, owned_lenses
            )
        ):
            return int(
                min(
                    COMMON_FOCAL_LENGTHS,
                    key=lambda x: abs(x - preferred_focal_length),
                )
            )
        elif percentage_taken_at_lowest_value > 30 and [
            i for i in WIDE_ANGLE_FOCAL_RANGE if i in current_focal_range
        ]:
            return 28
        elif percentage_taken_at_highest_value > 30 and [
            i for i in TELEPHOTO_FOCAL_RANGE if i in current_focal_range
        ]:
            return 135
        elif [i for i in NORMAL_FOCAL_RANGE if i in current_focal_range]:
            return 50
        return None

    @staticmethod
    def build_recommended_aperture_by_gaps(
        current_widest_aperture: float,
        percentage_wide_open: float,
        percentage_high_iso: float,
    ) -> float:
        if (
            percentage_wide_open > PERCENTAGE_LIMIT_FOR_WIDE_APERTURE
            or percentage_high_iso > PERCENTAGE_LIMIT_FOR_HIGH_ISO
        ):
            recommended_aperture: float = (
                RecommendationService.get_next_smallest_aperture_value(
                    current_widest_aperture
                )
            )
        else:
            recommended_aperture = current_widest_aperture

        return recommended_aperture

    @staticmethod
    def build(
        results: Results,
        repo: AlbatrossRepository,
        db_enabled: bool = True,
        call_llm: bool = True,
    ) -> "Recommendations":
        cameras: list[Camera] = results.metrics.cameras
        primary_camera: Camera | None = max(
            (
                camera
                for camera in cameras
                if isinstance(camera, Camera) and camera.model != "Unknown"
            ),
            key=lambda cam: results.metrics.camera_frequency[cam.model]["frequency"],  # type: ignore
            default=None,
        )

        primary_mount_lenses: list[Lens] = [
            lens
            for lens in results.metrics.lenses
            if lens.mount == primary_camera.mount  # type: ignore
        ]

        current_widest_aperture: float | None = None
        if results.metrics.lenses:  # pragma: no branch
            try:
                current_widest_aperture = min(
                    [
                        lens.largest_aperture_at_minimum_focal_length
                        for lens in results.metrics.lenses
                        if lens.largest_aperture_at_minimum_focal_length
                    ]
                )
            except ValueError:  # pragma: no cover
                current_widest_aperture = None

        favourite_focal_length: int | None = None
        if results.focal_length:  # pragma: no branch
            favourite_focal_length = int(results.focal_length.mode)

        recommended_aperture: float | None = None
        if (
            results.aperture and results.iso and current_widest_aperture
        ):  # pragma: no branch
            recommended_aperture = RecommendationService.build_recommended_aperture_by_gaps(  # noqa: E501
                current_widest_aperture=current_widest_aperture,
                percentage_wide_open=results.aperture.percentage_taken_at_lowest_value,
                percentage_high_iso=results.iso.percentage_taken_at_highest_value,
            )

        recommended_focal_length: int | None = None
        if results.focal_length and results.metrics.focal_range:
            recommended_focal_length = (
                RecommendationService.build_recommended_focal_length_by_gaps(
                    results.metrics.focal_range,
                    favourite_focal_length,
                    results.metrics.lenses,
                    results.focal_length.percentage_taken_at_lowest_value,
                    results.focal_length.percentage_taken_at_highest_value,
                )
            )

        recommendations_statement = RecommendationService.build_minimized_analysis(
            primary_camera, results
        )

        llm_lens_recommendation, llm_camera_recommendation = None, None
        if call_llm:
            try:
                (
                    llm_lens_recommendation,
                    llm_camera_recommendation,
                ) = RecommendationService.get_llm_recommendations(
                    recommendations_statement
                )
            except NotImplementedError:
                log.warning("LLM service not turned on")
            except ConnectionError:  # pragma: no cover
                log.warning("LLM service not working")
                log.error(traceback.format_exc())

        from albatross.models.recommendations import Recommendations

        recommendations = Recommendations(
            primary_camera=primary_camera,
            primary_mount_lenses=primary_mount_lenses,
            current_widest_aperture=current_widest_aperture,
            favourite_focal_length=favourite_focal_length,
            recommended_aperture=recommended_aperture,
            recommended_focal_length=recommended_focal_length,
            results=results,
            recommendation_statement=recommendations_statement,
            llm_lens_recommendation=llm_lens_recommendation,
            llm_camera_recommendation=llm_camera_recommendation,
        )

        if db_enabled:
            recommendations = repo.persist(recommendations)

        return recommendations

    @staticmethod
    def get_llm_recommendations(
        recommendation_statement: str,
    ) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
        if not LLM_ENABLED:
            raise NotImplementedError("LLM service not implemented")
        try:
            if LLM_PRODUCT == "gemini":
                llm_service = GeminiService()  # pragma: no cover
            else:
                raise NotImplementedError("LLM service not implemented")

            analysis: str = recommendation_statement
            lens_recommendation, camera_recommendation = (
                llm_service.build_recommendations(analysis)
            )
            return lens_recommendation, camera_recommendation
        except Exception:  # pragma: no cover
            log.warning("LLM service not working")
            log.debug(traceback.format_exc())
            raise ConnectionError("LLM service not working")

    @staticmethod
    def get_from_persisted_id(
        recommendations_id: UUID,
        repo: AlbatrossRepository,
    ) -> "Recommendations":
        recommendation = repo.get_recommendation(recommendations_id)
        if recommendation:
            return recommendation
        raise ValueError("No recommendation found with that ID")

    @staticmethod
    def populate_llm_recommendations(
        recommendations_id: UUID,
        repo: AlbatrossRepository,
    ) -> "Recommendations":
        """Fetch LLM recommendations for a persisted record and update it."""
        recommendation = RecommendationService.get_from_persisted_id(
            recommendations_id,
            repo=repo,
        )

        if (
            hasattr(recommendation, "llm_lens_recommendation")
            and hasattr(recommendation, "llm_camera_recommendation")
            and recommendation.llm_lens_recommendation
            and recommendation.llm_camera_recommendation
        ):
            return recommendation

        try:
            lens_rec, camera_rec = RecommendationService.get_llm_recommendations(
                recommendation.recommendation_statement
            )
            recommendation.llm_lens_recommendation = lens_rec
            recommendation.llm_camera_recommendation = camera_rec
        except NotImplementedError:  # pragma: no cover
            log.warning("LLM service not turned on")
        except ConnectionError:  # pragma: no cover
            log.warning("LLM service not working")
            log.error(traceback.format_exc())

        repo.persist(recommendation)
        return recommendation

    @staticmethod
    def build_minimized_analysis(primary_camera: Camera, results: Results) -> str:
        stripped_down_analysis: dict[str, Any] = {
            "current_gear": {
                "primary_camera": {
                    "name": (
                        f"{getattr(primary_camera, 'brand', 'Unknown')} "
                        f"{getattr(primary_camera, 'model', 'Unknown')}"
                    ),
                    "sensor_size": getattr(
                        getattr(primary_camera, "sensor_size", None),
                        "name",
                        "Unknown",
                    ),
                    "mount": getattr(
                        getattr(primary_camera, "mount", None),
                        "name",
                        "Unknown",
                    ),
                },
                "compatible_lenses": [
                    getattr(lens, "model", "Unknown")
                    for lens in getattr(results.metrics, "lenses", [])
                    if getattr(lens, "mount", None)
                    == getattr(primary_camera, "mount", None)
                ],
            },
            "analysis_of_pictures": {
                "focal_length": {
                    "percentage_taken_at_maximum_zoom": getattr(
                        results.focal_length,
                        "percentage_taken_at_highest_value",
                        "Unknown",
                    ),
                    "percentage_taken_at_minimum_zoom": getattr(
                        results.focal_length,
                        "percentage_taken_at_lowest_value",
                        0,
                    ),
                    "mean": getattr(results.focal_length, "mean", 0),
                    "mode": getattr(results.focal_length, "mode", "Unknown"),
                },
                "aperture": {
                    "percentage_taken_at_widest": getattr(
                        results.aperture,
                        "percentage_taken_at_lowest_value",
                        "Unknown",
                    ),
                    "mean": getattr(results.aperture, "mean", 0),
                    "mode": getattr(results.aperture, "mode", "Unknown"),
                },
                "iso": {
                    f"percentage_above_{HIGH_ISO_LIMIT}": getattr(
                        results.iso,
                        "percentage_taken_at_highest_value",
                        "Unknown",
                    ),
                    "mean": getattr(results.iso, "mean", 0),
                    "mode": getattr(results.iso, "mode", "Unknown"),
                },
                "shutter_speed": {
                    "percentage_exceeding_reciprocal_rule": getattr(
                        results.shutter_speed,
                        "percentage_taken_at_lowest_value",
                        "Unknown",
                    ),
                    "mean": getattr(
                        results.shutter_speed,
                        "human_readable_mean",
                        "Unknown",
                    ),
                    "mode": getattr(
                        results.shutter_speed,
                        "human_readable_mode",
                        "Unknown",
                    ),
                },
                "exposure": {
                    "illuminance": {
                        light_level: f"{values['percentage']}%"
                        for light_level, values in getattr(
                            getattr(results, "exposure", None),
                            "illuminance",
                            {},
                        ).items()
                    }
                },
                "metrics": {
                    "focal_range": (
                        f"{results.metrics.focal_range.start} -"
                        f" {results.metrics.focal_range.stop}"
                        if results.metrics.focal_range
                        else "unknown"
                    ),
                    "camera_usage": {
                        camera_model: f"{frequency.get('percentage_of_all', 'Unknown')}"
                        for camera_model, frequency in getattr(
                            results.metrics, "camera_frequency", {}
                        ).items()
                    },
                    "lens_usage": {
                        lens_model: f"{frequency.get('percentage_of_all', 'Unknown')}"
                        for lens_model, frequency in getattr(
                            results.metrics, "lens_frequency", {}
                        ).items()
                    },
                },
            },
        }
        return json.dumps(stripped_down_analysis)
