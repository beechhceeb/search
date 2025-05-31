import logging
from typing import Any

from albatross.config import EXIF_WHITELIST
from albatross.models.image_exif import ImageExif
from albatross.models.metrics import Metrics
from albatross.models.recommendations import Recommendations
from albatross.models.results import Results
from albatross.repository.base_repository import AlbatrossRepository
from albatross.services.image_exif import ImageExifService
from albatross.services.metrics import MetricsService
from albatross.services.recommendation import RecommendationService

log = logging.getLogger(__name__)


def analyse_extracted_data(
    exif_data: list[ImageExif], repo: AlbatrossRepository, call_llm: bool = True
) -> Recommendations:
    """
    Takes list of exif data and builds useful map
    :param exif_data:
    :return:
    """

    # Build a list of quantifiables used in the results
    metrics: Metrics = MetricsService.from_exif(exif_data)

    # Assemble results into object to pass to jinja template
    results: Results = Results.build(metrics)

    # Build a list of arguments to present to the user as recommendations
    recommendations: Recommendations = RecommendationService.build(
        results, repo=repo, call_llm=call_llm
    )

    return recommendations


def handle_uploaded_exif(
    raw_exif_json: dict[str, Any], repo: AlbatrossRepository, call_llm: bool = True
) -> Recommendations:
    """
    Handles uploaded exif data
    """
    exifs: list[ImageExif] = [
        ImageExifService.from_exif(
            {field: exif.get(field) for field in EXIF_WHITELIST if field in exif},
            filename="",
            repo=repo,
        )
        for exif in raw_exif_json.get("exifData", {})
    ]
    recommendations: Recommendations = analyse_extracted_data(
        exifs, call_llm=call_llm, repo=repo
    )
    return recommendations
