import json
from typing import Any
from unittest.mock import Mock

import pytest
from requests import Response


@pytest.fixture
def search_requests_get_response() -> Response:
    return Mock(
        spec=Response,
        status_code=200,
        text=json.dumps(
            {
                "results": [
                    {
                        "model_id": {"values": ["71193"]},
                        "model_images": {
                            "values": [
                                "/media-service/a450727b-b7ae-4c0f-8dde-413e5106ea09"
                            ]
                        },
                        "model_name": {"values": ["Nikon Z9"]},
                        "model_url_segment": {"values": ["nikon-z9"]},
                        "product_price": {"values": ["341900"]},
                    }
                ],
                "result_count": 1,
                "total_results": 1,
                "spellcheck": {"suggestions": []},
            }
        ),
    )


@pytest.fixture
def search_via_proxy_response() -> dict[str, Any]:
    return {
        "result_count": 1,
        "results": [
            {
                "model_id": {"values": ["71193"]},
                "model_images": {
                    "values": ["/media-service/a450727b-b7ae-4c0f-8dde-413e5106ea09"]
                },
                "model_name": {"values": ["Nikon Z9"]},
                "model_url_segment": {"values": ["nikon-z9"]},
                "product_price": {"values": ["341900"]},
            }
        ],
        "spellcheck": {"suggestions": []},
        "total_results": 1,
    }


@pytest.fixture
def search_via_proxy_multiple_results_response() -> dict[str, Any]:
    return {
        "result_count": 2,
        "results": [
            {
                "model_id": {"values": ["71193"]},
                "model_images": {
                    "values": ["/media-service/a450727b-b7ae-4c0f-8dde-413e5106ea09"]
                },
                "model_name": {"values": ["Nikon Z9"]},
                "model_url_segment": {"values": ["nikon-z9"]},
                "product_price": {"values": ["341900"]},
            },
            {
                "model_id": {"values": ["71193"]},
                "model_images": {
                    "values": ["/media-service/a450727b-b7ae-4c0f-8dde-413e5106ea09"]
                },
                "model_name": {"values": ["Nikon Z9"]},
                "model_url_segment": {"values": ["nikon-z9"]},
                "product_price": {"values": ["341900"]},
            },
        ],
        "spellcheck": {"suggestions": []},
        "total_results": 2,
    }
