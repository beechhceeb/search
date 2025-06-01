from search.dataset import Dataset
from search.config import (
    BQ_PROJECT_ID,
    BQ_DATASET_ID,
    BQ_DAW_DATASET_ID,
    BQ_SQL_FOLDER,
    QUERY_FILE,
    RAW_DB_SAVE_PATH,
    PROD_DB_SAVE_PATH,
    RESULTS_SAVE_PATH,
    RELOAD,
    MARKET,
)
from dsci_utilities import BQHelper
from search.config import log
from search.pipeline import build_pipeline
from search.matchers import FuzzyMatcher, SemanticMatcher, ExactMatcher, PopularMatcher
from search.transformers import SentenceTransformerWrapper
from search.engine import SearchEngine
from tqdm import tqdm
import os
import pandas as pd

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
model = SentenceTransformerWrapper(model_name="all-MiniLM-L6-v2")

# Try to load from PROD_DB_SAVE_PATH first for speed
if os.path.exists(PROD_DB_SAVE_PATH):
    log.info(f"Loading processed dataset from Parquet: {PROD_DB_SAVE_PATH}")
    df = pd.read_parquet(PROD_DB_SAVE_PATH)
    dataset = Dataset(QUERY_FILE, bq, RAW_DB_SAVE_PATH, market=MARKET)
    dataset._df = df  # Directly set the DataFrame
else:
    dataset = Dataset(QUERY_FILE, bq, RAW_DB_SAVE_PATH, market=MARKET)
    dataset.load(reload=RELOAD)
    dataset.write(overwrite=True)
    dataset.summary()
    dataset.prepare(pipeline=build_pipeline(model=model))
    dataset.summary()
    dataset.write(save_path=PROD_DB_SAVE_PATH, overwrite=True)
    log.info("Dataset processing completed successfully.")

# Instantiate matchers with df at init
fuzzy_model = FuzzyMatcher(column="model_name", df=dataset.df)
fuzzy_brand = FuzzyMatcher(column="brand", df=dataset.df)
fuzzy_blob = FuzzyMatcher(column="blob", df=dataset.df)
semantic_model = SemanticMatcher(
    embedding_column="model_name_embedding",
    encoder=model,
    df=dataset.df,
)
semantic_blob = SemanticMatcher(
    embedding_column="blob_embedding",
    encoder=model,
    df=dataset.df,
)
exact_model = ExactMatcher(column="model_name", df=dataset.df)
exact_blob = ExactMatcher(column="blob", df=dataset.df)
popular = PopularMatcher(
    popularity_column="count_of_buy_products",
    df=dataset.df,
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

query = "Canon  5D  IV"
log.info(f"Searching for query: '{query}'")
for i in tqdm(range(1), desc="Searching", unit="query"):
    results = search_engine.search_multi(
        query, matcher_weights=matcher_weights, top_k=10
    )
results.drop(columns=["model_name_embedding", "blob_embedding"], inplace=True, errors='ignore')
results.to_csv(RESULTS_SAVE_PATH, index=False)
