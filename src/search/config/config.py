import re

from search.enums.enums import CameraType, MountType, SensorSize
from albatross.models.photographer_classification import PhotographerClassification

HIGH_ISO_LIMIT: int = 6400
PERCENTAGE_LIMIT_FOR_HIGH_ISO: int = 30
PERCENTAGE_LIMIT_FOR_WIDE_APERTURE: int = 30

BRIGHT_APERTURE_CUTOFF: int = 4

WIDE_ANGLE_FOCAL_RANGE: range = range(0, 39)
NORMAL_FOCAL_RANGE: range = range(40, 69)
TELEPHOTO_FOCAL_RANGE: range = range(70, 2000)

SENSOR_CROP_FACTOR: dict[SensorSize, float] = {
    SensorSize.FULL_FRAME: 1,
    SensorSize.APSC: 1.5,
    SensorSize.CANON_APSC: 1.6,
    SensorSize.MEDIUM_FORMAT: 0.79,
    SensorSize.FOUR_THIRDS: 2,
    SensorSize.ONE_INCH: 2.7,
    SensorSize.TWO_THIRDS: 3.9,
    SensorSize.ONE_OVER_TWO_POINT_THREE: 5.6,
}

BRANDS = [
    "nikon",
    "canon",
    "sony",
    "fujifilm",
    "panasonic",
    "leica",
    "olympus",
    "om",
    "pentax",
]

CAMERA_TYPES_WITHOUT_MOUNT = [
    CameraType.COMPACT,
    CameraType.ACTION,
]

MAP_BRAND_TYPE_MOUNT: dict[str, dict[CameraType, dict[SensorSize, MountType]]] = {
    "nikon": {
        CameraType.DSLR: {
            SensorSize.APSC: MountType.F,
            SensorSize.FULL_FRAME: MountType.F,
        },
        CameraType.MIRRORLESS: {
            SensorSize.FULL_FRAME: MountType.Z,
            SensorSize.ONE_INCH: MountType.NIKON_1,
        },
    },
    "canon": {
        CameraType.DSLR: {
            SensorSize.CANON_APSC: MountType.EF_S,
            SensorSize.FULL_FRAME: MountType.EF,
        },
        CameraType.MIRRORLESS: {
            SensorSize.CANON_APSC: MountType.RF_S,
            SensorSize.FULL_FRAME: MountType.RF,
        },
    },
    "olympus": {
        CameraType.DSLR: {SensorSize.FOUR_THIRDS: MountType.FOUR_THIRDS},
        CameraType.MIRRORLESS: {SensorSize.FOUR_THIRDS: MountType.M43},
    },
    "sony": {
        CameraType.DSLR: {
            SensorSize.APSC: MountType.A,
            SensorSize.FULL_FRAME: MountType.A,
        },
        CameraType.MIRRORLESS: {
            SensorSize.APSC: MountType.E,
            SensorSize.FULL_FRAME: MountType.FE,
        },
    },
    "hasselblad": {
        CameraType.DSLR: {SensorSize.MEDIUM_FORMAT: MountType.HCD},
        CameraType.MIRRORLESS: {SensorSize.MEDIUM_FORMAT: MountType.XCD},
    },
    "pentax": {
        CameraType.DSLR: {
            SensorSize.APSC: MountType.K,
            SensorSize.FULL_FRAME: MountType.K,
            SensorSize.MEDIUM_FORMAT: MountType.PENTAX_645,
        },
    },
    "leica": {
        CameraType.MIRRORLESS: {
            SensorSize.FULL_FRAME: MountType.L,
            SensorSize.APSC: MountType.TL,
        },
        CameraType.RANGEFINDER: {
            SensorSize.FULL_FRAME: MountType.M,
        },
    },
    "fujifilm": {
        CameraType.MIRRORLESS: {
            SensorSize.APSC: MountType.X,
            SensorSize.MEDIUM_FORMAT: MountType.G,
        }
    },
    "panasonic": {
        CameraType.DSLR: {
            SensorSize.FOUR_THIRDS: MountType.M43,
            SensorSize.FULL_FRAME: MountType.L,
        }
    },
    "gopro": {
        CameraType.ACTION: {
            SensorSize.ONE_OVER_TWO_POINT_THREE: MountType.NONE,
        }
    },
}

