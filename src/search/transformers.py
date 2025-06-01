from sentence_transformers import SentenceTransformer
import pandas as pd
from tqdm import tqdm
import logging
from abc import ABC, abstractmethod
from typing import List

log = logging.getLogger(__name__)


class TransformerBase(ABC):
    """
    Abstract base class for text embedding transformers.
    Subclasses must implement encode(texts: List[str], **kwargs) -> List or np.ndarray.
    """

    @abstractmethod
    def encode(self, texts: List[str], **kwargs):
        """
        Encode a list of texts into embeddings.
        """
        pass

    def embed_columns(
        self, df: pd.DataFrame, columns: List[str], batch_size: int = 64
    ) -> pd.DataFrame:
        """
        Embed specified columns in the DataFrame and add new columns with _embedding suffix.
        """
        for col in tqdm(columns, desc="Embedding columns"):
            if col not in df.columns:
                log.error(f"Column '{col}' not found in DataFrame.")
                raise ValueError(f"Column '{col}' not found in DataFrame.")
            log.info(f"Embedding column: {col}")
            texts = df[col].fillna("").astype(str).tolist()
            embeddings = self.encode(texts, batch_size=batch_size)
            df[col + "_embedding"] = list(embeddings)
            log.info(f"Completed embedding for column: {col}")
        log.info("All embeddings complete.")
        return df

    def encode_one(self, text: str, **kwargs):
        """
        Encode a single string into an embedding.
        """
        return self.encode([text], **kwargs)[0]


class SentenceTransformerWrapper(TransformerBase):
    """
    Wrapper for HuggingFace SentenceTransformer.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        log.info(f"Loading transformer model: {model_name}")
        try:
            self.model = SentenceTransformer(model_name)
            log.info(f"Successfully loaded transformer model: {model_name}")
        except Exception as e:
            log.error(f"Failed to load transformer model '{model_name}': {e}")
            raise RuntimeError(f"Failed to load transformer model '{model_name}': {e}")

    def encode(self, texts: List[str], batch_size: int = 64, **kwargs):
        """
        Encode a list of texts using the underlying SentenceTransformer model.
        """
        return self.model.encode(
            texts, show_progress_bar=True, batch_size=batch_size, **kwargs
        )

    def encode_one(self, text: str, **kwargs):
        """
        Encode a single string using the underlying SentenceTransformer model.
        """
        return self.encode([text], **kwargs)[0]
