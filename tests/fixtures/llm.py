from typing import Any

import pytest


@pytest.fixture
def llm_recommendation_response() -> str:
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


@pytest.fixture
def llm_recommendation_camera(llm_recommendation_response: str) -> str:
    return llm_recommendation_response.split("\n\n")[1].strip()


@pytest.fixture
def llm_recommendation_lens(llm_recommendation_response: str) -> str:
    return llm_recommendation_response.split("\n\n")[0].strip()


@pytest.fixture
def lens_psv() -> list[str]:
    return [
        "Low|Tamron 35-150mm f/2.8-4 Di III VXD|35-150mm|f/2.8-4|No|795|Portrait, Travel, Events|🟢 Best Value, 🟡 Versatile|Offers a very versatile zoom range in a single lens, covering wide-angle to short telephoto.|Provides a longer reach compared to the Z 24-70mm f/4 S at a similar price, although with a variable aperture.|https://www.mpb.com/product/tamron-35-150mm-f-2-8-4-di-iii-vxd-for-nikon-z",
        "Low|Nikon NIKKOR Z 85mm f/1.8 S|85mm|f/1.8|No|470|Portrait, Events|🟢 Best Value, 🟡 Compact|A compact and sharp prime lens, ideal for portraits with beautiful bokeh.|Significantly sharper and faster than the 80-200mm f/2.8 at a similar focal length, while also being more affordable.|https://www.mpb.com/product/nikon-nikkor-z-85mm-f-1-8-s",
        "Mid|Nikon NIKKOR Z 70-200mm f/2.8 VR S|70-200mm|f/2.8|Yes|1360|Portrait, Sports, Wildlife|🔴 Pro Level, 🟡 Versatile|A professional-grade telephoto zoom lens with excellent image quality and fast aperture.|Significantly sharper and with better build quality than the older 80-200mm f/2.8, and adds vibration reduction.|https://www.mpb.com/product/nikon-nikkor-z-70-200mm-f-2-8-vr-s",
        "Mid|Sigma 24-70mm f/2.8 DG DN Art for Nikon Z|24-70mm|f/2.8|No|835|Wedding, Events, Landscape|🟡 Versatile, 🟢 Best Value|A great alternative 24-70mm lens for the Nikon Z system that is incredibly sharp.|A faster and more versatile option than the Z 24-70mm f/4 S, though larger and lacks stabilization.|https://www.mpb.com/product/sigma-24-70mm-f-2-8-dg-dn-art-for-nikon-z",
        "High|Nikon NIKKOR Z 50mm f/1.2 S|50mm|f/1.2|No|1090|Portrait, Low Light|🔴 Pro Level, 🟡 High Performance|An extremely fast prime lens with exceptional sharpness and beautiful bokeh.|Offers a significant improvement in low-light performance and bokeh compared to the Z 50mm f/1.8 S, though much larger and heavier.|https://www.mpb.com/product/nikon-nikkor-z-50mm-f-1-2-s",
        "High|Nikon NIKKOR Z 100-400mm f/4.5-5.6 VR S|100-400mm|f/4.5-5.6|Yes|1355|Wildlife, Sports|🔴 Pro Level, 🟡 Versatile|A versatile telephoto zoom lens with excellent image quality and vibration reduction.|Provides a much longer reach than the Z 70-200mm f/2.8 VR S, making it ideal for wildlife and sports photography.|https://www.mpb.com/product/nikon-nikkor-z-100-400mm-f-4-5-5-6-vr-s",
    ]


@pytest.fixture
def camera_psv() -> list[str]:
    return [
        "Low|Nikon Z 5|FULL_FRAME|24.3|Yes|Yes|4K UHD|4.5|🟢 Best Value, 🔵 Most Versatile|An excellent entry-level full-frame camera with great image quality and in-body image stabilization.|Offers dual card slots and IBIS compared to the Z 6 at a similar price point.|https://www.mpb.com/product/nikon-z-5",
        "Low|Nikon Z fc|APS-C|20.9|No|No|4K UHD|11|🟡 Travel Friendly, 🟢 Best Value|A compact and stylish APS-C camera with a retro design, perfect for travel and everyday photography.|A good balance of price, features and performance.|https://www.mpb.com/product/nikon-z-fc",
        "Mid|Nikon Z 6II|FULL_FRAME|24.5|Yes|Yes|4K UHD|14|🔵 Most Versatile, 🟡 Upgraded Performance|An upgraded version of the Z 6 with improved autofocus, dual card slots, and faster burst shooting.|Offers significant improvements in autofocus and usability compared to the original Z 6, making it a more well-rounded camera.|https://www.mpb.com/product/nikon-z-6ii",
        "Mid|Nikon Z 7|FULL_FRAME|45.7|Yes|No|4K UHD|9|🟡 Upgraded Performance, 🔴 High Resolution|A high-resolution full-frame camera perfect for landscapes, portraits, and other detail-oriented photography.|Offers a much higher resolution sensor than the Z 6, capturing more detail in images.|https://www.mpb.com/product/nikon-z-7",
        "High|Nikon Z 7II|FULL_FRAME|45.7|Yes|Yes|4K UHD|10|🔴 Pro Level, 🔵 Most Versatile|An upgraded version of the Z 7 with improved autofocus, dual card slots, and faster burst shooting.|Offers significant improvements in autofocus and usability compared to the original Z 7, making it a more capable camera for professional use.|https://www.mpb.com/product/nikon-z-7ii",
        "High|Nikon Z 8|FULL_FRAME|45.7|Yes|Yes|8K UHD|20|🔴 Pro Level, 🔵 Most Versatile|Nikon's Z8 offers top-of-the-line features in a smaller package.|Similar performance to the Z 9, but in a more compact and lighter body.|https://www.mpb.com/product/nikon-z-8",
    ]


