from typing import Any

import pytest

from albatross.enums.enums import ProductType
from albatross.services.llm.base_llm import BaseLLM


class MockLLM(BaseLLM):
    def chat(self, prompt: str) -> str:
        return """
```
|Budget|Lens|Focal Length|Max Aperture|Stabilized|Weight (g)|Purpose/Genres|Tags|Reasoning|Why This Over Alternatives?|mpb.com_url|
|---|---|---|---|---|---|---|---|---|---|---|
|Low|Tamron 35-150mm f/2.8-4 Di III VXD|35-150mm|f/2.8-4|No|795|Portrait, Travel, Events|🟢 Best Value, 🟡 Versatile|Offers a very versatile zoom range in a single lens, covering wide-angle to short telephoto.|Provides a longer reach compared to the Z 24-70mm f/4 S at a similar price, although with a variable aperture.|https://www.mpb.com/product/tamron-35-150mm-f-2-8-4-di-iii-vxd-for-nikon-z|
|Low|Nikon NIKKOR Z 85mm f/1.8 S|85mm|f/1.8|No|470|Portrait, Events|🟢 Best Value, 🟡 Compact|A compact and sharp prime lens, ideal for portraits with beautiful bokeh.|Significantly sharper and faster than the 80-200mm f/2.8 at a similar focal length, while also being more affordable.|https://www.mpb.com/product/nikon-nikkor-z-85mm-f-1-8-s|
|Mid|Nikon NIKKOR Z 70-200mm f/2.8 VR S|70-200mm|f/2.8|Yes|1360|Portrait, Sports, Wildlife|🔴 Pro Level, 🟡 Versatile|A professional-grade telephoto zoom lens with excellent image quality and fast aperture.|Significantly sharper and with better build quality than the older 80-200mm f/2.8, and adds vibration reduction.|https://www.mpb.com/product/nikon-nikkor-z-70-200mm-f-2-8-vr-s|
|Mid|Sigma 24-70mm f/2.8 DG DN Art for Nikon Z|24-70mm|f/2.8|No|835|Wedding, Events, Landscape|🟡 Versatile, 🟢 Best Value|A great alternative 24-70mm lens for the Nikon Z system that is incredibly sharp.|A faster and more versatile option than the Z 24-70mm f/4 S, though larger and lacks stabilization.|https://www.mpb.com/product/sigma-24-70mm-f-2-8-dg-dn-art-for-nikon-z|
|High|Nikon NIKKOR Z 50mm f/1.2 S|50mm|f/1.2|No|1090|Portrait, Low Light|🔴 Pro Level, 🟡 High Performance|An extremely fast prime lens with exceptional sharpness and beautiful bokeh.|Offers a significant improvement in low-light performance and bokeh compared to the Z 50mm f/1.8 S, though much larger and heavier.|https://www.mpb.com/product/nikon-nikkor-z-50mm-f-1-2-s|
|High|Nikon NIKKOR Z 100-400mm f/4.5-5.6 VR S|100-400mm|f/4.5-5.6|Yes|1355|Wildlife, Sports|🔴 Pro Level, 🟡 Versatile|A versatile telephoto zoom lens with excellent image quality and vibration reduction.|Provides a much longer reach than the Z 70-200mm f/2.8 VR S, making it ideal for wildlife and sports photography.|https://www.mpb.com/product/nikon-nikkor-z-100-400mm-f-4-5-5-6-vr-s|
```

```
|Budget|Camera|Sensor|Megapixels|IBIS|Dual Card Slots|Max Video Resolution|FPS|Tags|Reasoning|Why This Over Alternatives?|mpb.com_url|
|---|---|---|---|---|---|---|---|---|---|---|
|Low|Nikon Z 5|FULL_FRAME|24.3|Yes|Yes|4K UHD|4.5|🟢 Best Value, 🔵 Most Versatile|An excellent entry-level full-frame camera with great image quality and in-body image stabilization.|Offers dual card slots and IBIS compared to the Z 6 at a similar price point.|https://www.mpb.com/product/nikon-z-5|
|Low|Nikon Z fc|APS-C|20.9|No|No|4K UHD|11|🟡 Travel Friendly, 🟢 Best Value|A compact and stylish APS-C camera with a retro design, perfect for travel and everyday photography.|A good balance of price, features and performance.|https://www.mpb.com/product/nikon-z-fc|
|Mid|Nikon Z 6II|FULL_FRAME|24.5|Yes|Yes|4K UHD|14|🔵 Most Versatile, 🟡 Upgraded Performance|An upgraded version of the Z 6 with improved autofocus, dual card slots, and faster burst shooting.|Offers significant improvements in autofocus and usability compared to the original Z 6, making it a more well-rounded camera.|https://www.mpb.com/product/nikon-z-6ii|
|Mid|Nikon Z 7|FULL_FRAME|45.7|Yes|No|4K UHD|9|🟡 Upgraded Performance, 🔴 High Resolution|A high-resolution full-frame camera perfect for landscapes, portraits, and other detail-oriented photography.|Offers a much higher resolution sensor than the Z 6, capturing more detail in images.|https://www.mpb.com/product/nikon-z-7|
|High|Nikon Z 7II|FULL_FRAME|45.7|Yes|Yes|4K UHD|10|🔴 Pro Level, 🔵 Most Versatile|An upgraded version of the Z 7 with improved autofocus, dual card slots, and faster burst shooting.|Offers significant improvements in autofocus and usability compared to the original Z 7, making it a more capable camera for professional use.|https://www.mpb.com/product/nikon-z-7ii|
|High|Nikon Z 8|FULL_FRAME|45.7|Yes|Yes|8K UHD|20|🔴 Pro Level, 🔵 Most Versatile|Nikon's Z8 offers top-of-the-line features in a smaller package.|Similar performance to the Z 9, but in a more compact and lighter body.|https://www.mpb.com/product/nikon-z-8|
```
"""  # noqa: E501


