# matrx_utils\socket\schema\validations\validation_registry.py
from matrx_utils.socket.schema.validations.validation_functions import (
    fake_db_check,
    fake_stream_check,
    validate_url,
    validate_urls,
)
import datetime


def validate_date(date_str):
    if not isinstance(date_str, str):
        raise ValueError("Date must be a string")

    try:
        year, month, day = map(int, date_str.split("-"))
        datetime.date(year, month, day)
        return None

    except ValueError as e:
        if "invalid literal for int" in str(e):
            raise ValueError("Date must be in YYYY-MM-DD format with numeric values")
        elif "too many values to unpack" in str(e) or "not enough values to unpack" in str(e):
            raise ValueError("Date must be in YYYY-MM-DD format")
        else:
            raise ValueError(f"Invalid date: {e}")


VALIDATION_REGISTRY = {
    "validate_scrape_url": validate_url,
    "validate_scrape_urls": validate_urls,
    "validate_date": validate_date,
}


CUSTOM_VALIDATIONS = {
    "validate_recipe_exists": lambda value: fake_db_check(value),
    "validate_stream_active": lambda value: fake_stream_check(value),
}
