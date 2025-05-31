import uuid
from unittest.mock import Mock

import pytest

from albatross.models.camera import Camera
from albatross.models.lens import Lens
from albatross.models.photographer_classification import (
    Achievement,
    PhotographerClassification,
)
from albatross.models.recommendations import Recommendations
from albatross.models.results import Results
from albatross.photographer_classifier import PhotographerClassifier
from albatross.models.recommendations import Recommendations
from albatross.serializers.recommendations import RecommendationsSerializer
from albatross.services.recommendation import RecommendationService


@pytest.fixture
def recommendations_without_llm_response(
    results: Results, camera: Camera, lenses: list[Lens]
) -> Recommendations:
    return Recommendations(
        primary_camera=camera,
        primary_mount_lenses=lenses,
        current_widest_aperture=2.8,
        favourite_focal_length=50,
        recommended_aperture=2.8,
        recommended_focal_length=50,
        recommendation_statement="Use a wider aperture for portraits.",
        results=results,
    )


@pytest.fixture
def recommendations_with_llm_response(
    recommendations_without_llm_response: Recommendations,
) -> Recommendations:
    recommendations_without_llm_response.id = uuid.uuid4()
    recommendations_without_llm_response.llm_lens_recommendation = [
        {
            "Budget": "low",
            "Lens": "Panasonic Lumix G 25mm f/1.7 ASPH",
            "Purpose/Genres": "Portrait, Street",
            "Reasoning": "A fast prime lens that will perform well in low light and create a shallow depth of field, especially useful given the high ISO images.",  # noqa: E501
            "product_link": "",
        },
        {
            "Budget": "mid",
            "Lens": "Olympus M.Zuiko Digital ED 12-40mm f/2.8 PRO",
            "Purpose/Genres": "Versatile, General Use",
            "Reasoning": "A weather-sealed, sharp zoom lens suitable for a wide range of subjects. F/2.8 is better than the standard kit lens.",  # noqa: E501
            "product_link": "https://www.mpb.com/product/olympus-m-zuiko-digital-ed-12-40mm-f-2-8-pro",
        },
        {
            "Budget": "unlimited",
            "Lens": "Olympus M.Zuiko Digital ED 150-400mm f/4.5 TC1.25x IS PRO",
            "Purpose/Genres": "Wildlife, Sports",
            "Reasoning": "A super-telephoto zoom lens with a built-in teleconverter, image stabilization, and weather sealing. This would be useful if you want to bring your 'zoom' percentage up. This is outside of your budget, so I would also recommend the Olympus M.Zuiko Digital ED 300mm f/4 IS PRO as an alternative.",  # noqa: E501
            "product_link": "https://www.mpb.com/product/olympus-m-zuiko-digital-ed-150-400mm-f-4-5-tc1-25x-is-pro",
        },
    ]
    recommendations_without_llm_response.llm_camera_recommendation = [
        {
            "Basic Specs": "20.4MP, Weather Sealed",
            "Budget": "low",
            "Camera": "Olympus OM-D E-M1 Mark II",
            "Reasoning": "A robust and capable camera with excellent image stabilization and weather sealing, an upgrade to an older camera.",  # noqa: E501
            "product_link": "https://www.mpb.com/product/olympus-om-d-e-m1-mark-ii",
        },
        {
            "Basic Specs": "20.4MP, Advanced Features",
            "Budget": "mid",
            "Camera": "Olympus OM-D E-M1 Mark III",
            "Reasoning": "Builds upon the Mark II with enhanced autofocus, image stabilization, and computational photography features, suited for demanding shooting situations.",  # noqa: E501
            "product_link": "https://www.mpb.com/product/olympus-om-d-e-m1-mark-iii",
        },
        {
            "Basic Specs": "20.4MP, Flagship Model",
            "Budget": "unlimited",
            "Camera": "OM System OM-1",
            "Reasoning": "The flagship model from OM System, successor to Olympus, with cutting-edge autofocus, image stabilization, and computational photography capabilities.",  # noqa: E501
            "product_link": "https://www.mpb.com/product/om-system-om-1",
        },
    ]

    recommendations_without_llm_response.photographer_classifier = Mock(
        spec=PhotographerClassifier,
        top_classification=PhotographerClassification(
            name="The Bokeh Master",
            description="Shoots wide open often",
            blurb="Shallow depth is your love language. You crave dreamy backgrounds"
            " and subject isolation.",
            score=0,
            styling={
                "icon": "bi-fire",
                "colour_1": "#e83e8c",
                "colour_2": "#8c3ee8",
                "colour_3": "#3ee89c",
            },
            lesson="""Your love of shallow depth of field gives your images a dreamy, artistic feel; but relying on it too often can become a creative comfort zone. Shooting wide open isolates your subject beautifully, yet it can also limit storytelling through background context and compositional variety.
            for the next week, shoot exclusively at apertures of f/5.6 or narrower. It might feel restrictive at first, but you'll begin to see the environment in new ways; discovering new layers, framing opportunities, and story elements in your scenes.""",  # noqa: E501
            video_title="This video encourages photographers to challenge traditional composition rules, including the overuse of shallow depth of field, promoting a broader storytelling perspective.",  # noqa: E501
            video_url="https://www.youtube.com/embed/OIpe3KgeqOo?si=qUCEs7-qQhVrRJmI",
        ),
        achievements=[Mock(spec=Achievement)],
        scores={},
    )
    return recommendations_without_llm_response


@pytest.fixture
def recommendations_json_abridged(
    recommendations_without_llm_response: Recommendations,
) -> str:
    abridged: str = RecommendationsSerializer.to_json_abridged(
        recommendations_without_llm_response
    )
    return abridged


@pytest.fixture
def recommendations_short_analysis_json(
    recommendations_without_llm_response: Recommendations,
) -> str:
    analysis: str = RecommendationService.build_minimized_analysis(
        recommendations_without_llm_response.primary_camera,
        recommendations_without_llm_response.results,
    )
    return analysis
