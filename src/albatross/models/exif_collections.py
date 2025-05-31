import math
import statistics
from bisect import bisect_left
from collections import Counter
from typing import OrderedDict

from albatross.config import COMMON_SHUTTER_SPEEDS_BELOW_1, HIGH_ISO_LIMIT
from albatross.utils import classify_illuminance


class BaseExifAttribute:
    def __init__(
        self,
        instances: list[float],
        instances_max: list[float] | None = None,
        instances_min: list[float] | None = None,
        decimal_places: int = 0,
    ) -> None:
        if not instances:
            raise ValueError("instances must be provided to build a BaseExifAttribute")

        self.total_images: int = len(instances)
        self.instances: list[float] = self.sort_instances(instances)
        self.instances_at_highest_value: list[float] = instances_max or []
        self.instances_at_lowest_value: list[float] = instances_min or []

        if instances_max:
            self.highest_value: float = max(instances_max)
            self.percentage_taken_at_highest_value = self.calculate_percentage(
                len(instances_max), self.total_images
            )
            self.mode_instances_at_highest_value: float | None = self.calculate_mode(
                instances_max
            )
        else:
            self.percentage_taken_at_highest_value = 0
            self.mode_instances_at_highest_value = None

        if instances_min:
            self.lowest_value: float = min(instances_min)
            self.percentage_taken_at_lowest_value: float = self.calculate_percentage(
                len(instances_min), self.total_images
            )
            self.mode_instances_at_lowest_value: float | None = self.calculate_mode(
                instances_min
            )
        else:
            self.percentage_taken_at_lowest_value = 0
            self.mode_instances_at_lowest_value = None

        self.mean: float = self.calculate_mean(instances, decimal_places)
        self.mode: float = self.calculate_mode(instances)

    @staticmethod
    def calculate_percentage(number: float, total: float) -> float:
        return round((number / total) * 100)

    @staticmethod
    def calculate_mean(instances: list[float], decimal_places: int) -> float:
        try:
            return round(statistics.fmean(instances), decimal_places)
        except ZeroDivisionError:  # pragma: no cover
            # Avoid div by zero errors
            return 0.0

    @staticmethod
    def calculate_mode(instances: list[float]) -> float:
        return statistics.mode(instances)

    @staticmethod
    def sort_instances(instances: list[float]) -> list[float]:
        return sorted(instances)


