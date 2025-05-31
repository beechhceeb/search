import logging
from datetime import datetime
from typing import Any, Optional

from albatross.config import APERTURES_IN_THIRD_STEPS, DB_ENABLED
from albatross.models.camera import Camera
from albatross.models.image_exif import ImageExif
from albatross.models.lens import Lens
from albatross.repository.base_repository import AlbatrossRepository
from albatross.services.camera import CameraService
from albatross.services.lens import LensService
from albatross.utils import (
    calculate_ev,
    ev100_to_illuminance,
    get_closest_round_aperture_value,
)

log = logging.getLogger(__name__)


class ImageExifService:
    @staticmethod
    def from_exif(
        exif: dict[str, Any],
        filename: str,
        repo: AlbatrossRepository,
        db_enabled: bool = DB_ENABLED,
    ) -> ImageExif:
        exif_version: Optional[str] = exif.get("ExifVersion", None)
        camera: Camera = CameraService.from_exif(
            exif_data=exif, repo=repo, db_enabled=db_enabled
        )
        lens: Optional[Lens] = None
        try:
            # FIXME: we assume that the crop factor and mount of the camera matches the
            #  lens. this doesn't account for adapted lenses
            lens = LensService.from_exif(
                exif,
                mount=camera.mount,
                camera_brand=camera.brand,
                crop_factor=camera.crop_factor,
                db_enabled=db_enabled,
                repo=repo,
            )
        except ValueError:
            log.debug(
                f"Could not extract lens information from {filename}, no lens set"
            )

        shutter_speed: float | None = ImageExifService.extract_exif_value(
            exif, "ExposureTime", "ShutterSpeedValue"
        )

        raw_aperture = ImageExifService.extract_exif_value(
            exif, "ApertureValue", "FNumber"
        )
        aperture: float | None = (
            get_closest_round_aperture_value(raw_aperture, APERTURES_IN_THIRD_STEPS)
            if raw_aperture
            else None
        )

        iso: float | None = ImageExifService.extract_exif_value(exif, "ISOSpeedRatings")

        focal_length: float | None = ImageExifService.extract_exif_value(
            exif, "FocalLength", "FocalLengthIn35mmFilm"
        )

        shutter_count_number: int | None = ImageExifService.extract_exif_value(
            exif, "Image Number"
        )

        aspect_ratio: float | None = None
        image_size: tuple[float, float] | None = ImageExifService.extract_exif_value(
            exif, "ImageSize"
        )
        if not image_size:  # pragma: no branch
            image_width: float | None = ImageExifService.extract_exif_value(
                exif, "XResolution"
            )
            image_height: float | None = ImageExifService.extract_exif_value(
                exif, "YResolution"
            )
            if image_height and image_width:  # pragma: no branch
                image_size = image_height, image_width
        if image_size:  # pragma: no branch
            aspect_ratio = image_size[0] / image_size[1]

        created: datetime | None = ImageExifService.extract_exif_value(
            exif, "DateTimeOriginal"
        )

        # calculate the exposure value
        illuminance: float | None = None
        if (
            aperture and iso and shutter_speed and camera.sensor_size
        ):  # pragma: no branch # noqa: E501
            ev100, adjusted_ev, sensor_correction = calculate_ev(
                aperture=aperture,
                iso=int(iso),
                shutter_speed=shutter_speed,
                sensor_type=camera.sensor_size,
            ).values()
            illuminance = ev100_to_illuminance(ev100)

        return ImageExif(
            camera=camera,
            lens=lens,
            filename=filename,
            iso=iso,
            shutter_speed=shutter_speed,
            aperture=aperture,
            focal_length=focal_length,
            exif_version=exif_version,
            exposure=illuminance,
            aspect_ratio=aspect_ratio,
            created=created,
            shutter_count=shutter_count_number,
        )

    @staticmethod
    def extract_exif_value(
        exif: dict[str, Any], key: str, secondary_key: Optional[str] = None
    ) -> Any:
        value = exif.get(key) or (exif.get(secondary_key) if secondary_key else None)
        if isinstance(value, list) and len(value) == 2:
            return float(value[0] / value[1])
        elif isinstance(value, int):
            return float(value)
        elif isinstance(value, float):
            return value
        return None  # pragma: no cover
