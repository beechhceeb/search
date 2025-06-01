import logging
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
        score_frames = []
        for matcher, weight in matcher_weights.items():
            if matcher not in self.matchers:
                log.warning(f"Matcher '{matcher}' not found, skipping.")
                continue
            df = self.matchers[matcher].match(
                query, self.dataset.df, top_k=None
            )  # get all results
            score_col = [col for col in df.columns if col.endswith("_score")]
            if not score_col:
                log.warning(
                    f"Matcher '{matcher}' did not return a score column, skipping."
                )
                continue
            score_col = score_col[0]
            temp = df[[score_col]].copy()
            temp.index = df.index
            temp.rename(columns={score_col: matcher + "_score"}, inplace=True)
            temp[matcher + "_score"] *= weight
            score_frames.append(temp)
        if not score_frames:
            log.error("No valid matcher results to combine.")
            return pd.DataFrame()
        combined = pd.concat(score_frames, axis=1).fillna(0)
        combined["combined_score"] = combined.sum(axis=1)
        # Attach original rows
        results = self.dataset.df.loc[combined.index].copy()
        results["combined_score"] = combined["combined_score"]
        results = (
            results.sort_values("combined_score", ascending=False)
            .head(top_k)
            .reset_index(drop=True)
        )
        log.info(f"Multi-matcher search complete. Returning {len(results)} results.")
        return results
