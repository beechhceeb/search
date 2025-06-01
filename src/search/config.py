from pathlib import Path
import logging
import os
from dotenv import load_dotenv
from enum import Enum

load_dotenv()


logging.basicConfig(
    level="DEBUG" if os.getenv("DEBUG", False) else "INFO",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)

log = logging.getLogger(__name__)


ROOT = Path(__file__).parent.parent.parent

BQ_PROJECT_ID = "mpb-data-science-dev-ab-602d"
BQ_DATASET_ID = "dsci_pricing_model"
BQ_DAW_DATASET_ID = "dsci_daw"
BQ_SQL_FOLDER = ROOT / "sql"

QUERY_FILE = "get_raw_model_database"
RAW_DB_SAVE_PATH = ROOT / "data" / "db_raw.parquet"
PROD_DB_SAVE_PATH = ROOT / "data" / "db_prod.parquet"
RESULTS_SAVE_PATH = ROOT / "data" / "results.csv"
LIMIT = None
RELOAD = True


SCHEMA_COLUMNS = [
    "model_id",
    "model_name",
    "market",
    "performance_group",
    "count_of_buy_products",
    "primary_category",
    "secondary_category",
    "product_type",
    "product_system",
    "brand",
]

TEXT_COLUMNS = [
    "brand",
    "model_name",
    "primary_category",
    "secondary_category",
    "product_type",
    "product_system",
]

MARKET_COLUMN = "market"

NOISE_WORDS = set(
    [
        "camera",
        "cameras",
        "cam",
        "product",
        "category",
        "brand",
        "family",
    ]
)


class Market(Enum):
    UK = "UK"
    US = "US"
    EU = "EU"


MARKET = Market.UK
