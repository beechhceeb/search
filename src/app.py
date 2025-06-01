from search.dataset import Dataset
from search.config import (
    BQ_PROJECT_ID,
    BQ_DATASET_ID,
    BQ_DAW_DATASET_ID,
    BQ_SQL_FOLDER,
    QUERY_FILE,
    RAW_DB_SAVE_PATH,
    PROD_DB_SAVE_PATH,
    RELOAD,
    MARKET,
)
from dsci_utilities import BQHelper
from search.config import log
from search.pipeline import build_pipeline
from search.matchers import FuzzyMatcher, SemanticMatcher, ExactMatcher, PopularMatcher
from search.transformers import SentenceTransformerWrapper
from search.engine import SearchEngine

log.info("Starting dataset processing...")

bq = BQHelper(
    billing_project_id=BQ_PROJECT_ID,
    write_project_id=BQ_PROJECT_ID,
    read_project_id=BQ_PROJECT_ID,
    write_dataset=BQ_DATASET_ID,
    read_dataset=BQ_DATASET_ID,
    daw_dataset=BQ_DAW_DATASET_ID,
    sql_folder=BQ_SQL_FOLDER,
)

dataset = Dataset(QUERY_FILE, bq, RAW_DB_SAVE_PATH, market=MARKET)
dataset.load(reload=RELOAD)
dataset.write(overwrite=True)
dataset.summary()
dataset.prepare(pipeline=build_pipeline())
dataset.summary()
dataset.write(save_path=PROD_DB_SAVE_PATH, overwrite=True)

log.info("Dataset processing completed successfully.")

fuzzy_model = FuzzyMatcher(column="model_name")
fuzzy_brand = FuzzyMatcher(column="brand")
fuzzy_blob = FuzzyMatcher(column="blob")
semantic_model = SemanticMatcher(
    embedding_column="model_name_embedding",
    encoder=SentenceTransformerWrapper(model_name="all-MiniLM-L6-v2"),
)
semantic_blob = SemanticMatcher(
    embedding_column="blob_embedding",
    encoder=SentenceTransformerWrapper(model_name="all-MiniLM-L6-v2"),
)
exact_model = ExactMatcher(column="model_name")
exact_blob = ExactMatcher(column="blob")
popular = PopularMatcher(
    popularity_column="count_of_buy_products",
)
search_engine = SearchEngine(
    dataset=dataset,
    matchers={
        "fuzzy_model": fuzzy_model,
        "fuzzy_brand": fuzzy_brand,
        "fuzzy_blob": fuzzy_blob,
        "semantic_model": semantic_model,
        "semantic_blob": semantic_blob,
        "exact_model": exact_model,
        "exact_blob": exact_blob,
        "popular": popular,
    },
)
matcher_weights = {
    "fuzzy_model": 0.5,
    "fuzzy_brand": 0.3,
    "fuzzy_blob": 0.2,
    "semantic_model": 0.4,
    "semantic_blob": 0.4,
    "exact_model": 0.1,
    "exact_blob": 0.1,
    "popular": 0.2,
}

query = "Canon EOS 5D Mark IV"
log.info(f"Searching for query: '{query}'")
results = search_engine.search_multi(query, matcher_weights=matcher_weights, top_k=10)
log.info(
    f"Search results for query '{query}':\n{results[['model_name', 'combined_score']].head(10)}"
)