class FocalLength(BaseExifAttribute):
    def __init__(
        self,
        instances_max: list[float],
        instances_min: list[float],
        instances: list[float],
        instances_primes: list[float] | None = None,
        instances_zooms: list[float] | None = None,
    ) -> None:
        super().__init__(
            instances_max=instances_max,
            instances_min=instances_min,
            instances=instances,
        )
        self.instances_binned = FocalLength.bin_focal_lengths(instances)
        self.instances_primes = instances_primes
        self.instances_zooms = instances_zooms
        if instances_zooms and instances_primes:
            self.instances_binned_primes = FocalLength.bin_focal_lengths(
                instances_primes
            )
            self.instances_binned_zooms = FocalLength.bin_focal_lengths(instances_zooms)
            self.instances_discrete_primes = (
                FocalLength.calculate_focal_length_frequencies(instances_primes)
            )
            self.instances_discrete_zooms = (
                FocalLength.calculate_focal_length_frequencies(instances_zooms)
            )
            self.instances_discrete_all = (
                FocalLength.calculate_focal_length_frequencies(instances)
            )

    @staticmethod
    def bin_focal_lengths(instances: list[float]) -> dict[str, int]:
        """
        Bin the focal lengths into ranges.
        :param instances:
        :return:
        """
        bins: OrderedDict[str, int] = OrderedDict[str, int](
            [
                ("<20mm Ultra Wide", 0),
                ("20-27mm Wide", 0),
                ("28-35mm Wide", 0),
                ("36-44mm Wide Standard", 0),
                ("45-59mm Standard", 0),
                ("60-69mm Long Standard", 0),
                ("70-100mm Moderate Telephoto", 0),
                ("100-200mm Telephoto", 0),
                ("200-300mm Long Telephoto", 0),
                ("300mm+ Ultra Telephoto", 0),
            ]
        )
        for instance in instances:
            if instance < 20:
                bins["<20mm Ultra Wide"] += 1
            elif instance < 28:
                bins["20-27mm Wide"] += 1
            elif instance < 36:
                bins["28-35mm Wide"] += 1
            elif instance < 45:
                bins["36-44mm Wide Standard"] += 1
            elif instance < 60:
                bins["45-59mm Standard"] += 1
            elif instance < 70:
                bins["60-69mm Long Standard"] += 1
            elif instance < 100:
                bins["70-100mm Moderate Telephoto"] += 1
            elif instance < 200:
                bins["100-200mm Telephoto"] += 1
            elif instance < 300:
                bins["200-300mm Long Telephoto"] += 1
            else:
                bins["300mm+ Ultra Telephoto"] += 1
        return bins

    @staticmethod
    def calculate_focal_length_frequencies(
        focal_lengths: list[float],
    ) -> list[tuple[int, int]]:
        """
        Groups focal lengths and returns frequency counts as (index, count) pairs.
        """
        focal_lengths = sorted([int(fl) for fl in focal_lengths])
        start, end = focal_lengths[0], focal_lengths[-1]

        counter: Counter[float] = Counter()

        for fl in focal_lengths:
            counter[fl] += 1

        return [
            (focal_length, counter[focal_length])
            for focal_length in range(math.floor(start), math.ceil(end) + 1)
        ]


class Aperture(BaseExifAttribute):
    def __init__(
        self, instances_wide_open: list[float], instances: list[float]
    ) -> None:
        super().__init__(
            decimal_places=1,
            instances_min=instances_wide_open,
            instances=instances,
        )


class ISO(BaseExifAttribute):
    def __init__(self, instances: list[float]) -> None:
        super().__init__(
            instances_max=[i for i in instances if i > HIGH_ISO_LIMIT],
            instances=instances,
        )


class ShutterSpeed(BaseExifAttribute):
    def __init__(self, exceeds_reciprocal: list[float], instances: list[float]) -> None:
        super().__init__(
            instances_min=exceeds_reciprocal,
            instances=instances,
            decimal_places=6,
        )

        self.human_readable_mean: str = self.make_rational_shutter_speed_human_readable(
            self.mean
        )
        self.human_readable_mode: str = self.make_rational_shutter_speed_human_readable(
            self.mode
        )

    @staticmethod
    def make_rational_shutter_speed_human_readable(shutter_speed: float) -> str:
        if shutter_speed >= 1:
            return f"{shutter_speed}'"

        if shutter_speed not in COMMON_SHUTTER_SPEEDS_BELOW_1:
            # If the shutter speed is an uncommon one, round to the nearest common one
            shutter_speed = ShutterSpeed.find_closest(
                list(COMMON_SHUTTER_SPEEDS_BELOW_1.keys()), shutter_speed
            )

        human_readable: str = COMMON_SHUTTER_SPEEDS_BELOW_1[shutter_speed]
        return human_readable

    @staticmethod
    def find_closest(sorted_list: list[float], target: float) -> float:
        pos = bisect_left(sorted_list, target)

        if pos == 0:
            first_value: float = sorted_list[0]
            return first_value
        if pos == len(sorted_list):
            last_value: float = sorted_list[-1]
            return last_value

        before = sorted_list[pos - 1]
        after = sorted_list[pos]

        closest: float = (
            before if abs(before - target) <= abs(after - target) else after
        )

        return closest


class Illuminance(BaseExifAttribute):
    def __init__(self, instances: list[float], instances_in_dark: list[float]) -> None:
        super().__init__(
            instances=instances,
            instances_min=instances_in_dark,
            decimal_places=2,
        )
        self.illuminance = classify_illuminance(instances)
