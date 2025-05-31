from unittest.mock import Mock, patch

from albatross.models.camera import Camera
from albatross.models.lens import Lens
from albatross.models.photographer_classification import PhotographerClassification
from albatross.models.results import Results
from albatross.photographer_classifier import PhotographerClassifier


def test_score_collector_professional_minimalist(results: Results) -> None:
    # Given results with lenses and cameras
    photographer_types = {
        "The Collector": PhotographerClassification(
            name="The Collector",
            description="Owns lots of gear, minimal usage spread",
            blurb="You love gear almost as much as photos. "
            "Every lens has a story — even if you only use two.",
            score=0,
            styling={"icon": "bi-boxes", "colour": "#6f42c1"},
            lesson="lesson",
        ),
        "The Professional": PhotographerClassification(
            name="The Professional",
            description="Owns lots of gear, uses it all",
            blurb="Someone's paying you to shoot, aren't they? "
            "You know your gear inside and out, and you use it all.",
            score=0,
            styling={"icon": "bi-cash-stack", "colour": "#003366"},
            lesson="lesson",
        ),
        "The Minimalist": PhotographerClassification(
            name="The Minimalist",
            description="Few lenses, high usage concentration",
            blurb="One camera, one lens — and you make it work like a pro.",
            score=0,
            styling={"icon": "bi-slash", "colour": "#6c757d"},
            lesson="lesson",
        ),
    }

    # When calling the _score_collector_professional_minimalist method
    PhotographerClassifier._score_collector_professional_minimalist(
        results, photographer_types
    )

    # Then it should adjust scores for 'The Collector', 'The Professional',
    # and 'The Minimalist'
    assert photographer_types["The Collector"].score > 0
    assert photographer_types["The Professional"].score > 0
    assert photographer_types["The Minimalist"].score < 0


def test_score_base_percentages(results: Results) -> None:
    # Given results with valid aperture, focal length, and ISO data
    photographer_types = {
        "The Bokeh Master": PhotographerClassification(
            name="The Bokeh Master",
            description="Shoots wide open often",
            blurb="Shallow depth is your love language. You crave dreamy"
            " backgrounds and subject isolation.",
            score=0,
            styling={"icon": "bi-fire", "colour": "#e83e8c"},
            lesson="lesson",
        ),
        "The Sniper": PhotographerClassification(
            name="The Sniper",
            description="Shoots at max zoom a lot",
            blurb="You keep your distance. Whether it’s wildlife or"
            " candids, you shoot from the shadows.",
            score=0,
            styling={"icon": "bi-crosshair", "colour": "#0d6efd"},
            lesson="lesson",
        ),
        "The Studio Shooter": PhotographerClassification(
            name="The Studio Shooter",
            description="Low ISO, fast shutter, consistent settings",
            blurb="Controlled. Consistent. Intentional. You probably own a tripod.",
            score=0,
            styling={"icon": "bi-lightbulb", "colour": "#fd7e14"},
            lesson="lesson",
        ),
    }

    # When calling the _score_base_percentages method
    PhotographerClassifier._score_base_percentages(results, photographer_types)

    # Then it should adjust scores for 'The Bokeh Master', 'The Sniper',
    # and 'The Studio Shooter'
    assert photographer_types["The Bokeh Master"].score > 0
    assert photographer_types["The Sniper"].score > 0
    assert photographer_types["The Studio Shooter"].score > 0


def test_score_stargazer_and_vampire(results: Results) -> None:
    # Given results with valid exposure and shutter speed data
    photographer_types = {
        "The Stargazer": PhotographerClassification(
            name="The Stargazer",
            description="High ISO, slow shutter speed",
            blurb="You love the night sky. You’re a master at long exposures,"
            " capturing the stars in all their glory.",
            score=0,
            styling={"icon": "bi-stars", "colour": "#212529"},
            lesson="lesson",
        ),
        "The Vampire": PhotographerClassification(
            name="The Vampire",
            description="High ISO, moderate shutter speed",
            blurb="You embrace the darkness, emerging to hunt at night"
            " or at least in places hidden away from the sun.",
            score=0,
            styling={"icon": "bi-moon-stars", "colour": "#A12529"},
            lesson="lesson",
        ),
    }

    # When calling the _score_stargazer_and_vampire method
    PhotographerClassifier._score_stargazer_and_vampire(results, photographer_types)

    # Then it should adjust scores for 'The Stargazer' and 'The Vampire'
    assert photographer_types["The Stargazer"].score == 49
    assert photographer_types["The Vampire"].score == 69


