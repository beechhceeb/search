import logging
from typing import Any

log = logging.getLogger(__name__)


class SearchResultModel:
    def __init__(
        self,
        model_name: str,
        model_id: str,
        image_link: str,
        model_url_segment: str,
        price: float | None = None,
    ):
        self.model_name: str = model_name
        self.model_id: str = model_id
        self.image_link: str = image_link
        self.model_url_segment: str = model_url_segment
        if price:
            self.price: float | None = float(price)
        else:
            self.price = None

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__

    @staticmethod
    def from_dict(search_result_input: dict[str, Any]) -> "SearchResultModel":
        return SearchResultModel(
            model_name=search_result_input["model_name"],
            model_id=search_result_input["model_id"],
            image_link=search_result_input["image_link"],
            model_url_segment=search_result_input["model_url_segment"],
            price=search_result_input.get("price"),
        )


class SearchResponse:
    def __init__(self, results: list[SearchResultModel]):
        self.results: list[SearchResultModel] = results

    @staticmethod
    def from_json_response(response: dict[str, Any]) -> "SearchResponse":
        results = []
        for result in response["results"]:
            try:
                results.append(
                    SearchResultModel(
                        model_name=result["model_name"]["values"][0],
                        model_id=result["model_id"]["values"][0],
                        image_link=result["model_images"]["values"][0],
                        model_url_segment=result["model_url_segment"]["values"][0],
                    )
                )
            except KeyError as e:
                log.warning(f"Missing key in search result: {e}")
        return SearchResponse(results=results)