@pytest.fixture
def camera_recommendation() -> list[dict[str, Any]]:
    return [
        {
            "Budget": "Low",
            "Camera": "Nikon Z 5",
            "Dual Card Slots": "Yes",
            "FPS": "4.5",
            "IBIS": "Yes",
            "Max Video Resolution": "4K UHD",
            "Megapixels": "24.3",
            "Reasoning": "An excellent entry-level full-frame camera with great image quality and in-body image stabilization.",
            "Sensor": "FULL_FRAME",
            "Tags": "🟢 Best Value, 🔵 Most Versatile",
            "Why This Over Alternatives?": "Offers dual card slots and IBIS compared to the Z 6 at a similar price point.",
            "product_link": "https://www.mpb.com/product/nikon-z-5",
        },
        {
            "Budget": "Low",
            "Camera": "Nikon Z fc",
            "Dual Card Slots": "No",
            "FPS": "11",
            "IBIS": "No",
            "Max Video Resolution": "4K UHD",
            "Megapixels": "20.9",
            "Reasoning": "A compact and stylish APS-C camera with a retro design, perfect for travel and everyday photography.",
            "Sensor": "APS-C",
            "Tags": "🟡 Travel Friendly, 🟢 Best Value",
            "Why This Over Alternatives?": "A good balance of price, features and performance.",
            "product_link": "https://www.mpb.com/product/nikon-z-fc",
        },
        {
            "Budget": "Mid",
            "Camera": "Nikon Z 6II",
            "Dual Card Slots": "Yes",
            "FPS": "14",
            "IBIS": "Yes",
            "Max Video Resolution": "4K UHD",
            "Megapixels": "24.5",
            "Reasoning": "An upgraded version of the Z 6 with improved autofocus, dual card slots, and faster burst shooting.",
            "Sensor": "FULL_FRAME",
            "Tags": "🔵 Most Versatile, 🟡 Upgraded Performance",
            "Why This Over Alternatives?": "Offers significant improvements in autofocus and usability compared to the original Z 6, making it a more well-rounded camera.",
            "product_link": "https://www.mpb.com/product/nikon-z-6ii",
        },
        {
            "Budget": "Mid",
            "Camera": "Nikon Z 7",
            "Dual Card Slots": "No",
            "FPS": "9",
            "IBIS": "Yes",
            "Max Video Resolution": "4K UHD",
            "Megapixels": "45.7",
            "Reasoning": "A high-resolution full-frame camera perfect for landscapes, portraits, and other detail-oriented photography.",
            "Sensor": "FULL_FRAME",
            "Tags": "🟡 Upgraded Performance, 🔴 High Resolution",
            "Why This Over Alternatives?": "Offers a much higher resolution sensor than the Z 6, capturing more detail in images.",
            "product_link": "https://www.mpb.com/product/nikon-z-7",
        },
        {
            "Budget": "High",
            "Camera": "Nikon Z 7II",
            "Dual Card Slots": "Yes",
            "FPS": "10",
            "IBIS": "Yes",
            "Max Video Resolution": "4K UHD",
            "Megapixels": "45.7",
            "Reasoning": "An upgraded version of the Z 7 with improved autofocus, dual card slots, and faster burst shooting.",
            "Sensor": "FULL_FRAME",
            "Tags": "🔴 Pro Level, 🔵 Most Versatile",
            "Why This Over Alternatives?": "Offers significant improvements in autofocus and usability compared to the original Z 7, making it a more capable camera for professional use.",
            "product_link": "https://www.mpb.com/product/nikon-z-7ii",
        },
        {
            "Budget": "High",
            "Camera": "Nikon Z 8",
            "Dual Card Slots": "Yes",
            "FPS": "20",
            "IBIS": "Yes",
            "Max Video Resolution": "8K UHD",
            "Megapixels": "45.7",
            "Reasoning": "Nikon's Z8 offers top-of-the-line features in a smaller package.",
            "Sensor": "FULL_FRAME",
            "Tags": "🔴 Pro Level, 🔵 Most Versatile",
            "Why This Over Alternatives?": "Similar performance to the Z 9, but in a more compact and lighter body.",
            "product_link": "https://www.mpb.com/product/nikon-z-8",
        },
    ]


