from albatross.config import CameraType, MountType, SensorSize
from albatross.models.camera import Camera


def test_initialise_camera(camera: Camera) -> None:
    # Given the correct params
    # When I initialise the Camera object
    # Then the Camera object should be initialised with the correct values
    assert camera.brand == "sony"
    assert camera.model == "a7 iii"
    assert camera.crop_factor == 1
    assert camera.sensor_size == SensorSize.FULL_FRAME
    assert camera.type == CameraType.MIRRORLESS
    assert camera.mount == MountType.FE
