import os
import logging
import pandas as pd
from dsci_utilities import BQHelper
from config.settings import Market, LIMIT
from .pipeline import Pipeline

log = logging.getLogger(__name__)


class Dataset:
    """
    Handles loading, saving, and summarizing datasets from BigQuery or CSV files.
    """

    def __init__(
        self,
        query_file: str,
        bq_helper: BQHelper,
        save_path: str,
        market: Market,
    ):
        self.query_file = query_file
        self.bq_helper = bq_helper
        self._df: pd.DataFrame | None = None
        self.save_path = save_path
        self.market = market

    @property
    def df(self) -> pd.DataFrame:
        if self._df is None:
            raise ValueError("DataFrame is not loaded. Call load() first.")
        return self._df

    def load(self, reload: bool = False) -> pd.DataFrame:
        """
        Loads the dataset from a CSV file if it exists, otherwise queries BigQuery.
        """
        if self.save_path and os.path.exists(self.save_path) and not reload:
            log.info(f"Loading dataset from CSV: {self.save_path}")
            self._df = pd.read_parquet(self.save_path)
        else:
            if not self.bq_helper:
                raise ValueError(
                    "bq_helper must be provided to load data from BigQuery."
                )
            log.info(f"Querying BigQuery using file: {self.query_file}")
            df = self.bq_helper.get(self.query_file)
            self._df = df[df["market"] == self.market.value][:LIMIT].reset_index(
                drop=True
            )
        log.info(f"Dataset loaded with shape: {self._df.shape}")
        return self._df

    def write(self, overwrite: bool = False, save_path: str = None) -> None:
        """
        Writes the loaded DataFrame to a CSV file.
        """
        if self._df is None:
            raise ValueError("DataFrame is not loaded. Call load() first.")

        path = save_path or self.save_path
        if not path:
            raise ValueError("Save path is not specified.")

        if os.path.exists(path) and not overwrite:
            raise FileExistsError(
                f"File {path} already exists. Use overwrite=True to replace it."
            )

        os.makedirs(os.path.dirname(path), exist_ok=True)
        log.info(f"Writing DataFrame to CSV: {path}")
        self._df.to_parquet(path, index=False)
        log.info(f"Write complete: {path}")

    def summary(self) -> pd.DataFrame:
        """
        Returns a statistical summary of the loaded DataFrame and logs key info.
        """
        if self._df is None:
            raise ValueError("DataFrame is not loaded. Call load() first.")
        cols_to_drop = [col for col in self._df.columns if col.endswith("_embedding")]
        summary_df = self._df.describe(include="all").drop(columns=cols_to_drop)
        log.info(f"Summary generated for DataFrame with shape: {self._df.shape}")
        log.info(f"Summary columns: {list(summary_df.columns)}")
        log.info(
            f"Summary preview (excluding embeddings):\n{summary_df.head().to_string()}"
        )
        return summary_df

    def prepare(self, pipeline: Pipeline) -> pd.DataFrame:
        self._df = pipeline.run(self._df)
