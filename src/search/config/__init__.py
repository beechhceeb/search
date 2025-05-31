import logging
import os
from dotenv import load_dotenv

load_dotenv()


logging.basicConfig(
    level="DEBUG" if os.getenv("DEBUG", False) else "INFO",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)

log = logging.getLogger(__name__)

from .config import *  # noqa: E402, F403
