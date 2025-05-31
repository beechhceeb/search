import pytest

from albatross.config import CameraType, MountType, SensorSize
from albatross.models.camera import Camera


@pytest.fixture
def camera() -> Camera:
    camera: Camera = Camera(
        brand="sony",
        model="a7 iii",
        crop_factor=1,
        sensor_size=SensorSize.FULL_FRAME,
        type=CameraType.MIRRORLESS,
        mount=MountType.FE,
        ibis=True,
    )
    return camera


@pytest.fixture
def crop_sensor_camera() -> Camera:
    camera: Camera = Camera(
        brand="Canon",
        model="EOS 80D",
        crop_factor=1.6,
        sensor_size=SensorSize.CANON_APSC,
        type=CameraType.DSLR,
        mount=MountType.EF,
    )
    return camera


@pytest.fixture
def cameras() -> list[Camera]:
    cameras: list[Camera] = [
        Camera(
            brand="Sony",
            model="A7 III",
            crop_factor=1,
            sensor_size=SensorSize.FULL_FRAME,
            type=CameraType.MIRRORLESS,
            mount=MountType.E,
        ),
        Camera(
            brand="Canon",
            model="EOS R5",
            crop_factor=1,
            sensor_size=SensorSize.FULL_FRAME,
            type=CameraType.MIRRORLESS,
            mount=MountType.RF,
        ),
        Camera(
            brand="Nikon",
            model="Z6",
            crop_factor=1,
            sensor_size=SensorSize.FULL_FRAME,
            type=CameraType.MIRRORLESS,
            mount=MountType.Z,
        ),
    ]
    return cameras
