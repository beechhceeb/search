import os
from typing import Any
from uuid import UUID

from albatross.repository.base_repository import repository
from flask import Flask, Response, jsonify, render_template, request

from albatross.config import (
    CACHE_FILE,
    EXIF_WHITELIST,  # noqa: E402
    FLASK_SECRET_KEY,
    PHOTOGRAPHER_CLASSIFICATIONS,
    TABLE_HEADERS,
    log,
    ASYNC_MODE,
)
from albatross.controller import handle_uploaded_exif  # noqa: E402
from albatross.enums.enums import ProductType
from albatross.models.recommendations import Recommendations  # noqa: E402
from albatross.services.recommendation import RecommendationService  # noqa: E402


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = FLASK_SECRET_KEY

    @app.route("/healthz")
    def health_check() -> Response:
        log.info("Health check endpoint called")
        return Response(status=200)

    @app.route("/exif-whitelist", methods=["GET"])
    def get_exif_whitelist() -> Response:
        log.info("exif whitelist requested")
        return jsonify(EXIF_WHITELIST)

    @app.route("/clear-lm-cache", methods=["DELETE"])
    def clear_lm_cache() -> Response:  # pragma: no cover
        log.info("Clear lm cache endpoint called")
        # remove the cache file if it exists
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)
            log.info("LM Cache file removed")
        else:
            log.warning("LM Cache file does not exist")
        return Response(status=200)

    @app.route("/", methods=["GET"])
    def index() -> str:
        log.info("index route called")
        header_fragment: str = render_template("fragments/header.html")
        footer_fragment: str = render_template("fragments/footer.html")
        landing_page: str = render_template(
            "index.html", header=header_fragment, footer=footer_fragment
        )
        return landing_page

    @app.route("/<recommendations_id>", methods=["GET"])
    def recall(recommendations_id: str) -> str:
        log.info(f"recall route called with id {recommendations_id}")
        page: str = render_template("index.html", recommendations_id=recommendations_id)
        log.info("recall page successfully returned")
        return page

    @app.route("/process-exif", methods=["POST"])
    def process_exif_data() -> Response:
        log.info("process-exif route called")
        data: dict[str, Any] = request.get_json()
        log.debug(f"process-exif called with data: {data}")
        call_llm = not ASYNC_MODE  # If ASYNC_MODE is enabled, we don't call the LLM
        recommendations: Recommendations = handle_uploaded_exif(
            data, call_llm=call_llm, repo=repository
        )
        classification_badge_fragment = render_template(
            "fragments/classification.html",
            photographer_classification=recommendations.photographer_classifier.top_classification,
            scores=recommendations.photographer_classifier.scores,
            achievements=recommendations.photographer_classifier.achievements,
        )
        total_kit_value = (
            sum(
                [
                    lens.price
                    for lens in recommendations.results.metrics.lenses
                    if lens.price
                ]
                + [
                    camera.price
                    for camera in recommendations.results.metrics.cameras
                    if camera.price
                ]
            )
            / 100
        )
        formatted_kit_value = f"£{total_kit_value:,.0f}" if total_kit_value else ""
        kit_fragment: str = (
            render_template(
                "fragments/your-current-gear.html",
                kit=recommendations.results.metrics,
                total_kit_value=formatted_kit_value,
            )
            if recommendations.results.metrics.lenses
            or recommendations.results.metrics.cameras
            else ""
        )
        analysis_fragment: str = (
            render_template(
                "fragments/how-you-shoot.html", recommendations=recommendations
            )
            if recommendations.results.aperture
            or recommendations.results.iso
            or recommendations.results.shutter_speed
            or recommendations.results.exposure
            else ""
        )
        if (
            recommendations.llm_camera_recommendation
            and recommendations.llm_lens_recommendation
        ):
            camera_recommendations_table = render_template(
                "fragments/recommendations-table.html",
                rows=recommendations.llm_camera_recommendation,
                display_headers=TABLE_HEADERS[ProductType.CAMERA]["display"],
            )
            lens_recommendations_table = render_template(
                "fragments/recommendations-table.html",
                rows=recommendations.llm_lens_recommendation,
                display_headers=TABLE_HEADERS[ProductType.LENS]["display"],
            )
            recommendations_fragment = render_template(
                "fragments/what-could-make-your-kit-better.html",
                recommendations_input=render_template(
                    "fragments/recommendations-json-tree.html",
                    data=recommendations.recommendation_statement,
                ),
                recommendations_lens_recommendation=lens_recommendations_table,
                recommendations_camera_recommendation=camera_recommendations_table,
            )
        else:
            recommendations_fragment = '<div id="recommendations-fragment"></div>'

        lesson_lines = (
            recommendations.photographer_classifier.top_classification.lesson.split(
                "\n"
            )
        )
        challenge_fragment: str = ""
        if lesson_lines:  # pragma: no branch
            challenge_fragment = render_template(
                "fragments/challenge.html",
                lesson_p1=lesson_lines[0],
                lesson_p2=lesson_lines[1] if len(lesson_lines) > 1 else "",
            )

        improve_fragment: str = render_template(
            "fragments/how-can-you-improve.html",
            video_url=recommendations.photographer_classifier.top_classification.video_url,
            video_title=recommendations.photographer_classifier.top_classification.video_title,
            challenge=challenge_fragment,
        )

        thanks_fragment: str = render_template("fragments/thanks.html")
        header_fragment: str = render_template(
            "fragments/header.html", page_title="Your Results", show_sidebar=True
        )
        footer_fragment: str = render_template(
            "fragments/footer.html",
            colour=recommendations.photographer_classifier.top_classification.styling[
                "colour_1"
            ],
        )

        response: Response = jsonify(
            {
                # FIXME: render this without passing a closing div tag
                "template": header_fragment
                + '<div class="side-shift">'
                + classification_badge_fragment
                + '<div class="results-wrapper">'
                + kit_fragment
                + analysis_fragment
                + recommendations_fragment
                + improve_fragment
                + thanks_fragment
                + "</div></div></div>"
                + footer_fragment,
                "additional_data": {
                    "recommendations_id": str(recommendations.id),
                    "focal_lengths": {
                        "binned": {
                            "primes": list(
                                recommendations.results.focal_length.instances_binned_primes.items()
                                if hasattr(
                                    recommendations.results.focal_length,
                                    "instances_binned_primes",
                                )
                                else {}
                            ),
                            "zooms": list(
                                recommendations.results.focal_length.instances_binned_zooms.items()
                                if hasattr(
                                    recommendations.results.focal_length,
                                    "instances_binned_zooms",
                                )
                                else {}
                            ),
                            "all": list(
                                recommendations.results.focal_length.instances_binned.items()
                                if hasattr(
                                    recommendations.results.focal_length,
                                    "instances_binned",
                                )
                                else {}
                            ),
                        },
                        "discrete": {
                            "primes": list(
                                recommendations.results.focal_length.instances_discrete_primes
                                if hasattr(
                                    recommendations.results.focal_length,
                                    "instances_discrete_primes",
                                )
                                else []
                            ),
                            "zooms": list(
                                recommendations.results.focal_length.instances_discrete_zooms
                                if hasattr(
                                    recommendations.results.focal_length,
                                    "instances_discrete_zooms",
                                )
                                else []
                            ),
                            "all": list(
                                recommendations.results.focal_length.instances_discrete_all
                                if hasattr(
                                    recommendations.results.focal_length,
                                    "instances_discrete_all",
                                )
                                else []
                            ),
                        },
                    },
                    "style_colours": [  # noqa: E501
                        recommendations.photographer_classifier.top_classification.styling[
                            "colour_1"
                        ],
                        recommendations.photographer_classifier.top_classification.styling[
                            "colour_2"
                        ],
                        recommendations.photographer_classifier.top_classification.styling[
                            "colour_3"
                        ],
                    ],
                    "aperture": getattr(
                        getattr(recommendations.results, "aperture"),
                        "percentage_taken_at_lowest_value",
                        None,
                    ),  # noqa: E501
                    "iso": getattr(
                        getattr(recommendations.results, "iso", None),
                        "percentage_taken_at_highest_value",
                        None,
                    ),  # noqa: E501
                    "shutter_speed": getattr(
                        getattr(recommendations.results, "shutter_speed", None),
                        "percentage_taken_at_lowest_value",
                        None,
                    ),  # noqa: E501
                    "exposure": getattr(
                        getattr(recommendations.results, "exposure", None),
                        "percentage_taken_at_lowest_value",
                        None,
                    ),  # noqa: E501
                    "camera_count": len(
                        getattr(
                            getattr(recommendations.results, "metrics", None),
                            "cameras",
                            [],
                        )
                    ),
                    "lens_count": len(
                        getattr(
                            getattr(recommendations.results, "metrics", None),
                            "lenses",
                            [],
                        )
                    ),
                },
            }
        )

        log.info("process-exif successfully returned")
        log.debug(f"returning response: {response.json}")

        return response

    @app.route("/recall/<recommendations_id>", methods=["GET"])
    def get_recalled_recommendations(recommendations_id: str) -> str:
        log.info(f"recall route called with id {recommendations_id}")
        try:
            recommendations: Recommendations = (
                RecommendationService.get_from_persisted_id(
                    recommendations_id=UUID(recommendations_id),
                    repo=repository,
                )
            )
        except ValueError:
            # If there's no recommendations with that ID, return to the index page
            return render_template("index.html", recommendations_id=None)
        classification_badge = render_template(
            "fragments/classification.html",
            photographer_classification=recommendations.photographer_classifier.top_classification,
            scores=recommendations.photographer_classifier.scores,
        )
        html_fragment: str = render_template(
            "fragments/how-you-shoot.html", recommendations=recommendations
        )
        log.info("recall page successfully returned")
        return classification_badge + html_fragment

    @app.route("/llm-recommendations/<recommendations_id>", methods=["GET"])
    def get_llm_recommendations(recommendations_id: str) -> str:
        log.info(f"llm recommendations requested for {recommendations_id}")
        try:
            recommendations: Recommendations = (
                RecommendationService.populate_llm_recommendations(
                    UUID(recommendations_id), repo=repository
                )
            )
            if not (
                recommendations.llm_camera_recommendation
                or recommendations.llm_lens_recommendation
            ):
                raise ValueError  # pragma: no cover
        except ValueError:  # pragma: no cover
            log.warning(
                f"No recommendations found for the given ID: {recommendations_id}"
            )
            return ""

        camera_recommendations_table = render_template(
            "fragments/recommendations-table.html",
            rows=recommendations.llm_camera_recommendation,
            display_headers=TABLE_HEADERS[ProductType.CAMERA]["display"],
        )
        lens_recommendations_table = render_template(
            "fragments/recommendations-table.html",
            rows=recommendations.llm_lens_recommendation,
            display_headers=TABLE_HEADERS[ProductType.LENS]["display"],
        )
        return render_template(
            "fragments/what-could-make-your-kit-better.html",
            recommendations_input=render_template(
                "fragments/recommendations-json-tree.html",
                data=recommendations.recommendation_statement,
            ),
            recommendations_lens_recommendation=lens_recommendations_table,
            recommendations_camera_recommendation=camera_recommendations_table,
        )

    @app.route("/test-badges", methods=["GET"])
    def test_badges() -> str:
        # This is a test route to display the classification badge
        # You can modify this to suit your needs
        badges: list[str] = []
        for photographer_classification in PHOTOGRAPHER_CLASSIFICATIONS.values():
            badges.append(
                render_template(
                    "fragments/classification.html",
                    photographer_classification=photographer_classification,
                    scores={
                        name: classifier.score
                        for name, classifier in PHOTOGRAPHER_CLASSIFICATIONS.items()
                    },
                )
            )

        return render_template("index.html", recommendations_id=None) + "\n".join(
            badges
        )

    @app.route("/swagger", methods=["GET"])
    def swagger_ui() -> str:
        log.info("Swagger UI endpoint called")
        return render_template("swagger-ui.html")

    return app


app: Flask = create_app()
