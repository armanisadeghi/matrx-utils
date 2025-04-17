def fake_db_check(recipe_id: str):
    """
    Simulates a database check for a valid recipe ID.
    In reality, this would query the actual database.
    """
    valid_ids = {"RCP123", "RCP456", "RCP789"}  # Example valid IDs
    if recipe_id not in valid_ids:
        raise ValueError(f"Invalid recipe ID: {recipe_id}")


def fake_stream_check(stream_id: str):
    """
    Simulates a check for whether a stream is active.
    In reality, this would query a service or database.
    """
    active_streams = {"STREAM_A", "STREAM_B"}
    if stream_id not in active_streams:
        raise ValueError(f"Stream {stream_id} is not active.")


def validate_url(url: str):
    """Validates if the given string is a valid URL."""
    try:
        if not url:
            raise ValueError(f"Url cannot be empty: {url}")
        if not isinstance(url, str):
            raise ValueError(f"Invalid URL: {url}")
    except Exception as e:
        raise ValueError(f"Invalid URL: {url}. Error: {e}")


def validate_urls(urls):
    """Validates a list of URLs."""
    if not isinstance(urls, list):
        raise ValueError("URLs must be provided as a list.")
    for url in urls:
        validate_url(url)


# def validate_noise_config(config):
#     """Validates the structure of a noise config."""
#     from scraper.logic.data_class import NoiseRemoverOverride
#
#     try:
#         NoiseRemoverOverride.from_dict(config)
#     except Exception as e:
#         raise ValueError(f"Cannot validate noise config: {e}")


# def validate_filter_config(config):
    # """Validates the structure of a filter config."""
    # from scraper.logic.data_class import ContentFilterOverride
    #
    # try:
    #     ContentFilterOverride.from_dict(config)
    # except Exception as e:
    #     raise ValueError(f"Cannot validate filter config: {e}")
    #

def validate_overrides(overrides):
    return {
        "model_override": str(overrides.get("model_override", "")),
        "processor_overrides": overrides.get("processor_overrides", {}),
        "other_overrides": overrides.get("other_overrides", {}),
    }


def validate_message_object(message_object):
    return {
        "id": str(message_object.get("id", "")),
        "conversation_id": str(message_object.get("conversation_id", "")),
        "content": str(message_object.get("content", "")),
        "role": str(message_object.get("role", "")),
        "type": str(message_object.get("type", "")),
        "metadata": message_object.get("metadata", {}),
    }
