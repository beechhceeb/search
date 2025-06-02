"""
Business logic for search and suggestion endpoints.
"""
import logging
import functools
import hashlib
from bootstrap.bootstrap import search_engine, matcher_weights, dataset

log = logging.getLogger(__name__)

def _make_cache_key(*args, **kwargs):
    """Create a cache key from args/kwargs, robust to unhashable types."""
    key = str(args) + str(sorted(kwargs.items()))
    return hashlib.sha256(key.encode()).hexdigest()

def cached_search(maxsize=128):
    """Decorator for caching search results with custom key."""
    def decorator(func):
        cache = {}
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = _make_cache_key(*args, **kwargs)
            if key in cache:
                log.debug(f"Cache hit for {func.__name__} with key: {key}")
                return cache[key]
            log.debug(f"Cache miss for {func.__name__} with key: {key}")
            result = func(*args, **kwargs)
            if len(cache) >= maxsize:
                cache.pop(next(iter(cache)))  # Remove oldest
            cache[key] = result
            return result
        return wrapper
    return decorator

def get_popular_results(top_k: int = 10):
    """Return top_k most popular products as a list of dicts."""
    pop_df = dataset.df.sort_values("count_of_buy_products", ascending=False)
    return pop_df.head(top_k).to_dict(orient="records")


@cached_search(maxsize=256)
def perform_search(query: str, top_k: int = 10):
    """Perform a multi-matcher search and return results as a list of dicts. Cached."""
    results = search_engine.search_multi(query, matcher_weights=matcher_weights, top_k=top_k)
    # Drop columns not needed for display
    results.drop(
        columns=[
            "model_name_embedding",
            "blob_embedding",
            "blob",
            "model_id",
            "performance_group",
            "market",
            "count_of_buy_products",
        ],
        inplace=True,
        errors="ignore",
    )
    return results.to_dict(orient="records")


@cached_search(maxsize=256)
def get_suggestions(partial: str, top_k: int = 10):
    """Return a list of suggestions for the given partial query. Cached."""
    try:
        if not partial:
            pop_df = dataset.df.sort_values("count_of_buy_products", ascending=False)
            suggestions = pop_df["model_name"].dropna().astype(str).head(top_k).tolist()
        else:
            results = search_engine.search_multi(partial, matcher_weights=matcher_weights, top_k=top_k)
            suggestions = results["model_name"].dropna().astype(str).tolist()
    except Exception as e:
        log.error(f"Error in get_suggestions: {e}")
        suggestions = []
    return suggestions
