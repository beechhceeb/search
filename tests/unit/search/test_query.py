from typing import Any
from unittest.mock import Mock, patch

import pytest
from requests import Response, RequestException

from albatross.services.search.query import Search, SearchResultModel


@patch("albatross.services.search.query.requests.get")
@patch("albatross.services.search.query.Search.search_product_price_via_proxy")
def test_search_via_proxy(
    mock_search_price: Mock,
    mock_requests_get: Mock,
    search_requests_get_response: Response,
) -> None:
    mock_search_price.return_value = 12345
    mock_requests_get.return_value = search_requests_get_response

    # Given a model name
    model_name: str = "Nikon z9"

    # When the search_via_proxy method is called
    result: SearchResultModel = Search.search_model_via_proxy(model_name)

    # Then the results should be returned
    assert result.model_name.lower() == model_name.lower()
    assert result.model_id == "71193"
    assert result.price == 12345.0
    assert result.image_link == "/media-service/a450727b-b7ae-4c0f-8dde-413e5106ea09"
    assert result.model_url_segment == "nikon-z9"


@patch("albatross.services.search.query.requests.get")
@patch("albatross.services.search.query.Search.search_product_price_via_proxy")
def test_search_model_via_proxy_when_search_product_price_via_proxy_raises_exception(
    mock_search_price: Mock,
    mock_requests_get: Mock,
    search_requests_get_response: Response,
) -> None:
    mock_requests_get.return_value = search_requests_get_response

    # Given a model name
    model_name: str = "Nikon z9"

    # When the search_product_price_via_proxy method raises an exception
    mock_search_price.side_effect = Exception("Test exception")

    # Then the search_model_via_proxy method should raise an exception
    with pytest.raises(Exception, match="Test exception"):
        Search.search_model_via_proxy(model_name)


@patch("albatross.services.search.query.requests.get")
def test_search_via_proxy_rate_limited(
    mock_requests_get: Mock,
) -> None:
    # Given the search service proxy returns a 429 response
    mock_requests_get.return_value = Mock(spec=Response, status_code=429)

    # When we call the search_via_proxy method
    result = Search.search_via_proxy({"query": "anything"}, 0)

    # Then the mock_requests_get should be called twice
    assert mock_requests_get.call_count == 2

    # And nothing is returned
    assert result is None


def test_search_via_proxy_requests_get_raises_exception() -> None:
    # Given the search service proxy raises an exception
    with patch("albatross.services.search.query.requests.get") as mock_requests_get:
        mock_requests_get.side_effect = RequestException("Network error")

        # When we call the search_via_proxy method
        result = Search.search_via_proxy({"query": "anything"}, 0)

        # Then nothing is returned
        assert result is None


def test_search_via_proxy_request_returns_429_once_then_raises_request_exception() -> (
    None
):
    # Given the search service proxy returns a 429 response,
    # then raises a request exception
    with patch("albatross.services.search.query.requests.get") as mock_requests_get:
        mock_requests_get.side_effect = [
            Mock(spec=Response, status_code=429),
            RequestException("Network error"),
        ]

        # When we call the search_via_proxy method
        result = Search.search_via_proxy({"query": "anything"}, 0)

        # Then the mock_requests_get should be called twice
        assert mock_requests_get.call_count == 2

        # And nothing is returned
        assert result is None


def test_search_via_proxy_json_loads_raises_jsondecodeerror() -> None:
    # Given the search service proxy returns a response that cannot be decoded
    with patch("albatross.services.search.query.requests.get") as mock_requests_get:
        mock_response = Mock(spec=Response, status_code=200)
        mock_response.text = "Invalid JSON"
        mock_requests_get.return_value = mock_response

        # When we call the search_via_proxy method
        result = Search.search_via_proxy({"query": "anything"}, 0)

        # Then nothing is returned
        assert result is None


def test_search_via_proxy_with_no_query_raises_value_error() -> None:
    # Given a params object with an empty query
    params = {"query": ""}
    # When we call the search_via_proxy method
    # Then a ValueError should be raised
    with pytest.raises(ValueError, match="Query parameter is required"):
        Search.search_via_proxy(params, 0)

    # Given a params object without a query
    # When we call the search_via_proxy method
    # Then a ValueError should be raised
    with pytest.raises(ValueError, match="Query parameter is required"):
        Search.search_via_proxy({}, 0)


