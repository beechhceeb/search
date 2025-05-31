import re
from typing import Any, Dict, Optional

from albatross.config import (
    BRANDS,
    CAMERA_TYPES_WITHOUT_MOUNT,
    COMPACT_PATTERNS,
    DB_ENABLED,
    DSLR_PATTERNS,
    MAP_BRAND_MODEL_TO_SENSOR_SIZE,
    MAP_BRAND_TYPE_MOUNT,
    MIRRORLESS_PATTERNS,
    PHONE_PATTERNS,
    SENSOR_CROP_FACTOR,
    SONY_CAMERA_INTERNAL_MODEL_TO_PUBLIC,
)
from albatross.enums.enums import CameraType, MountType, SensorSize
from albatross.models.camera import Camera
from albatross.models.search import SearchResultModel
from albatross.repository.base_repository import AlbatrossRepository
from albatross.services.search.query import Search
from albatross.utils import clean_string, get_value_from_unknown_type_value


class CameraService:
    @staticmethod
    def from_exif(
        exif_data: Dict[str, Any],
        repo: AlbatrossRepository,
        db_enabled: bool = DB_ENABLED,
    ) -> Camera:
        model: str = clean_string(
            exif_data.get("Model", "Unknown Model").strip()
        ).lower()

        sensor_size: SensorSize = SensorSize.UNKNOWN
        mount: MountType = MountType.UNKNOWN

        brand: str = exif_data.get("Make", "Unknown Brand").strip().lower()
        brand = next((b for b in BRANDS if b in brand), brand)

        if brand == "sony":
            model = CameraService.map_sony_internal_to_public_model(model).lower()

        # we should check if camera already exists,
        # so we don't create duplicates
        if db_enabled:
            if camera := repo.get_camera_by_model(model):  # pragma: no branch
                return camera

        focal_length: Optional[float] = get_value_from_unknown_type_value(
            exif_data.get("FocalLength", None)
        )

        focal_length_35mm: Optional[float] = get_value_from_unknown_type_value(
            exif_data.get("FocalLengthIn35mmFilm", None)
        )

        camera_type: CameraType = CameraService.classify_camera(brand, model)

        crop_factor: Optional[float] = None

        # Check if the camera is a known model with a specific sensor size
        try:
            for pattern, sensor in MAP_BRAND_MODEL_TO_SENSOR_SIZE[brand]:
                if re.search(pattern, model):
                    sensor_size = sensor
                    crop_factor = CameraService.get_crop_factor_by_sensor_size(
                        sensor_size
                    )
                    break
        except KeyError:
            # If the brand is not in the mapping, we can skip this step
            pass

        if not crop_factor:
            crop_factor = CameraService.get_camera_crop_factor(
                focal_length, focal_length_35mm, brand, camera_type
            )

        if crop_factor and sensor_size is SensorSize.UNKNOWN:  # pragma: no branch
            sensor_size = CameraService.calculate_sensor_size(crop_factor=crop_factor)

        if sensor_size and mount is MountType.UNKNOWN:  # pragma: no branch
            mount = CameraService.get_camera_mount(
                sensor_size=sensor_size, brand=brand, camera_type=camera_type
            )

        search_model: SearchResultModel | None = None
        if model != "unknown model":
            # We can try to get the model from the search service
            search_model = Search.search_model_via_proxy(model)  # pragma: no cover

        camera = Camera(
            brand=brand,
            model=model,
            crop_factor=crop_factor,
            sensor_size=sensor_size,
            type=camera_type,
            mount=mount,
            mpb_model_id=getattr(search_model, "model_id", None),
            price=getattr(search_model, "price", None),
            image_link=getattr(search_model, "image_link", None),
            model_url_segment=getattr(search_model, "model_url_segment", None),
            mpb_model=getattr(search_model, "model_name", None),
        )

        if db_enabled and model != "unknown model":
            repo.persist(camera)  # pragma: no cover
        return camera

    @staticmethod
    def get_camera_crop_factor(
        focal_length: Optional[float],
        focal_length_35mm: Optional[float],
        brand: str,
        camera_type: CameraType,
    ) -> Optional[float]:
        # Easiest way first
        if focal_length and focal_length_35mm:
            return focal_length_35mm / focal_length

        # Next method is to try to infer from the brand, as some brands only make one
        # sensor size
        crop_factor: float | None = CameraService.attempt_to_get_crop_factor_from_brand(
            brand, camera_type
        )
        if crop_factor:
            return crop_factor

        return None

    @staticmethod
    def attempt_to_get_crop_factor_from_brand(
        brand: str, camera_type: CameraType
    ) -> Optional[float]:
        """
        Some brands only make cameras with one sensor size. We can infer the crop factor
        from the brand if this is the case.
        """
        matching_brands = CameraService.get_matching_brands(brand)
        if len(matching_brands) != 1:
            # if we can't match the brand, or there are multiple matching brands then
            # we can't infer the crop factor
            return None

        brand_key = matching_brands[0]

        # if we've already got the camera type, we can use that to get the sensor size
        # so long as the brand only makes one sensor size in that camera type
        if camera_type != CameraType.UNKNOWN:  # pragma: no branch
            sensor_sizes = CameraService.get_possible_sensor_sizes_from_brand_and_type(
                brand_key, camera_type
            )
            if len(sensor_sizes) == 1 and sensor_sizes[0] != SensorSize.UNKNOWN:
                return CameraService.get_crop_factor_by_sensor_size(sensor_sizes[0])
            # FIXME: we could do with a way to get compact camera sensor sizes here

        return None

    @staticmethod
    def get_matching_brands(brand: str) -> list[str]:
        return [b for b in MAP_BRAND_TYPE_MOUNT.keys() if b in brand]

    @staticmethod
    def get_possible_sensor_sizes_from_brand_and_type(
        brand: str, camera_type: CameraType
    ) -> list[SensorSize]:
        try:
            return list(MAP_BRAND_TYPE_MOUNT[brand][camera_type].keys())
        except KeyError:
            return [SensorSize.UNKNOWN]

    @staticmethod
    def get_crop_factor_by_sensor_size(sensor_size: SensorSize) -> Optional[float]:
        return SENSOR_CROP_FACTOR.get(sensor_size, None)  # type: ignore

    @staticmethod
    def classify_camera(brand: str, model: str) -> CameraType:
        for keyword in DSLR_PATTERNS:
            if re.search(keyword, model):
                return CameraType.DSLR

        for keyword in MIRRORLESS_PATTERNS:
            if re.search(keyword, model):
                return CameraType.MIRRORLESS

        for keyword in COMPACT_PATTERNS:
            if re.search(keyword, model):
                return CameraType.COMPACT

        for keyword in PHONE_PATTERNS:
            if re.search(keyword, model):
                return CameraType.PHONE

        if brand == "nikon" and re.search("j[0-9]+", model):
            return CameraType.MIRRORLESS
        if brand == "pentax" and re.search("q", model):
            return CameraType.MIRRORLESS
        if brand == "fujifilm" and re.search("gfx", model):
            return CameraType.MIRRORLESS
        if brand == "gopro":
            return CameraType.ACTION
        if brand == "dji":
            return CameraType.DRONE

        return CameraType.UNKNOWN

    @staticmethod
    def map_sony_internal_to_public_model(model: str) -> str:
        return_model: str = SONY_CAMERA_INTERNAL_MODEL_TO_PUBLIC.get(model, model)
        return return_model

    @staticmethod
    def get_camera_mount(
        brand: str, sensor_size: SensorSize, camera_type: CameraType
    ) -> MountType:
        if camera_type in CAMERA_TYPES_WITHOUT_MOUNT:
            return MountType.NONE
        if (
            brand == "unknown brand"
            or camera_type == CameraType.UNKNOWN
            or sensor_size == SensorSize.UNKNOWN
        ):
            return MountType.UNKNOWN

        mount: MountType = (
            MAP_BRAND_TYPE_MOUNT.get(brand, {})
            .get(camera_type, {})
            .get(sensor_size, MountType.UNKNOWN)
        )
        return mount

    @staticmethod
    def calculate_sensor_size(crop_factor: float) -> SensorSize:
        # swap around key and value on the crop factor dict to make it
        # easier to search for the crop factor
        crop_factor_sensor = {val: key for key, val in SENSOR_CROP_FACTOR.items()}
        return crop_factor_sensor.get(
            crop_factor,
            SensorSize.MEDIUM_FORMAT if crop_factor > 1 else SensorSize.UNKNOWN,
        )
