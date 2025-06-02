from typing import Callable
import pandas as pd
import logging
from .transforms import (
    normalise,
    drop_na,
    blob,
    remove_stopwords,
    remove_duplicates,
    log_normalise,
)
from .transformers import SentenceTransformerWrapper
from config.settings import SCHEMA_COLUMNS, TEXT_COLUMNS, NOISE_WORDS

log = logging.getLogger(__name__)


class Pipeline:
    """
    Base pipeline for chaining DataFrame transformations.
    Each step is a (function, kwargs) tuple.
    """

    def __init__(self, steps: list = None):
        self.steps = steps or []

    def add_step(self, func: Callable, **kwargs):
        log.info(f"Adding step: {func.__name__} with kwargs: {kwargs}")
        self.steps.append((func, kwargs))
        return self

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        log.info(f"Running pipeline with {len(self.steps)} steps.")
        for i, (func, kwargs) in enumerate(self.steps):
            log.info(f"Step {i + 1}/{len(self.steps)}: {func.__name__}")
            df = func(df, **kwargs)
        log.info("Pipeline run complete.")
        return df


def build_pipeline(model: SentenceTransformerWrapper) -> Pipeline:
    """
    Build and return the default search pipeline.
    """
    pipeline = Pipeline()
    pipeline.add_step(drop_na, columns=SCHEMA_COLUMNS)
    pipeline.add_step(remove_stopwords, columns=TEXT_COLUMNS, stopwords=NOISE_WORDS)
    pipeline.add_step(normalise, columns=TEXT_COLUMNS)
    pipeline.add_step(blob, columns_to_blob=TEXT_COLUMNS, blob_column="blob")
    pipeline.add_step(remove_duplicates, columns=["blob"])
    pipeline.add_step(model.embed_columns, columns=["model_name", "blob"])
    pipeline.add_step(log_normalise, columns=["count_of_buy_products"])
    return pipeline
