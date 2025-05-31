import logging
import re

from albatross.config import (
    BUDGETS,
    PROMPT_TEMPLATE,
    RECOMMENDATIONS_PER_BUDGET,
    TABLE_HEADERS,
)
from albatross.enums.enums import ProductType

log = logging.getLogger(__name__)


class BaseLLM:
    """
    Base class for the LLM service.
    it should enforce the following methods:
    - chat
    - build_recommendations
    """

    def chat(self, prompt: str) -> str:
        raise NotImplementedError("Chat method not implemented by subclass")

    def build_recommendations(
        self, analysis: str
    ) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
        prompt = f"""
                {PROMPT_TEMPLATE}:

                {analysis}
                """
        response_text: str = self.chat(prompt)
        return BaseLLM.parse_llm_recommendations_response(response_text)

    @staticmethod
    def parse_llm_recommendations_response(
        response_text: str,
    ) -> tuple[list[dict[str, str]], list[dict[str, str]]]:  # noqa: E501
        # Parse the recommendations into the lens and camera table data
        lens_number_of_rows: int = (
            len(BUDGETS[ProductType.LENS].keys()) * RECOMMENDATIONS_PER_BUDGET
        )
        camera_number_of_rows: int = (
            len(BUDGETS[ProductType.CAMERA].keys()) * RECOMMENDATIONS_PER_BUDGET
        )

        # Split the response text into lens and camera recommendations
        lens_data, camera_data = re.split(r"```\s*```", response_text)

        lens_recommendation_psv = BaseLLM.convert_recommendations_response_text_to_psv(
            lens_data, lens_number_of_rows, ProductType.LENS
        )

        camera_recommendation_psv = (
            BaseLLM.convert_recommendations_response_text_to_psv(
                camera_data, camera_number_of_rows, ProductType.CAMERA
            )
        )

        lens_recommendation_table_data: list[dict[str, str]] = (
            BaseLLM.convert_psv_to_renderable_table(  # noqa: E501
                lens_recommendation_psv, ProductType.LENS
            )
        )
        camera_recommendation_table_data: list[dict[str, str]] = (
            BaseLLM.convert_psv_to_renderable_table(  # noqa: E501
                camera_recommendation_psv, ProductType.CAMERA
            )
        )

        return lens_recommendation_table_data, camera_recommendation_table_data

    @staticmethod
    def convert_recommendations_response_text_to_psv(
        raw_recommendations: str, number_of_rows: int, product_type: ProductType
    ) -> list[str]:
        recommendations: list[str] = []

        lines: list[str] = raw_recommendations.splitlines()

        # Remove lines that are just '```'
        # or `'|---|---|---|---|---|---|---|---|---|---|---|'`
        lines = [
            line
            for line in lines
            if line and not line.startswith("```") and not line.startswith("|---|")
        ]

        expected_header_row = "|".join(TABLE_HEADERS[product_type]["request"])

        for line_index, line in enumerate(lines):  # pragma: no branch
            if expected_header_row in line:  # pragma: no branch
                recommendations = lines[
                    line_index + 1 : line_index + number_of_rows + 1
                ]
                break
        if not recommendations:
            log.error(
                f"{product_type.name} recommendations matching headers "
                f"not found in llm response",
                extra={
                    "mpb": {
                        "response": raw_recommendations,
                        "expected_table_headers": TABLE_HEADERS[product_type][
                            "request"
                        ],
                    }
                },
            )
            raise ValueError(
                f"recommendations not in recognised form in LLM response: {raw_recommendations}"  # noqa: E501
            )

        # Before returning, we need to strip the leading and trailing |s from each line
        recommendations = [line.strip("|") for line in recommendations]

        return recommendations

    @staticmethod
    def convert_row_from_request_to_display(
        row: dict[str, str], request_headers: list[str], display_headers: list[str]
    ) -> dict[str, str]:
        display_row: dict[str, str] = {}
        display_row["product_link"] = row["mpb.com_url"]
        for header_index, header in enumerate(request_headers):
            if header in display_headers:
                display_row[header] = row[header]
        return display_row

    @staticmethod
    def convert_psv_to_renderable_table(
        lines: list[str], product_type: ProductType
    ) -> list[dict[str, str]]:
        """
        Deserialize PSV string to a list of dictionaries.
        """

        request_headers: list[str] = TABLE_HEADERS[product_type]["request"]
        display_headers: list[str] = TABLE_HEADERS[product_type]["display"]

        # Convert the rows from PSV to a list of lists
        requested_rows: list[list[str]] = [line.split("|") for line in lines]

        # Convert the rows from a list of strings to a dictionary, with headers as keys
        rows: list[dict[str, str]] = []
        try:
            for requested_row in requested_rows:
                row = {}
                for header_index, header in enumerate(request_headers):
                    row[header] = requested_row[header_index].strip()
                rows.append(row)
        except IndexError as e:  # pragma: no cover
            log.error(
                f"Less rows than expected in response for {product_type.name} table: {e}",  # noqa: E501
                extra={
                    "mpb": {
                        "response": lines,
                        "expected_table_headers": request_headers,
                    }
                },
            )
            raise

        # Convert the rows into a display format
        display_rows: list[dict[str, str]] = []
        for row in rows:
            display_rows.append(
                BaseLLM.convert_row_from_request_to_display(
                    row, request_headers, display_headers
                )
            )
        return display_rows
