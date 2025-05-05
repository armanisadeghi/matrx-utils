SCHEMA = {
    "definitions": {
        "scrape_urls": {
            "REQUIRED": True,
            "DEFAULT": None,
            "VALIDATION": None,
            "DATA_TYPE": "array",
            "CONVERSION": None,
            "REFERENCE": None,
            "COMPONENT": "arrayField",
            "COMPONENT_PROPS": {},
            "DESCRIPTION": "Enter the urls to be scraped.",
            "ICON_NAME": "Link",
            "TEST_VALUE": None
        },
        "scrape_get_organized_data": {
            "REQUIRED": False, "DEFAULT": False, "VALIDATION": None, "DATA_TYPE": "boolean", "CONVERSION": None,
            "REFERENCE": None,
            "COMPONENT": "Switch", "COMPONENT_PROPS": {},
            "DESCRIPTION": "Get organized json content for the scrape page.", "ICON_NAME": "Braces", "TEST_VALUE": None
        },
        "scrape_get_structured_data": {
            "REQUIRED": False, "DEFAULT": False, "VALIDATION": None, "DATA_TYPE": "boolean", "CONVERSION": None,
            "REFERENCE": None,
            "COMPONENT": "Switch", "COMPONENT_PROPS": {},
            "DESCRIPTION": "Get structured data json content for the scrape page.", "ICON_NAME": "Braces",
            "TEST_VALUE": None
        },
        "scrape_get_overview": {
            "REQUIRED": False, "DEFAULT": False, "VALIDATION": None, "DATA_TYPE": "boolean", "CONVERSION": None,
            "REFERENCE": None,
            "COMPONENT": "Switch", "COMPONENT_PROPS": {},
            "DESCRIPTION": "Get overview content for the scraped page. Overview contains basic information for the page like title, other metadata etc.",
            "ICON_NAME": "Target", "TEST_VALUE": None
        },
        "scrape_get_text_data": {
            "REQUIRED": False, "DEFAULT": True, "VALIDATION": None, "DATA_TYPE": "boolean", "CONVERSION": None,
            "REFERENCE": None,
            "COMPONENT": "Switch", "COMPONENT_PROPS": {},
            "DESCRIPTION": "Get parsed text data for the scraped page. Generated from 'organized data'.",
            "ICON_NAME": "LetterText", "TEST_VALUE": None
        },
        "scrape_get_main_image": {
            "REQUIRED": False, "DEFAULT": False, "VALIDATION": None, "DATA_TYPE": "boolean", "CONVERSION": None,
            "REFERENCE": None,
            "COMPONENT": "Switch", "COMPONENT_PROPS": {},
            "DESCRIPTION": "Get main image for the scraped page. Main image is usually the biggest or most relevant image on the page. Extracted from OG metadata or other meta tags.",
            "ICON_NAME": "Image", "TEST_VALUE": None
        },
        "scrape_get_links": {
            "REQUIRED": False, "DEFAULT": False, "VALIDATION": None, "DATA_TYPE": "boolean", "CONVERSION": None,
            "REFERENCE": None,
            "COMPONENT": "Switch", "COMPONENT_PROPS": {},
            "DESCRIPTION": "Get all the links from the scraped page. Links are categorized as internal, external, document, archive etc.",
            "ICON_NAME": "Link", "TEST_VALUE": None
        },
        "scrape_get_content_filter_removal_details": {
            "REQUIRED": False, "DEFAULT": False, "VALIDATION": None, "DATA_TYPE": "boolean", "CONVERSION": None,
            "REFERENCE": None,
            "COMPONENT": "Switch", "COMPONENT_PROPS": {},
            "DESCRIPTION": "Get list of objects that were ignored during parsing page based on settings.",
            "ICON_NAME": "RemoveFormatting", "TEST_VALUE": None
        },
        "scrape_include_highlighting_markers": {
            "REQUIRED": False, "DEFAULT": True, "VALIDATION": None, "DATA_TYPE": "boolean", "CONVERSION": None,
            "REFERENCE": None,
            "COMPONENT": "Switch", "COMPONENT_PROPS": {},
            "DESCRIPTION": "Include /exclude highlighting markers like 'underline', 'list markers' etc... from text.",
            "ICON_NAME": "Underline", "TEST_VALUE": None
        },
        "scrape_include_media": {
            "REQUIRED": False, "DEFAULT": True, "VALIDATION": None, "DATA_TYPE": "boolean", "CONVERSION": None,
            "REFERENCE": None,
            "COMPONENT": "Switch", "COMPONENT_PROPS": {}, "DESCRIPTION": "Include media content in text output.",
            "ICON_NAME": "TvMinimalPlay", "TEST_VALUE": None
        },
        "scrape_include_media_links": {
            "REQUIRED": False, "DEFAULT": True, "VALIDATION": None, "DATA_TYPE": "boolean", "CONVERSION": None,
            "REFERENCE": None,
            "COMPONENT": "Switch", "COMPONENT_PROPS": {},
            "DESCRIPTION": "Include media links (image , video, audio) in text. Triggered when include_media is turned on.",
            "ICON_NAME": "Link", "TEST_VALUE": None
        },
        "scrape_include_media_description": {
            "REQUIRED": False, "DEFAULT": True, "VALIDATION": None, "DATA_TYPE": "boolean", "CONVERSION": None,
            "REFERENCE": None,
            "COMPONENT": "Switch", "COMPONENT_PROPS": {},
            "DESCRIPTION": "Include media description (media caption etc.) in text. Triggers when include_media is turned on.",
            "ICON_NAME": "WholeWord", "TEST_VALUE": None
        },
        "scrape_include_anchors": {
            "REQUIRED": False, "DEFAULT": True, "VALIDATION": None, "DATA_TYPE": "boolean", "CONVERSION": None,
            "REFERENCE": None,
            "COMPONENT": "Switch", "COMPONENT_PROPS": {}, "DESCRIPTION": "Include hyperlinks in scraped text",
            "ICON_NAME": "ExternalLink", "TEST_VALUE": None
        },
        "scrape_anchor_size": {
            "REQUIRED": False, "DEFAULT": 100, "VALIDATION": None, "DATA_TYPE": "integer", "CONVERSION": None,
            "REFERENCE": None,
            "COMPONENT": "NumberInput", "COMPONENT_PROPS": {"min": 10, "max": 500},
            "DESCRIPTION": "Size of hyperlinks in scraped text",
            "ICON_NAME": "Ruler", "TEST_VALUE": None
        },
        "search_keywords_array": {
            "REQUIRED": True, "DEFAULT": None, "VALIDATION": None, "DATA_TYPE": "array", "CONVERSION": None,
            "REFERENCE": None,
            "COMPONENT": "ArrayField", "COMPONENT_PROPS": {}, "DESCRIPTION": "Enter the queries to search for.",
            "ICON_NAME": "WholeWord", "TEST_VALUE": None
        },
        "search_keyword_string": {
            "REQUIRED": True, "DEFAULT": None, "VALIDATION": None, "DATA_TYPE": "string", "CONVERSION": None,
            "REFERENCE": None,
            "COMPONENT": "input", "COMPONENT_PROPS": {}, "DESCRIPTION": "Enter query to search and get results for.",
            "ICON_NAME": "WholeWord", "TEST_VALUE": None
        },
        "search_country_code": {
            "REQUIRED": False, "DEFAULT": "all", "VALIDATION": None, "DATA_TYPE": "string", "CONVERSION": None,
            "REFERENCE": None,
            "COMPONENT": "Select",
            "COMPONENT_PROPS": {"options": [
                {"label": "Argentina", "value": "AR"}, {"label": "Australia", "value": "AU"},
                {"label": "Austria", "value": "AT"},
                {"label": "Belgium", "value": "BE"}, {"label": "Brazil", "value": "BR"},
                {"label": "Canada", "value": "CA"},
                {"label": "Chile", "value": "CL"}, {"label": "Denmark", "value": "DK"},
                {"label": "Finland", "value": "FI"},
                {"label": "France", "value": "FR"}, {"label": "Germany", "value": "DE"},
                {"label": "Hong Kong", "value": "HK"},
                {"label": "India", "value": "IN"}, {"label": "Indonesia", "value": "ID"},
                {"label": "Italy", "value": "IT"},
                {"label": "Japan", "value": "JP"}, {"label": "Korea", "value": "KR"},
                {"label": "Malaysia", "value": "MY"},
                {"label": "Mexico", "value": "MX"}, {"label": "Netherlands", "value": "NL"},
                {"label": "New Zealand", "value": "NZ"},
                {"label": "Norway", "value": "NO"}, {"label": "Peoples Republic of China", "value": "CN"},
                {"label": "Poland", "value": "PL"},
                {"label": "Portugal", "value": "PT"}, {"label": "Republic of the Philippines", "value": "PH"},
                {"label": "Russia", "value": "RU"},
                {"label": "Saudi Arabia", "value": "SA"}, {"label": "South Africa", "value": "ZA"},
                {"label": "Spain", "value": "ES"},
                {"label": "Sweden", "value": "SE"}, {"label": "Switzerland", "value": "CH"},
                {"label": "Taiwan", "value": "TW"},
                {"label": "Turkey", "value": "TR"}, {"label": "United Kingdom", "value": "GB"},
                {"label": "United States", "value": "US"},
                {"label": "All Regions", "value": "ALL"}]
            },
            "DESCRIPTION": "Enter the country code to get search results for.", "ICON_NAME": "Flag", "TEST_VALUE": None
        },
        "search_type": {
            "REQUIRED": False, "DEFAULT": "all", "VALIDATION": None, "DATA_TYPE": "string", "CONVERSION": None,
            "REFERENCE": None,
            "COMPONENT": "RadioGroup", "COMPONENT_PROPS": {
                "options": [{"label": "All", "value": "all"}, {"label": "Web", "value": "web"},
                            {"label": "News", "value": "news"}], "orientation": "vertical"},
            "DESCRIPTION": "Kind of search type to scrape, 'web', 'news', or 'all'.", "ICON_NAME": "Rss",
            "TEST_VALUE": None
        },
        "search_total_results_slider_10_30": {
            "REQUIRED": False, "DEFAULT": 10, "VALIDATION": None, "DATA_TYPE": "integer", "CONVERSION": None,
            "REFERENCE": None,
            "COMPONENT": "slider", "COMPONENT_PROPS": {"min": 10, "max": 30, "step": 1, "range": "False"},
            "DESCRIPTION": "Enter the number of results per keyword to get.", "ICON_NAME": "SlidersHorizontal",
            "TEST_VALUE": None
        },
        "search_total_results_slider_1_100": {
            "REQUIRED": False, "DEFAULT": 5, "VALIDATION": None, "DATA_TYPE": "integer", "CONVERSION": None,
            "REFERENCE": None,
            "COMPONENT": "slider", "COMPONENT_PROPS": {"min": 1, "max": 100, "step": 1, "range": "False"},
            "DESCRIPTION": "Enter the number of results per keyword to get. Note: Total results per keyword may deviate from this number due to the search engine results.",
            "ICON_NAME": "SlidersHorizontal", "TEST_VALUE": None
        },
        "search_max_page_read_slider_1_20": {
            "REQUIRED": False, "DEFAULT": 10, "VALIDATION": None, "DATA_TYPE": "integer", "CONVERSION": None,
            "REFERENCE": None,
            "COMPONENT": "slider", "COMPONENT_PROPS": {"min": 1, "max": 20, "step": 1, "range": "False"},
            "DESCRIPTION": "Enter the number of results per keyword to get.", "ICON_NAME": "SlidersHorizontal",
            "TEST_VALUE": None
        },
        "MIC_CHECK_DEFINITION": {  # Assuming MIC_CHECK is treated as a global definition structure
            "mic_check_message": {
                "REQUIRED": False, "DEFAULT": "", "VALIDATION": None, "DATA_TYPE": "string", "CONVERSION": None,
                "REFERENCE": None,
                "COMPONENT": "input", "COMPONENT_PROPS": {}, "ICON_NAME": "Check",
                "DESCRIPTION": "Enter any message and the same message will be streamed back to you as a test of the mic.",
                "TEST_VALUE": None
            }
        }
    },
    "tasks": {
        "scraper_service_v2": {
            "quick_scrape": {
                "urls": {"$ref": "definitions/scrape_urls", "TEST_VALUE": ["https://en.wikipedia.org/wiki/Donald_Trump",
                                                                           "https://titaniumsuccess.com/arman-sadeghi/business-coach/"]},
                "get_organized_data": {"$ref": "definitions/scrape_get_organized_data", "TEST_VALUE": False},
                "get_structured_data": {"$ref": "definitions/scrape_get_structured_data", "TEST_VALUE": False},
                "get_overview": {"$ref": "definitions/scrape_get_overview", "TEST_VALUE": False},
                "get_text_data": {"$ref": "definitions/scrape_get_text_data", "TEST_VALUE": True},
                "get_main_image": {"$ref": "definitions/scrape_get_main_image", "TEST_VALUE": True},
                "get_links": {"$ref": "definitions/scrape_get_links", "TEST_VALUE": False},
                "get_content_filter_removal_details": {"$ref": "definitions/scrape_get_content_filter_removal_details",
                                                       "TEST_VALUE": False},
                "include_highlighting_markers": {"$ref": "definitions/scrape_include_highlighting_markers",
                                                 "TEST_VALUE": False},
                "include_media": {"$ref": "definitions/scrape_include_media", "TEST_VALUE": True},
                "include_media_links": {"$ref": "definitions/scrape_include_media_links", "TEST_VALUE": True},
                "include_media_description": {"$ref": "definitions/scrape_include_media_description",
                                              "TEST_VALUE": True},
                "include_anchors": {"$ref": "definitions/scrape_include_anchors", "TEST_VALUE": True},
                "anchor_size": {"$ref": "definitions/scrape_anchor_size", "TEST_VALUE": 100}
            },
            "quick_scrape_stream": {
                "urls": {"$ref": "definitions/scrape_urls", "TEST_VALUE": ["https://en.wikipedia.org/wiki/Donald_Trump",
                                                                           "https://titaniumsuccess.com/arman-sadeghi/business-coach/"]},
                "get_organized_data": {"$ref": "definitions/scrape_get_organized_data", "TEST_VALUE": False},
                "get_structured_data": {"$ref": "definitions/scrape_get_structured_data", "TEST_VALUE": False},
                "get_overview": {"$ref": "definitions/scrape_get_overview", "TEST_VALUE": False},
                "get_text_data": {"$ref": "definitions/scrape_get_text_data", "TEST_VALUE": True},
                "get_main_image": {"$ref": "definitions/scrape_get_main_image", "TEST_VALUE": True},
                "get_links": {"$ref": "definitions/scrape_get_links", "TEST_VALUE": False},
                "get_content_filter_removal_details": {"$ref": "definitions/scrape_get_content_filter_removal_details",
                                                       "TEST_VALUE": False},
                "include_highlighting_markers": {"$ref": "definitions/scrape_include_highlighting_markers",
                                                 "TEST_VALUE": False},
                "include_media": {"$ref": "definitions/scrape_include_media", "TEST_VALUE": True},
                "include_media_links": {"$ref": "definitions/scrape_include_media_links", "TEST_VALUE": True},
                "include_media_description": {"$ref": "definitions/scrape_include_media_description",
                                              "TEST_VALUE": True},
                "include_anchors": {"$ref": "definitions/scrape_include_anchors", "TEST_VALUE": True},
                "anchor_size": {"$ref": "definitions/scrape_anchor_size", "TEST_VALUE": 100}
            },
            "search_and_scrape": {
                "keywords": {"$ref": "definitions/search_keywords_array",
                             "TEST_VALUE": ["apple stock price", "apple stock best time to buy",
                                            "apple stock forecast"]},
                "country_code": {"$ref": "definitions/search_country_code", "TEST_VALUE": "US"},
                "total_results_per_keyword": {"$ref": "definitions/search_total_results_slider_10_30",
                                              "TEST_VALUE": 10},
                "search_type": {"$ref": "definitions/search_type", "DEFAULT": "all"},
                "get_organized_data": {"$ref": "definitions/scrape_get_organized_data", "TEST_VALUE": False},
                "get_structured_data": {"$ref": "definitions/scrape_get_structured_data", "TEST_VALUE": False},
                "get_overview": {"$ref": "definitions/scrape_get_overview", "TEST_VALUE": False},
                "get_text_data": {"$ref": "definitions/scrape_get_text_data", "TEST_VALUE": True},
                "get_main_image": {"$ref": "definitions/scrape_get_main_image", "TEST_VALUE": True},
                "get_links": {"$ref": "definitions/scrape_get_links", "TEST_VALUE": False},
                "get_content_filter_removal_details": {"$ref": "definitions/scrape_get_content_filter_removal_details",
                                                       "TEST_VALUE": False},
                "include_highlighting_markers": {"$ref": "definitions/scrape_include_highlighting_markers",
                                                 "TEST_VALUE": False},
                "include_media": {"$ref": "definitions/scrape_include_media", "TEST_VALUE": True},
                "include_media_links": {"$ref": "definitions/scrape_include_media_links", "TEST_VALUE": True},
                "include_media_description": {"$ref": "definitions/scrape_include_media_description",
                                              "TEST_VALUE": True},
                "include_anchors": {"$ref": "definitions/scrape_include_anchors", "TEST_VALUE": True},
                "anchor_size": {"$ref": "definitions/scrape_anchor_size", "TEST_VALUE": 100}
            },
            "search_keywords": {
                "keywords": {"$ref": "definitions/search_keywords_array",
                             "TEST_VALUE": ["apple stock price", "apple stock best time to buy",
                                            "apple stock forecast"]},
                "country_code": {"$ref": "definitions/search_country_code", "TEST_VALUE": "US"},
                "total_results_per_keyword": {"$ref": "definitions/search_total_results_slider_1_100", "TEST_VALUE": 5},
                "search_type": {"$ref": "definitions/search_type", "DEFAULT": "All"}
            },
            "search_and_scrape_limited": {
                "keyword": {"$ref": "definitions/search_keyword_string", "TEST_VALUE": "apple stock price"},
                "country_code": {"$ref": "definitions/search_country_code", "TEST_VALUE": "US"},
                "max_page_read": {"$ref": "definitions/search_max_page_read_slider_1_20", "TEST_VALUE": 5},
                "search_type": {"$ref": "definitions/search_type", "DEFAULT": "all"},
                "get_organized_data": {"$ref": "definitions/scrape_get_organized_data", "TEST_VALUE": False},
                "get_structured_data": {"$ref": "definitions/scrape_get_structured_data", "TEST_VALUE": False},
                "get_overview": {"$ref": "definitions/scrape_get_overview", "TEST_VALUE": False},
                "get_text_data": {"$ref": "definitions/scrape_get_text_data", "TEST_VALUE": True},
                "get_main_image": {"$ref": "definitions/scrape_get_main_image", "TEST_VALUE": True},
                "get_links": {"$ref": "definitions/scrape_get_links", "TEST_VALUE": False},
                "get_content_filter_removal_details": {"$ref": "definitions/scrape_get_content_filter_removal_details",
                                                       "TEST_VALUE": False},
                "include_highlighting_markers": {"$ref": "definitions/scrape_include_highlighting_markers",
                                                 "TEST_VALUE": False},
                "include_media": {"$ref": "definitions/scrape_include_media", "TEST_VALUE": True},
                "include_media_links": {"$ref": "definitions/scrape_include_media_links", "TEST_VALUE": True},
                "include_media_description": {"$ref": "definitions/scrape_include_media_description",
                                              "TEST_VALUE": True},
                "include_anchors": {"$ref": "definitions/scrape_include_anchors", "TEST_VALUE": True},
                "anchor_size": {"$ref": "definitions/scrape_anchor_size", "TEST_VALUE": 100}
            },
            "mic_check": {
                "$ref": "definitions/MIC_CHECK_DEFINITION"
            }
        },
        "LOG_SERVICE": {
            "READ_LOGS": {
                "filename": {
                    "REQUIRED": False, "DEFAULT": "application logs", "VALIDATION": None, "DATA_TYPE": "string",
                    "CONVERSION": None, "REFERENCE": None,
                    "COMPONENT": "Select",
                    "COMPONENT_PROPS": {"options": [{"value": "application logs", "label": "Application Logs"},
                                                    {"value": "daphne logs", "label": "Daphne Logs"},
                                                    {"value": "local logs", "label": "Local Logs"}]},
                    "ICON_NAME": "Document",
                    "DESCRIPTION": "The log file to read (Application Logs, Daphne Logs, or Local Logs).",
                    "TEST_VALUE": None
                },
                "lines": {
                    "REQUIRED": False, "DEFAULT": 100, "VALIDATION": None, "DATA_TYPE": "integer", "CONVERSION": None,
                    "REFERENCE": None,
                    "COMPONENT": "NumberInput", "COMPONENT_PROPS": {}, "ICON_NAME": "Number",
                    "DESCRIPTION": "The number of lines to read from the log file (0 for all).", "TEST_VALUE": None
                },
                "search": {
                    "REQUIRED": False, "DEFAULT": None, "VALIDATION": None, "DATA_TYPE": "string", "CONVERSION": None,
                    "REFERENCE": None,
                    "COMPONENT": "input", "COMPONENT_PROPS": {}, "ICON_NAME": "Search",
                    "DESCRIPTION": "A search term to filter log lines (case-insensitive).", "TEST_VALUE": None
                }
            },
            "TAIL_LOGS": {
                "filename": {
                    "REQUIRED": False, "DEFAULT": "application logs", "VALIDATION": None, "DATA_TYPE": "string",
                    "CONVERSION": None, "REFERENCE": None,
                    "COMPONENT": "Select",
                    "COMPONENT_PROPS": {"options": [{"value": "application logs", "label": "Application Logs"},
                                                    {"value": "daphne logs", "label": "Daphne Logs"},
                                                    {"value": "local logs", "label": "Local Logs"}]},
                    "ICON_NAME": "Document",
                    "DESCRIPTION": "The log file to tail (Application Logs, Daphne Logs, or Local Logs).",
                    "TEST_VALUE": None
                },
                "interval": {
                    "REQUIRED": False, "DEFAULT": 1.0, "VALIDATION": None, "DATA_TYPE": "float", "CONVERSION": None,
                    "REFERENCE": None,
                    "COMPONENT": "NumberInput", "COMPONENT_PROPS": {}, "ICON_NAME": "Clock",
                    "DESCRIPTION": "The interval (in seconds) between checks for new log lines.", "TEST_VALUE": None
                }
            },
            "STOP_TAIL_LOGS": {},
            "GET_LOG_FILES": {},
            "GET_ALL_LOGS": {
                "filename": {
                    "REQUIRED": False, "DEFAULT": "application logs", "VALIDATION": None, "DATA_TYPE": "string",
                    "CONVERSION": None, "REFERENCE": None,
                    "COMPONENT": "Select",
                    "COMPONENT_PROPS": {"options": [{"value": "application logs", "label": "Application Logs"},
                                                    {"value": "daphne logs", "label": "Daphne Logs"},
                                                    {"value": "local logs", "label": "Local Logs"}]},
                    "ICON_NAME": "Document",
                    "DESCRIPTION": "The log file to read all lines from (Application Logs, Daphne Logs, or Local Logs).",
                    "TEST_VALUE": None
                }
            }
        }

    }
}

def get_schema():
    return SCHEMA
