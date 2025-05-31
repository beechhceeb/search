import uuid

from albatross.models.lens import Lens
from albatross.serializers.lens import LensSerializer


def test_serialize_given_lens_object_when_serialized_then_returns_json_string() -> None:
    # Given a valid lens
    id = uuid.uuid4()
    lens = Lens(
        brand="Canon",
        model="EF 24-70mm f/2.8L II USM",
        focal_length_min=24.0,
        focal_length_max=70.0,
        largest_aperture_at_minimum_focal_length=2.8,
        largest_aperture_at_maximum_focal_length=2.8,
        prime=False,
        id=id,
    )

    # When we serialise it
    serialized_lens = LensSerializer.serialize(lens)

    # Then it looks as we expect
    expected_json = (
        '{"id": '
        f'"{id}", '
        '"brand": "Canon", '
        '"model": "EF 24-70mm f/2.8L II USM", "model_url_encoded": '
        '"EF_24_70mm_f_2_8L_II_USM", "focal_length_min": 24.0, '
        '"focal_length_max": 70.0, '
        '"largest_aperture_at_minimum_focal_length": 2.8, '
        '"largest_aperture_at_maximum_focal_length": 2.8, "prime": false, '
        '"mount": null, "crop_factor": null, "mpb_model_id": null, '
        '"price": null, "formatted_price": null, "image_link": null, '
        '"model_url_segment": null, "mpb_model": null}'
    )

    assert serialized_lens == expected_json


def test_deserialize_given_json_string_when_deserialized_then_returns_lens_object() -> (
    None
):
    # Given a JSON string
    json_data = (
        '{"brand": "Canon", "model": "EF 24-70mm f/2.8L II USM", '
        '"focal_length_min": 24.0, "focal_length_max": 70.0, '
        '"largest_aperture_at_minimum_focal_length": 2.8, '
        '"largest_aperture_at_maximum_focal_length": 2.8, '
        '"prime": false, "mount": null}'
    )

    # When the JSON string is deserialized
    lens = LensSerializer.deserialize(json_data)

    # Then the lens object should be initialized with the correct values
    assert lens.brand == "Canon"
    assert lens.model == "EF 24-70mm f/2.8L II USM"
    assert lens.focal_length_min == 24.0
    assert lens.focal_length_max == 70.0
    assert lens.largest_aperture_at_minimum_focal_length == 2.8
    assert lens.largest_aperture_at_maximum_focal_length == 2.8
    assert lens.prime is False
    assert lens.mount is None
