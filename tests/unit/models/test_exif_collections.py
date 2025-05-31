from collections import OrderedDict

import pytest

from albatross.models.exif_collections import (
    ISO,
    Aperture,
    BaseExifAttribute,
    FocalLength,
    Illuminance,
    ShutterSpeed,
)


def test_base_exif_attribute_initialization() -> None:
    # Given: Valid instances
    instances = [1.0, 2.0, 3.0]

    # When: Initializing BaseExifAttribute
    attribute = BaseExifAttribute(instances=instances)

    # Then: Verify attributes are set correctly
    assert attribute.total_images == 3
    assert attribute.instances == [1.0, 2.0, 3.0]
    assert attribute.mean == 2.0
    assert attribute.mode == 1.0


def test_base_exif_attribute_invalid_initialization() -> None:
    # Given: Empty instances
    instances: list[float] = []

    # When/Then: Initializing BaseExifAttribute should raise ValueError
    with pytest.raises(
        ValueError, match="instances must be provided to build a BaseExifAttribute"
    ):
        BaseExifAttribute(instances=instances)


def test_shutter_speed_human_readable() -> None:
    # Given: Valid shutter speed instances
    instances = [0.5, 0.25, 0.25, 0.5, 3.5]
    exceeds_reciprocal = [0.25]

    # When: Initializing ShutterSpeed
    shutter_speed = ShutterSpeed(
        instances=instances, exceeds_reciprocal=exceeds_reciprocal
    )

    # Then: Verify human-readable values
    assert shutter_speed.human_readable_mean == "1.0'"
    assert shutter_speed.human_readable_mode == "1/2"


def test_aperture_initialization() -> None:
    # Given: Valid aperture instances
    instances = [2.8, 4.0, 5.6]
    instances_wide_open = [2.8]

    # When: Initializing Aperture
    aperture = Aperture(instances=instances, instances_wide_open=instances_wide_open)

    # Then: Verify attributes
    assert aperture.mean == 4.1
    assert aperture.mode == 2.8


def test_iso_initialization() -> None:
    # Given: Valid ISO instances
    instances = [100, 200, 3200, 6400, 7200]

    # When: Initializing ISO
    iso = ISO(instances=instances)

    # Then: Verify high ISO values
    assert iso.instances_at_highest_value == [7200]
    assert iso.percentage_taken_at_highest_value == 20


def test_exposure_initialization() -> None:
    # Given: Valid exposure instances
    instances = [0.5, 1.0, 1.5]
    instances_in_dark = [0.5]

    # When: Initializing Exposure
    exposure = Illuminance(instances=instances, instances_in_dark=instances_in_dark)

    # Then: Verify attributes
    assert exposure.mean == 1.0
    assert exposure.percentage_taken_at_lowest_value == 33


def test_calculate_mean() -> None:
    # Given: A list of instances and decimal places
    instances = [1.0, 2.0, 3.0]
    decimal_places = 2

    # When: Calculating the mean
    mean = BaseExifAttribute.calculate_mean(instances, decimal_places)

    # Then: Verify the mean is calculated correctly
    assert mean == 2.0


def test_calculate_mean_zero_division() -> None:
    # Given: a list of instances that sum to zero
    instances = [0.0]
    decimal_places = 2

    # When: Calculating the mean
    mean = BaseExifAttribute.calculate_mean(instances, decimal_places)

    # Then: Verify the mean is 0.0 to handle ZeroDivisionError
    assert mean == 0.0


def test_bin_focal_lengths() -> None:
    # Given: A list of focal lengths
    instances = [18.0, 24.0, 35.0, 42.0, 50.0, 65.0, 85.0, 135.0, 200.0, 600.0]

    # When: Binning focal lengths
    binned_focal_lengths = FocalLength.bin_focal_lengths(instances)

    # Then: Verify the bins are correct
    assert binned_focal_lengths == OrderedDict(
        {
            "<20mm Ultra Wide": 1,
            "20-27mm Wide": 1,
            "28-35mm Wide": 1,
            "36-44mm Wide Standard": 1,
            "45-59mm Standard": 1,
            "60-69mm Long Standard": 1,
            "70-100mm Moderate Telephoto": 1,
            "100-200mm Telephoto": 1,
            "200-300mm Long Telephoto": 1,
            "300mm+ Ultra Telephoto": 1,
        }
    )