MAP_BRAND_MODEL_TO_SENSOR_SIZE: dict[str, list[tuple[re.Pattern[str], SensorSize]]] = {
    "canon": [
        (re.compile(r"EOS R[3-9]?\b", re.IGNORECASE), SensorSize.FULL_FRAME),
        (re.compile(r"EOS RP\b", re.IGNORECASE), SensorSize.FULL_FRAME),
        (
            re.compile(
                r"EOS[ -_][0-6]{1}D(x|s| X| S)?[ -_]?(Mark|MK)?[ -_]?(I{1,3}|IV|V)?\b",
                re.IGNORECASE,
            ),
            SensorSize.FULL_FRAME,
        ),
        (re.compile(r"EOS M\d+", re.IGNORECASE), SensorSize.CANON_APSC),
        (re.compile(r"EOS [0-9]{3,4}D", re.IGNORECASE), SensorSize.CANON_APSC),
    ],
    "nikon": [
        (re.compile(r"Z [5-9]", re.IGNORECASE), SensorSize.FULL_FRAME),
        (re.compile(r"Z 50|Z fc|Z 30", re.IGNORECASE), SensorSize.APSC),
        (
            re.compile(
                r"D(?:1(?:s|x)?|4s?|5|6|600|610|700|750|780|800|810|850)\b",
                re.IGNORECASE,
            ),
            SensorSize.FULL_FRAME,
        ),
        (re.compile(r"D[3-9][0-9][0-9]?[s]?", re.IGNORECASE), SensorSize.APSC),
        # Nikon 1
        (re.compile(r"1.?[a-zA-Z](w|W)?[1-4]", re.IGNORECASE), SensorSize.ONE_INCH),
    ],
    "sony": [
        (re.compile(r"A[789]\b", re.IGNORECASE), SensorSize.FULL_FRAME),
        (re.compile(r"A6[0-9]{2}", re.IGNORECASE), SensorSize.APSC),
        (re.compile(r"RX10|RX100", re.IGNORECASE), SensorSize.ONE_INCH),
    ],
    "fujifilm": [
        (re.compile(r"GFX", re.IGNORECASE), SensorSize.MEDIUM_FORMAT),
        (re.compile(r"X[ATPH][\d]+", re.IGNORECASE), SensorSize.APSC),
    ],
    "panasonic": [
        (re.compile(r"S[1-9]", re.IGNORECASE), SensorSize.FULL_FRAME),
        (re.compile(r"G[0-9]+", re.IGNORECASE), SensorSize.FOUR_THIRDS),
        (re.compile(r"GH[0-9]+", re.IGNORECASE), SensorSize.FOUR_THIRDS),
    ],
    "olympus": [
        (re.compile(r"E-M1|E-M5|E-M10|PEN", re.IGNORECASE), SensorSize.FOUR_THIRDS),
    ],
    "leica": [
        (re.compile(r"SL2|M10|Q2", re.IGNORECASE), SensorSize.FULL_FRAME),
        (re.compile(r"TL2|CL", re.IGNORECASE), SensorSize.APSC),
    ],
    "ricoh": [
        (re.compile(r"GR III\b", re.IGNORECASE), SensorSize.APSC),
    ],
}

