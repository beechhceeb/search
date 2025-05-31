import os

from albatross.enums.enums import ProductType

LLM_ENABLED = os.environ.get("LLM_ENABLED", "true") == "true"

ASYNC_MODE = os.environ.get("ASYNC_MODE", "true") == "true"

LLM_PRODUCT = os.environ.get("LLM_PRODUCT", "gemini")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash-preview-04-17")
THINKING_BUDGET = 0


CACHE_FILE = "llm_cache.json"

MARKET = "en-uk"
MARKET_TO_CURRENCY_SYMBOL = {
    "en-uk": "£",
    "en-us": "$",
    "de-de": "€",
    "fr-fr": "€",
    "it-it": "€",
    "es-es": "€",
    "nl-nl": "€",
}
BUDGETS = {
    ProductType.LENS: {"low": 300, "mid": 1000, "unlimited": 5000},
    ProductType.CAMERA: {"low": 1500, "mid": 2500, "unlimited": 5000},
}
TABLE_HEADERS = {
    ProductType.LENS: {
        "request": [
            "Budget",
            "Lens",
            "Focal Length",
            "Max Aperture",
            "Stabilized",
            "Weight (g)",
            "Purpose/Genres",
            "Tags",
            "Reasoning",
            "Why This Over Alternatives?",
            "mpb.com_url",
        ],
        "display": [
            "Budget",
            "Lens",
            "Focal Length",
            "Max Aperture",
            "Stabilized",
            "Weight (g)",
            "Purpose/Genres",
            "Tags",
            "Reasoning",
            "Why This Over Alternatives?",
        ],
    },
    ProductType.CAMERA: {
        "request": [
            "Budget",
            "Camera",
            "Sensor",
            "Megapixels",
            "IBIS",
            "Dual Card Slots",
            "Max Video Resolution",
            "FPS",
            "Tags",
            "Reasoning",
            "Why This Over Alternatives?",
            "mpb.com_url",
        ],
        "display": [
            "Budget",
            "Camera",
            "Sensor",
            "Megapixels",
            "IBIS",
            "Dual Card Slots",
            "Max Video Resolution",
            "FPS",
            "Tags",
            "Reasoning",
            "Why This Over Alternatives?",
        ],
    },
}

RECOMMENDATIONS_PER_BUDGET = int(os.getenv("LLM_RECOMMENDATION_OPTIONS_PER_BUDGET", 2))

PROMPT_TEMPLATE = f"""
You are an expert photography gear assistant. Based on the user's current photographic kit and image analysis, recommend upgrade options for both lenses and cameras.

Generate two separate pipe-separated tables:

For each of the following budgets — recommend **{RECOMMENDATIONS_PER_BUDGET} lenses compatible with the user's primary camera** with the user's system. Each lens must be available on [mpb.com](https://www.mpb.com/). Include detailed specs and a comparison-oriented justification.
   - Low budget: < {MARKET_TO_CURRENCY_SYMBOL[MARKET]}{BUDGETS[ProductType.LENS]["low"]}
   - Mid budget: < {MARKET_TO_CURRENCY_SYMBOL[MARKET]}{BUDGETS[ProductType.LENS]["mid"]}
   - High budget: < {MARKET_TO_CURRENCY_SYMBOL[MARKET]}{BUDGETS[ProductType.LENS]["unlimited"]}

**Output Format:**

|{"|".join(TABLE_HEADERS[ProductType.LENS]["request"])}|
|{"|".join([f"{header} data" for header in TABLE_HEADERS[ProductType.LENS]["request"]])}|

- **Stabilized**: Yes/No
- **Tags**: E.g. 🟢 Best Value, 🔴 Pro Level, 🟡 Travel Friendly
- **Why This Over Alternatives?**: One-sentence comparison to a similar or previous-generation product

---

2. **Camera Upgrade Recommendations**

For each of the following budgets — *Low*, *Mid*, and *High* — recommend **{RECOMMENDATIONS_PER_BUDGET} cameras as an upgrade from the user's primary camera, compatible with the user's lenses with the same mount as the primary camera**. All cameras must be available on [mpb.com](https://www.mpb.com/). Include key specs for direct comparison.
   - Low budget: < {MARKET_TO_CURRENCY_SYMBOL[MARKET]}{BUDGETS[ProductType.CAMERA]["low"]}
   - Mid budget: < {MARKET_TO_CURRENCY_SYMBOL[MARKET]}{BUDGETS[ProductType.CAMERA]["mid"]}
   - High budget: < {MARKET_TO_CURRENCY_SYMBOL[MARKET]}{BUDGETS[ProductType.CAMERA]["unlimited"]}

**Output Format:**
|{"|".join(TABLE_HEADERS[ProductType.CAMERA]["request"])}|
|{"|".join([f"{header} data" for header in TABLE_HEADERS[ProductType.CAMERA]["request"]])}|


- **IBIS / Dual Card Slots**: Yes/No
- **FPS**: Max continuous shooting rate
- **Tags**: E.g. 🟢 Best Value, 🔴 Pro Level, 🔵 Most Versatile

---

**Rules:**
- Output only the two tables.
- Use markdown triple backticks (```) to enclose each table.
- Only include gear currently or previously available on [mpb.com](https://www.mpb.com/) — link using `https://www.mpb.com/product/<model-name>` format.
- Do not duplicate items across budgets.
- Order the items from low to high price.
- Upgrades must be substantive improvements over the user's current gear.
- Upgrade options must be compatible with the user's primary camera.
- If you cannot find enough options to fit the number of requested recommendations, include a row in the table with "No recommendations available" in the "Lens" or "Camera" column, and N/A in the other columns.


Customer Analysis:
"""  # noqa: E501
