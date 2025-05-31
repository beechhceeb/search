from datetime import datetime
from typing import Optional

from albatross.models.camera import Camera
from albatross.models.lens import Lens


class ImageExif:
    def __init__(
        self,
        camera: Camera,
        lens: Lens,
        filename: str,
        iso: Optional[int] = None,
        shutter_speed: Optional[float] = None,
        aperture: Optional[float] = None,
        focal_length: Optional[float] = None,
        exif_version: Optional[str] = None,
        exposure: Optional[float] = None,
        aspect_ratio: Optional[float] = None,
        created: Optional[datetime] = None,
        shutter_count: Optional[float] = None,
    ):
        self.camera = camera
        self.lens = lens
        self.filename = filename
        self.iso = iso
        self.shutter_speed = shutter_speed
        self.aperture = aperture
        self.focal_length = focal_length
        self.exif_version = exif_version
        self.exposure = exposure
        self.aspect_ratio = aspect_ratio
        self.created = created
        self.shutter_count = shutter_count

    frequency: int = 0