def test_base_llm_chat_not_implemented() -> None:
    # Given: An instance of BaseLLM
    base_llm = BaseLLM()

    # When/Then: Calling chat should raise NotImplementedError
    with pytest.raises(
        NotImplementedError, match="Chat method not implemented by subclass"
    ):
        base_llm.chat("Test prompt")


def test_base_llm_build_recommendations(
    recommendations_short_analysis_json: str,
    camera_recommendation: dict[str, Any],
    lens_recommendation: dict[str, Any],
) -> None:
    # Given: A mock subclass of BaseLLM

    # Create a mock instance of the LLM, overriding the chat method with mock_chat
    mock_llm = MockLLM()

    # When: Calling build_recommendations
    lens_actual, camera_actual = mock_llm.build_recommendations(
        recommendations_short_analysis_json
    )

    # Then: Verify the output
    assert lens_recommendation == lens_actual
    assert camera_recommendation == camera_actual


def test_convert_camera_recommendations_response_text_to_psv(
    camera_psv: list[str], llm_recommendation_camera: str
) -> None:
    # Given chat output
    # When: Calling convert_recommendations_response_text_to_psv
    result = BaseLLM.convert_recommendations_response_text_to_psv(
        llm_recommendation_camera, 9, ProductType.CAMERA
    )

    # Then: Verify the output
    assert result == camera_psv


def test_convert_lens_recommendations_response_text_to_psv(
    lens_psv: list[str], llm_recommendation_lens: str
) -> None:
    # Given chat output
    # When: Calling convert_recommendations_response_text_to_psv
    result = BaseLLM.convert_recommendations_response_text_to_psv(
        llm_recommendation_lens, 9, ProductType.LENS
    )

    # Then: Verify the output
    assert result == lens_psv


def test_convert_recommendations_response_text_to_psv_with_invalid_data_raise_value_error(  # noqa: E501
    llm_recommendation_camera: str,
) -> None:
    # Given a psv with a missing header
    # When: Calling convert_recommendations_response_text_to_psv with invalid data
    with pytest.raises(ValueError):
        BaseLLM.convert_recommendations_response_text_to_psv(
            llm_recommendation_camera[190:], 9, ProductType.CAMERA
        )


def test_convert_psv_to_renderable_table(
    lens_psv: list[str],
    camera_psv: list[str],
    lens_recommendation: dict[str, Any],
    camera_recommendation: dict[str, Any],
) -> None:
    # Given: Lens and Camera recommendations in PSV format

    # When: Calling convert_psv_to_renderable_table
    lens_recommendation_table_data = BaseLLM.convert_psv_to_renderable_table(
        lens_psv, ProductType.LENS
    )
    camera_recommendation_table_data = BaseLLM.convert_psv_to_renderable_table(
        camera_psv, ProductType.CAMERA
    )

    # Then: Verify the output
    assert lens_recommendation_table_data == lens_recommendation
    assert camera_recommendation_table_data == camera_recommendation
