import pytest

from albatross.models.camera import Camera
from albatross.models.lens import Lens
from albatross.models.metrics import Metrics
from albatross.models.results import ISO, Aperture, FocalLength, Results, ShutterSpeed


def test_focal_length(metrics: Metrics) -> None:
    # Given a set of metrics
    # When we create a FocalLength object
    focal_length = FocalLength(
        instances_max=metrics.highest_possible_focal_length,
        instances_min=metrics.lowest_possible_focal_length,
        instances=metrics.instances_focal_length,
    )

    # Then we should have the correct values
    assert focal_length.mean == 83.0
    assert focal_length.mode == 35.0


def test_aperture(metrics: Metrics) -> None:
    # Given a set of metrics

    # When we create an Aperture object
    aperture = Aperture(
        instances_wide_open=metrics.instances_aperture_at_widest,
        instances=metrics.instances_aperture,
    )

    # Then we should have the correct values
    assert aperture.mean == 4.2
    assert aperture.mode == 2.8


def test_iso(metrics: Metrics) -> None:
    # When we create an ISO object
    iso = ISO(
        instances=metrics.instances_iso,
    )

    # Then we should have the correct values
    assert iso.mean == 1383.0
    assert iso.mode == 400


def test_shutter_speed(metrics: Metrics) -> None:
    # When we create a ShutterSpeed object
    shutter_speed: ShutterSpeed = ShutterSpeed(
        instances=metrics.instances_shutter_speed,
        exceeds_reciprocal=metrics.instances_exceeds_reciprocal,
    )

    # Then we should have the correct values
    assert shutter_speed.mean == 0.009361
    assert shutter_speed.mode == 0.0125
    assert shutter_speed.human_readable_mean == "1/125"
    assert shutter_speed.human_readable_mode == "1/60"


def test_exif_attribute_given_no_instances_then_raises_exception() -> None:
    # Given no instances
    # When we create a ShutterSpeed object
    # Then we should raise a ValueError
    with pytest.raises(ValueError):
        ShutterSpeed(
            instances=[],
            exceeds_reciprocal=[],
        )


def test_results_build(
    cameras: list[Camera], lenses: list[Lens], metrics: Metrics
) -> None:
    # Given a set of cameras, lenses, and metrics
    metrics.cameras = cameras
    metrics.lenses = lenses

    # When we create a Results object
    results = Results.build(metrics=metrics)

    # Then we should have the correct values
    assert results.metrics.cameras == cameras
    assert results.metrics.lenses == lenses
    assert results.aperture.mean == 4.2
    assert results.iso.mean == 1383.0
    assert results.shutter_speed.mean == 0.009361


def test_make_rational_shutter_speed_human_readable_given_shutter_speed_greater_than_one_when_converted_then_returns_human_readable_format() -> (  # noqa: E501
    None
):
    # Given a shutter speed greater than one
    shutter_speed = 2.0

    # When we convert the shutter speed to a human readable format
    result = ShutterSpeed.make_rational_shutter_speed_human_readable(shutter_speed)

    # Then we should have the correct value
    assert result == "2.0'"


def test_make_rational_shutter_speed_human_readable_given_shutter_speed_less_than_one_when_converted_then_returns_fraction() -> (  # noqa: E501
    None
):
    # Given a shutter speed less than one
    shutter_speed = 0.5

    # When we convert the shutter speed to a human readable format
    result = ShutterSpeed.make_rational_shutter_speed_human_readable(shutter_speed)

    # Then we should have the correct value
    assert result == "1/2"


@pytest.mark.parametrize(
    "sorted_list, target, expected",
    [
        ([0.5, 1.0, 2.0, 4.0, 8.0], 2.0, 2.0),
        ([0.5, 1.0, 2.0, 4.0, 8.0], 3.0, 2.0),
        ([0.5, 1.0, 2.0, 4.0, 8.0], 1.5, 1.0),
        ([0.5, 1.0, 2.0, 4.0, 8.0], 0.1, 0.5),
        ([0.5, 1.0, 2.0, 4.0, 8.0], 10.0, 8.0),
    ],
)
def test_find_closest(sorted_list: list[float], target: float, expected: float) -> None:
    # Given a sorted list and a target value

    # When we find the closest value in the list
    result = ShutterSpeed.find_closest(sorted_list, target)

    # Then we should have the correct value
    assert result == expected


def test_results_build_with_focal_length(metrics: Metrics) -> None:
    # Given metrics with focal length data
    metrics.instances_focal_length = [24.0, 50.0, 85.0]
    metrics.highest_possible_focal_length = [85.0]
    metrics.lowest_possible_focal_length = [24.0]

    # When building Results
    results = Results.build(metrics=metrics)

    # Then focal length should be set correctly
    assert results.focal_length.instances == [24.0, 50.0, 85.0]
    assert results.focal_length.instances_at_highest_value == [85.0]
    assert results.focal_length.instances_at_lowest_value == [24.0]


