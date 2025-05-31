from albatross.config import MountType
from albatross.models.lens import Lens


def test_initialise_lens(lens: Lens) -> None:
    # Given the correct params
    # When I initialise the Lens object
    # Then the Lens object should be initialised with the correct values
    assert lens.brand == "Canon"
    assert lens.model == "EF 24-70mm f/2.8L II USM"
    assert lens.focal_length_min == 24.0
    assert lens.focal_length_max == 70.0
    assert lens.largest_aperture_at_minimum_focal_length == 2.8
    assert lens.largest_aperture_at_maximum_focal_length == 2.8
    assert lens.mount is MountType.EF
    assert lens.prime is False
