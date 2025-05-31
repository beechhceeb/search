import copy
import logging
import math
import statistics
import traceback
from enum import Enum
from typing import Any

from albatross.config import INITIAL_LUMINANCE_VALUES, SENSOR_EV_CORRECTIONS
from albatross.enums.enums import SensorSize

log = logging.getLogger(__name__)


def get_value_from_unknown_type_value(value: Any) -> Any:
    """
    Get the value from an unknown type value
    """
    if type(value) is list:
        if type(value[0]) is int:
            if len(value) == 1:
                return float(value[0])
            elif len(value) == 2:
                if value[1] == 0:  # Avoid division by zero
                    return float(value[0])
                return float(value[0] / value[1])
            else:
                log.warning("More than two values in rational number")
                log.debug(traceback.format_exc())
        elif type(value[0]) is list:  # pragma: no branch
            return [get_value_from_unknown_type_value(v) for v in value]
    return value


def calculate_ev(
    aperture: float,
    shutter_speed: float,
    iso: int,
    sensor_type: SensorSize = SensorSize.FULL_FRAME,
) -> dict[str, float]:
    """
    Calculates EV100 and optionally sensor-adjusted EV.
    """
    ev100 = math.log2((aperture**2) / shutter_speed) - math.log2(iso / 100)

    # Sensor correction
    correction = SENSOR_EV_CORRECTIONS.get(sensor_type, 0)
    adjusted_ev = ev100 + correction

    return {
        "ev100": round(ev100, 2),
        "adjusted_ev": round(adjusted_ev, 2),
        "sensor_correction": correction,
    }


def ev100_to_illuminance(ev100: float) -> float:
    """
    Converts EV100 to approximate scene illuminance in lux.
    Assumes an 18% gray card reflectance (standard calibration).
    """
    luminance = (2**ev100) * 0.3  # cd/m²
    illuminance = math.pi * luminance  # lux
    return illuminance


def classify_illuminance(lux_values: list[float]) -> dict[str, dict[str, float]]:
    luminance_values: dict[str, dict[str, float]] = copy.deepcopy(
        INITIAL_LUMINANCE_VALUES
    )
    classification_boundaries: list[tuple[str, float]] = [
        (classification, specs["boundary"])
        for (classification, specs) in INITIAL_LUMINANCE_VALUES.items()
    ]
    for lux in lux_values:
        for classification, boundary in classification_boundaries:  # pragma: no branch
            if lux < boundary:
                luminance_values[classification]["instances"] += 1
                break
    # once we've looped through, we can calculate the percentages
    for classification, specs in INITIAL_LUMINANCE_VALUES.items():
        luminance_values[classification]["percentage"] = round(
            (luminance_values[classification]["instances"] / len(lux_values)) * 100, 2
        )

    return luminance_values


def get_closest_round_aperture_value(
    aperture: float, aperture_list: list[float]
) -> float:
    closest_aperture: float = min(aperture_list, key=lambda x: abs(x - aperture))
    return closest_aperture


def focal_length_to_field_of_view(
    focal_length_mm: float, sensor_width_mm: float = 36.0
) -> float:
    # Returns angle of view in degrees for a given focal length
    # (default full-frame width)
    # we use this to create linear focal length scaling
    return 2 * math.degrees(math.atan(sensor_width_mm / (2 * focal_length_mm)))


def get_variation(input_stats: list[float | int]) -> float | int:
    # Calculate the variation of a list of numbers
    # Variation is defined as the standard deviation of the numbers
    if not input_stats:
        log.warning("Input list is empty. Cannot calculate variation. returning 0")
        return 0
    elif len(input_stats) == 1:
        log.warning(
            "Input list has less than 2 elements. "
            "Cannot calculate variation. returning 0"
        )
        return 0
    else:
        return statistics.stdev(input_stats)


def clean_string(input_string: str) -> str:
    """
    Cleans a string by removing all non-printable characters.
    """
    return "".join(char for char in input_string if char.isprintable())


def make_dictionary_serializable(input_dict: dict[str, Any]) -> dict[str, Any]:
    cleaned_dict: dict[str, Any] = {}
    for key, value in input_dict.items():
        if isinstance(value, Enum):
            cleaned_dict[key] = value.value
        if isinstance(value, range):
            cleaned_dict[key] = list(value)
        elif isinstance(value, list):
            cleaned_dict[key] = make_list_serializable(value)
        elif isinstance(value, dict):
            cleaned_dict[key] = make_dictionary_serializable(value)
        else:
            cleaned_dict[key] = value
    return cleaned_dict


def make_list_serializable(input_list: list[Any]) -> list[Any]:
    cleaned_list: list[Any] = []
    for item in input_list:
        if isinstance(item, range):
            cleaned_list.append(list(item))
        elif isinstance(item, dict):
            cleaned_list.append(make_dictionary_serializable(item))
        elif isinstance(item, list):
            cleaned_list.append(make_list_serializable(item))
        else:
            cleaned_list.append(item)
    return cleaned_list
