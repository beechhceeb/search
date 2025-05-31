import copy
import logging

from albatross.config import PHOTOGRAPHER_CLASSIFICATIONS
from albatross.models.photographer_classification import (
    Achievement,
    PhotographerClassification,
)
from albatross.models.results import Results
from albatross.utils import focal_length_to_field_of_view, get_variation

log = logging.getLogger(__name__)


class PhotographerClassifier:
    def __init__(self, results: Results, current_widest_aperture: float) -> None:
        photographer_types = copy.deepcopy(PHOTOGRAPHER_CLASSIFICATIONS)
        self.classifications: list[PhotographerClassification] = self.classify(
            results=results,
            current_widest_aperture=current_widest_aperture,
            photographer_types=photographer_types,
        )
        self.achievements: list[Achievement] = (
            PhotographerClassifier.build_achievements(results=results)
        )
        self.top_classification: PhotographerClassification = max(
            self.classifications, key=lambda x: x.score
        )
        self.scores: dict[str, int] = {
            classification.name: classification.score
            for classification in sorted(
                self.classifications, key=lambda x: x.score, reverse=True
            )
        }

    @staticmethod
    def classify(
        results: Results,
        photographer_types: dict[str, PhotographerClassification],
        current_widest_aperture: float,
    ) -> list[PhotographerClassification]:
        if not (results.focal_length and results.aperture and results.iso):
            photographer_types["The Stranger"].score = 100
            return list(photographer_types.values())

        PhotographerClassifier._score_collector_professional_minimalist(
            results, photographer_types
        )
        PhotographerClassifier._score_wanderer(results, photographer_types)
        PhotographerClassifier._score_bokeh_master(
            current_widest_aperture, photographer_types
        )
        PhotographerClassifier._score_base_percentages(results, photographer_types)
        PhotographerClassifier._score_stargazer_and_vampire(results, photographer_types)
        PhotographerClassifier._score_monk_and_quickdraw(results, photographer_types)

        scores = [(name, _type.score) for name, _type in photographer_types.items()]
        log.debug(f"Classification Scores: {str(scores)}")

        # Set negative scores to 0
        # Set scores above 100 to 100
        for name, _type in photographer_types.items():
            if _type.score < 0:
                _type.score = 0
            elif _type.score > 100:
                _type.score = 100

        return list(photographer_types.values())

    @staticmethod
    def _score_collector_professional_minimalist(
        results: Results,
        photographer_types: dict[str, PhotographerClassification],
    ) -> None:
        for _ in range(len(results.metrics.lenses) + len(results.metrics.cameras)):
            photographer_types["The Collector"].score += 3
            photographer_types["The Professional"].score += 3
            photographer_types["The Minimalist"].score -= 3

        lens_freq = [
            int(results.metrics.lens_frequency[lens.model]["frequency"])
            for lens in results.metrics.lenses
        ]
        camera_freq = [
            int(results.metrics.camera_frequency[camera.model]["frequency"])
            for camera in results.metrics.cameras
        ]
        total_lens, total_camera = sum(lens_freq), sum(camera_freq)

        normalized_lens = [f / total_lens for f in lens_freq]
        normalized_camera = [f / total_camera for f in camera_freq]

        # Take the standard deviation of the normalized values and use it as
        # a modifier for the scores
        variation = get_variation(normalized_lens + normalized_camera)

        photographer_types["The Professional"].score = int(
            photographer_types["The Professional"].score
            * (1 + ((variation - 0.3) * -1))
        )
        photographer_types["The Collector"].score = int(
            photographer_types["The Collector"].score * (1 + (variation - 0.3))
        )

    @staticmethod
    def _score_wanderer(
        results: Results,
        photographer_types: dict[str, PhotographerClassification],
    ) -> None:
        if results.metrics.focal_range:
            fov_narrow = focal_length_to_field_of_view(
                results.metrics.focal_range.start
            )
            fov_wide = focal_length_to_field_of_view(results.metrics.focal_range.stop)
            range_of_view = fov_narrow - fov_wide
            normalized_range = max(0, min((range_of_view - 10) / 120, 1))

            variation = get_variation(results.focal_length.instances)
            normalized_variation = max(0, min(variation / 30, 1))

            wanderer_score = int(100 * normalized_range * normalized_variation)
            photographer_types["The Wanderer"].score = wanderer_score

    @staticmethod
    def _score_bokeh_master(
        current_widest_aperture: float,
        photographer_types: dict[str, PhotographerClassification],
    ) -> None:
        if current_widest_aperture and current_widest_aperture < 2.8:
            photographer_types["The Bokeh Master"].score += 10

    @staticmethod
    def _score_base_percentages(
        results: Results,
        photographer_types: dict[str, PhotographerClassification],
    ) -> None:
        photographer_types[
            "The Bokeh Master"
        ].score += results.aperture.percentage_taken_at_lowest_value
        photographer_types[
            "The Sniper"
        ].score += results.focal_length.percentage_taken_at_highest_value
        percentage_iso_200_or_less: int = int(
            len([instance for instance in results.iso.instances if instance <= 200])
            / len(results.iso.instances)
            * 100
        )
        photographer_types["The Studio Shooter"].score += (
            results.shutter_speed.percentage_taken_at_lowest_value
            + percentage_iso_200_or_less
        ) / 2

    @staticmethod
    def _score_stargazer_and_vampire(
        results: Results,
        photographer_types: dict[str, PhotographerClassification],
    ) -> None:
        percentage_below_5 = (
            len([instance for instance in results.exposure.instances if instance < 5])
            / len(results.exposure.instances)
            * 100
        )
        slow_shutter_speed = results.shutter_speed.percentage_taken_at_lowest_value

        # percentage of images taken in generally dark conditions
        dark_percentage = results.exposure.percentage_taken_at_lowest_value

        # for the stargazer, we want to add the percentage of images taken at
        # low shutter speed
        # and the percentage of images taken at low exposure
        # the overall percentage of shots taken in the dark further boosts
        # the score (and penalises if it's low)
        photographer_types["The Stargazer"].score += int(
            (percentage_below_5 + slow_shutter_speed + dark_percentage) / 3
        )

        # for the vampire, we want to add the percentage of images not taken
        # at low shutter speed
        # and the percentage of images taken at low exposure
        photographer_types["The Vampire"].score += int(
            (percentage_below_5 + (100 - slow_shutter_speed) + dark_percentage) / 3
        )

    @staticmethod
    def _score_monk_and_quickdraw(
        results: Results,
        photographer_types: dict[str, PhotographerClassification],
    ) -> None:
        # the monk and the quickdraw are opposites
        percentage_iso_below_800: int = int(
            len([instance for instance in results.iso.instances if instance <= 800])
            / len(results.iso.instances)
            * 100
        )
        percentage_iso_above_800: int = 100 - percentage_iso_below_800

        slow_shutter_cutoff = 1 / 25 if results.metrics.cameras[0].ibis else 1 / 50
        slow_shutter_speed = int(
            len(
                [
                    instance
                    for instance in results.shutter_speed.instances
                    if instance > slow_shutter_cutoff
                ]
            )
            / len(results.shutter_speed.instances)
            * 100
        )
        fast_shutter_speed = int(
            len(
                [
                    instance
                    for instance in results.shutter_speed.instances
                    if instance < (1 / 500)
                ]
            )
            / len(results.shutter_speed.instances)
            * 100
        )

        photographer_types["The Monk"].score = int(
            (percentage_iso_below_800 + slow_shutter_speed) / 2
        )
        photographer_types["The Quickdraw"].score = int(
            (percentage_iso_above_800 + fast_shutter_speed) / 2
        )

    @staticmethod
    def build_achievements(results: Results) -> list[Achievement]:
        achievements: list[Achievement] = []

        # Everyone gets this
        achievements.append(
            Achievement(
                name=f"{len(results.metrics.cameras)} Cameras & "
                f"{len(results.metrics.lenses)} Lenses",
                styling={},
            )
        )

        brands: list[tuple[str, dict[str, float]]] = (
            PhotographerClassifier.brand_analysis(results)
        )

        if brands and brands[0][1]["percentage"] > 50:
            achievements.append(
                Achievement(name=f"{brands[0][0].title()} Fan", styling={})
            )

        if results.focal_length:
            if results.focal_length.mean > 70:
                achievements.append(
                    Achievement(
                        name="Distance Shooter",
                        styling={},
                    )
                )

            if results.focal_length.mean < 50:
                achievements.append(
                    Achievement(
                        name="Wide Angle Shooter",
                        styling={},
                    )
                )

            focal_length_frequency = results.focal_length.instances
            focal_length_variation = get_variation(focal_length_frequency)

            if focal_length_variation > 30:
                achievements.append(
                    Achievement(
                        name="Variable Shooter",
                        styling={},
                    )
                )

            if focal_length_variation < 10:
                achievements.append(
                    Achievement(
                        name=f"{int(results.focal_length.mode)} Purist",
                        styling={},
                    )
                )

        if results.metrics.primes and not results.metrics.zooms:
            achievements.append(
                Achievement(
                    name="Prime Fan",
                    styling={},
                )
            )

        if results.metrics.zooms and not results.metrics.primes:
            achievements.append(
                Achievement(
                    name="Zoom Fan",
                    styling={},
                )
            )

        if (
            results.shutter_speed
            and results.shutter_speed.percentage_taken_at_lowest_value > 40
        ):
            achievements.append(
                Achievement(
                    name="Steady Hand",
                    styling={},
                )
            )

        if results.exposure and results.exposure.mode < 3:
            achievements.append(
                Achievement(
                    name="Night Owl",
                    styling={},
                )
            )

        return achievements

    @staticmethod
    def brand_analysis(results: Results) -> list[tuple[str, dict[str, float]]]:
        brands: dict[str, dict[str, int | float]] = {}
        for camera in results.metrics.cameras:
            brand = camera.brand.lower()
            if brand == "unknown brand":
                continue
            if brand not in brands:
                brands[brand] = {"count": 1}
            else:
                brands[brand]["count"] += 1

        for lens in results.metrics.lenses:
            brand = lens.brand.lower()
            if brand == "unknown brand":
                continue
            if brand not in brands:
                brands[brand] = {"count": 1}
            else:
                brands[brand]["count"] += 1

        all_brands_count = sum(brand["count"] for brand in brands.values())
        for brand, data in brands.items():
            data["percentage"] = (brands[brand]["count"] / all_brands_count) * 100

        sorted_brands: list[tuple[str, dict[str, float]]] = sorted(
            brands.items(), key=lambda x: x[1]["percentage"], reverse=True
        )

        return sorted_brands
