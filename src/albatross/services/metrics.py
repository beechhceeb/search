import logging
import statistics

from albatross.config import HIGH_ISO_LIMIT, INITIAL_LUMINANCE_VALUES
from albatross.models.camera import Camera
from albatross.models.image_exif import ImageExif
from albatross.models.lens import Lens
from albatross.models.metrics import Metrics

log = logging.getLogger(__name__)


class MetricsService:
    @staticmethod
    def from_exif(all_exif_data: list[ImageExif]) -> Metrics:
        """
        create an object with quantifiable metrics from metadata
        """

        if not all_exif_data:
            raise ValueError("No images to process")

        lenses: list[Lens] = []
        cameras: list[Camera] = []

        all_apertures: list[float] = []
        all_isos: list[int] = []
        all_shutter_speeds: list[float] = []
        all_focal_lengths: list[float] = []
        focal_lengths_zooms: list[float] = []
        focal_lengths_primes: list[float] = []
        all_exposures: list[float] = []
        all_aspect_ratios: list[float] = []

        instances_aperture_at_widest: list[float] = []

        lowest_possible_focal_length: list[float] = []
        highest_possible_focal_length: list[float] = []
        zoom_focal_lengths_inbetween_min_max: list[float] = []

        instances_high_iso: list[int] = []

        instances_exceeds_reciprocal: list[float] = []

        instances_exposure_in_dark: list[float] = []

        camera_frequency: dict[str, dict[str, float]] = {}
        lens_frequency: dict[str, dict[str, float]] = {}

        # filter out results with unknown camera model
        all_exif_data = [
            exif for exif in all_exif_data if exif.camera.model != "unknown model"
        ]

        for image in all_exif_data:
            try:
                if image.lens:  # pragma: no branch
                    if image.lens.model not in [
                        _lens.model for _lens in lenses
                    ]:  # pragma: no branch
                        lenses.append(image.lens)
                        lens_frequency[image.lens.model] = {
                            "frequency": 1,
                            "percentage_of_all": 0,
                        }
                    else:
                        lens = next(
                            (
                                _lens
                                for _lens in lenses
                                if _lens.model == image.lens.model
                            ),
                            None,
                        )
                        if lens:  # pragma: no branch
                            lens_frequency[lens.model]["frequency"] += 1
                if image.camera:  # pragma: no branch
                    if image.camera.model not in [
                        c.model for c in cameras
                    ]:  # pragma: no branch
                        cameras.append(image.camera)
                        camera_frequency[image.camera.model] = {
                            "frequency": 1,
                            "percentage_of_all": 0,
                        }
                    else:
                        camera = next(
                            (c for c in cameras if c.model == image.camera.model), None
                        )
                        if camera:  # pragma: no branch
                            camera_frequency[camera.model]["frequency"] += 1

                focal_length: float | None = None

                if image.camera.crop_factor and image.focal_length:  # pragma: no branch
                    # Set focal length to its 35mm equivalent
                    focal_length = image.focal_length * image.camera.crop_factor

                # General metrics
                if image.aperture:  # pragma: no branch
                    all_apertures.append(image.aperture)
                    # Aperture
                    if (
                        image.lens
                        and image.lens.largest_aperture_at_minimum_focal_length
                        and (
                            image.aperture
                            == image.lens.largest_aperture_at_minimum_focal_length
                        )
                    ):  # pragma: no branch
                        instances_aperture_at_widest.append(image.aperture)

                # ISO
                if image.iso:  # pragma: no branch
                    all_isos.append(image.iso)
                    if image.iso > HIGH_ISO_LIMIT:
                        instances_high_iso.append(image.iso)

                # Shutter speed
                if image.shutter_speed:  # pragma: no branch
                    all_shutter_speeds.append(image.shutter_speed)
                    if image.focal_length and MetricsService.exceeds_reciprocal(
                        image.shutter_speed, image.focal_length
                    ):
                        instances_exceeds_reciprocal.append(image.shutter_speed)

                # Focal length
                if focal_length:  # pragma: no branch
                    all_focal_lengths.append(focal_length)

                    # If the lens is a zoom, we can calculate how often certain
                    # focal lengths are used
                    if image.lens and not image.lens.prime:
                        focal_lengths_zooms.append(focal_length)
                        if focal_length == image.lens.focal_length_min:
                            lowest_possible_focal_length.append(focal_length)
                        elif focal_length == image.lens.focal_length_max:
                            highest_possible_focal_length.append(focal_length)
                        else:
                            zoom_focal_lengths_inbetween_min_max.append(focal_length)
                    else:
                        focal_lengths_primes.append(focal_length)

                if image.exposure:
                    all_exposures.append(image.exposure)
                    if (
                        image.exposure
                        < INITIAL_LUMINANCE_VALUES["Dim Indoors / Blue Hour"][
                            "boundary"
                        ]
                    ):  # pragma: no branch
                        instances_exposure_in_dark.append(image.exposure)

                if image.aspect_ratio:
                    all_aspect_ratios.append(image.aspect_ratio)

            except Exception as e:  # pragma: no cover
                log.warning(f"Error processing image {image.filename}: {e}")
                log.debug(e, exc_info=True)
                continue

        # Once we know how many images were taken with each camera and lens
        # we can calculate the frequency percentage
        for camera in cameras:
            camera_frequency[camera.model]["percentage_of_all"] = round(
                camera_frequency[camera.model]["frequency"] / len(all_exif_data) * 100,
                2,
            )

        for lens in lenses:
            lens_frequency[lens.model]["percentage_of_all"] = round(
                lens_frequency[lens.model]["frequency"] / len(all_exif_data) * 100, 2
            )

        average_focal_length: float | None = None
        mode_focal_length: float | None = None
        shortest_focal_length: float | None = None
        longest_focal_length: float | None = None
        focal_range: range | None = None
        if all_focal_lengths:  # pragma: no branch
            average_focal_length = statistics.fmean(all_focal_lengths)
            mode_focal_length = statistics.mode(all_focal_lengths)
            shortest_focal_length = min(all_focal_lengths)
            longest_focal_length = max(all_focal_lengths)
            try:
                focal_range = MetricsService.calculate_focal_range(lenses)
            except ValueError:
                log.warning("No lenses to process to calculate focal range")
                focal_range = None

        # Sort lists
        highest_possible_focal_length.sort(reverse=True)
        lowest_possible_focal_length.sort()
        instances_aperture_at_widest.sort(reverse=True)

        return Metrics(
            highest_possible_focal_length=highest_possible_focal_length,
            shortest_focal_length=shortest_focal_length,
            lowest_possible_focal_length=lowest_possible_focal_length,
            longest_focal_length=longest_focal_length,
            zoom_focal_lengths_inbetween_min_max=zoom_focal_lengths_inbetween_min_max,
            average_focal_length=average_focal_length,
            mode_focal_length=mode_focal_length,
            instances_aperture_at_widest=instances_aperture_at_widest,
            total_images=len(all_exif_data),
            instances_high_iso=instances_high_iso,
            instances_exceeds_reciprocal=instances_exceeds_reciprocal,
            lenses=lenses,
            zooms=[lens for lens in lenses if not lens.prime],
            primes=[lens for lens in lenses if lens.prime],
            instances_aperture=all_apertures,
            instances_focal_length=all_focal_lengths,
            instances_focal_length_zooms=focal_lengths_zooms,
            instances_focal_length_primes=focal_lengths_primes,
            instances_iso=all_isos,
            instances_shutter_speed=all_shutter_speeds,
            cameras=cameras,
            camera_frequency=camera_frequency,
            lens_frequency=lens_frequency,
            focal_range=focal_range,
            instances_exposure_in_dark=instances_exposure_in_dark,
            instances_exposures=all_exposures,
            instances_aspect_ratio=all_aspect_ratios,
            images=all_exif_data,
        )

    @staticmethod
    def calculate_focal_range(lenses: list[Lens]) -> range:
        """
        Calculates the focal range of a list of lenses
        """
        if not lenses:
            raise ValueError("No lenses to process")

        shortest_focal_length = min(
            lens.focal_length_min for lens in lenses if lens.focal_length_min
        )
        longest_focal_length = max(
            lens.focal_length_max for lens in lenses if lens.focal_length_max
        )

        return range(int(shortest_focal_length), int(longest_focal_length))

    @staticmethod
    def exceeds_reciprocal(shutter_speed: float, focal_length: float) -> bool:
        reciprocal_limit = 1 / focal_length

        if float(shutter_speed) > reciprocal_limit:
            return True

        return False
