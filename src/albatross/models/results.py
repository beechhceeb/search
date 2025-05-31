from albatross.models.exif_collections import (
    ISO,
    Aperture,
    FocalLength,
    Illuminance,
    ShutterSpeed,
)
from albatross.models.metrics import Metrics


class Results:
    def __init__(
        self,
        focal_length: FocalLength | None,
        aperture: Aperture | None,
        iso: ISO | None,
        shutter_speed: ShutterSpeed | None,
        exposure: Illuminance | None,
        metrics: Metrics,
    ) -> None:
        self.focal_length: FocalLength | None = focal_length
        self.aperture: Aperture | None = aperture
        self.iso: ISO | None = iso
        self.shutter_speed: ShutterSpeed | None = shutter_speed
        self.exposure: Illuminance | None = exposure
        self.metrics: Metrics = metrics

    @staticmethod
    def build(metrics: Metrics) -> "Results":
        """
        Compose the object that will be returned to the view
        :param metrics:
        :return:
        """

        focal_length: FocalLength | None = None
        if metrics.instances_focal_length:
            focal_length = FocalLength(
                instances_max=metrics.highest_possible_focal_length,
                instances_min=metrics.lowest_possible_focal_length,
                instances=metrics.instances_focal_length,
                instances_zooms=metrics.instances_focal_length_zooms,
                instances_primes=metrics.instances_focal_length_primes,
            )

        aperture: Aperture | None = None
        if metrics.instances_aperture:
            aperture = Aperture(
                instances_wide_open=metrics.instances_aperture_at_widest,
                instances=metrics.instances_aperture,
            )

        iso: ISO | None = None
        if metrics.instances_iso:
            iso = ISO(
                instances=metrics.instances_iso,
            )

        shutter_speed: ShutterSpeed | None = None
        if metrics.instances_shutter_speed:
            shutter_speed = ShutterSpeed(
                instances=metrics.instances_shutter_speed,
                exceeds_reciprocal=metrics.instances_exceeds_reciprocal,
            )

        exposure: Illuminance | None = None
        if metrics.instances_exposures:
            exposure = Illuminance(
                instances=metrics.instances_exposures,
                instances_in_dark=metrics.instances_exposure_in_dark,
            )

        return Results(
            focal_length=focal_length,
            aperture=aperture,
            iso=iso,
            shutter_speed=shutter_speed,
            exposure=exposure,
            metrics=metrics,
        )
