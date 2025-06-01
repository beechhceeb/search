import pandas as pd
from abc import ABC, abstractmethod
import numpy as np
from .transformers import TransformerBase

# For fuzzy matching
from rapidfuzz import process, fuzz

# For semantic matching
from numpy.linalg import norm


class MatcherBase(ABC):
    """
    Abstract base class for all matchers.
    """

    @abstractmethod
    def match(self, query: str, df: pd.DataFrame, top_k: int = 10) -> pd.DataFrame:
        pass


class FuzzyMatcher(MatcherBase):
    """
    Fuzzy matcher using rapidfuzz to match query against a text column (e.g., 'blob').
    """

    def __init__(self, column: str):
        self.column = column

    def match(self, query: str, df: pd.DataFrame, top_k: int = 10) -> pd.DataFrame:
        # Get the column as a list
        choices = df[self.column].astype(str).tolist()
        # Get scores and indices
        results = process.extract(query, choices, scorer=fuzz.WRatio, limit=top_k)
        # results: List of (match_str, score, idx)
        indices = [idx for _, _, idx in results]
        scores = [score for _, score, _ in results]
        result_df = df.iloc[indices].copy()
        result_df["fuzzy_score"] = scores
        return result_df.sort_values("fuzzy_score", ascending=False).reset_index(
            drop=True
        )


class SemanticMatcher(MatcherBase):
    """
    Semantic matcher using cosine similarity on embedding columns.
    Assumes df has a column with precomputed embeddings (e.g., 'blob_embedding').
    """

    def __init__(self, embedding_column: str, encoder: TransformerBase):
        self.embedding_column = embedding_column
        self.encoder = encoder

    def match(self, query: str, df: pd.DataFrame, top_k: int = 10) -> pd.DataFrame:
        # Encode the query
        query_emb = np.array(self.encoder.encode_one(query))
        # Stack all embeddings from the DataFrame
        emb_matrix = np.stack(df[self.embedding_column].values)
        # Compute cosine similarity
        dot = emb_matrix @ query_emb
        emb_norms = norm(emb_matrix, axis=1)
        query_norm = norm(query_emb)
        scores = dot / (emb_norms * query_norm + 1e-8)
        # Get top_k indices
        top_idx = np.argsort(scores)[::-1][:top_k]
        result_df = df.iloc[top_idx].copy()
        result_df["semantic_score"] = scores[top_idx]
        return result_df.sort_values("semantic_score", ascending=False).reset_index(
            drop=True
        )


class ExactMatcher(MatcherBase):
    """
    Exact matcher that filters DataFrame rows based on exact match of a query string
    against a specified column.
    """

    def __init__(self, column: str):
        self.column = column

    def match(self, query: str, df: pd.DataFrame, top_k: int = 10) -> pd.DataFrame:
        result_df = df[df[self.column].str.contains(query, case=False, na=False)]
        return (
            result_df.head(top_k).reset_index(drop=True)
            if not result_df.empty
            else pd.DataFrame()
        )


class PopularMatcher(MatcherBase):
    """
    Popular matcher that returns the top K most popular items based on a specified popularity column.
    """

    def __init__(self, popularity_column: str):
        self.popularity_column = popularity_column

    def match(self, query: str, df: pd.DataFrame, top_k: int = 10) -> pd.DataFrame:
        if self.popularity_column not in df.columns:
            raise ValueError(
                f"Column '{self.popularity_column}' not found in DataFrame."
            )
        result_df = df.sort_values(by=self.popularity_column, ascending=False)
        return (
            result_df.head(top_k).reset_index(drop=True)
            if not result_df.empty
            else pd.DataFrame()
        )
