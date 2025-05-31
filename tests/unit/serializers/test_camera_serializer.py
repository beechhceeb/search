from albatross.config import MountType
from albatross.enums.enums import CameraType, SensorSize
from albatross.models.camera import Camera
from albatross.serializers.camera import CameraSerializer


def test_serialize_given_camera_object_when_serialized_then_returns_json_string() -> (
    None
):
    # Given
    camera = Camera(
        brand="Canon",
        model="EOS 5D",
        crop_factor=1,
        sensor_size=SensorSize.FULL_FRAME,
        type=CameraType.DSLR,
        mount=MountType.EF,
    )

    # When
    serialized_camera = CameraSerializer.serialize(camera)

    # Then
    expected_json = (
        '{"brand": "Canon", "model": "EOS 5D", "crop_factor": 1, '
        '"sensor_size": "FULL_FRAME", "type": "DSLR", "mount": "EF"}'
    )
    assert serialized_camera == expected_json


def test_to_dict_given_camera_object_when_called_then_returns_correct_dict(
    camera: Camera,
) -> None:
    # Given: A Camera object
    camera_dict = CameraSerializer.to_dict(camera)

    # Then: The dictionary should match the camera attributes
    assert camera_dict["brand"] == camera.brand
    assert camera_dict["model"] == camera.model
    assert camera_dict["crop_factor"] == camera.crop_factor


def test_serialize_given_camera_object_when_called_then_returns_correct_json(
    camera: Camera,
) -> None:
    # Given: A Camera object
    json_result = CameraSerializer.serialize(camera)

    # Then: The JSON string should match the camera attributes
    assert '"brand":' in json_result
    assert '"model":' in json_result
