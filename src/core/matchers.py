import pandas as pd
from abc import ABC, abstractmethod
import numpy as np
from .transformers import TransformerBase

# For fuzzy matching
from rapidfuzz import fuzz

# For semantic matching

import faiss

import logging
from typing import Sequence


class MatcherError(Exception):
    """Base exception for matcher errors."""
    pass

def get_column_safe(df: pd.DataFrame, column: str) -> pd.Series:
    """Utility to safely extract a column or raise a clear error."""
    if column not in df.columns:
        raise MatcherError(f"Column '{column}' not found in DataFrame.")
    return df[column]


class MatcherBase(ABC):
    __slots__ = ("df",)
    """
    Abstract base class for all matchers. Stores the DataFrame at initialization.
    """

    def __init__(self, df: pd.DataFrame):
        """
        Initialize the matcher with a DataFrame.
        Args:
            df (pd.DataFrame): The data to match against.
        """
        self.df = df

    @abstractmethod
    def match(self, query: str) -> list[float]:
        """
        Compute a list of scores for the query against the DataFrame.
        Args:
            query (str): The search query.
        Returns:
            list[float]: Scores for each row in the DataFrame.
        """
        pass


class FuzzyMatcher(MatcherBase):
    __slots__ = ("column", "choices")
    """
    Fuzzy matcher using rapidfuzz to match query against a text column (e.g., 'blob').
    Returns a list of scores (float), same length and order as df.
    Stores the choices at initialization for speed.
    """

    def __init__(self, column: str, df: pd.DataFrame):
        """
        Args:
            column (str): The column to match against.
            df (pd.DataFrame): The data.
        Raises:
            ValueError: If the column is not in the DataFrame.
        """
        super().__init__(df)
        self.column = column
        self.choices = get_column_safe(df, column).astype(str).fillna("").tolist()

    def match(self, query: str) -> Sequence[float]:
        logging.debug(f"FuzzyMatcher: Matching query '{query}' against column '{self.column}'")
        """
        Args:
            query (str): The search query.
        Returns:
            list[float]: Fuzzy match scores for each row.
        """
        if not isinstance(query, str):
            raise TypeError("Query must be a string.")
        # Defensive: handle empty DataFrame
        if not self.choices:
            return []
        return [
            round(fuzz.WRatio(query, choice) / 100.0, 3) for choice in self.choices
        ]


class FaissIndexManager:
    __slots__ = ("index", "id_map")
    """
    Handles FAISS index creation, normalization, and search for embeddings.
    """

    def __init__(self, emb_matrix: np.ndarray):
        """
        Args:
            emb_matrix (np.ndarray): 2D array of embeddings.
        Raises:
            ValueError: If emb_matrix is not 2D or is empty.
        """
        if emb_matrix.ndim != 2:
            raise ValueError("Embedding matrix must be 2-dimensional.")
        if emb_matrix.shape[0] == 0:
            raise ValueError("Embedding matrix is empty.")
        self.index = None
        self.id_map = None
        self._build_index(emb_matrix)

    def _build_index(self, emb_matrix: np.ndarray):
        emb_matrix = emb_matrix.astype(np.float32)
        faiss.normalize_L2(emb_matrix)
        index = faiss.IndexFlatIP(emb_matrix.shape[1])
        index.add(emb_matrix)
        self.index = index
        self.id_map = np.arange(len(emb_matrix))

    def search(self, query_emb: np.ndarray, k: int):
        """
        Search the FAISS index for the top k matches to the query embedding.
        Args:
            query_emb (np.ndarray): Query embedding.
            k (int): Number of top results to return.
        Returns:
            tuple: (distances, indices)
        """
        if query_emb.ndim == 1:
            query_emb = query_emb.reshape(1, -1)
        query_emb = query_emb.astype(np.float32)
        faiss.normalize_L2(query_emb)
        distances, indices = self.index.search(query_emb, k)
        return distances, indices