def test_results_build_with_aperture(metrics: Metrics) -> None:
    # Given metrics with aperture data
    metrics.instances_aperture = [2.8, 4.0, 5.6]
    metrics.instances_aperture_at_widest = [2.8]

    # When building Results
    results = Results.build(metrics=metrics)

    # Then aperture should be set correctly
    assert results.aperture.instances == [2.8, 4.0, 5.6]
    assert results.aperture.instances_at_lowest_value == [2.8]


def test_results_build_with_iso(metrics: Metrics) -> None:
    # Given metrics with ISO data
    metrics.instances_iso = [100, 200, 400, 800]

    # When building Results
    results = Results.build(metrics=metrics)

    # Then ISO should be set correctly
    assert results.iso.instances == [100, 200, 400, 800]


def test_results_build_with_shutter_speed_and_exposure(metrics: Metrics) -> None:
    # Given metrics with shutter speed and exposure data
    metrics.instances_shutter_speed = [0.5, 0.25, 0.125]
    metrics.instances_exceeds_reciprocal = [0.25]
    metrics.instances_exposures = [0.5, 1.0, 1.5]
    metrics.instances_exposure_in_dark = [0.5]

    # When building Results
    results = Results.build(metrics=metrics)

    # Then shutter speed and exposure should be set correctly
    assert results.shutter_speed.instances == [0.125, 0.25, 0.5]
    assert results.shutter_speed.instances_at_lowest_value == [0.25]
    assert results.exposure.instances == [0.5, 1.0, 1.5]
    assert results.exposure.instances_at_lowest_value == [0.5]


def test_focal_length_is_built_when_instances_exist(metrics: Metrics) -> None:
    # given metrics with focal length data
    metrics.highest_possible_focal_length = [100]
    metrics.lowest_possible_focal_length = [20]
    metrics.instances_focal_length = [100, 20]

    # when we build the results
    result = Results.build(metrics=metrics)

    # then we should have the correct values
    assert result.focal_length is not None
    assert result.focal_length.instances_at_highest_value == [100]
    assert result.focal_length.instances_at_lowest_value == [20]
    assert result.focal_length.instances == [20, 100]


def test_focal_length_is_none_when_instances_do_not_exist(metrics: Metrics) -> None:
    # given metrics without focal length data
    metrics.instances_focal_length = None

    # when we build the results
    result = Results.build(metrics=metrics)

    # then we should have None
    assert result.focal_length is None


def test_aperture_is_built_when_instances_exist(metrics: Metrics) -> None:
    # given metrics with aperture data
    metrics.instances_aperture_at_widest = [1.8]
    metrics.instances_aperture = [1.8, 2.0]

    # when we build the results
    result = Results.build(metrics=metrics)

    # then we should have the correct values
    assert result.aperture is not None
    assert result.aperture.instances_at_lowest_value == [1.8]
    assert result.aperture.instances == [1.8, 2.0]


def test_aperture_is_none_when_instances_do_not_exist(metrics: Metrics) -> None:
    # given metrics without aperture data
    metrics.instances_aperture = None

    # when we build the results
    result = Results.build(metrics=metrics)

    # then we should have None
    assert result.aperture is None


def test_iso_is_built_when_instances_exist(metrics: Metrics) -> None:
    # given metrics with ISO data
    metrics.instances_iso = [100, 200]

    # when we build the results
    result = Results.build(metrics=metrics)

    # then we should have the correct values
    assert result.iso is not None
    assert result.iso.instances == [100, 200]


def test_iso_is_none_when_instances_do_not_exist(metrics: Metrics) -> None:
    # given metrics without ISO data
    metrics.instances_iso = None

    # when we build the results
    result = Results.build(metrics=metrics)

    # then we should have None
    assert result.iso is None


def test_shutter_speed_is_built_when_instances_exist(metrics: Metrics) -> None:
    # given metrics with shutter speed data
    metrics.instances_shutter_speed = [1 / 100, 1 / 200]
    metrics.instances_exceeds_reciprocal = [1 / 100]

    # when we build the results
    result = Results.build(metrics=metrics)

    # then we should have the correct values
    assert result.shutter_speed is not None
    assert result.shutter_speed.instances == [1 / 200, 1 / 100]
    assert result.shutter_speed.instances_at_lowest_value == [1 / 100]


def test_shutter_speed_is_none_when_instances_do_not_exist(metrics: Metrics) -> None:
    # given metrics without shutter speed data
    metrics.instances_shutter_speed = None

    # when we build the results
    result = Results.build(metrics=metrics)

    # then we should have None
    assert result.shutter_speed is None


def test_exposure_is_built_when_instances_exist(metrics: Metrics) -> None:
    # given metrics with exposure data
    metrics.instances_exposures = [10, 20]
    metrics.instances_exposure_in_dark = [10]

    # when we build the results
    result = Results.build(metrics=metrics)

    # then we should have the correct values
    assert result.exposure is not None
    assert result.exposure.instances == [10, 20]
    assert result.exposure.instances_at_lowest_value == [10]


def test_exposure_is_none_when_instances_do_not_exist(metrics: Metrics) -> None:
    # given metrics without exposure data
    metrics.instances_exposures = None

    # when we build the results
    result = Results.build(metrics=metrics)

    # then we should have None
    assert result.exposure is None