@patch("albatross.services.search.query.requests.get")
def test_search_via_proxy_non_200_response(
    mock_requests_get: Mock,
) -> None:
    # Given the search service proxy returns a non 200 response
    mock_requests_get.return_value = Mock(spec=Response, status_code=500)

    # When we call the search_via_proxy method
    result = Search.search_via_proxy({"query": "anything"}, 0)

    # Then nothing is returned
    assert result is None


@patch("albatross.services.search.query.Search.search_via_proxy")
def test_search_model_via_proxy_empty_response(
    mock_search_via_proxy: Mock,
) -> None:
    # Given search_via_proxy returns None
    mock_search_via_proxy.return_value = None

    # When we call search_model_via_proxy
    result = Search.search_model_via_proxy("anything")

    # Then result is none
    assert result is None


@patch("albatross.services.search.query.Search.search_via_proxy")
def test_search_product_price_via_proxy(mock_search_via_proxy: Mock) -> None:
    # Given search_via_proxy returns a valid response
    mock_search_via_proxy.return_value = {
        "results": [
            {
                "model_id": "71193",
                "product_price": {"values": [12345]},
                "product_condition_star_rating": {"values": [4]},
                "image_link": "/media-service/a450727b-b7ae-4c0f-8dde-413e5106ea09",
                "model_url_segment": "nikon-z9",
            }
        ]
    }

    # When we call search_product_price_via_proxy
    result = Search.search_product_price_via_proxy("71193")

    # Then the price should be returned
    assert result == 8689


@patch("albatross.services.search.query.Search.search_via_proxy")
def test_search_product_price_via_proxy_when_no_response(
    mock_search_via_proxy: Mock,
) -> None:
    # Given search_via_proxy returns a None response
    mock_search_via_proxy.return_value = None

    # When we call search_product_price_via_proxy
    result = Search.search_product_price_via_proxy("71193")

    # Then None is returned
    assert result is None


@patch("albatross.services.search.query.Search.search_product_price_via_proxy")
@patch("albatross.services.search.query.Search.search_via_proxy")
def test_search_model_via_proxy(
    mock_search_via_proxy: Mock,
    mock_search_product_price_via_proxy: Mock,
    search_via_proxy_response: dict[str, Any],
) -> None:
    # Given a model name
    model_name: str = "Nikon z9"
    # And the search_via_proxy method returns a valid response
    mock_search_via_proxy.return_value = search_via_proxy_response
    # And the search_product_price_via_proxy method returns a valid price
    mock_search_product_price_via_proxy.return_value = 12345

    # When the search_model_via_proxy method is called
    result: SearchResultModel = Search.search_model_via_proxy(model_name)

    # Then the results should be returned
    assert result.model_name.lower() == model_name.lower()
    assert result.model_id == "71193"
    assert result.price == 12345.0
    assert result.image_link == "/media-service/a450727b-b7ae-4c0f-8dde-413e5106ea09"
    assert result.model_url_segment == "nikon-z9"


@patch("albatross.services.search.query.Search.search_product_price_via_proxy")
@patch("albatross.services.search.query.Search.search_via_proxy")
def test_search_model_via_proxy_no_results(
    mock_search_via_proxy: Mock,
    mock_search_product_price_via_proxy: Mock,
    search_via_proxy_response: dict[str, Any],
) -> None:
    # Given a model name
    model_name: str = "Nikon z9"
    # And the search_via_proxy method returns a valid response with no results
    search_via_proxy_response["results"] = []
    mock_search_via_proxy.return_value = search_via_proxy_response

    # When the search_model_via_proxy method is called
    result: SearchResultModel = Search.search_model_via_proxy(model_name)

    # Then nothing should be returned
    assert result is None