class SemanticMatcher(MatcherBase):
    __slots__ = ("embedding_column", "encoder", "faiss_manager")
    """
    Semantic matcher using cosine similarity on embedding columns.
    Uses FAISS for fast nearest neighbor search if available.
    Returns a list of scores (float), same length and order as df.
    Now delegates FAISS index management to FaissIndexManager.
    """

    def __init__(
        self, embedding_column: str, encoder: TransformerBase, df: pd.DataFrame
    ):
        """
        Args:
            embedding_column (str): The embedding column in the DataFrame.
            encoder (TransformerBase): The encoder for queries.
            df (pd.DataFrame): The data.
        Raises:
            ValueError: If the embedding column is not in the DataFrame.
        """
        super().__init__(df)
        self.embedding_column = embedding_column
        self.encoder = encoder
        emb_matrix = np.stack(get_column_safe(df, embedding_column).values)
        self.faiss_manager = FaissIndexManager(emb_matrix)

    def match(self, query: str) -> Sequence[float]:
        logging.debug(f"SemanticMatcher: Matching query '{query}' against embedding column '{self.embedding_column}'")
        """
        Args:
            query (str): The search query.
        Returns:
            list[float]: Semantic similarity scores for each row.
        """
        if not isinstance(query, str):
            raise TypeError("Query must be a string.")
        query_emb = np.array(self.encoder.encode_one(query))
        k = len(self.faiss_manager.id_map)
        distances, indices = self.faiss_manager.search(query_emb, k)
        scores = np.zeros(len(self.faiss_manager.id_map), dtype=float)
        for arr_idx, score in zip(indices[0], distances[0]):
            if arr_idx < len(self.faiss_manager.id_map):
                scores[arr_idx] = score
        return scores.tolist()


class ExactMatcher(MatcherBase):
    __slots__ = ("column", "col_values")
    """
    Exact matcher that returns 1.0 if the query is a substring of the column value (case-insensitive), 0.0 otherwise.
    Returns a list of scores (float), same length and order as df.
    """

    def __init__(self, column: str, df: pd.DataFrame):
        """
        Args:
            column (str): The column to match against.
            df (pd.DataFrame): The data.
        Raises:
            ValueError: If the column is not in the DataFrame.
        """
        super().__init__(df)
        self.column = column
        self.col_values = get_column_safe(df, column)

    def match(self, query: str) -> Sequence[float]:
        logging.debug(f"ExactMatcher: Matching query '{query}' against column '{self.column}'")
        """
        Args:
            query (str): The search query.
        Returns:
            list[float]: 1.0 if query is substring, else 0.0.
        """
        if not isinstance(query, str):
            raise TypeError("Query must be a string.")
        query_lower = query.lower()
        matches = self.col_values.astype(str).str.contains(query_lower, case=False, na=False)
        return matches.astype(float).tolist()


class PopularMatcher(MatcherBase):
    __slots__ = ("popularity_column", "scores")
    """
    Popular matcher that returns normalized popularity as a list of scores.
    Returns a list of scores (float), same length and order as df.
    Stores the popularity column as a numpy array for fast access.
    """

    def __init__(self, popularity_column: str, df: pd.DataFrame):
        """
        Args:
            popularity_column (str): The column with popularity values.
            df (pd.DataFrame): The data.
        Raises:
            ValueError: If the popularity column is not in the DataFrame.
        """
        super().__init__(df)
        self.popularity_column = popularity_column
        raw_scores = get_column_safe(df, popularity_column).to_numpy(dtype=float)
        max_score = raw_scores.max() if len(raw_scores) > 0 else 1.0
        self.scores = (np.log1p(raw_scores) / np.log1p(max_score)).round(3) if max_score > 0 else raw_scores

    def match(self, query: str) -> Sequence[float]:
        logging.debug(f"PopularMatcher: Returning popularity scores for query '{query}' (query ignored)")
        """
        Args:
            query (str): The search query (ignored).
        Returns:
            list[float]: Normalized popularity scores.
        """
        return self.scores.tolist()
