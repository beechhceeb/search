import logging
import numpy as np
import pandas as pd
from .dataset import Dataset

log = logging.getLogger(__name__)


class SearchEngine:
    """
    Search engine system that loads a dataset and supports multiple matching strategies.
    Matcher classes should implement a `match(query: str, df: pd.DataFrame, top_k: int) -> pd.DataFrame` method.
    """

    def __init__(self, dataset: Dataset, matchers: dict, weights: dict = None):
        """
        dataset: a Dataset instance (already loaded)
        matchers: dict of {matcher_name: matcher_instance}
        weights: dict of {matcher_name: float} for weighted search (optional)
        """
        self.dataset = dataset
        self.matchers = matchers
        self.weights = weights or {}

    def search_multi(
        self, query: str, matcher_weights: dict, top_k: int = 10
    ) -> pd.DataFrame:
        """
        Search using multiple matchers and combine results with specified weights.
        matcher_weights: dict of {matcher_name: weight}
        Returns a DataFrame of top results with a combined score.
        """

        log.info(
            f"Multi-matcher search for query: '{query}' with weights: {matcher_weights}"
        )
        n = len(self.dataset.df)
        combined_score = np.zeros(n, dtype=float)
        all_scores = {}
        # Normalize matcher weights to sum to 1
        total_weight = sum(matcher_weights.values())
        if total_weight == 0:
            log.error("Matcher weights sum to zero. Cannot normalize.")
            return pd.DataFrame()
        norm_weights = {k: v / total_weight for k, v in matcher_weights.items()}
        for matcher, weight in norm_weights.items():
            if matcher not in self.matchers:
                log.warning(f"Matcher '{matcher}' not found, skipping.")
                continue
            scores = self.matchers[matcher].match(query)
            if not isinstance(scores, list) or len(scores) != n:
                log.warning(
                    f"Matcher '{matcher}' did not return a valid score list, skipping."
                )
                continue
            all_scores[matcher + "_score"] = np.array(scores)
            combined_score += weight * np.array(scores)
        if np.all(combined_score == 0):
            log.error("No valid matcher results to combine.")
            return pd.DataFrame()
        # Get top_k indices
        top_idx = np.argsort(combined_score)[::-1][:top_k]
        results = self.dataset.df.iloc[top_idx].copy()
        # Add each individual matcher score column
        for col, arr in all_scores.items():
            results[col] = np.round(arr[top_idx], 3)
        results["combined_score"] = np.round(combined_score[top_idx], 3)
        results = results.reset_index(drop=True)
        log.info(f"Multi-matcher search complete. Returning {len(results)} results.")
        return results
