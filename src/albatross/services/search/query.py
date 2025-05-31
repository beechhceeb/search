import json
import logging
import re
import time
from typing import Any

import requests
from requests import RequestException

from albatross.config import (
    SEARCH_PROXY_HEADERS,
    SEARCH_PROXY_PARAMS_MODEL,
    SEARCH_PROXY_PARAMS_PRODUCT,
    SEARCH_PROXY_URL,
    SEARCH_STAR_RATING_TO_BEST_SELL_PRICE_FACTOR,
)
from albatross.models.search import SearchResponse, SearchResultModel

log = logging.getLogger(__name__)


class Search:
    """
    Service to interact with search SDK
    """

    # def __init__(self) -> None:
    #     self.search_service = SearchService(
    #     **config.SEARCH_SERVICE_GRPC_CLIENT_CONFIG
    #     )

    # def search_model(self, brand: str, model: str) -> list[dict[str, Any]] | None:
    #     """
    #     Given a model name, search for it in search service and return the model
    #     object
    #     :param model:
    #     :return:
    #     """
    #
    #     query = query_pb2.Query(
    #         query=f"{brand} {model}",
    #         collection=query_pb2.Collection.Enum.PRODUCT,
    #         filter_query={
    #             "object_type": query_pb2.FilterQueryValue(value=["model"]),
    #         },
    #         rows=1,
    #     )
    #
    #     query_request = query_pb2.QueryRequest(
    #         query=query,
    #     )
    #
    #     processed_search_results: list[dict[str, Any]] = []
    #
    #     try:
    #         query_response = self.search_service.query(query_request)
    #         for result in query_response.results:
    #             processed_search_results.append(
    #                 {key: value for key, value in result.fields.items()}
    #             )
    #
    #         return processed_search_results
    #     except UnavailableException:
    #         log.warning("Search service is unavailable")
    #         return None

    @staticmethod
    def search_via_proxy(
        params: dict[str, Any], retry_after_rate_limit_secs: int = 20
    ) -> dict[str, Any] | None:
        if "query" not in params or not params["query"]:
            raise ValueError("Query parameter is required")

        # initial model search
        try:
            response = requests.get(
                SEARCH_PROXY_URL,
                headers=SEARCH_PROXY_HEADERS,
                params=params,
            )
        except RequestException as exc:
            log.error(
                f"Search service request failed: {exc}",
                extra={"mpb": {"albatross": {"query": params["query"]}}},
            )
            return None

        if response.status_code == 429:
            # Rate limit exceeded, wait and retry
            log.warning(
                f"Search service proxy rate limit exceeded, delaying for"
                f" {retry_after_rate_limit_secs} seconds",
                extra={"mpb": {"albatross": {"query": params["query"]}}},
            )
            time.sleep(retry_after_rate_limit_secs)
            try:
                response = requests.get(
                    SEARCH_PROXY_URL,
                    headers=SEARCH_PROXY_HEADERS,
                    params=params,
                )
            except RequestException as exc:
                log.error(
                    f"Search service request failed: {exc}",
                    extra={"mpb": {"albatross": {"query": params["query"]}}},
                )
                return None
            if response.status_code == 429:  # pragma: no branch
                log.warning(
                    "Search service proxy still rate limited after waiting,"
                    "search failed.",
                    extra={"mpb": {"albatross": {"query": params["query"]}}},
                )
                return None

        if response.status_code != 200:
            log.warning(
                f"Search service returned {response.status_code} response",
                extra={
                    "mpb": {
                        "albatross": {
                            "query": params["query"],
                            "status_code": response.status_code,
                        }
                    }
                },
            )
            return None

        try:
            result: dict[str, Any] = json.loads(response.text)
        except json.JSONDecodeError as exc:
            log.error(
                f"Failed to decode search service response: {exc}",
                extra={"mpb": {"albatross": {"query": params["query"]}}},
            )
            return None

        return result

    @staticmethod
    def search_model_via_proxy(input_model_name: str) -> SearchResultModel | None:
        """
        This method doesn't use the SearchService directly, but rather uses
        the toucan proxy to interact with the search service.
        """

        # FIXME: this should do a bulk search to avoid rate limiting

        params: dict[str, Any] = SEARCH_PROXY_PARAMS_MODEL
        params["query"] = Search.normalize_model_name(input_model_name)
        response: dict[str, Any] | None = Search.search_via_proxy(params)

        if not response:
            return None

        search_response: SearchResponse = SearchResponse.from_json_response(response)
        if len(search_response.results) == 1:
            result = search_response.results[0]
            try:
                price: int | None = Search.search_product_price_via_proxy(
                    result.model_id
                )
                result.price = price
            except Exception as exc:
                log.warning(f"Couldn't find price for model: {exc}")
                raise
            return result
        for result in search_response.results:
            if (
                input_model_name.lower() in result.model_name.lower()
            ):  # pragma: no branch
                try:
                    price = Search.search_product_price_via_proxy(result.model_id)
                    result.price = price
                except Exception as exc:
                    log.warning(f"Couldn't find price for model: {exc}")
                    result.price = None
                return result
        log.warning(
            f"Search service proxy returned no results for query {input_model_name}"
        )
        return None

    @staticmethod
    def search_product_price_via_proxy(model_id: str) -> int | None:
        params: dict[str, Any] = SEARCH_PROXY_PARAMS_PRODUCT
        params["query"] = f"model_id:{model_id}"
        response: dict[str, Any] | None = Search.search_via_proxy(params)
        if not response:
            log.warning(f"Couldn't find price for model {model_id}")
            return None
        try:
            price = int(response["results"][0]["product_price"]["values"][0])
            condition: int = int(
                response["results"][0]["product_condition_star_rating"]["values"][0]
            )
            return Search.convert_sell_price_and_condition_to_buy_price(
                price, condition
            )
        except IndexError:  # pragma: no cover
            return None
        except KeyError:  # pragma: no cover
            return None

    @staticmethod
    def convert_sell_price_and_condition_to_buy_price(
        sell_price: int, condition: int
    ) -> int | None:
        """
        Given a sell price and condition, roughly estimate the buy price
        :param sell_price: The sell price
        :param condition: The condition
        :return: The buy price
        """
        return int(SEARCH_STAR_RATING_TO_BEST_SELL_PRICE_FACTOR[condition] * sell_price)

    @staticmethod
    def normalize_model_name(name: str) -> str:
        # Because the model name we get from the exif may not match
        # the model name stored by MPB, we may not get results from
        # search. we can try to normalise the model name and see if that works better
        # Make everything lowercase
        name = name.lower()
        # Remove spaces between a single letter and a number
        name = re.sub(r"\b([A-Z]) (\d)\b", r"\1\2", name)
        # Remove spaces between two numbers
        name = re.sub(r"(\d) (\d)", r"\1\2", name)
        # Remove anything in parentheses
        name = re.sub(r"\s*\([^)]*\)", "", name)
        # Replace multiple spaces with a single space
        name = re.sub(r"\s{2,}", " ", name)
        # Trim
        name = name.strip()
        # If mark or mk in name, check there's a space around it
        if "mark" in name or "mk" in name:
            name = re.sub(r"(mark|mk)", r" \1 ", name)
        # if there's a number, followed by a mm, not then followed by a space,
        # add a space
        name = re.sub(r"(\d+)(mm)(\S)", r"\1\2 \3", name)
        # Remove .0s
        name = re.sub(r"\.0", "", name)
        # Remove 'f/'
        name = re.sub(r"f/", "", name)
        # Remaining '/'s should be replaced with spaces
        name = re.sub(r"/", " ", name)
        # Special rule for nikon z cameras
        if name.startswith("nikon z "):
            name = name.replace("nikon z ", "nikon z")
        # Special rule for olympus/om cameras
        if "m." in name:
            name = name.replace("m.", "")

        return name
