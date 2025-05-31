import logging
import os

try:  # pragma: no cover - optional dependency
    from dotenv import load_dotenv

    load_dotenv()
except ModuleNotFoundError:  # pragma: no cover - handle missing dependency
    pass

# Set up logging configuration before we import other modules
logging.basicConfig(
    level="DEBUG" if os.getenv("DEBUG", False) else "INFO",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)

log = logging.getLogger(__name__)

from .classifier import *  # noqa: F403 E402
from .exif import *  # noqa: F403 E402
from .llm import *  # noqa: F403 E402
from .service import *  # noqa: F403 E402