@patch("albatross.services.search.query.Search.search_product_price_via_proxy")
@patch("albatross.services.search.query.Search.search_via_proxy")
def test_search_model_via_proxy_multiple_results(
    mock_search_via_proxy: Mock,
    mock_search_product_price_via_proxy: Mock,
    search_via_proxy_multiple_results_response: dict[str, Any],
) -> None:
    # Given a model name
    model_name: str = "Nikon z9"
    # And the search_via_proxy method returns a valid response with multiple results
    mock_search_via_proxy.return_value = search_via_proxy_multiple_results_response
    # And the search_product_price_via_proxy method returns a valid price
    mock_search_product_price_via_proxy.return_value = 12345

    # When the search_model_via_proxy method is called
    result: SearchResultModel = Search.search_model_via_proxy(model_name)

    # Then the results should be returned
    assert result.model_name.lower() == model_name.lower()
    assert result.model_id == "71193"
    assert result.price == 12345.0
    assert result.image_link == "/media-service/a450727b-b7ae-4c0f-8dde-413e5106ea09"
    assert result.model_url_segment == "nikon-z9"


@patch("albatross.services.search.query.Search.search_product_price_via_proxy")
@patch("albatross.services.search.query.Search.search_via_proxy")
def test_search_model_via_proxy_multiple_results_price_check_fails(
    mock_search_via_proxy: Mock,
    mock_search_product_price_via_proxy: Mock,
    search_via_proxy_multiple_results_response: dict[str, Any],
) -> None:
    # Given a model name
    model_name: str = "Nikon z9"
    # And the search_via_proxy method returns a valid response with multiple results
    mock_search_via_proxy.return_value = search_via_proxy_multiple_results_response
    # And the search_product_price_via_proxy method raises an exception
    mock_search_product_price_via_proxy.side_effect = Exception

    # When the search_model_via_proxy method is called
    result: SearchResultModel = Search.search_model_via_proxy(model_name)

    # Then the results should be returned
    assert result.model_name.lower() == model_name.lower()
    assert result.model_id == "71193"
    assert result.price is None
    assert result.image_link == "/media-service/a450727b-b7ae-4c0f-8dde-413e5106ea09"
    assert result.model_url_segment == "nikon-z9"


@pytest.mark.parametrize(
    "model_name, expected",
    [
        ("Nikon Z 9", "nikon z9"),
        ("Nikon Z9", "nikon z9"),
        ("Nikon Z 9 (Body Only)", "nikon z9"),
        ("Nikon  z 9", "nikon z9"),
        ("Nikon z9mark2", "nikon z9 mark 2"),
        ("Nikon 50.0mmf/1.8", "nikon 50mm 1.8"),
        ("Olympus M.40-150mm", "olympus 40-150mm"),
    ],
)
def test_normalize_model_name(model_name: str, expected: str) -> None:
    # Given a model name
    # When the normalize_model_name method is called
    result: str = Search.normalize_model_name(model_name)

    # Then the normalized model name should be returned
    assert result == expected


def test_convert_sell_price_and_condition_to_buy_price() -> None:
    # Given a sell price and condition
    sell_price: int = 1000
    condition: int = 4

    # When we call convert_sell_price_and_condition_to_buy_price
    result = Search.convert_sell_price_and_condition_to_buy_price(sell_price, condition)

    # Then the buy price should be calculated correctly
    assert result == 703


# The below is a test designed to run through known exif model names
# that don't map to a model name in our database.
# That could either be because we don't buy it,
# or because the model names are different enough
# to not match any results

