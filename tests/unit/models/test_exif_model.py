from albatross.models.camera import Camera
from albatross.models.image_exif import ImageExif
from albatross.models.lens import Lens


def test_init_exif(camera: Camera, lens: Lens) -> None:
    # Given
    filename = "test.jpg"
    iso = 100
    shutter_speed = 1 / 60
    aperture = 2.8
    focal_length = 50

    # When
    exif_data = ImageExif(
        camera, lens, filename, iso, shutter_speed, aperture, focal_length
    )

    # Then
    assert exif_data.camera == camera
    assert exif_data.lens == lens
    assert exif_data.filename == filename
    assert exif_data.iso == iso
    assert exif_data.shutter_speed == shutter_speed
    assert exif_data.aperture == aperture
    assert exif_data.focal_length == focal_length
