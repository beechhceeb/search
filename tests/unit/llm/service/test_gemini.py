from unittest.mock import MagicMock, Mock, patch

import pytest
from google.genai.types import GenerateContentConfig, ThinkingConfig

from albatross.config import LLM_MODEL
from albatross.services.llm.gemini import GeminiService


@patch("albatross.services.llm.gemini.genai.Client")
def test_gemini_service_initialization_failure(mock_client: Mock) -> None:
    # Given: Mock Gemini client to raise an exception during initialization
    mock_client.side_effect = Exception("Initialization error")

    # When/Then: Creating GeminiService should raise an exception
    with pytest.raises(Exception, match="Initialization error"):
        GeminiService()


@patch("albatross.services.llm.gemini.genai.Client")
def test_gemini_service_chat(mock_client: Mock) -> None:
    # Given: A mock Gemini client and a GeminiService instance
    mock_instance = MagicMock()
    mock_client.return_value = mock_instance
    mock_instance.models.generate_content.return_value = MagicMock(
        text="Mocked response"
    )
    service = GeminiService()

    # When: Calling the chat method
    response = service.chat("Test prompt", use_cache=False)

    # Then: Assert the Gemini client was called with the correct arguments
    mock_instance.models.generate_content.assert_called_once_with(
        model=LLM_MODEL,
        contents=["Test prompt"],
        config=GenerateContentConfig(
            http_options=None,
            system_instruction=None,
            temperature=None,
            top_p=None,
            top_k=None,
            candidate_count=None,
            max_output_tokens=None,
            stop_sequences=None,
            response_logprobs=None,
            logprobs=None,
            presence_penalty=None,
            frequency_penalty=None,
            seed=None,
            response_mime_type=None,
            response_schema=None,
            routing_config=None,
            model_selection_config=None,
            safety_settings=None,
            tools=None,
            tool_config=None,
            labels=None,
            cached_content=None,
            response_modalities=None,
            media_resolution=None,
            speech_config=None,
            audio_timestamp=None,
            automatic_function_calling=None,
            thinking_config=ThinkingConfig(include_thoughts=None, thinking_budget=0),
        ),
    )
    assert response == "Mocked response"
