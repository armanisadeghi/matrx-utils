from matrx_utils.socket.schema.validations.validation_functions import (
    fake_db_check,
    fake_stream_check,
    validate_url,
    validate_urls,
)
# from automation_matrix.processing.markdown.data_class import (
#     LineCategory,
#     CodeLanguage,
#     SectionType,
#     SectionGroupPatternType,
#     SegmentType,
# )
# from scraper.logic.data_class import ScrapeMode
# from knowledgebase.experts.ama_expert.pd_ratings.data_class import Side
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
    # Md related
    # "validate_md_code_language": CodeLanguage,
    # "validate_md_section_type": SectionType,
    # "validate_md_section_group_type": SectionGroupPatternType,
    # "validate_md_segment_type": SegmentType,
    # "validate_md_line_category": LineCategory,
    # Scrape related.
    "validate_scrape_url": validate_url,
    "validate_scrape_urls": validate_urls,
    # "validate_scrape_mode": ScrapeMode,
    # "validate_scrape_noise_config": validate_noise_config,
    # "validate_scrape_filter_config": validate_filter_config,
    "validate_date": validate_date,
    # "validate_wc_side": Side,
}


CUSTOM_VALIDATIONS = {
    "validate_recipe_exists": lambda value: fake_db_check(value),
    "validate_stream_active": lambda value: fake_stream_check(value),
}