@pytest.fixture
def lens_recommendation() -> list[dict[str, Any]]:
    return [
        {
            "Budget": "Low",
            "Focal Length": "35-150mm",
            "Lens": "Tamron 35-150mm f/2.8-4 Di III VXD",
            "Max Aperture": "f/2.8-4",
            "Purpose/Genres": "Portrait, Travel, Events",
            "Reasoning": "Offers a very versatile zoom range in a single lens, covering wide-angle to short telephoto.",
            "Stabilized": "No",
            "Tags": "🟢 Best Value, 🟡 Versatile",
            "Weight (g)": "795",
            "Why This Over Alternatives?": "Provides a longer reach compared to the Z 24-70mm f/4 S at a similar price, although with a variable aperture.",
            "product_link": "https://www.mpb.com/product/tamron-35-150mm-f-2-8-4-di-iii-vxd-for-nikon-z",
        },
        {
            "Budget": "Low",
            "Focal Length": "85mm",
            "Lens": "Nikon NIKKOR Z 85mm f/1.8 S",
            "Max Aperture": "f/1.8",
            "Purpose/Genres": "Portrait, Events",
            "Reasoning": "A compact and sharp prime lens, ideal for portraits with beautiful bokeh.",
            "Stabilized": "No",
            "Tags": "🟢 Best Value, 🟡 Compact",
            "Weight (g)": "470",
            "Why This Over Alternatives?": "Significantly sharper and faster than the 80-200mm f/2.8 at a similar focal length, while also being more affordable.",
            "product_link": "https://www.mpb.com/product/nikon-nikkor-z-85mm-f-1-8-s",
        },
        {
            "Budget": "Mid",
            "Focal Length": "70-200mm",
            "Lens": "Nikon NIKKOR Z 70-200mm f/2.8 VR S",
            "Max Aperture": "f/2.8",
            "Purpose/Genres": "Portrait, Sports, Wildlife",
            "Reasoning": "A professional-grade telephoto zoom lens with excellent image quality and fast aperture.",
            "Stabilized": "Yes",
            "Tags": "🔴 Pro Level, 🟡 Versatile",
            "Weight (g)": "1360",
            "Why This Over Alternatives?": "Significantly sharper and with better build quality than the older 80-200mm f/2.8, and adds vibration reduction.",
            "product_link": "https://www.mpb.com/product/nikon-nikkor-z-70-200mm-f-2-8-vr-s",
        },
        {
            "Budget": "Mid",
            "Focal Length": "24-70mm",
            "Lens": "Sigma 24-70mm f/2.8 DG DN Art for Nikon Z",
            "Max Aperture": "f/2.8",
            "Purpose/Genres": "Wedding, Events, Landscape",
            "Reasoning": "A great alternative 24-70mm lens for the Nikon Z system that is incredibly sharp.",
            "Stabilized": "No",
            "Tags": "🟡 Versatile, 🟢 Best Value",
            "Weight (g)": "835",
            "Why This Over Alternatives?": "A faster and more versatile option than the Z 24-70mm f/4 S, though larger and lacks stabilization.",
            "product_link": "https://www.mpb.com/product/sigma-24-70mm-f-2-8-dg-dn-art-for-nikon-z",
        },
        {
            "Budget": "High",
            "Focal Length": "50mm",
            "Lens": "Nikon NIKKOR Z 50mm f/1.2 S",
            "Max Aperture": "f/1.2",
            "Purpose/Genres": "Portrait, Low Light",
            "Reasoning": "An extremely fast prime lens with exceptional sharpness and beautiful bokeh.",
            "Stabilized": "No",
            "Tags": "🔴 Pro Level, 🟡 High Performance",
            "Weight (g)": "1090",
            "Why This Over Alternatives?": "Offers a significant improvement in low-light performance and bokeh compared to the Z 50mm f/1.8 S, though much larger and heavier.",
            "product_link": "https://www.mpb.com/product/nikon-nikkor-z-50mm-f-1-2-s",
        },
        {
            "Budget": "High",
            "Focal Length": "100-400mm",
            "Lens": "Nikon NIKKOR Z 100-400mm f/4.5-5.6 VR S",
            "Max Aperture": "f/4.5-5.6",
            "Purpose/Genres": "Wildlife, Sports",
            "Reasoning": "A versatile telephoto zoom lens with excellent image quality and vibration reduction.",
            "Stabilized": "Yes",
            "Tags": "🔴 Pro Level, 🟡 Versatile",
            "Weight (g)": "1355",
            "Why This Over Alternatives?": "Provides a much longer reach than the Z 70-200mm f/2.8 VR S, making it ideal for wildlife and sports photography.",
            "product_link": "https://www.mpb.com/product/nikon-nikkor-z-100-400mm-f-4-5-5-6-vr-s",
        },
    ]