# @pytest.mark.parametrize(
#     "model_name",
#     [
#         "Canon PowerShot G9 X Mark II",
#         "EOS 200D II",
#         "EOS 9000D",
#         "EOS D2000",
#         "EOS D30",
#         "EOS Digital REBEL",
#         "EOS Digital Rebel XS",
#         "EOS Digital Rebel XSi",
#         "EOS Digital Rebel XT",
#         "EOS Digital Rebel XTi",
#         "EOS KISS M",
#         "EOS Kiss Digital F",
#         "EOS Kiss Digital X2",
#         "EOS Kiss X10i",
#         "EOS Kiss X50",
#         "EOS Kiss X70",
#         "EOS Kiss X90",
#         "EOS M50 Mark II",
#         "EOS M6 Mark II",
#         "EOS-1D",
#         "EOS-1D Mark II",
#         "EOS-1D Mark II N",
#         "EOS-1D Mark III",
#         "EOS-1D Mark IV",
#         "EOS-1D X",
#         "EOS-1D X Mark II",
#         "EOS-1Ds",
#         "EOS-1Ds Mark II",
#         "EOS-1Ds Mark III",
#         "IXUS 125 HS",
#         "IXUS 220 HS",
#         "IXUS 30",
#         "IXUS 40",
#         "IXUS 400",
#         "IXUS 430",
#         "IXUS 50",
#         "IXUS 500",
#         "IXUS 55",
#         "IXUS 70",
#         "IXUS 700",
#         "IXUS 750",
#         "IXUS 80 IS",
#         "IXUS 95 IS",
#         "IXUS II",
#         "IXUS i",
#         "IXUS v2",
#         "IXY 200a",
#         "IXY 220F",
#         "IXY 30",
#         "IXY 40",
#         "IXY 400",
#         "IXY 450",
#         "IXY 50",
#         "IXY 500",
#         "IXY 55",
#         "IXY Digital 600",
#         "IXY Digital 700",
#         "PowerShot A10",
#         "PowerShot A20",
#         "PowerShot A30",
#         "PowerShot A40",
#         "PowerShot A4000 IS",
#         "PowerShot A490",
#         "PowerShot A495",
#         "PowerShot A510",
#         "PowerShot A520",
#         "PowerShot A60",
#         "PowerShot A610",
#         "PowerShot A620",
#         "PowerShot A640",
#         "PowerShot A650 IS",
#         "PowerShot A70",
#         "PowerShot A720 IS",
#         "PowerShot A75",
#         "PowerShot A80",
#         "PowerShot A85",
#         "PowerShot A95",
#         "PowerShot G1 X Mark II",
#         "PowerShot G1 X Mark III",
#         "PowerShot G10",
#         "PowerShot G11",
#         "PowerShot G2",
#         "PowerShot G3 X (3:2)",
#         "PowerShot G5 X (16:9)",
#         "PowerShot G5 X (3:2)",
#         "PowerShot G5 X (4:3)",
#         "PowerShot G5 X Mark II",
#         "PowerShot G6",
#         "PowerShot G7 X (16:9)",
#         "PowerShot G7 X (3:2)",
#         "PowerShot G7 X (4:3)",
#         "PowerShot G7 X Mark II (16:9)",
#         "PowerShot G7 X Mark II (3:2)",
#         "PowerShot G7 X Mark II (4:3)",
#         "PowerShot G7 X Mark III (3:2)",
#         "PowerShot Pro1",
#         "PowerShot Pro70",
#         "PowerShot Pro90 IS",
#         "PowerShot S1 IS",
#         "PowerShot S100",
#         "PowerShot S110",
#         "PowerShot S120",
#         "PowerShot S2 IS",
#         "PowerShot S200",
#         "PowerShot S30",
#         "PowerShot S40",
#         "PowerShot S400",
#         "PowerShot S410",
#         "PowerShot S45",
#         "PowerShot S5 IS",
#         "PowerShot S50",
#         "PowerShot S500",
#         "PowerShot S60",
#         "PowerShot S70",
#         "PowerShot S80",
#         "PowerShot S90",
#         "PowerShot S95",
#         "PowerShot SD10",
#         "PowerShot SD100",
#         "PowerShot SD110",
#         "PowerShot SD1100 IS",
#         "PowerShot SD200",
#         "PowerShot SD300",
#         "PowerShot SD400",
#         "PowerShot SD450",
#         "PowerShot SD500",
#         "PowerShot SD550",
#         "PowerShot SD950 IS",
#         "PowerShot SX1 IS",
#         "PowerShot SX10 IS",
#         "PowerShot SX130 IS",
#         "PowerShot SX150 IS",
#         "PowerShot SX160 IS",
#         "PowerShot SX220 HS",
#         "PowerShot SX230 HS",
#         "PowerShot SX240 HS",
#         "PowerShot SX260 HS",
#         "PowerShot SX30 IS",
#         "Powershot A1200",
#         "Powershot ELPH 110 HS",
#         "Powershot SX50 HS",
#         "Powershot SX60 HS",
#         "EX-FH20",
#         "EX-P600",
#         "EX-P700",
#         "EX-Z3",
#         "EX-Z30",
#         "EX-Z4",
#         "EX-Z40",
#         "EX-Z55",
#         "EX-Z750",
#         "QV-3000EX",
#         "QV-3500EX",
#         "QV-4000",
#         "Air 2S",
#         "FC6310",
#         "Mavic Air FC2103",
#         "Mavic Pro FC220",
#         "Mini 3 Pro",
#         "Phantom 3 Pro FC300X",
#         "Phantom 4 RTK",
#         "Phantom Vision FC200",
#         "R-D1",
#         "FinePix 3800",
#         "FinePix A370",
#         "FinePix E550",
#         "FinePix F10",
#         "FinePix F11",
#         "FinePix F200EXR",
#         "FinePix F601 ZOOM",
#         "FinePix F710",
#         "FinePix F770EXR",
#         "FinePix F810",
#         "FinePix F810 widescreen mode",
#         "FinePix HS20EXR",
#         "FinePix HS30EXR",
#         "FinePix IS Pro",
#         "FinePix S1 Pro",
#         "FinePix S2 Pro",
#         "FinePix S20Pro",
#         "FinePix S3 Pro",
#         "FinePix S3000",
#         "FinePix S304",
#         "FinePix S5100",
#         "FinePix S5500",
#         "FinePix S5600",
#         "FinePix S602 ZOOM",
#         "FinePix S7000",
#         "FinePix S9000",
#         "FinePix S9500",
#         "FinePix S9600",
#         "FinePix X100",
#         "FinePix2800ZOOM",
#         "GFX 100",
#         "GFX 50R",
#         "GFX 50S",
#         "GFX100 II",
#         "GFX100S",
#         "GFX100S II",
#         "GFX50S II",
#         "X-Pro1",
#         "X-Pro2",
#         "X-Pro3",
#         "X100S",
#         "XQ1",
#         "HD2",
#         "HERO4 Black",
#         "HERO4 Silver",
#         "Hero10 black",
#         "Hero3+ black",
#         "CFV 100C/907X",
#         "CFV II 50C/907X",
#         "DJI Mavic 2 Pro",
#         "DJI Mavic 3",
#         "Hasselblad 500 mech.",
#         "Hasselblad H3D",
#         "X1D II 50C",
#         "X2D 100C",
#         "C-Lux (Typ 1546)",
#         "CL (Typ 7323)",
#         "D-Lux 2",
#         "Digilux 2",
#         "Digilux 3",
#         "M (Typ 240)",
#         "M Monochrom (Typ 246)",
#         "M10 Monochrom",
#         "M10-D",
#         "M10-P",
#         "M10-R",
#         "M11 Monochrom",
#         "M11-D",
#         "M8 Digital Camera",
#         "M9 Digital Camera",
#         "Mamiya 645",
#         "Mamiya ZD",
#         "35mm film: full frame",
#         "Coolpix 4200",
#         "Coolpix 4500",
#         "Coolpix 4800",
#         "Coolpix 5000",
#         "Coolpix 5200",
#         "Coolpix 5400",
#         "Coolpix 5700",
#         "Coolpix 5900",
#         "Coolpix 7600",
#         "Coolpix 7900",
#         "Coolpix 8400",
#         "Coolpix 8700",
#         "Coolpix 8800",
#         "Coolpix 950",
#         "Coolpix 990",
#         "Coolpix 995",
#         "Coolpix P330",
#         "Coolpix P340",
#         "Coolpix P6000",
#         "Coolpix S3300",
#         "D1H",
#         "D300S",
#         "D3S",
#         "Z 30",
#         "Z 5",
#         "Z 50",
#         "Z 6",
#         "Z 6II",
#         "Z 7",
#         "Z 7II",
#         "Z 8",
#         "Z 9",
#         "Z50II",
#         "Z5II",
#         "Z6III",
#         "OM-1 II",
#         "C-2040 Zoom",
#         "C-3040 Zoom",
#         "C-4000 Zoom",
#         "C-4100 Zoom",
#         "C-4040 Zoom",
#         "C-50 Zoom variant of the X-2",
#         "C-5050 Zoom",
#         "C-5060 Wide Zoom",
#         "C-70 Zoom",
#         "C-7000 Zoom",
#         "C-700 Ultra Zoom",
#         "C-7070 Wide Zoom",
#         "C-730 Ultra Zoom",
#         "C-750 Ultra Zoom",
#         "C-8080 Wide Zoom",
#         "C-860L",
#         "D-360L variant of the C-860L",
#         "E-1",
#         "E-10",
#         "E-20",
#         "E-20N",
#         "E-20P",
#         "E-3",
#         "E-30",
#         "E-300",
#         "E-330",
#         "E-400",
#         "E-410",
#         "E-420",
#         "E-450",
#         "E-5",
#         "E-500",
#         "E-510",
#         "E-520",
#         "E-600",
#         "E-620",
#         "E-M1 II",
#         "E-M1 III",
#         "E-M10 II",
#         "E-M10 III",
#         "E-M10 III S",
#         "E-M10 IV",
#         "E-M5 II",
#         "E-M5 III",
#         "SP-350",
#         "SP-500 Ultra Zoom",
#         "SP-560 Ultra Zoom",
#         "Stylus 1",
#         "Stylus 1",
#         "1s",
#         "Stylus Epic",
#         "Stylus Verve Digital variant of the µ-mini Digital",
#         "Tough TG-1",
#         "Tough TG-2",
#         "Tough TG-3",
#         "Tough TG-4",
#         "X-2",
#         "XZ-1",
#         "XZ-2",
#         "µ-II",
#         "µ-mini Digital",
#         "DC-FZ10002",
#         "DC-G99",
#         "DC-G9M2",
#         "DC-GH5M2",
#         "DC-GH5S",
#         "DC-GX7MK3",
#         "DC-LX100M2",
#         "DC-S1RM2",
#         "DC-S5M2",
#         "DC-S5M2X",
#         "DC-ZS200D",
#         "DMC-FX150",
#         "DMC-FX2",
#         "DMC-FX7",
#         "DMC-FX8",
#         "DMC-FX9",
#         "DMC-FZ100 (3:2)",
#         "DMC-FZ18",
#         "DMC-FZ28",
#         "DMC-FZ35",
#         "DMC-FZ40",
#         "DMC-FZ40 (3:2)",
#         "DMC-FZ45",
#         "DMC-FZ45 (3:2)",
#         "DMC-FZ5",
#         "DMC-FZ50",
#         "DMC-L1",
#         "DMC-L10",
#         "DMC-LC1",
#         "DMC-LX1 16:9",
#         "DMC-LX1 3:2",
#         "DMC-LX1 4:3",
#         "DMC-LX2",
#         "DMC-LX3 16:9",
#         "DMC-LX3 1:1",
#         "DMC-LX3 3:2",
#         "DMC-LX3 4:3",
#         "DMC-LX5 4:3",
#         "DMC-LX7 4:3",
#         "DMC-LZ1",
#         "DMC-LZ2",
#         "DMC-TZ61",
#         "DMC-TZ90",
#         "DMC-TZ91",
#         "DMC-TZ96",
#         "DMC-ZS70",
#         "645D",
#         "645Z",
#         "K-1 II",
#         "K-3 III Monochrome",
#         "K-m",
#         "K-x",
#         "K100D",
#         "K100D Super",
#         "K110D",
#         "K2000",
#         "K200D",
#         "Optio 230GS",
#         "Optio 330GS",
#         "Optio 33L",
#         "Optio 33LF",
#         "Optio 430",
#         "Optio 43WR",
#         "Optio 450",
#         "Optio 550",
#         "Optio 555",
#         "Optio 750Z",
#         "Q-S1",
#         "Q10",
#         "Q7",
#         "IQ140",
#         "IQ180",
#         "P 25",
#         "Caplio GX",
#         "Caplio GX8",
#         "Caplio RR30",
#         "2.8E",
#         "EX2F",
#         "GX-1S",
#         "GX10",
#         "GX20",
#         "Galaxy NX",
#         "Galaxy Note 8",
#         "Galaxy S21",
#         "Galaxy S7",
#         "Galaxy S8",
#         "NX mini",
#         "NX1",
#         "NX10",
#         "NX100",
#         "NX1000",
#         "NX11",
#         "NX1100",
#         "NX20",
#         "NX200",
#         "NX2000",
#         "NX210",
#         "NX30",
#         "NX300",
#         "NX3000",
#         "NX300M",
#         "NX5",
#         "NX500",
#         "WB2000",
#         "BF",
#         "DP1S",
#         "DP1X",
#         "DP2S",
#         "DP2X",
#         "SD14",
#         "SD15",
#         "SD9",
#         "fp",
#         "fp L",
#         "sd Quattro",
#         "sd Quattro H",
#         "Alpha 1",
#         "Alpha 1 II",
#         "Alpha 100",
#         "Alpha 200",
#         "Alpha 230",
#         "Alpha 300",
#         "Alpha 3000",
#         "Alpha 33",
#         "Alpha 330",
#         "Alpha 35",
#         "Alpha 350",
#         "Alpha 37",
#         "Alpha 380",
#         "Alpha 390",
#         "Alpha 450",
#         "Alpha 500",
#         "Alpha 5000",
#         "Alpha 5100",
#         "Alpha 55",
#         "Alpha 550",
#         "Alpha 560",
#         "Alpha 57",
#         "Alpha 58",
#         "Alpha 580",
#         "Alpha 6000",
#         "Alpha 6100",
#         "Alpha 6300",
#         "Alpha 6400",
#         "Alpha 65",
#         "Alpha 6500",
#         "Alpha 6600",
#         "Alpha 6700",
#         "Alpha 68",
#         "Alpha 7",
#         "Alpha 7 II",
#         "Alpha 7 III",
#         "Alpha 7 IV",
#         "Alpha 700",
#         "Alpha 77",
#         "Alpha 77 II",
#         "Alpha 7C",
#         "Alpha 7C II",
#         "Alpha 7CR",
#         "Alpha 7R",
#         "Alpha 7R II",
#         "Alpha 7R III",
#         "Alpha 7R IIIA",
#         "Alpha 7R IV",
#         "Alpha 7R IV A",
#         "Alpha 7R V",
#         "Alpha 7S",
#         "Alpha 7S II",
#         "Alpha 7S III",
#         "Alpha 850",
#         "Alpha 9",
#         "Alpha 9 II",
#         "Alpha 9 III",
#         "Alpha 900",
#         "Alpha 99",
#         "Alpha 99 II",
#         "Alpha 99V",
#         "Cyber-shot DSC-F707",
#         "Cyber-shot DSC-F717",
#         "Cyber-shot DSC-S75",
#         "Cyber-shot DSC-S85",
#         "DSC-F828",
#         "DSC-H1",
#         "DSC-HX20V",
#         "DSC-P100",
#         "DSC-P150",
#         "DSC-P200",
#         "DSC-P73",
#         "DSC-P93",
#         "DSC-R1",
#         "DSC-S60",
#         "DSC-S80",
#         "DSC-S90",
#         "DSC-ST80",
#         "DSC-T1",
#         "DSC-V1",
#         "DSC-V3",
#         "DSC-W1",
#         "DSC-W12",
#         "DSC-W15",
#         "DSC-W5",
#         "DSC-W7",
#         "RX0 II",
#         "RX1 R II",
#         "RX10 II",
#         "RX10 III",
#         "RX10 IV",
#         "RX100 III",
#         "RX100 IV",
#         "RX100 VA",
#         "Xperia Z3",
#     ],
# )
# def test_search_by_proxy_parameterised(model_name: str) -> None:
#     # Given a model name
#     time.sleep(5)
#     # When the search_via_proxy method is called
#     result: SearchResultModel = Search.search_via_proxy(model_name)
#     # Then the results should be returned
#     assert model_name.lower() in result.model_name.lower()
#     print(f"{model_name} == {result.model_name}")