## Camera classification patterns
# DSLR Keywords (can be expanded)
DSLR_PATTERNS = [
    "d[0-9]{3}",
    "d[0-9]{4}",
    "d[0-9]x",
    "d[0-9]h",  # Nikon D series,  Canon EOS like 5D, 6D etc
    "eos[ -_]?[0-9]+d[ -_]?(?:mark[ -_]?(i{1,3}|iv|v|vi|vii))?",
    "eos rebel",  # Canon EOS
    "alpha [0-9][0-9]*",  # Sony Alpha
    "k-[0-9][0-9]*",  # Pentax K series
    "sigma sd",
]

# Mirrorless Keywords (can be expanded)
MIRRORLESS_PATTERNS = [
    "z[0-9]+",
    "z [0-9]+",  # Nikon Z series
    "e[0-9]+",
    "eos r[0-9]+",
    "nex",
    "a[0-9][0-9]*",  # Sony E mount, NEX (older)
    "x[0-9][0-9]*",
    "x-t[0-9][0-9]*",
    "x-e[0-9][0-9]*",
    "x-pro[0-9][0-9]*",  # Fuji X series
    "m[0-9]+",
    "om-[0-9]",
    "dc-g[0-9]+",  # Panasonic Lumix G
    "dc-gh[0-9]+",
    "gx[0-9]+",
    "dc-s",
    "eos m[0-9]+",  # Canon EOS M
    "gf[0-9]+",  # Panasonic GF
    "pen-f",  # Olympus Pen F
    "leica q",
    "sigma fp",
    "sigma bf",
    "nikon 1",  # Nikon 1 series
]

# Compact Keywords (can be expanded)
COMPACT_PATTERNS = [
    "powershot",
    "coolpix",
    "cyber-shot",
    "lumix",
    "stylus",
    "finepix",
    "ixus",
    "elph",
    # Common compact lines
    "rx[0-9][0-9]*",
    # Sony RX series (some are high-end but generally considered compact style)
    "g[0-9][0-9]*",  # Canon G series
    "lx[0-9][0-9]*",  # Panasonic LX
    "sigma dp",
]

PHONE_PATTERNS = [
    "samsung",
    "iphone",
    "pixel",
    "nothing",
    "lg",
]
##

SONY_CAMERA_INTERNAL_MODEL_TO_PUBLIC = {
    # A1 Series
    "ilce-1": "A1",
    "ilce-1m2": "A1 II",
    # A7 Series
    "ilce-7": "A7",
    "ilce-7m2": "A7 II",
    "ilce-7m3": "A7 III",
    "ilce-7r": "A7R",
    "ilce-7rm2": "A7R II",
    "ilce-7rm3": "A7R III",
    "ilce-7rm4": "A7R IV",
    "ilce-7s": "A7S",
    "ilce-7sm2": "A7S II",
    "ilce-7c": "A7C",
    "ilce-7cr": "A7CR",
    # A9 Series
    "ilce-9": "A9",
    "ilce-9m2": "A9 II",
    "ilce-9m3": "A9 III",
    # A6000 Series
    "ilce-6000": "A6000",
    "ilce-6100": "A6100",
    "ilce-6300": "A6300",
    "ilce-6400": "A6400",
    "ilce-6500": "A6500",
    "ilce-6600": "A6600",
    # A5000 Series
    "ilce-5000": "A5000",
    "ilce-5100": "A5100",
    # A3000 Series
    "ilce-3000": "A3000",
    # Alpha A-mount Series
    "ilca-68": "Alpha 68",
    "ilca-77m2": "Alpha 77 II",
    # RX Series
    "dsc-rx0": "RX0",
    "dsc-rx0m2": "RX0 II",
    "dsc-rx1": "RX1",
    "dsc-rx1r": "RX1R",
    "dsc-rx1rm2": "RX1R II",
    "dsc-rx10": "RX10",
    "dsc-rx10m2": "RX10 II",
    "dsc-rx10m3": "RX10 III",
    "dsc-rx10m4": "RX10 IV",
    "dsc-rx100": "RX100",
    "dsc-rx100m2": "RX100 II",
    "dsc-rx100m3": "RX100 III",
    "dsc-rx100m4": "RX100 IV",
    "dsc-rx100m5": "RX100 V",
    "dsc-rx100m5a": "RX100 VA",
    "dsc-rx100m6": "RX100 VI",
    "dsc-rx100m7": "RX100 VII",
    # ZV Series
    "zv-1": "ZV-1",
    "zv-1f": "ZV-1F",
    "zv-e10": "ZV-E10",
}

