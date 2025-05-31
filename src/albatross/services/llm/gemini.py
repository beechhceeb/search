import json
import logging
import os
from typing import Any

from google import genai
from google.genai import types

from albatross.config import CACHE_FILE, LLM_MODEL, THINKING_BUDGET
from albatross.services.llm.base_llm import BaseLLM

log = logging.getLogger(__name__)


class GeminiService(BaseLLM):
    # def __init__(self) -> None:
    #     self.client = genai.Client(api_key=GEMINI_API_KEY)

    def __init__(self) -> None:
        self.client = genai.Client()

    def chat(self, prompt: str, use_cache: bool = True) -> str:
        log.debug(f"GEMINI PROMPT: {prompt}")

        # Check cache if enabled
        if use_cache:  # pragma: no cover
            cache: dict[str, str] = {}
            if os.path.exists(CACHE_FILE):
                try:
                    with open(CACHE_FILE, "r") as f:
                        cache = json.load(f)
                except (json.JSONDecodeError, OSError) as exc:
                    log.warning(
                        "Failed to load cache, starting with empty cache",
                        extra={"mpb": {"error": str(exc)}},
                    )

            # Return from cache if exists
            if prompt in cache:
                log.debug(f"RESPONSE: {cache[prompt]}")
                return cache[prompt]

        response: Any = self.client.models.generate_content(
            model=LLM_MODEL,
            contents=[prompt],
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=THINKING_BUDGET)
            ),
        )

        response_text = str(response.text)
        log.debug(f"GEMINI RESPONSE: {response_text}")

        # Update cache if enabled
        if use_cache:  # pragma: no cover
            # Load cache again to avoid overwrites
            cache = {}
            if os.path.exists(CACHE_FILE):
                try:
                    with open(CACHE_FILE, "r") as f:
                        cache = json.load(f)
                except (json.JSONDecodeError, OSError) as exc:
                    log.warning(
                        "Failed to load cache, starting with empty cache",
                        extra={"mpb": {"error": str(exc)}},
                    )

            # Add to cache and save
            cache[prompt] = response_text
            try:
                with open(CACHE_FILE, "w") as f:
                    json.dump(cache, f)
            except OSError as e:
                log.error(f"Failed to save cache: {e}")

        return response_text
