import pandas as pd
from abc import ABC, abstractmethod
import numpy as np
from .transformers import TransformerBase

# For fuzzy matching
from rapidfuzz import fuzz

# For semantic matching

import faiss


class MatcherBase(ABC):
    """
    Abstract base class for all matchers. Stores the DataFrame at initialization.
    """
    def __init__(self, df: pd.DataFrame):
        self.df = df

    @abstractmethod
    def match(self, query: str) -> list[float]:
        pass


class FuzzyMatcher(MatcherBase):
    """
    Fuzzy matcher using rapidfuzz to match query against a text column (e.g., 'blob').
    Returns a list of scores (float), same length and order as df.
    Stores the choices at initialization for speed.
    """
    def __init__(self, column: str, df: pd.DataFrame):
        super().__init__(df)
        self.column = column
        self.choices = self.df[self.column].astype(str).tolist()

    def match(self, query: str) -> list[float]:
        scores = [fuzz.WRatio(query, choice) / 100.0 for choice in self.choices]
        return scores


class SemanticMatcher(MatcherBase):
    """
    Semantic matcher using cosine similarity on embedding columns.
    Uses FAISS for fast nearest neighbor search if available.
    Returns a list of scores (float), same length and order as df.
    Now builds and stores the FAISS index and id map once at init.
    """
    def __init__(self, embedding_column: str, encoder: TransformerBase, df: pd.DataFrame):
        super().__init__(df)
        self.embedding_column = embedding_column
        self.encoder = encoder
        self.faiss_index = None
        self.faiss_id_map = None
        self._build_faiss(df)

    def _build_faiss(self, df: pd.DataFrame):
        emb_matrix = np.stack(df[self.embedding_column].values).astype(np.float32)
        index = faiss.IndexFlatIP(emb_matrix.shape[1])  # Cosine similarity via inner product
        faiss.normalize_L2(emb_matrix)
        index.add(emb_matrix)
        self.faiss_index = index
        # Use positional indices for id map to avoid index mismatch
        self.faiss_id_map = np.arange(len(df))

    def match(self, query: str) -> list[float]:
        query_emb = np.array(self.encoder.encode_one(query)).astype(np.float32)
        faiss.normalize_L2(query_emb.reshape(1, -1))
        k = len(self.faiss_id_map)
        D, I = self.faiss_index.search(query_emb.reshape(1, -1), k)
        scores = np.zeros(len(self.faiss_id_map), dtype=float)
        for arr_idx, score in zip(I[0], D[0]):
            if arr_idx < len(self.faiss_id_map):
                scores[arr_idx] = score
        return scores.tolist()
      


class ExactMatcher(MatcherBase):
    """
    Exact matcher that returns 1.0 if the query is a substring of the column value (case-insensitive), 0.0 otherwise.
    Returns a list of scores (float), same length and order as df.
    """
    def __init__(self, column: str, df: pd.DataFrame):
        super().__init__(df)
        self.column = column
        self.col_values = self.df[self.column]

    def match(self, query: str) -> list[float]:
        query_lower = query.lower()
        matches = self.col_values.str.contains(query_lower)
        scores = matches.astype(float).tolist()
        return scores


class PopularMatcher(MatcherBase):
    """
    Popular matcher that returns normalized popularity as a list of scores.
    Returns a list of scores (float), same length and order as df.
    Stores the popularity column as a numpy array for fast access.
    """
    def __init__(self, popularity_column: str, df: pd.DataFrame):
        super().__init__(df)
        self.popularity_column = popularity_column
        self.scores = self.df[self.popularity_column].to_numpy()

    def match(self, query: str) -> list[float]:
        return self.scores.tolist()
