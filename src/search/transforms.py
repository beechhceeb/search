import pandas as pd
import logging
import numpy as np

log = logging.getLogger(__name__)


def normalise(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    log.info(f"Normalising columns: {columns}")
    for col in columns:
        df[col] = df[col].str.lower().str.strip()
    log.info(f"Normalisation complete for columns: {columns}")
    return df


def blob(
    df: pd.DataFrame, columns_to_blob: list[str], blob_column: str = "blob"
) -> pd.DataFrame:
    log.info(f"Creating blob column '{blob_column}' from columns: {columns_to_blob}")
    df[blob_column] = df[columns_to_blob].astype(str).agg(" ".join, axis=1)
    log.info(f"Blob column '{blob_column}' created.")
    return df


def remove_stopwords(
    df: pd.DataFrame, columns: list[str], stopwords: set[str]
) -> pd.DataFrame:
    log.info(f"Removing stopwords from columns: {columns}")
    for col in columns:
        df[col] = df[col].apply(
            lambda x: " ".join(
                word for word in x.split() if word.lower() not in stopwords
            )
        )
    log.info(f"Stopwords removed from columns: {columns}")
    return df


def remove_duplicates(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    log.info(f"Removing duplicate words in columns: {columns}")
    for col in columns:
        df[col] = df[col].apply(lambda x: " ".join(set(x.split())))
    log.info(f"Duplicates removed in columns: {columns}")
    return df


def drop_na(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    log.info(f"Dropping rows with NA in columns: {columns}")
    result = df.dropna(subset=columns)
    log.info(f"Rows after drop_na: {result.shape[0]}")
    return result


def log_normalise(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """
    Normalises specified columns in the DataFrame by converting to lowercase and stripping whitespace.
    """
    log.info(f"Normalising columns: {columns}")
    for col in columns:
        log.info(
            f"Original range for column '{col}': {df[col].min()} - {df[col].max()}"
        )
        df[col] = np.log1p(df[col] / np.log1p(df[col].max()))
        log.info(
            f"Normalised range for column '{col}': {df[col].min()} - {df[col].max()}"
        )
    log.info(f"Normalisation complete for columns: {columns}")
    return df
