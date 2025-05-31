import os

# FIXME: this will need to be externalised to an env var
FLASK_SECRET_KEY: str = "49c7c424-0162-49f6-8987-6348483bd62f"

DB_ENABLED = os.environ.get("DB_ENABLED", "true") == "true"
DATABASE_URL = "sqlite:///albatross.db"

SEARCH_SERVICE_GRPC_CLIENT_CONFIG = {
    "address": os.environ.get(
        "SEARCH_SERVICE_GRPC_ADDRESS",
        os.environ.get(
            "SEARCH_SERVICE_DOMAIN",
            "localhost",
        ),
    ),
    "port": os.environ.get(
        "SEARCH_SERVICE_GRPC_PORT",
        50051,
    ),
    "secure": os.environ.get(
        "SEARCH_SERVICE_GRPC_SECURE",
        "false",
    )
    == "true",
    "ssl_root_file": os.environ.get(
        "SEARCH_SERVICE_GRPC_SSL_ROOTS_FILE",
        NotImplemented,  # Every consumer will have different structure.
    ),
    "ssl_key_file": os.environ.get(
        "SEARCH_SERVICE_GRPC_SSL_KEY_FILE",
        NotImplemented,  # Every consumer will have different structure.
    ),
    "ssl_cert_file": os.environ.get(
        "SEARCH_SERVICE_GRPC_SSL_CERT_FILE",
        NotImplemented,  # Every consumer will have different structure.
    ),
    "batch_size": os.environ.get(
        "SEARCH_SERVICE_GRPC_BATCH_SIZE",
        1000,
    ),
}

SEARCH_PROXY_URL = os.environ.get(
    "SEARCH_PROXY_URL", "https://www.mpb.com/search-service/product/query/"
)

SEARCH_PROXY_HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-GB,en;q=0.6",
    "content-language": "en_GB",
}

SEARCH_PROXY_PARAMS_MODEL = {
    "field_list": [
        "model_id",
        "model_name",
        "model_images",
        "model_url_segment",
    ],
    "rows": 1,
    "start": 0,
    "filter_query[object_type]": "model",
}

SEARCH_PROXY_PARAMS_PRODUCT = {
    "field_list": [
        "product_price",
        "product_condition_star_rating",
    ],
    "sort[product_price]": "ASC",
    "rows": 1,
    "start": 0,
    "minimum_match": "100%",
    "filter_query[object_type]": "product",
    "filter_query[product_condition_star_rating]": "[1 TO 5]",
    "filter_query[model_market]": "UK",
}

# Since we are using search buy prices, we need a lookup to rough sell prices
# this is a rough estimate, better results would be gotten if we directly
# query the product service for the sell price.
SEARCH_STAR_RATING_TO_BEST_SELL_PRICE_FACTOR: dict[int, float] = {
    5: 0.6698895028,
    4: 0.7039187228,
    3: 0.8029801325,
    2: 1.002066116,
    1: 1.279683377,
}