def test_score_monk_and_quickdraw(results: Results) -> None:
    # Given results with valid ISO and shutter speed data
    photographer_types = {
        "The Monk": PhotographerClassification(
            name="The Monk",
            description="Low ISO, slow shutter speed",
            blurb="You take your time. You’re patient and deliberate,"
            " waiting for the perfect moment to capture.",
            score=0,
            styling={"icon": "bi-hourglass-split", "colour": "#0dcaf0"},
            lesson="lesson",
        ),
        "The Quickdraw": PhotographerClassification(
            name="The Quickdraw",
            description="High ISO, fast shutter speed",
            blurb="Birds? Cars? Athletes? Whatever you're shooting, it moves FAST."
            " You need quick reactions to keep up.",
            score=0,
            styling={"icon": "bi-speedometer", "colour": "#198754"},
            lesson="lesson",
        ),
    }

    # When calling the _score_monk_and_quickdraw method
    PhotographerClassifier._score_monk_and_quickdraw(results, photographer_types)

    # Then it should adjust scores for 'The Monk' and 'The Quickdraw'
    assert photographer_types["The Monk"].score > 0
    assert photographer_types["The Quickdraw"].score > 0


def test_classify_with_missing_data(results: Results) -> None:
    # Given results with missing focal length, aperture, and ISO
    results.focal_length = None
    results.aperture = None
    results.iso = None
    photographer_types = {
        "The Stranger": PhotographerClassification(
            name="The Stranger",
            description="Unrecognizable camera and lens",
            blurb="You like to keep people guessing. Your camera and lens are a"
            " mystery to everyone (well, to me at least.)",
            score=0,
            styling={"icon": "bi-question-circle", "colour": "#000000"},
            lesson="lesson",
        )
    }

    # When calling the classify method
    classifications = PhotographerClassifier.classify(
        results=results,
        photographer_types=photographer_types,
        current_widest_aperture=2.8,
    )

    # Then it should classify as 'The Stranger' with a score of 100
    assert len(classifications) == 1
    assert classifications[0].name == "The Stranger"
    assert classifications[0].score == 100


@patch(
    "albatross.photographer_classifier.PhotographerClassifier._score_collector_professional_minimalist"
)
@patch(
    "albatross.photographer_classifier.PhotographerClassifier._score_base_percentages"
)
@patch(
    "albatross.photographer_classifier.PhotographerClassifier._score_stargazer_and_vampire"
)
@patch(
    "albatross.photographer_classifier.PhotographerClassifier._score_monk_and_quickdraw"
)
def test_classify_negative_scores(
    mock_score_collector_professional_minimalist: Mock,
    mock_score_base_percentages: Mock,
    mock_score_stargazer_and_vampire: Mock,
    mock_score_monk_and_quickdraw: Mock,
    results: Results,
) -> None:
    results.metrics.focal_range = None
    # Given photographer types with negative scores
    photographer_types = {
        "The Minimalist": PhotographerClassification(
            name="The Minimalist",
            description="Few lenses, high usage concentration",
            blurb="One camera, one lens — and you make it work like a pro.",
            score=-10,
            styling={"icon": "bi-slash", "colour": "#6c757d"},
            lesson="lesson",
        )
    }

    # When calling the classify method
    classifications = PhotographerClassifier.classify(
        results=results,
        photographer_types=photographer_types,
        current_widest_aperture=2.8,
    )

    # Then it should set negative scores to 0
    assert classifications[0].score == 0


