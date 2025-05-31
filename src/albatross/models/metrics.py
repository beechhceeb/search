from typing import Optional

from albatross.models.camera import Camera
from albatross.models.image_exif import ImageExif
from albatross.models.lens import Lens


class Metrics:
    def __init__(
        self,
        highest_possible_focal_length: list[float],
        longest_focal_length: float,
        lowest_possible_focal_length: list[float],
        shortest_focal_length: float,
        zoom_focal_lengths_inbetween_min_max: list[float],
        average_focal_length: float | None,
        mode_focal_length: float | None,
        instances_aperture_at_widest: list[float],
        total_images: int,
        instances_high_iso: list[int],
        instances_exceeds_reciprocal: list[float],
        lenses: list[Lens],
        zooms: list[Lens],
        primes: list[Lens],
        instances_aperture: list[float],
        instances_focal_length: list[float],
        instances_focal_length_zooms: list[float],
        instances_focal_length_primes: list[float],
        instances_iso: list[float],
        instances_shutter_speed: list[float],
        cameras: list[Camera],
        camera_frequency: Optional[dict[str, dict[str, float]]] = None,
        lens_frequency: Optional[dict[str, dict[str, float]]] = None,
        focal_range: range | None = None,
        instances_exposure_in_dark: Optional[list[float]] = None,
        instances_exposures: Optional[list[float]] = None,
        instances_aspect_ratio: Optional[list[float]] = None,
        images: Optional[list[ImageExif]] = None,
    ):
        self.highest_possible_focal_length = highest_possible_focal_length
        self.longest_focal_length = longest_focal_length
        self.lowest_possible_focal_length = lowest_possible_focal_length
        self.shortest_focal_length = shortest_focal_length
        self.zoom_focal_lengths_inbetween_min_max = zoom_focal_lengths_inbetween_min_max
        self.average_focal_length = average_focal_length
        self.mode_focal_length = mode_focal_length
        self.instances_aperture_at_widest = instances_aperture_at_widest
        self.total_images = total_images
        self.instances_high_iso = instances_high_iso
        self.instances_exceeds_reciprocal = instances_exceeds_reciprocal
        self.lenses = lenses
        self.zooms = sorted(
            zooms,
            key=lambda lens: (
                lens_frequency[lens.model]["frequency"] if lens_frequency else 0
            ),
            reverse=True,
        )
        self.primes = sorted(
            primes,
            key=lambda lens: (
                lens_frequency[lens.model]["frequency"] if lens_frequency else 0
            ),
            reverse=True,
        )
        self.instances_aperture = instances_aperture
        self.instances_focal_length = instances_focal_length
        self.instances_focal_length_zooms = instances_focal_length_zooms
        self.instances_focal_length_primes = instances_focal_length_primes
        self.instances_iso = instances_iso
        self.instances_shutter_speed = instances_shutter_speed
        self.cameras = sorted(
            [camera for camera in cameras if camera.model.lower() != "unknown model"],
            key=lambda camera: (
                camera_frequency[camera.model]["frequency"] if camera_frequency else 0
            ),
            reverse=True,
        )
        self.camera_frequency = camera_frequency
        self.lens_frequency = lens_frequency
        self.focal_range = focal_range
        self.instances_exposure_in_dark = instances_exposure_in_dark
        self.instances_exposures = instances_exposures
        self.instances_aspect_ratio = instances_aspect_ratio
        self.images = images