SENSOR_EV_CORRECTIONS: dict[SensorSize, int] = {
    SensorSize.FULL_FRAME: 0,
    SensorSize.APSC: -1,
    SensorSize.FOUR_THIRDS: -2,
    SensorSize.ONE_INCH: -3,
    SensorSize.MEDIUM_FORMAT: 1,
}

# calculated with this formula: [round((2 ** (i / 6)),1) for i in range(0,30)]
# and then manually setting 5.7 -> 5.6. this gives third step increments
APERTURES_IN_THIRD_STEPS: list[float] = [
    0.7,
    0.95,
    1.0,
    1.1,
    1.2,
    1.4,
    # 1.6,
    1.8,
    2.0,
    2.2,
    2.5,
    2.8,
    3.2,
    3.6,
    4.0,
    4.5,
    5.0,
    5.6,
    6.3,
    7.1,
    8.0,
    9.0,
    10.1,
    11.3,
    12.7,
    14.3,
    16.0,
    18.0,
    20.2,
    22.6,
    25.4,
    28.5,
]

COMMON_LENS_MAX_APERTURES: list[float] = [
    1.0,
    1.2,
    1.4,
    1.8,
    2.8,
    4.0,
    5.6,
    8.0,
    11,
    16.0,
]

COMMON_FOCAL_LENGTHS: list[int] = [20, 24, 28, 35, 40, 50, 85, 105, 135, 200, 300, 400]

COMMON_SHUTTER_SPEEDS_BELOW_1: dict[float, str] = {
    1 / 8000: "1/8000",
    1 / 4000: "1/4000",
    1 / 2000: "1/2000",
    1 / 1000: "1/1000",
    1 / 500: "1/500",
    1 / 250: "1/250",
    1 / 125: "1/125",
    1 / 60: "1/60",
    1 / 30: "1/30",
    1 / 15: "1/15",
    1 / 8: "1/8",
    1 / 4: "1/4",
    1 / 2: "1/2",
}