@patch(
    "albatross.photographer_classifier.PhotographerClassifier._score_collector_professional_minimalist"
)
@patch(
    "albatross.photographer_classifier.PhotographerClassifier._score_base_percentages"
)
@patch(
    "albatross.photographer_classifier.PhotographerClassifier._score_stargazer_and_vampire"
)
@patch(
    "albatross.photographer_classifier.PhotographerClassifier._score_monk_and_quickdraw"
)
def test_classify_scores_above_100(
    mock_score_collector_professional_minimalist: Mock,
    mock_score_base_percentages: Mock,
    mock_score_stargazer_and_vampire: Mock,
    mock_score_monk_and_quickdraw: Mock,
    results: Results,
) -> None:
    results.metrics.focal_range = None
    # Given photographer types with scores above 100
    photographer_types = {
        "The Professional": PhotographerClassification(
            name="The Professional",
            description="Owns lots of gear, uses it all",
            blurb="Someone's paying you to shoot, aren't they? "
            "You know your gear inside and out, and you use it all.",
            score=150,
            styling={"icon": "bi-cash-stack", "colour": "#003366"},
            lesson="lesson",
        )
    }

    # When calling the classify method
    classifications = PhotographerClassifier.classify(
        results=results,
        photographer_types=photographer_types,
        current_widest_aperture=2.8,
    )

    # Then it should cap scores at 100
    assert classifications[0].score == 100


def test_brand_analysis(
    results: Results, cameras: list[Camera], lenses: list[Lens]
) -> None:
    # Given results with valid camera and lens data
    cameras[0].brand = lenses[0].brand = "Canon"
    cameras[1].brand = lenses[1].brand = "Nikon"

    results.metrics.cameras = [cameras[0], cameras[1]]
    results.metrics.lenses = [lenses[0], lenses[1]]

    # When calling the brand_analysis method
    brands = PhotographerClassifier.brand_analysis(results)

    # Then it should return a sorted list of brands with their counts
    assert brands == [
        ("canon", {"count": 2, "percentage": 50.0}),
        ("nikon", {"count": 2, "percentage": 50.0}),
    ]


def test_build_achievements_no_cameras_or_lenses(results: Results) -> None:
    # Given results with no cameras, lenses or any other data
    results.metrics.cameras = []
    results.metrics.lenses = []
    results.focal_length = None
    results.metrics.primes = []
    results.metrics.zooms = []
    results.shutter_speed = None
    results.exposure = None

    # When calling the build_achievements method
    achievements = PhotographerClassifier.build_achievements(results)

    # Then it should return a default achievement
    assert len(achievements) == 1
    assert achievements[0].name == "0 Cameras & 0 Lenses"


def test_build_achievements_distance_shooter(results: Results) -> None:
    # Given results with a high focal length mean
    results.focal_length.mean = 80

    # When calling the build_achievements method
    achievements = PhotographerClassifier.build_achievements(results)

    # Then it should include the 'Distance Shooter' achievement
    assert any(achievement.name == "Distance Shooter" for achievement in achievements)


def test_build_achievements_wide_angle_shooter(results: Results) -> None:
    # Given results with a low focal length mean
    results.focal_length.mean = 24

    # When calling the build_achievements method
    achievements = PhotographerClassifier.build_achievements(results)

    # Then it should include the 'Wide Angle Shooter' achievement
    assert any(achievement.name == "Wide Angle Shooter" for achievement in achievements)


def test_gets_prime_fan_when_only_primes(results: Results, lens: Lens) -> None:
    # Given results with only prime lenses
    results.metrics.primes = [lens]
    results.metrics.zooms = []

    # When calling the build_achievements method
    achievements = PhotographerClassifier.build_achievements(results)

    # Then it should include the 'Prime Fan' achievement
    assert any(achievement.name == "Prime Fan" for achievement in achievements)


def test_steady_hand(results: Results) -> None:
    # Given results with a low shutter speed mean
    results.shutter_speed.percentage_taken_at_lowest_value = 50

    # When calling the build_achievements method
    achievements = PhotographerClassifier.build_achievements(results)

    # Then it should include the 'Steady Hand' achievement
    assert any(achievement.name == "Steady Hand" for achievement in achievements)


def test_brand_analysis_ignores_unknown_brand(
    results: Results, cameras: list[Camera], lenses: list[Lens]
) -> None:
    # Given results with unknown brand
    cameras[0].brand = lenses[0].brand = "Unknown Brand"
    cameras[1].brand = lenses[1].brand = "Canon"

    results.metrics.cameras = [cameras[0], cameras[1]]
    results.metrics.lenses = [lenses[0], lenses[1]]

    # When calling the brand_analysis method
    brands = PhotographerClassifier.brand_analysis(results)

    # Then it should return a sorted list of brands with their counts
    assert brands == [
        ("canon", {"count": 2, "percentage": 100.0}),
    ]
