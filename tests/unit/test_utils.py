import json
from typing import Any
import math

import pytest

from albatross.enums.enums import SensorSize

from albatross.utils import (
    calculate_ev,
    focal_length_to_field_of_view,
    get_closest_round_aperture_value,
    get_value_from_unknown_type_value,
    get_variation,
    make_list_serializable,
    ev100_to_illuminance,
    classify_illuminance,
    clean_string,
    make_dictionary_serializable,
)


def test_get_value_from_unknown_type_value() -> None:
    # Given a list representing a rational number
    value = [10, 2]

    # When calling get_value_from_unknown_type_value
    result = get_value_from_unknown_type_value(value)

    # Then it should return the correct float value
    assert result == 5.0

    # Given a list with a single integer
    value = [10]

    # When calling get_value_from_unknown_type_value
    result = get_value_from_unknown_type_value(value)

    # Then it should return the float representation of the integer
    assert result == 10.0


def test_calculate_ev() -> None:
    # Given valid aperture, shutter speed, and ISO values
    aperture = 2.8
    shutter_speed = 1 / 60
    iso = 100

    # When calling calculate_ev
    result = calculate_ev(aperture, shutter_speed, iso)

    # Then it should return the correct EV100 and adjusted EV
    assert result["ev100"] == 8.88
    assert result["adjusted_ev"] == 8.88
    assert result["sensor_correction"] == 0


def test_get_closest_round_aperture_value() -> None:
    # Given an aperture value and a list of standard apertures
    aperture = 2.7
    aperture_list = [1.4, 2.0, 2.8, 4.0, 5.6]

    # When calling get_closest_round_aperture_value
    result = get_closest_round_aperture_value(aperture, aperture_list)

    # Then it should return the closest aperture value
    assert result == 2.8


def test_focal_length_to_field_of_view() -> None:
    # Given a focal length and sensor width
    focal_length_mm = 50.0
    sensor_width_mm = 36.0

    # When calling focal_length_to_field_of_view
    result = focal_length_to_field_of_view(focal_length_mm, sensor_width_mm)

    # Then it should return the correct field of view in degrees
    assert result == pytest.approx(39.5978, 0.0001)


def test_get_variation() -> None:
    # Given a list of numbers
    input_stats = [10, 20, 30, 40, 50]

    # When calling get_variation
    result = get_variation(input_stats)

    # Then it should return the standard deviation of the numbers
    assert result == pytest.approx(15.8114, 0.0001)


def test_get_variation_empty_list() -> None:
    # Given an empty list
    input_stats: list[float] = []

    # When calling get_variation
    result = get_variation(input_stats)

    # Then it should return 0 and log a warning
    assert result == 0


def test_get_variation_single_element() -> None:
    # Given a list with a single element
    input_stats = [10]

    # When calling get_variation
    result = get_variation(input_stats)

    # Then it should return 0 and log a warning
    assert result == 0


def test_get_value_from_unknown_type_value_avoids_div_by_zero() -> None:
    # Given a list representing a rational number with division by zero
    value = [10, 0]

    # When calling get_value_from_unknown_type_value
    result = get_value_from_unknown_type_value(value)

    # Then it should return the float representation of the numerator
    assert result == 10.0


def test_get_value_from_unknown_type_value_with_more_than_two_values() -> None:
    # Given a list with more than two values
    value = [10, 2, 3]

    # When calling get_value_from_unknown_type_value
    result = get_value_from_unknown_type_value(value)

    # Then it should return the original value and log a warning
    assert result == value


def test_get_value_from_unknown_type_value_nested_list() -> None:
    # Given a nested list
    value = [[10, 2], [5, 0]]

    # When calling get_value_from_unknown_type_value
    result = get_value_from_unknown_type_value(value)

    # Then it should return a list of processed values
    assert result == [5.0, 5.0]


def test_make_list_serializable() -> None:
    # Given a list of data with different types that are not directly seralizable
    input: list[Any] = [
        {"key": "value", "nested": [1, 2, 3]},
        range(5),
        [1, 2, 3],
        "string",
        42,
        None,
    ]

    # When we call make_list_serializable
    return_list = make_list_serializable(input)

    # Then serializing the list should not raise an error
    assert return_list == [
        {"key": "value", "nested": [1, 2, 3]},
        [0, 1, 2, 3, 4],
        [1, 2, 3],
        "string",
        42,
        None,
    ]

    json.dumps(return_list)


def test_ev100_to_illuminance() -> None:
    # Given an EV100 value
    ev_value = 10.0

    # When we convert it to illuminance
    result = ev100_to_illuminance(ev_value)

    # Then it should return the expected illuminance in lux
    expected_luminance = (2**ev_value) * 0.3
    expected = math.pi * expected_luminance
    assert result == pytest.approx(expected)


def test_classify_illuminance() -> None:
    # Given a list of lux values
    lux_values = [
        0.0005,
        0.005,
        0.05,
        5,
        50,
        500,
        5000,
        50000,
        150000,
    ]
    # When we call classify_illuminance
    result = classify_illuminance(lux_values)
    # Then the result should be a dictionary with classifications
    for classification in result.values():
        assert classification["instances"] == 1
        assert classification["percentage"] == pytest.approx(11.11, 0.01)


def test_clean_string() -> None:
    # Given a string with unwanted characters
    input_string = "he\x00llo\nworld"
    # When we call clean_string
    result = clean_string(input_string)
    # Then the result should be cleaned of non-printable characters
    assert result == "helloworld"


def test_make_dictionary_serializable() -> None:
    # Given an input dictionary with various types including Enums and ranges
    input_dict: dict[str, Any] = {
        "enum": SensorSize.FULL_FRAME,
        "range": range(3),
        "nested_list": [range(2), {"inner_enum": SensorSize.APSC}],
        "nested_dict": {"enum": SensorSize.MEDIUM_FORMAT},
    }

    # When we call make_dictionary_serializable
    output = make_dictionary_serializable(input_dict)

    # Then the output should be serializable
    json.dumps(output)