PHOTOGRAPHER_CLASSIFICATIONS: dict[str, PhotographerClassification] = {
    "The Bokeh Master": PhotographerClassification(
        name="The Bokeh Master",
        description="Shoots wide open often",
        blurb="Shallow depth is your love language. You crave dreamy backgrounds"
        " and subject isolation.",
        score=0,
        styling={
            "icon": "bi-fire",
            "colour_1": "#e83e8c",
            "colour_2": "#8c3ee8",
            "colour_3": "#3ee89c",
        },
        lesson="""Your love of shallow depth of field gives your images a dreamy, artistic feel; but relying on it too often can become a creative comfort zone. Shooting wide open isolates your subject beautifully, yet it can also limit storytelling through background context and compositional variety.
            for the next week, shoot exclusively at apertures of f/5.6 or narrower. It might feel restrictive at first, but you'll begin to see the environment in new ways; discovering new layers, framing opportunities, and story elements in your scenes.""",  # noqa: E501
        video_title="This video encourages photographers to challenge traditional composition rules, including the overuse of shallow depth of field, promoting a broader storytelling perspective.",  # noqa: E501
        video_url="https://www.youtube.com/embed/OIpe3KgeqOo?si=qUCEs7-qQhVrRJmI",
    ),
    "The Sniper": PhotographerClassification(
        name="The Sniper",
        description="Shoots at max zoom a lot",
        blurb="You keep your distance. Whether it’s wildlife or candids,"
        " you shoot from the shadows.",
        score=0,
        styling={
            "icon": "bi-crosshair",
            "colour_1": "#0d6efd",
            "colour_2": "#fd0d6e",
            "colour_3": "#6efd0d",
        },
        lesson="""Your ability to capture fleeting moments from a distance is impressive; you know how to stay invisible and strike when the time is right. But always shooting long can disconnect your viewer from the intimacy of a scene and flatten its emotional weight.
            spend the next few outings shooting exclusively at 35mm or wider. Get physically closer, engage more with your subjects, and see how proximity changes the emotion and energy in your work.""",  # noqa: E501
        video_url="https://www.youtube.com/embed/2wMDrU4bLuY?si=lmDalQ0gxwyN0gEL",
        video_title="This 24-hour street photography challenge emphasizes the use of wider lenses and close engagement with subjects, fostering a more immersive shooting experience. ",  # noqa: E501
    ),
    "The Wanderer": PhotographerClassification(
        name="The Wanderer",
        description="Big spread of focal lengths, frequent zoom use",
        blurb="Your lens cap rarely stays on. You explore all kinds of scenes, "
        "from wide landscapes to tight details.",
        score=0,
        styling={
            "icon": "bi-compass",
            "colour_1": "#20c997",
            "colour_2": "#c92053",
            "colour_3": "#2046c9",
        },
        lesson="""You're a visual explorer, comfortable in any terrain; from wide landscapes to macro detail. That versatility is a huge strength, but it can also keep you from truly mastering any one perspective or style.
            pick one focal length and stick with it for a full week. Force yourself to adapt, frame, and compose with constraints; you might be surprised how much creativity thrives within them.""",  # noqa: E501
        video_url="https://www.youtube.com/embed/pV3IuPlFGng?si=8rU5EY4Gbl3FGzmk",
        video_title="This tutorial focuses on essential composition techniques, encouraging photographers to refine their skills by limiting their gear choices.",  # noqa: E501
    ),
    "The Studio Shooter": PhotographerClassification(
        name="The Studio Shooter",
        description="Low ISO, fast shutter, consistent settings",
        blurb="Controlled. Consistent. Intentional. You probably own a tripod.",
        score=0,
        styling={
            "icon": "bi-lightbulb",
            "colour_1": "#fd7e14",
            "colour_2": "#147efd",
            "colour_3": "#14fd7e",
        },
        lesson="""Your consistency and control show real technical skill; you know how to create exactly what you envision. But when every shot is deliberate, you may miss the raw, unexpected moments that come from improvisation.
            leave the tripod and strobes behind for a day and shoot handheld in natural light. Let go of control and allow spontaneity to shape your images.""",  # noqa: E501
        video_url="https://www.youtube.com/embed/nqqmudb747c?si=F5DYG1H9QmeSRTnn",
        video_title="While centered on studio photography, this masterclass offers insights into creative approaches that can be adapted to natural light settings.",  # noqa: E501
    ),
    "The Minimalist": PhotographerClassification(
        name="The Minimalist",
        description="Few lenses, high usage concentration",
        blurb="One camera, one lens; and you make it work like a pro.",
        score=30,
        styling={
            "icon": "bi-slash",
            "colour_1": "#6c757d",
            "colour_2": "#7d6c75",
            "colour_3": "#756c7d",
        },
        lesson="""You’ve made simplicity a superpower; mastering your gear inside and out. But sticking with just one tool all the time can limit experimentation and make your vision predictable.
            borrow or rent a lens that’s outside your usual comfort zone. A fisheye, a tilt-shift, or even a vintage manual lens; anything that makes you think differently about composition.""",  # noqa: E501
        video_url="https://www.youtube.com/embed/X-vF-k-9q6Q?si=O01AGt6EVg6C-p2v",
        video_title="This video explores macro photography gear, encouraging minimalists to try specialized lenses for new perspectives.",  # noqa: E501
    ),
    "The Collector": PhotographerClassification(
        name="The Collector",
        description="Owns lots of gear, minimal usage spread",
        blurb="You love gear almost as much as photos. Every lens has a story; even if"
        " you only use two.",
        score=0,
        styling={
            "icon": "bi-boxes",
            "colour_1": "#6f42c1",
            "colour_2": "#c16f42",
            "colour_3": "#42c16f",
        },
        lesson="""You’ve got an enviable collection; and you know exactly what each piece can do. But if most of it stays on the shelf, it might be holding you back more than helping you move forward.
            pick one lens you rarely use and commit to shooting with it for a week. No matter how weird or awkward it feels, let it lead you somewhere new.""",  # noqa: E501
        video_url="https://www.youtube.com/embed/CA2bWswN5wc?si=htyKqr_T6MJ9_IRb",
        video_title="This video discusses the value of exploring different equipment, inspiring collectors to make the most of their gear collection.",  # noqa: E501
    ),
    "The Vampire": PhotographerClassification(
        name="The Vampire",
        description="High ISO, moderate shutter speed",
        blurb="You embrace the darkness, emerging to hunt at night or at least "
        "in places hidden away from the sun. ",
        score=0,
        styling={
            "icon": "bi-moon-stars",
            "colour_1": "#A12529",
            "colour_2": "#25A1A1",
            "colour_3": "#A17F25",
        },
        lesson="""You thrive in low light, capturing mood and atmosphere others miss entirely. But darkness can become a stylistic safety net, masking composition issues with shadows and grain.
            shoot in broad daylight for a few sessions. Embrace harsh light and deep contrast; push yourself to find drama in brightness instead of darkness.""",  # noqa: E501
        video_url="https://www.youtube.com/embed/ALrg388HPcs?si=By0KVe0PXshDzMGm",
        video_title="This tutorial provides guidance on capturing compelling images in daylight, challenging nocturnal photographers to adapt to brighter environments.",  # noqa: E501
    ),
    "The Stargazer": PhotographerClassification(
        name="The Stargazer",
        description="High ISO, slow shutter speed",
        blurb="You love the night sky. You’re a master at long exposures, "
        "capturing the stars in all their glory.",
        score=0,
        styling={
            "icon": "bi-stars",
            "colour_1": "#212529",
            "colour_2": "#292521",
            "colour_3": "#252921",
        },
        lesson="""Your night skies are mesmerizing; you turn slow shutter and high ISO into visual poetry. But those long exposures can make you dependent on static subjects and familiar setups.
            shoot fast-moving subjects with limited light; handheld street photography at dusk, for example. Explore storytelling in low light without leaning on long exposures.""",  # noqa: E501
        video_url="https://www.youtube.com/embed/693Hq-eoiNY?si=K5_RtcPXV3APWgYp",
        video_title="This video delves into techniques for photographing dynamic subjects in challenging lighting, offering insights applicable to stargazers seeking to diversify their skills.",  # noqa: E501
    ),
    "The Monk": PhotographerClassification(
        name="The Monk",
        description="Low ISO, slow shutter speed",
        blurb="You take your time. You’re patient and deliberate, "
        "waiting for the perfect moment to capture.",
        score=0,
        styling={
            "icon": "bi-hourglass-split",
            "colour_1": "#0dcaf0",
            "colour_2": "#f00dca",
            "colour_3": "#caf00d",
        },
        lesson="""Your patience is remarkable; you wait for just the right moment and capture it with precision. But always working slowly can mean missing spontaneous, imperfect beauty.
            spend a day shooting in burst mode, reacting quickly and embracing imperfection. Let your instincts guide you instead of your planning.""",  # noqa: E501
        video_url="https://www.youtube.com/embed/2wMDrU4bLuY?si=lmDalQ0gxwyN0gEL",
        video_title="This challenge encourages photographers to capture candid moments, fostering a more reactive shooting style.",  # noqa: E501
    ),
    "The Quickdraw": PhotographerClassification(
        name="The Quickdraw",
        description="High ISO, fast shutter speed",
        blurb="Birds? Cars? Athletes? Whatever you're shooting, it moves FAST. You "
        "need quick reactions to keep up with your quarry.",
        score=0,
        styling={
            "icon": "bi-speedometer",
            "colour_1": "#198754",
            "colour_2": "#875419",
            "colour_3": "#541987",
        },
        lesson="""You live in the moment, ready to capture action in a split second. But speed can come at the cost of depth; sometimes the story lives in the stillness between the movement.
            slow down and shoot static subjects. Try architectural details, portraits, or still life. Discover what storytelling looks like when everything stands still.""",  # noqa: E501
        video_url="https://www.youtube.com/embed/pV3IuPlFGng?si=8rU5EY4Gbl3FGzmk",
        video_title="This tutorial emphasizes thoughtful composition, guiding quickdraw photographers to appreciate the depth in stillness.",  # noqa: E501
    ),
    "The Professional": PhotographerClassification(
        name="The Professional",
        description="Owns lots of gear, uses it all",
        blurb="Someone's paying you to shoot, aren't they? You know your gear inside "
        "and out, and you use it all.",
        score=0,
        styling={
            "icon": "bi-cash-stack",
            "colour_1": "#003366",
            "colour_2": "#660033",
            "colour_3": "#336600",
        },
        lesson="""You know your gear, your workflow, and your craft; your results are reliable and polished. But sometimes, consistency can stifle creativity and lead to burnout or repetition.
            take on a personal project with no client and no expectations. Let go of perfection and shoot purely for fun; rediscover why you started.""",  # noqa: E501
        video_url="https://www.youtube.com/embed/OIpe3KgeqOo?si=qUCEs7-qQhVrRJmI",
        video_title="This video encourages professionals to break free from routine by experimenting with unconventional techniques.",  # noqa: E501
    ),
    "The Stranger": PhotographerClassification(
        name="The Stranger",
        description="Unrecognizable camera and lens",
        blurb="You like to keep people guessing. Your camera and lens are a mystery to "
        "everyone (well, to me at least.)",
        score=0,
        styling={
            "icon": "bi-question-circle",
            "colour_1": "#000000",
            "colour_2": "#333333",
            "colour_3": "#666666",
        },
        lesson="""I can't really offer you too much advice on how to improve as a photographer without more data from your pictures.
            If you'd like me to help you improve as a photographer, I'd suggest you look at your current workflow to see if you can work out why your pictures don't have embedded EXIF data. It could be that you downloaded your pictures from an online service that has stripped the metadata from your pictures.""",  # noqa: E501
        video_url="https://www.youtube.com/embed/bN2jqsJgbBs?si=udZz0VC0eJ67BTmb",
        video_title="This video will teach you how to use lightroom, a popular photo editing software, to edit your photos and improve your photography skills.",  # noqa: E501
    ),
}

INITIAL_LUMINANCE_VALUES: dict[str, dict[str, float]] = {
    "Deep Sky / Dark Skies": {"instances": 0, "percentage": 0, "boundary": 0.001},
    "Astro Night": {"instances": 0, "percentage": 0, "boundary": 0.01},
    "Bright Night": {"instances": 0, "percentage": 0, "boundary": 0.1},
    "Night / Twilight": {"instances": 0, "percentage": 0, "boundary": 10},
    "Dim Indoors / Blue Hour": {"instances": 0, "percentage": 0, "boundary": 100},
    "Indoor Lighting": {"instances": 0, "percentage": 0, "boundary": 1000},
    "Overcast Day": {"instances": 0, "percentage": 0, "boundary": 10_000},
    "Bright Daylight": {"instances": 0, "percentage": 0, "boundary": 100_000},
    "Extreme Light": {"instances": 0, "percentage": 0, "boundary": float("inf")},
}
