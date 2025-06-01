import logging
import numpy as np
import pandas as pd
import cProfile
import pstats
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
        self, query: str, matcher_weights: dict, top_k: int = 10, profile: bool = False
    ) -> pd.DataFrame:
        """
        Search using multiple matchers and combine results with specified weights.
        matcher_weights: dict of {matcher_name: weight}
        Returns a DataFrame of top results with a combined score.
        If profile=True, runs cProfile and prints top slowest lines.
        """
        def _search_body():
            log.info(
                f"Multi-matcher search for query: '{query}' with weights: {matcher_weights}"
            )
            n = len(self.dataset.df)
            combined_score = np.zeros(n, dtype=float)
            all_scores = {}
            for matcher, weight in matcher_weights.items():
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
                results[col] = arr[top_idx]
            results["combined_score"] = combined_score[top_idx]
            results = results.reset_index(drop=True)
            log.info(f"Multi-matcher search complete. Returning {len(results)} results.")
            return results
        if profile:
            profiler = cProfile.Profile()
            profiler.enable()
            result = _search_body()
            profiler.disable()
            stats = pstats.Stats(profiler).strip_dirs().sort_stats('cumtime')
            print("\n--- Profiling Results (Top 20 cumulative time) ---")
            stats.print_stats(20)
            return result
        else:
            return _search_body()
