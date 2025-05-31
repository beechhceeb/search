import json
from typing import Any

from albatross.enums.enums import CameraType, MountType, SensorSize
from albatross.models.camera import Camera


class CameraSerializer:
    @staticmethod
    def serialize(camera: Camera) -> str:
        """
        Serializes the Camera object to JSON.
        """
        return json.dumps(
            {
                "brand": camera.brand,
                "model": camera.model,
                "crop_factor": camera.crop_factor,
                "sensor_size": camera.sensor_size.name,
                "type": camera.type.name,
                "mount": camera.mount.name,
            }
        )

    @staticmethod
    def from_dict(camera_dict: dict[str, Any]) -> Camera:
        """
        Deserialize a camera from a dictionary.
        """
        brand = camera_dict.get("brand", "Unknown Brand").strip().lower()
        model = camera_dict.get("model", "Unknown Model").strip().lower()
        crop_factor = camera_dict.get("crop_factor")
        sensor_size = (
            SensorSize(camera_dict["sensor_size"])
            if camera_dict["sensor_size"]
            else SensorSize.UNKNOWN
        )
        camera_type = (
            CameraType(camera_dict["type"])
            if camera_dict["type"]
            else CameraType.UNKNOWN
        )
        mount = (
            MountType(camera_dict["mount"])
            if camera_dict["mount"]
            else MountType.UNKNOWN
        )

        return Camera(
            brand=brand,
            model=model,
            crop_factor=crop_factor,
            sensor_size=sensor_size,
            type=camera_type,
            mount=mount,
        )

    @staticmethod
    def to_dict(camera: Camera) -> dict[str, Any]:
        return {
            "brand": getattr(camera, "brand", None),
            "model": getattr(camera, "model", None),
            "crop_factor": getattr(camera, "crop_factor", None),
            "sensor_size": getattr(camera, "sensor_size", None),
            "type": getattr(camera, "type", None),
            "mount": getattr(camera, "mount", None),
            "mpb_model_id": getattr(camera, "mpb_model_id", None),
            "price": getattr(camera, "price", None),
            "image_link": getattr(camera, "image_link", None),
            "model_url_segment": getattr(camera, "model_url_segment", None),
        }
