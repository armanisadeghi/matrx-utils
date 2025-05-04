# matrx_utils\socket\schema\context_registry.py
import os
import json
from typing import Dict, Any
from matrx_utils import vcprint ,print_link

# Icon names MUST be names of actual icons from "Lucide-React" - Go to https://lucide.dev/icons/ to find official names and use them freely here.

# Do not use the same icon name for everything out of laziness.

# 'key' should be used for anything that referes to the id from the database.

DEFAULT_DEFINITION = {
    "data": {
        "REQUIRED": False,
        "DEFAULT": {},
        "VALIDATION": None,
        "DATA_TYPE": "object",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "JsonEditor",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the data to be processed.",
        "ICON_NAME": "Parentheses",
    }
}

MIC_CHECK_DEFINITION = {
    "mic_check_message": {
        "REQUIRED": False,
        "DEFAULT": "",
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Check",
        "DESCRIPTION": "Enter any message and the same message will be streamed back to you as a test of the mic.",
    },
}

SAMPLE_SCHEMA_FIELDS = {
    "slider_field": {
        "REQUIRED": False,
        "DEFAULT": 50,
        "VALIDATION": None,
        "DATA_TYPE": "number",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "slider",
        "COMPONENT_PROPS": {
            "min": 0,
            "max": 100,
            "step": 1,
            "range": "False",
        },
        "ICON_NAME": "Sliders",
        "DESCRIPTION": "Adjust the value between 0 and 100",
        "TEST_VALUE": 75,
    },
    "select_field": {
        "REQUIRED": True,
        "DEFAULT": "option2",
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Select",
        "COMPONENT_PROPS": {"options": [{"label": "Option 1", "value": "option1"}, {"label": "Option 2", "value": "option2"}, {"label": "Option 3", "value": "option3"}]},
        "ICON_NAME": "List",
        "DESCRIPTION": "Select an option from the dropdown",
        "TEST_VALUE": "option3",
    },
    "radio_field": {
        "REQUIRED": True,
        "DEFAULT": "radio1",
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "RadioGroup",
        "COMPONENT_PROPS": {
            "options": [{"label": "Radio Option 1", "value": "radio1"}, {"label": "Radio Option 2", "value": "radio2"}, {"label": "Radio Option 3", "value": "radio3"}],
            "orientation": "vertical",
        },
        "ICON_NAME": "Radio",
        "DESCRIPTION": "Choose one of the options",
        "TEST_VALUE": "radio2",
    },
    "file_field": {
        "REQUIRED": False,
        "DEFAULT": "",
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "FileUpload",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "File",
        "DESCRIPTION": "Upload a document (PDF, DOCX, or TXT)",
        "TEST_VALUE": "sample-document.pdf",
    },
    "files_field": {
        "REQUIRED": False,
        "DEFAULT": [],
        "VALIDATION": None,
        "DATA_TYPE": "array",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "MultiFileUpload",
        "COMPONENT_PROPS": {
            "accept": "image/*",
            "maxfiles": 5,
            "maxsize": 2000000,
        },
        "ICON_NAME": "Files",
        "DESCRIPTION": "Upload up to 5 images (max 2MB each)",
        "TEST_VALUE": ["image1.jpg", "image2.png"],
    },
    "json_field": {
        "REQUIRED": False,
        "DEFAULT": {"key": "value"},
        "VALIDATION": None,
        "DATA_TYPE": "object",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "JsonEditor",
        "COMPONENT_PROPS": {
            "spellCheck": "False",
        },
        "ICON_NAME": "Code",
        "DESCRIPTION": "Edit JSON configuration",
        "TEST_VALUE": {"test": "data", "nested": {"value": 123}},
    },
    "switch_field": {
        "REQUIRED": False,
        "DEFAULT": True,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {"size": "default"},
        "ICON_NAME": "ToggleLeft",
        "DESCRIPTION": "Enable or disable this feature",
        "TEST_VALUE": False,
    },
    "checkbox_field": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Checkbox",
        "COMPONENT_PROPS": {"indeterminate": "False"},
        "ICON_NAME": "CheckSquare",
        "DESCRIPTION": "Agree to the terms and conditions",
        "TEST_VALUE": True,
    },
    "textarea_field": {
        "REQUIRED": False,
        "DEFAULT": "",
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Textarea",
        "COMPONENT_PROPS": {"rows": 6, "maxLength": 500, "placeholder": "Enter your detailed description here...", "resize": "vertical"},
        "ICON_NAME": "FileText",
        "DESCRIPTION": "Provide a detailed description (max 500 characters)",
        "TEST_VALUE": "This is a sample text that would be used in test mode.",
    },
}


BROKER_DEFINITION = {
    "name": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the name of the broker.",
        "ICON_NAME": "User",
    },
    "id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the id of the broker.",
        "ICON_NAME": "Key",
        "TEST_VALUE": "5d8c5ed2-5a84-476a-9258-6123a45f996a",
    },
    "value": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the value of the broker.",
        "ICON_NAME": "LetterText",
        "TEST_VALUE": "I have an app that let's users create task lists from audio files.",
    },
    "ready": {
        "REQUIRED": False,
        "DEFAULT": "true",
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Whether the broker's value is DIRECTLY ready exactly as it is.",
        "ICON_NAME": "Check",
    },
}

OVERRIDE_DEFINITION = {
    "model_override": {
        "REQUIRED": False,
        "DEFAULT": "",
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the id of the model to use.",
        "ICON_NAME": "Key",
    },
    "processor_overrides": {
        "REQUIRED": False,
        "DEFAULT": {},
        "VALIDATION": None,
        "DATA_TYPE": "object",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "JsonEditor",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "This is a complex field that requires a pre-determined structure to get specific processors and extractors.",
        "ICON_NAME": "Parentheses",
    },
    "other_overrides": {
        "REQUIRED": False,
        "DEFAULT": {},
        "VALIDATION": None,
        "DATA_TYPE": "object",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "JsonEditor",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Some additional overrides may be provided for processing.",
        "ICON_NAME": "Parentheses",
    },
}

COCKPIT_INSTANT_DEFINITION = {
    "cockpit_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Not sure what this is for yet.",
        "ICON_NAME": "Key",
    },
    "broker_values": {
        "REQUIRED": True,
        "DEFAULT": [],
        "VALIDATION": None,
        "DATA_TYPE": "array",
        "CONVERSION": "convert_broker_data",
        "REFERENCE": BROKER_DEFINITION,
        "COMPONENT": "relatedArrayObject",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the broker values to be used in the recipe.",
        "ICON_NAME": "Parentheses",
    },
    "overrides": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "object",
        "CONVERSION": None,
        "REFERENCE": OVERRIDE_DEFINITION,
        "COMPONENT": "relatedObject",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the overrides to be applied. These will override the 'settings' for the recipe, if overrides are allowed for the recipe.",
        "ICON_NAME": "Parentheses",
    },
}

RUN_RECIPE_DEFINITION = {
    "recipe_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the id of the recipe to run.",
        "ICON_NAME": "Key",
        "TEST_VALUE": "e2049ce6-c340-4ff7-987e-deb24a977853",
    },
    "broker_values": {
        "REQUIRED": False,
        "DEFAULT": [],
        "VALIDATION": None,
        "DATA_TYPE": "array",
        "CONVERSION": "convert_broker_data",
        "REFERENCE": BROKER_DEFINITION,
        "COMPONENT": "relatedArrayObject",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the broker values to be used in the recipe.",
        "ICON_NAME": "Parentheses",
    },
    "overrides": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "object",
        "CONVERSION": None,
        "REFERENCE": OVERRIDE_DEFINITION,
        "COMPONENT": "relatedObject",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the overrides to be applied. These will override the 'settings' for the recipe, if overrides are allowed for the recipe.",
        "ICON_NAME": "Parentheses",
    },
    "stream": {
        "REQUIRED": True,
        "DEFAULT": True,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Whether the response should be streamed or sent all at once.",
        "ICON_NAME": "Check",
    },
}

RUN_COMPILED_RECIPE_DEFINITION = {
    "recipe_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the id of the recipe to run.",
        "ICON_NAME": "Key",
        "TEST_VALUE": "e2049ce6-c340-4ff7-987e-deb24a977853",
    },
    "compiled_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the id of the compiled recipe to run.",
        "ICON_NAME": "Key",
    },
    "compiled_recipe": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the compiled recipe to run.",
        "ICON_NAME": "Key",
    },
    "stream": {
        "REQUIRED": True,
        "DEFAULT": True,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Whether the response should be streamed or sent all at once.",
        "ICON_NAME": "Check",
    },
}

ADD_RECIPE_DEFINITION = {
    "recipe_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the id of the recipe to add.",
        "ICON_NAME": "Key",
        "TEST_VALUE": "e2049ce6-c340-4ff7-987e-deb24a977853",
    },
    "compiled_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the id of the compiled recipe to add.",
        "ICON_NAME": "Key",
    },
    "compiled_recipe": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the compiled recipe to add.",
        "ICON_NAME": "Key",
    },
}

GET_RECIPE_DEFINITION = {
    "recipe_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the id of the recipe to get.",
        "ICON_NAME": "Key",
        "TEST_VALUE": "e2049ce6-c340-4ff7-987e-deb24a977853",
    },
}

GET_COMPILED_RECIPE_DEFINITION = {
    "compiled_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the id of the compiled recipe to get.",
        "ICON_NAME": "Key",
    },
}


######## Markdown related.
CLASSIFY_MARKDOWN_DEFINITION = {
    "raw_markdown": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "textarea",
        "COMPONENT_PROPS": {"rows": 10},
        "DESCRIPTION": "Enter the raw markdown to be classified.",
        "ICON_NAME": "Key",
    }
}

GET_CODE_BLOCKS_BY_LANGUAGE_DEFINITION = {
    "raw_markdown": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "textarea",
        "COMPONENT_PROPS": {"rows": 10},
        "DESCRIPTION": "Enter the raw markdown to be classified.",
        "ICON_NAME": "Key",
    },
    "language": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": "validate_md_code_language",
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the language of the code blocks to be extracted.",
        "ICON_NAME": "Key",
    },
    "remove_comments": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Check",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Whether to remove comments from the code blocks.",
        "ICON_NAME": "Check",
    },
}

GET_ALL_CODE_BLOCKS_DEFINITION = {
    "raw_markdown": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "textarea",
        "COMPONENT_PROPS": {"rows": 10},
        "DESCRIPTION": "Enter the raw markdown to be classified.",
        "ICON_NAME": "Key",
    },
    "remove_comments": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Check",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Whether to remove comments from the code blocks.",
        "ICON_NAME": "Check",
    },
}

GET_SECTION_BLOCKS_DEFINITION = {
    "raw_markdown": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "textarea",
        "COMPONENT_PROPS": {"rows": 10},
        "DESCRIPTION": "Enter the raw markdown to be classified.",
        "ICON_NAME": "Key",
    },
    "section_type": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": "validate_md_section_type",
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the type of section to be extracted.",
        "ICON_NAME": "Key",
    },
}

GET_SECTION_GROUPS_DEFINITION = {
    "raw_markdown": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "textarea",
        "COMPONENT_PROPS": {"rows": 10},
        "DESCRIPTION": "Enter the raw markdown to be classified.",
        "ICON_NAME": "Key",
    },
    "section_group_type": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": "validate_md_section_group_type",
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the type of section group to be extracted.",
        "ICON_NAME": "Key",
    },
}

GET_SEGMENTS_DEFINITION = {
    "raw_markdown": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "textarea",
        "COMPONENT_PROPS": {"rows": 10},
        "DESCRIPTION": "Enter the raw markdown to be classified.",
        "ICON_NAME": "Key",
    },
    "segment_type": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": "validate_md_segment_type",
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the type of segment to be extracted.",
        "ICON_NAME": "Key",
    },
}

REMOVE_FIRST_AND_LAST_PARAGRAPH_DEFINITION = {
    "raw_markdown": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "textarea",
        "COMPONENT_PROPS": {"rows": 10},
        "DESCRIPTION": "Enter the raw markdown to be classified.",
        "ICON_NAME": "Key",
    }
}

GET_PYTHON_DICTS_DEFINITION = {
    "raw_markdown": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "textarea",
        "COMPONENT_PROPS": {"rows": 10},
        "DESCRIPTION": "Enter the raw markdown to be classified.",
        "ICON_NAME": "Key",
    },
    "dict_variable_name": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the variable name of the dictionary to be created.",
        "ICON_NAME": "Key",
    },
}

GET_ALL_PYTHON_COMMENTS_DEFINITION = {
    "raw_markdown": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "textarea",
        "COMPONENT_PROPS": {"rows": 10},
        "DESCRIPTION": "Enter the raw markdown to be classified.",
        "ICON_NAME": "Key",
    }
}

GET_ALL_PYTHON_FUNCTION_DOCSTRINGS_DEFINITION = {
    "raw_markdown": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "textarea",
        "COMPONENT_PROPS": {"rows": 10},
        "DESCRIPTION": "Enter the raw markdown to be classified.",
        "ICON_NAME": "Key",
    }
}

GET_ALL_PYTHON_CLASS_DOCSTRINGS_DEFINITION = {
    "raw_markdown": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "textarea",
        "COMPONENT_PROPS": {"rows": 10},
        "DESCRIPTION": "Enter the raw markdown to be classified.",
        "ICON_NAME": "Key",
    }
}

GET_STRUCTURED_DATA_DEFINITION = {
    "raw_markdown": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "textarea",
        "COMPONENT_PROPS": {"rows": 10},
        "DESCRIPTION": "Enter the raw markdown to be classified.",
        "ICON_NAME": "Key",
    }
}

# Group all tasks under the MARKDOWN service
MARKDOWN_SERVICE_DEFINITIONS = {
    "CLASSIFY_MARKDOWN": CLASSIFY_MARKDOWN_DEFINITION,
    "GET_CODE_BLOCKS_BY_LANGUAGE": GET_CODE_BLOCKS_BY_LANGUAGE_DEFINITION,
    "GET_STRUCTURED_DATA": GET_STRUCTURED_DATA_DEFINITION,
    "GET_ALL_CODE_BLOCKS": GET_ALL_CODE_BLOCKS_DEFINITION,
    "GET_SECTION_BLOCKS": GET_SECTION_BLOCKS_DEFINITION,
    "GET_SECTION_GROUPS": GET_SECTION_GROUPS_DEFINITION,
    "GET_SEGMENTS": GET_SEGMENTS_DEFINITION,
    "REMOVE_FIRST_AND_LAST_PARAGRAPH": REMOVE_FIRST_AND_LAST_PARAGRAPH_DEFINITION,
    "GET_PYTHON_DICTS": GET_PYTHON_DICTS_DEFINITION,
    "GET_ALL_PYTHON_COMMENTS": GET_ALL_PYTHON_COMMENTS_DEFINITION,
    "GET_ALL_PYTHON_FUNCTION_DOCSTRINGS": GET_ALL_PYTHON_FUNCTION_DOCSTRINGS_DEFINITION,
    "GET_ALL_PYTHON_CLASS_DOCSTRINGS": GET_ALL_PYTHON_CLASS_DOCSTRINGS_DEFINITION,
    "MIC_CHECK": MIC_CHECK_DEFINITION,
}

########## Scrape related definitions ########### || NOTE: The descriptions I've used are just random. Not good for explaining what this actually does. Please update them.
GET_DOMAINS_DEFINITION = {}

GET_DOMAIN_CONFIG_DEFINITION = {
    "domain_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the id of the domain to get.",
        "ICON_NAME": "Key",
    }
}

CREATE_DOMAIN_CONFIG_DEFINITION = {
    "domain_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the id of the domain to create.",
        "ICON_NAME": "Key",
    },
    "path_pattern": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the path pattern to be used for the domain.",
        "ICON_NAME": "Key",
    },
    "noise_config_id": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the id of the noise config to be used for the domain.",
        "ICON_NAME": "Key",
    },
    "filter_config_id": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the id of the filter config to be used for the domain.",
        "ICON_NAME": "Key",
    },
    "plugin_ids": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "array",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "ArrayField",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the ids of the plugins to be used for the domain.",
        "ICON_NAME": "Blocks",
    },
    "interaction_settings_id": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the id of the interaction settings to be used for the domain.",
        "ICON_NAME": "Key",
    },
    "use_mode": {
        "REQUIRED": False,
        "DEFAULT": "normal",
        "VALIDATION": "validate_scrape_mode",
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the mode to be used for the domain.",
        "ICON_NAME": "Key",
    },
}

UPDATE_DOMAIN_CONFIG_DEFINITION = {
    "domain_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the id of the domain to update.",
        "ICON_NAME": "Key",
    },
    "path_pattern": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the path pattern to be used for the domain.",
        "ICON_NAME": "Key",
    },
    "noise_config_id": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the id of the noise config to be used for the domain.",
        "ICON_NAME": "Key",
    },
    "filter_config_id": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the id of the filter config to be used for the domain.",
        "ICON_NAME": "Key",
    },
    "plugin_ids": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "array",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "ArrayField",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the ids of the plugins to be used for the domain.",
        "ICON_NAME": "Blocks",
    },
    "interaction_settings_id": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the id of the interaction settings to be used for the domain.",
        "ICON_NAME": "Key",
    },
    "use_mode": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": "validate_scrape_mode",
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the mode to be used for the domain.",
        "ICON_NAME": "Key",
    },
}

CREATE_DOMAIN_DEFINITION = {
    "domain": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the domain to be created.",
        "ICON_NAME": "Key",
    }
}

CREATE_INTERACTION_SETTINGS_DEFINITION = {
    "interaction_settings_name": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the name of the interaction settings to be created.",
        "ICON_NAME": "Key",
    }
}

GET_NOISE_CONFIG_DEFINITION = {
    "noise_config_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the id of the noise config to be used for the domain.",
        "ICON_NAME": "Key",
    }
}

GET_NOISE_CONFIGS_DEFINITION = {}

GET_FILTER_CONFIG_DEFINITION = {
    "filter_config_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the id of the filter config to be used for the domain.",
        "ICON_NAME": "Key",
    }
}

GET_FILTER_CONFIGS_DEFINITION = {}

GET_INTERACTION_SETTINGS_DEFINITION = {
    "interaction_settings_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the id of the interaction settings to be used for the domain.",
        "ICON_NAME": "Key",
    }
}

CREATE_NOISE_CONFIG_DEFINITION = {
    "noise_config_name": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the name of the noise config to be created.",
        "ICON_NAME": "Key",
    }
}

CREATE_FILTER_CONFIG_DEFINITION = {
    "filter_config_name": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the name of the filter config to be created.",
        "ICON_NAME": "Key",
    }
}

SAVE_NOISE_CONFIG_DEFINITION = {
    "noise_config_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the id of the noise config to be used for the domain.",
        "ICON_NAME": "Key",
    },
    "new_noise_config": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": "validate_scrape_noise_config",
        "DATA_TYPE": "object",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the new noise config to be used for the domain.",
        "ICON_NAME": "Key",
    },
}

SAVE_FILTER_CONFIG_DEFINITION = {
    "filter_config_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the id of the filter config to be used for the domain.",
        "ICON_NAME": "Key",
    },
    "new_filter_config": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": "validate_scrape_filter_config",
        "DATA_TYPE": "object",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the new filter config to be used for the domain.",
        "ICON_NAME": "Key",
    },
}

SAVE_INTERACTION_SETTINGS_DEFINITION = {
    "interaction_settings_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the id of the interaction settings to be used for the domain.",
        "ICON_NAME": "Key",
    },
    "new_interaction_settings": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "object",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the new interaction settings to be used for the domain.",
        "ICON_NAME": "Key",
    },
}

QUICK_SCRAPE_DEFINITION = {
    "urls": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": "validate_scrape_urls",
        "DATA_TYPE": "array",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "ArrayField",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the urls to be scraped.",
        "ICON_NAME": "Link",
    },
    "get_anchors": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Whether to get anchors.",
        "ICON_NAME": "Check",
    },
}

CREATE_SCRAPE_TASKS_DEFINITION = {
    "urls": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": "validate_scrape_urls",
        "DATA_TYPE": "array",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "ArrayField",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the urls to be scraped.",
        "ICON_NAME": "Link",
    },
    "use_configs": {
        "REQUIRED": False,
        "DEFAULT": True,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Whether to use configs.",
        "ICON_NAME": "Cog",
    },
    "use_mode": {
        "REQUIRED": False,
        "DEFAULT": "normal",
        "VALIDATION": "validate_scrape_mode",
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the mode to be used for the scrape.",
        "ICON_NAME": "Blend",
    },
    "interaction_settings_id": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the interaction settings id to be used for the scrape.",
        "ICON_NAME": "Key",
    },
}

SCRAPE_PAGE_DEFINITION = {
    "url": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the url to be scraped.",
        "ICON_NAME": "Link",
    },
    "use_mode": {
        "REQUIRED": False,
        "DEFAULT": "normal",
        "VALIDATION": "validate_scrape_mode",
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the mode to be used for the scrape.",
        "ICON_NAME": "Blend",
    },
    "interaction_settings_id": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the interaction settings id to be used for the scrape.",
        "ICON_NAME": "Key",
    },
}

PARSE_RESPONSE_DEFINITION = {
    "scrape_task_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the scrape task id to be parsed.",
        "ICON_NAME": "Key",
    },
    "use_configs": {
        "REQUIRED": False,
        "DEFAULT": True,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Whether to use configs.",
        "ICON_NAME": "Cog",
    },
    "noise_config_id": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the noise config id to be used for the scrape.",
        "ICON_NAME": "Key",
    },
    "filter_config_id": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the filter config id to be used for the scrape.",
        "ICON_NAME": "Key",
    },
}

PARSE_RESPONSES_DEFINITION = {
    "scrape_task_ids": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "array",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "ArrayField",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the scrape task ids to be parsed.",
        "ICON_NAME": "ChartNetwork",
    },
    "use_configs": {
        "REQUIRED": False,
        "DEFAULT": True,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Whether to use configs.",
        "ICON_NAME": "Cog",
    },
    "noise_config_id": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the noise config id to be used for the scrape.",
        "ICON_NAME": "Key",
    },
    "filter_config_id": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the filter config id to be used for the scrape.",
        "ICON_NAME": "Key",
    },
}

GET_SCRAPE_HISTORY_URL_DEFINITION = {
    "url": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the url to be scraped.",
        "ICON_NAME": "Link",
    }
}

GET_SCRAPE_HISTORY_TASK_DEFINITION = {
    "scrape_task_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the scrape task id to be scraped.",
        "ICON_NAME": "Key",
    }
}

GET_SCRAPE_TASK_DETAILS_DEFINITION = {
    "scrape_task_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the scrape task id to be scraped.",
        "ICON_NAME": "Key",
    }
}

CREATE_FULL_SITE_SCRAPE_DEFINITION = {
    "urls": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": "validate_scrape_urls",
        "DATA_TYPE": "array",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "ArrayField",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the urls to be scraped.",
        "ICON_NAME": "Link",
    }
}

GET_FULL_SITE_SCRAPE_PROGRESS_DEFINITION = {
    "full_site_scrape_task_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the full site scrape task id to be scraped.",
        "ICON_NAME": "Key",
    }
}

GET_FULL_SITE_SCRAPE_PROGRESS_DETAILED_DEFINITION = {
    "full_site_scrape_task_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the full site scrape task id to be scraped.",
        "ICON_NAME": "Key",
    }
}

FULL_SITE_SCRAPE_TASK_DEFINITION = {
    "full_site_scrape_task_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the full site scrape task id to be scraped.",
        "ICON_NAME": "Key",
    }
}

GET_PARSED_PAGES_DEFINITION = {
    "full_site_scrape_task_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the full site scrape task id to be scraped.",
        "ICON_NAME": "Key",
    },
    "cursor": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the cursor to be used for the scrape.",
        "ICON_NAME": "Key",
    },
    "page_size": {
        "REQUIRED": False,
        "DEFAULT": 1000,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the page size to be used for the scrape.",
        "ICON_NAME": "Key",
    },
}

VIEW_PARSED_PAGE_DEFINITION = {
    "parsed_content_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the parsed content id to be viewed.",
        "ICON_NAME": "Key",
    }
}

CREATE_CONTENT_GROUPING_DEFINITION = {
    "full_site_scrape_task_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the full site scrape task id to be scraped.",
        "ICON_NAME": "Key",
    },
    "content_grouping_config": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "object",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "JsonEditor",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the content grouping config to be used for the scrape.",
        "ICON_NAME": "Bolt",
    },
}

TRACK_CONTENT_GROUPING_DEFINITION = {
    "content_grouping_run_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the content grouping run id to be tracked.",
        "ICON_NAME": "Key",
    }
}

# Task definitions map
SCRAPE_SERVICE_DEFINITIONS = {
    "GET_DOMAINS": GET_DOMAINS_DEFINITION,
    "GET_DOMAIN_CONFIG_BY_ID": GET_DOMAIN_CONFIG_DEFINITION,
    "CREATE_DOMAIN_CONFIG": CREATE_DOMAIN_CONFIG_DEFINITION,
    "UPDATE_DOMAIN_CONFIG": UPDATE_DOMAIN_CONFIG_DEFINITION,
    "CREATE_DOMAIN": CREATE_DOMAIN_DEFINITION,
    "CREATE_INTERACTION_SETTINGS": CREATE_INTERACTION_SETTINGS_DEFINITION,
    "GET_NOISE_CONFIG_BY_ID": GET_NOISE_CONFIG_DEFINITION,
    "GET_NOISE_CONFIGS": GET_NOISE_CONFIGS_DEFINITION,
    "GET_FILTER_CONFIG_BY_ID": GET_FILTER_CONFIG_DEFINITION,
    "GET_FILTER_CONFIGS": GET_FILTER_CONFIGS_DEFINITION,
    "GET_INTERACTION_SETTINGS_BY_ID": GET_INTERACTION_SETTINGS_DEFINITION,
    "CREATE_NOISE_CONFIG": CREATE_NOISE_CONFIG_DEFINITION,
    "CREATE_FILTER_CONFIG": CREATE_FILTER_CONFIG_DEFINITION,
    "SAVE_NOISE_CONFIG": SAVE_NOISE_CONFIG_DEFINITION,
    "SAVE_FILTER_CONFIG": SAVE_FILTER_CONFIG_DEFINITION,
    "SAVE_INTERACTION_SETTINGS": SAVE_INTERACTION_SETTINGS_DEFINITION,
    "QUICK_SCRAPE": QUICK_SCRAPE_DEFINITION,
    "CREATE_SCRAPE_TASKS": CREATE_SCRAPE_TASKS_DEFINITION,
    "SCRAPE_PAGE": SCRAPE_PAGE_DEFINITION,
    "PARSE_RESPONSE_BY_ID": PARSE_RESPONSE_DEFINITION,
    "PARSE_RESPONSES_BY_ID": PARSE_RESPONSES_DEFINITION,
    "GET_SCRAPE_HISTORY_BY_URL": GET_SCRAPE_HISTORY_URL_DEFINITION,
    "GET_SCRAPE_HISTORY_BY_TASK_ID": GET_SCRAPE_HISTORY_TASK_DEFINITION,
    "GET_SCRAPE_TASK_DETAILS": GET_SCRAPE_TASK_DETAILS_DEFINITION,
    "CREATE_FULL_SITE_SCRAPE_TASK": CREATE_FULL_SITE_SCRAPE_DEFINITION,
    "GET_FULL_SITE_SCRAPE_PROGRESS": GET_FULL_SITE_SCRAPE_PROGRESS_DEFINITION,
    "GET_FULL_SITE_SCRAPE_PROGRESS_DETAILED": GET_FULL_SITE_SCRAPE_PROGRESS_DETAILED_DEFINITION,
    "CANCEL_FULL_SITE_SCRAPE_TASK": FULL_SITE_SCRAPE_TASK_DEFINITION,
    "PAUSE_FULL_SITE_SCRAPE_TASK": FULL_SITE_SCRAPE_TASK_DEFINITION,
    "RESUME_FULL_SITE_SCRAPE_TASK": FULL_SITE_SCRAPE_TASK_DEFINITION,
    "GET_PARSED_PAGES": GET_PARSED_PAGES_DEFINITION,
    "VIEW_PARSED_PAGE": VIEW_PARSED_PAGE_DEFINITION,
    "CREATE_CONTENT_GROUPING_RUN": CREATE_CONTENT_GROUPING_DEFINITION,
    "TRACK_CONTENT_GROUPING_RUN": TRACK_CONTENT_GROUPING_DEFINITION,
    "MIC_CHECK": MIC_CHECK_DEFINITION,
}


QUICK_SCRAPE_V2_DEFINITION = {
    "urls": {
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
        "TEST_VALUE": ["https://en.wikipedia.org/wiki/Donald_Trump", "https://titaniumsuccess.com/arman-sadeghi/business-coach/"]
    },
    "get_organized_data": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Get organized json content for the scrape page.",
        "ICON_NAME": "Braces",
        "TEST_VALUE": False
    },
    "get_structured_data": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Get structured data json content for the scrape page.",
        "ICON_NAME": "Braces",
        "TEST_VALUE": False
    },
    "get_overview": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Get overview content for the scraped page. Overview contains basic information for the page like title, other metadata etc.",
        "ICON_NAME": "Target",
        "TEST_VALUE": False
    },
    "get_text_data": {
        "REQUIRED": False,
        "DEFAULT": True,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Get parsed text data for the scraped page. Generated from 'organized data'.",
        "ICON_NAME": "LetterText",
        "TEST_VALUE": True
    },
    "get_main_image": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Get main image for the scraped page. Main image is usually the biggest or most relevant image on the page. Extracted from OG metadata or other meta tags.",
        "ICON_NAME": "Image",
        "TEST_VALUE": True
    },
    "get_links": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Get all the links from the scraped page. Links are categorized as internal, external, document, archive etc.",
        "ICON_NAME": "Link",
        "TEST_VALUE": False
    },
    "get_content_filter_removal_details": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Get list of objects that were ignored during parsing page based on settings.",
        "ICON_NAME": "RemoveFormatting",
        "TEST_VALUE": False
    },
    "include_highlighting_markers": {
        "REQUIRED": False,
        "DEFAULT": True,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Include /exclude highlighting markers like 'underline', 'list markers' etc... from text.",
        "ICON_NAME": "Underline",
        "TEST_VALUE": False
    },
    "include_media": {
        "REQUIRED": False,
        "DEFAULT": True,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Include media content in text output.",
        "ICON_NAME": "TvMinimalPlay",
        "TEST_VALUE": True
    },
    "include_media_links": {
        "REQUIRED": False,
        "DEFAULT": True,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Include media links (image , video, audio) in text. Triggered when include_media is turned on.",
        "ICON_NAME": "Link",
        "TEST_VALUE": True
    },
    "include_media_description": {
        "REQUIRED": False,
        "DEFAULT": True,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Include media description (media caption etc.) in text. Triggers when include_media is turned on.",
        "ICON_NAME": "WholeWord",
        "TEST_VALUE": True
    },
    "include_anchors": {
        "REQUIRED": False,
        "DEFAULT": True,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Include hyperlinks in scraped text",
        "ICON_NAME": "ExternalLink",
        "TEST_VALUE": True
    },
    "anchor_size": {
        "REQUIRED": False,
        "DEFAULT": 100,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {"min": 10, "max": 500},
        "DESCRIPTION": "Size of hyperlinks in scraped text",
        "ICON_NAME": "Ruler",
        "TEST_VALUE": 100
    }
}


QUICK_SCRAPE_V2_STREAM_DEFINITION = {
    "urls": {
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
        "TEST_VALUE": ["https://en.wikipedia.org/wiki/Donald_Trump", "https://titaniumsuccess.com/arman-sadeghi/business-coach/"]
    },
    "get_organized_data": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Get organized json content for the scrape page.",
        "ICON_NAME": "Braces",
        "TEST_VALUE": False
    },
    "get_structured_data": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Get structured data json content for the scrape page.",
        "ICON_NAME": "Braces",
        "TEST_VALUE": False
    },
    "get_overview": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Get overview content for the scraped page. Overview contains basic information for the page like title, other metadata etc.",
        "ICON_NAME": "Target",
        "TEST_VALUE": False
    },
    "get_text_data": {
        "REQUIRED": False,
        "DEFAULT": True,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Get parsed text data for the scraped page. Generated from 'organized data'.",
        "ICON_NAME": "LetterText",
        "TEST_VALUE": True
    },
    "get_main_image": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Get main image for the scraped page. Main image is usually the biggest or most relevant image on the page. Extracted from OG metadata or other meta tags.",
        "ICON_NAME": "Image",
        "TEST_VALUE": True
    },
    "get_links": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Get all the links from the scraped page. Links are categorized as internal, external, document, archive etc.",
        "ICON_NAME": "Link",
        "TEST_VALUE": False
    },
    "get_content_filter_removal_details": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Get list of objects that were ignored during parsing page based on settings.",
        "ICON_NAME": "RemoveFormatting",
        "TEST_VALUE": False
    },
    "include_highlighting_markers": {
        "REQUIRED": False,
        "DEFAULT": True,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Include /exclude highlighting markers like 'underline', 'list markers' etc... from text.",
        "ICON_NAME": "Underline",
        "TEST_VALUE": False
    },
    "include_media": {
        "REQUIRED": False,
        "DEFAULT": True,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Include media content in text output.",
        "ICON_NAME": "TvMinimalPlay",
        "TEST_VALUE": True
    },
    "include_media_links": {
        "REQUIRED": False,
        "DEFAULT": True,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Include media links (image , video, audio) in text. Triggered when include_media is turned on.",
        "ICON_NAME": "Link",
        "TEST_VALUE": True
    },
    "include_media_description": {
        "REQUIRED": False,
        "DEFAULT": True,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Include media description (media caption etc.) in text. Triggers when include_media is turned on.",
        "ICON_NAME": "WholeWord",
        "TEST_VALUE": True
    },
    "include_anchors": {
        "REQUIRED": False,
        "DEFAULT": True,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Include hyperlinks in scraped text",
        "ICON_NAME": "ExternalLink",
        "TEST_VALUE": True
    },
    "anchor_size": {
        "REQUIRED": False,
        "DEFAULT": 100,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {"min": 10, "max": 500},
        "DESCRIPTION": "Size of hyperlinks in scraped text",
        "ICON_NAME": "Ruler",
        "TEST_VALUE": 100
    }

}


SEARCH_AND_SCRAPE_DEFINITION = {
    "keywords": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "array",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "ArrayField",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the queries to search for.",
        "ICON_NAME": "WholeWord",
        "TEST_VALUE": [ "apple stock price", "apple stock best time to buy" , "apple stock forecast"]
    },
    "country_code": {
        "REQUIRED": False,
        "DEFAULT": "all",
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Select",
        "COMPONENT_PROPS": {
            "options": [
                {"label": "Argentina", "value": "AR"},
                {"label": "Australia", "value": "AU"},
                {"label": "Austria", "value": "AT"},
                {"label": "Belgium", "value": "BE"},
                {"label": "Brazil", "value": "BR"},
                {"label": "Canada", "value": "CA"},
                {"label": "Chile", "value": "CL"},
                {"label": "Denmark", "value": "DK"},
                {"label": "Finland", "value": "FI"},
                {"label": "France", "value": "FR"},
                {"label": "Germany", "value": "DE"},
                {"label": "Hong Kong", "value": "HK"},
                {"label": "India", "value": "IN"},
                {"label": "Indonesia", "value": "ID"},
                {"label": "Italy", "value": "IT"},
                {"label": "Japan", "value": "JP"},
                {"label": "Korea", "value": "KR"},
                {"label": "Malaysia", "value": "MY"},
                {"label": "Mexico", "value": "MX"},
                {"label": "Netherlands", "value": "NL"},
                {"label": "New Zealand", "value": "NZ"},
                {"label": "Norway", "value": "NO"},
                {"label": "Peoples Republic of China", "value": "CN"},
                {"label": "Poland", "value": "PL"},
                {"label": "Portugal", "value": "PT"},
                {"label": "Republic of the Philippines", "value": "PH"},
                {"label": "Russia", "value": "RU"},
                {"label": "Saudi Arabia", "value": "SA"},
                {"label": "South Africa", "value": "ZA"},
                {"label": "Spain", "value": "ES"},
                {"label": "Sweden", "value": "SE"},
                {"label": "Switzerland", "value": "CH"},
                {"label": "Taiwan", "value": "TW"},
                {"label": "Turkey", "value": "TR"},
                {"label": "United Kingdom", "value": "GB"},
                {"label": "United States", "value": "US"},
                {"label": "All Regions", "value": "ALL"},
            ]
        },
        "DESCRIPTION": "Enter the country code to get search results for.",
        "ICON_NAME": "Flag",
        "TEST_VALUE": "US"
    },
    "total_results_per_keyword": {
        "REQUIRED": False,
        "DEFAULT": 10,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "slider",
        "COMPONENT_PROPS": {"min": 10, "max": 30, "step": 1, "range": "False"},
        "DESCRIPTION": "Enter the number of results per keyword to get.",
        "ICON_NAME": "SlidersHorizontal",
        "TEST_VALUE": 10
    },
    "search_type": {
        "REQUIRED": False,
        "DEFAULT": "all",
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "RadioGroup",
        "COMPONENT_PROPS": {"options": [{"label": "All", "value": "all"}, {"label": "Web", "value": "web"}, {"label": "News", "value": "news"}], "orientation": "vertical"},
        "DESCRIPTION": "Kind of search type to scrape, 'web', 'news', or 'all'.",
        "ICON_NAME": "Rss",
    },
    "get_organized_data": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Get organized json content for the scrape page.",
        "ICON_NAME": "Braces",
        "TEST_VALUE": False
    },
    "get_structured_data": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Get structured data json content for the scrape page.",
        "ICON_NAME": "Braces",
        "TEST_VALUE": False
    },
    "get_overview": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Get overview content for the scraped page. Overview contains basic information for the page like title, other metadata etc.",
        "ICON_NAME": "Target",
        "TEST_VALUE": False
    },
    "get_text_data": {
        "REQUIRED": False,
        "DEFAULT": True,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Get parsed text data for the scraped page. Generated from 'organized data'.",
        "ICON_NAME": "LetterText",
        "TEST_VALUE": True
    },
    "get_main_image": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Get main image for the scraped page. Main image is usually the biggest or most relevant image on the page. Extracted from OG metadata or other meta tags.",
        "ICON_NAME": "Image",
        "TEST_VALUE": True
    },
    "get_links": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Get all the links from the scraped page. Links are categorized as internal, external, document, archive etc.",
        "ICON_NAME": "Link",
        "TEST_VALUE": False
    },
    "get_content_filter_removal_details": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Get list of objects that were ignored during parsing page based on settings.",
        "ICON_NAME": "RemoveFormatting",
        "TEST_VALUE": False
    },
    "include_highlighting_markers": {
        "REQUIRED": False,
        "DEFAULT": True,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Include /exclude highlighting markers like 'underline', 'list markers' etc... from text.",
        "ICON_NAME": "Underline",
        "TEST_VALUE": False
    },
    "include_media": {
        "REQUIRED": False,
        "DEFAULT": True,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Include media content in text output.",
        "ICON_NAME": "TvMinimalPlay",
        "TEST_VALUE": True
    },
    "include_media_links": {
        "REQUIRED": False,
        "DEFAULT": True,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Include media links (image , video, audio) in text. Triggered when include_media is turned on.",
        "ICON_NAME": "Link",
        "TEST_VALUE": True
    },
    "include_media_description": {
            "REQUIRED": False,
            "DEFAULT": True,
            "VALIDATION": None,
            "DATA_TYPE": "boolean",
            "CONVERSION": None,
            "REFERENCE": None,
            "COMPONENT": "Switch",
            "COMPONENT_PROPS": {},
            "DESCRIPTION": "Include media description (media caption etc.) in text. Triggers when include_media is turned on.",
            "ICON_NAME": "WholeWord",
            "TEST_VALUE": True
        },
    "include_anchors":{
            "REQUIRED": False,
            "DEFAULT": True,
            "VALIDATION": None,
            "DATA_TYPE": "boolean",
            "CONVERSION": None,
            "REFERENCE": None,
            "COMPONENT": "Switch",
            "COMPONENT_PROPS": {},
            "DESCRIPTION": "Include hyperlinks in scraped text",
            "ICON_NAME": "ExternalLink",
            "TEST_VALUE": True
        },
    "anchor_size": {
            "REQUIRED": False,
            "DEFAULT": 100,
            "VALIDATION": None,
            "DATA_TYPE": "integer",
            "CONVERSION": None,
            "REFERENCE": None,
            "COMPONENT": "NumberInput",
            "COMPONENT_PROPS": {"min": 10, "max": 500},
            "DESCRIPTION": "Size of hyperlinks in scraped text",
            "ICON_NAME": "Ruler",
            "TEST_VALUE": 100
        }
}


SEARCH_KEYWORDS_DEFINITION ={
    "keywords": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "array",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "arrayField",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the queries to search for.",
        "ICON_NAME": "WholeWord",
        "TEST_VALUE": [ "apple stock price", "apple stock best time to buy" , "apple stock forecast"]
    },
    "country_code": {
        "REQUIRED": False,
        "DEFAULT": "all",
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Select",
        "COMPONENT_PROPS": {
            "options": [
                {"label": "Argentina", "value": "AR"},
                {"label": "Australia", "value": "AU"},
                {"label": "Austria", "value": "AT"},
                {"label": "Belgium", "value": "BE"},
                {"label": "Brazil", "value": "BR"},
                {"label": "Canada", "value": "CA"},
                {"label": "Chile", "value": "CL"},
                {"label": "Denmark", "value": "DK"},
                {"label": "Finland", "value": "FI"},
                {"label": "France", "value": "FR"},
                {"label": "Germany", "value": "DE"},
                {"label": "Hong Kong", "value": "HK"},
                {"label": "India", "value": "IN"},
                {"label": "Indonesia", "value": "ID"},
                {"label": "Italy", "value": "IT"},
                {"label": "Japan", "value": "JP"},
                {"label": "Korea", "value": "KR"},
                {"label": "Malaysia", "value": "MY"},
                {"label": "Mexico", "value": "MX"},
                {"label": "Netherlands", "value": "NL"},
                {"label": "New Zealand", "value": "NZ"},
                {"label": "Norway", "value": "NO"},
                {"label": "Peoples Republic of China", "value": "CN"},
                {"label": "Poland", "value": "PL"},
                {"label": "Portugal", "value": "PT"},
                {"label": "Republic of the Philippines", "value": "PH"},
                {"label": "Russia", "value": "RU"},
                {"label": "Saudi Arabia", "value": "SA"},
                {"label": "South Africa", "value": "ZA"},
                {"label": "Spain", "value": "ES"},
                {"label": "Sweden", "value": "SE"},
                {"label": "Switzerland", "value": "CH"},
                {"label": "Taiwan", "value": "TW"},
                {"label": "Turkey", "value": "TR"},
                {"label": "United Kingdom", "value": "GB"},
                {"label": "United States", "value": "US"},
                {"label": "All Regions", "value": "ALL"},
            ]
        },
        "DESCRIPTION": "Enter the country code to get search results for.",
        "ICON_NAME": "Flag",
        "TEST_VALUE": "US"
    },
    "total_results_per_keyword": {
        "REQUIRED": False,
        "DEFAULT": 5,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "slider",
        "COMPONENT_PROPS": {"min": 1, "max": 100, "step": 1, "range": "False"},
        "DESCRIPTION": "Enter the number of results per keyword to get. Note: Total results per keyword may deviate from this number due to the search engine results.",
        "ICON_NAME": "SlidersHorizontal",
        "TEST_VALUE": 5
    },
    "search_type": {
        "REQUIRED": False,
        "DEFAULT": "All",
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "RadioGroup",
        "COMPONENT_PROPS": {"options": [{"label": "All", "value": "all"}, {"label": "Web", "value": "web"}, {"label": "News", "value": "news"}], "orientation": "vertical"},
        "DESCRIPTION": "Kind of search type to scrape, 'web', 'news', or 'all'.",
        "ICON_NAME": "Rss",
    },
}


SEARCH_AND_SCRAPE_LIMITED_DEFINITION = {
    "keyword": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter query to search and get results for.",
        "ICON_NAME": "WholeWord",
        "TEST_VALUE": "apple stock price"
    },
    "country_code": {
        "REQUIRED": False,
        "DEFAULT": "all",
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Select",
        "COMPONENT_PROPS": {
            "options": [
                {"label": "Argentina", "value": "AR"},
                {"label": "Australia", "value": "AU"},
                {"label": "Austria", "value": "AT"},
                {"label": "Belgium", "value": "BE"},
                {"label": "Brazil", "value": "BR"},
                {"label": "Canada", "value": "CA"},
                {"label": "Chile", "value": "CL"},
                {"label": "Denmark", "value": "DK"},
                {"label": "Finland", "value": "FI"},
                {"label": "France", "value": "FR"},
                {"label": "Germany", "value": "DE"},
                {"label": "Hong Kong", "value": "HK"},
                {"label": "India", "value": "IN"},
                {"label": "Indonesia", "value": "ID"},
                {"label": "Italy", "value": "IT"},
                {"label": "Japan", "value": "JP"},
                {"label": "Korea", "value": "KR"},
                {"label": "Malaysia", "value": "MY"},
                {"label": "Mexico", "value": "MX"},
                {"label": "Netherlands", "value": "NL"},
                {"label": "New Zealand", "value": "NZ"},
                {"label": "Norway", "value": "NO"},
                {"label": "Peoples Republic of China", "value": "CN"},
                {"label": "Poland", "value": "PL"},
                {"label": "Portugal", "value": "PT"},
                {"label": "Republic of the Philippines", "value": "PH"},
                {"label": "Russia", "value": "RU"},
                {"label": "Saudi Arabia", "value": "SA"},
                {"label": "South Africa", "value": "ZA"},
                {"label": "Spain", "value": "ES"},
                {"label": "Sweden", "value": "SE"},
                {"label": "Switzerland", "value": "CH"},
                {"label": "Taiwan", "value": "TW"},
                {"label": "Turkey", "value": "TR"},
                {"label": "United Kingdom", "value": "GB"},
                {"label": "United States", "value": "US"},
                {"label": "All Regions", "value": "ALL"},
            ]
        },
        "DESCRIPTION": "Enter the country code to get search results for.",
        "ICON_NAME": "Flag",
        "TEST_VALUE": "US"
    },
    "max_page_read": {
        "REQUIRED": False,
        "DEFAULT": 10,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "slider",
        "COMPONENT_PROPS": {"min": 1, "max": 20, "step": 1, "range": "False"},
        "DESCRIPTION": "Enter the number of results per keyword to get.",
        "ICON_NAME": "SlidersHorizontal",
        "TEST_VALUE": 5
    },
    "search_type": {
        "REQUIRED": False,
        "DEFAULT": "all",
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "RadioGroup",
        "COMPONENT_PROPS": {"options": [{"label": "All", "value": "all"}, {"label": "Web", "value": "web"}, {"label": "News", "value": "news"}], "orientation": "vertical"},
        "DESCRIPTION": "Kind of search type to scrape, 'web', 'news', or 'all'.",
        "ICON_NAME": "Rss",
    },
    "get_organized_data": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Get organized json content for the scrape page.",
        "ICON_NAME": "Braces",
        "TEST_VALUE": False
    },
    "get_structured_data": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Get structured data json content for the scrape page.",
        "ICON_NAME": "Braces",
        "TEST_VALUE": False
    },
    "get_overview": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Get overview content for the scraped page. Overview contains basic information for the page like title, other metadata etc.",
        "ICON_NAME": "Target",
        "TEST_VALUE": False
    },
    "get_text_data": {
        "REQUIRED": False,
        "DEFAULT": True,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Get parsed text data for the scraped page. Generated from 'organized data'.",
        "ICON_NAME": "LetterText",
        "TEST_VALUE": True
    },
    "get_main_image": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Get main image for the scraped page. Main image is usually the biggest or most relevant image on the page. Extracted from OG metadata or other meta tags.",
        "ICON_NAME": "Image",
        "TEST_VALUE": True
    },
    "get_links": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Get all the links from the scraped page. Links are categorized as internal, external, document, archive etc.",
        "ICON_NAME": "Link",
        "TEST_VALUE": False
    },
    "get_content_filter_removal_details": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Get list of objects that were ignored during parsing page based on settings.",
        "ICON_NAME": "RemoveFormatting",
        "TEST_VALUE": False
    },
    "include_highlighting_markers": {
        "REQUIRED": False,
        "DEFAULT": True,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Include /exclude highlighting markers like 'underline', 'list markers' etc... from text.",
        "ICON_NAME": "Underline",
        "TEST_VALUE": False
    },
    "include_media": {
        "REQUIRED": False,
        "DEFAULT": True,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Include media content in text output.",
        "ICON_NAME": "TvMinimalPlay",
        "TEST_VALUE": True
    },
    "include_media_links": {
        "REQUIRED": False,
        "DEFAULT": True,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Include media links (image , video, audio) in text. Triggered when include_media is turned on.",
        "ICON_NAME": "Link",
        "TEST_VALUE": True
    },
    "include_media_description": {
            "REQUIRED": False,
            "DEFAULT": True,
            "VALIDATION": None,
            "DATA_TYPE": "boolean",
            "CONVERSION": None,
            "REFERENCE": None,
            "COMPONENT": "Switch",
            "COMPONENT_PROPS": {},
            "DESCRIPTION": "Include media description (media caption etc.) in text. Triggers when include_media is turned on.",
            "ICON_NAME": "WholeWord",
            "TEST_VALUE": True
        },
    "include_anchors":{
            "REQUIRED": False,
            "DEFAULT": True,
            "VALIDATION": None,
            "DATA_TYPE": "boolean",
            "CONVERSION": None,
            "REFERENCE": None,
            "COMPONENT": "Switch",
            "COMPONENT_PROPS": {},
            "DESCRIPTION": "Include hyperlinks in scraped text",
            "ICON_NAME": "ExternalLink",
            "TEST_VALUE": True
        },
    "anchor_size": {
            "REQUIRED": False,
            "DEFAULT": 100,
            "VALIDATION": None,
            "DATA_TYPE": "integer",
            "CONVERSION": None,
            "REFERENCE": None,
            "COMPONENT": "NumberInput",
            "COMPONENT_PROPS": {"min": 10, "max": 500},
            "DESCRIPTION": "Size of hyperlinks in scraped text",
            "ICON_NAME": "Ruler",
            "TEST_VALUE": 100
        }
}



SCRAPER_SERVICE_V2_DEFINITIONS = {
    "QUICK_SCRAPE": QUICK_SCRAPE_V2_DEFINITION,
    "QUICK_SCRAPE_STREAM": QUICK_SCRAPE_V2_STREAM_DEFINITION,
    "SEARCH_AND_SCRAPE": SEARCH_AND_SCRAPE_DEFINITION,
    "SEARCH_KEYWORDS": SEARCH_KEYWORDS_DEFINITION,
    "SEARCH_AND_SCRAPE_LIMITED": SEARCH_AND_SCRAPE_LIMITED_DEFINITION,
    "MIC_CHECK": MIC_CHECK_DEFINITION,
}

# California's workers compensation

# 1. Create WC Claim Task Definition
CREATE_WC_CLAIM_DEFINITION = {
    "date_of_injury": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": "validate_date",
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "TextInput",
        "COMPONENT_PROPS": {"placeholder": "YYYY-MM-DD"},
        "DESCRIPTION": "Date of injury in YYYY-MM-DD format",
        "ICON_NAME": "Calendar"
    },
    "date_of_birth": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": "validate_date",
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "TextInput",
        "COMPONENT_PROPS": {"placeholder": "YYYY-MM-DD"},
        "DESCRIPTION": "Date of birth in YYYY-MM-DD format",
        "ICON_NAME": "Calendar"
    },
    "age_at_doi": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {"min": 0, "max": 120},
        "DESCRIPTION": "Age at the date of injury",
        "ICON_NAME": "Hash"
    },
    "occupational_code": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Occupational code",
        "ICON_NAME": "Briefcase"
    },
    "weekly_earnings": {
        "REQUIRED": False,
        "DEFAULT": 290.0,
        "VALIDATION": None,
        "DATA_TYPE": "float",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {"step": 0.01, "min": 0},
        "DESCRIPTION": "Weekly earnings in dollars",
        "ICON_NAME": "DollarSign"
    },
    "applicant_name": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "TextInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Full name of the applicant",
        "ICON_NAME": "User"
    }
}

# 2. Create WC Report Task Definition
CREATE_WC_REPORT_DEFINITION = {
    "claim_id": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "TextInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "ID of the associated claim",
        "ICON_NAME": "FileText"
    }
}

# 3. Create WC Injury Task Definition
CREATE_WC_INJURY_DEFINITION = {
    "report_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "TextInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "ID of the associated report",
        "ICON_NAME": "FileText"
    },
    "impairment_definition_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "TextInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "ID of the impairment definition",
        "ICON_NAME": "FileText"
    },
    "digit": {
        "REQUIRED": False,
        "DEFAULT": 0,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {"min": 0},
        "DESCRIPTION": "Digit impairment rating",
        "ICON_NAME": "Hash"
    },
    "wpi": {
        "REQUIRED": False,
        "DEFAULT": 0,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {"min": 0, "max": 100},
        "DESCRIPTION": "Whole person impairment percentage",
        "ICON_NAME": "Hash"
    },
    "le": {
        "REQUIRED": False,
        "DEFAULT": 0,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {"min": 0},
        "DESCRIPTION": "Lower extremity impairment rating",
        "ICON_NAME": "Hash"
    },
    "ue": {
        "REQUIRED": False,
        "DEFAULT": 0,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {"min": 0},
        "DESCRIPTION": "Upper extremity impairment rating",
        "ICON_NAME": "Hash"
    },
    "industrial": {
        "REQUIRED": False,
        "DEFAULT": 100,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {"min": 0, "max": 100},
        "DESCRIPTION": "Industrial apportionment percentage",
        "ICON_NAME": "Hash"
    },
    "pain": {
        "REQUIRED": False,
        "DEFAULT": 0,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {"min": 0},
        "DESCRIPTION": "Pain add-on rating",
        "ICON_NAME": "Hash"
    },
    "side": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": "validate_wc_side",
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Select",
        "COMPONENT_PROPS": {
            "options": [
                {"label": "Left", "value": "left"},
                {"label": "Right", "value": "right"},
                {"label": "Bilateral", "value": "bilateral"}
            ]
        },
        "DESCRIPTION": "Side of the injury (left, right, or bilateral)",
        "ICON_NAME": "ArrowLeftRight"
    }
}

# 4. Calculate WC Ratings Task Definition
CALCULATE_WC_RATINGS_DEFINITION = {
    "report_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "TextInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "ID of the report to calculate ratings for",
        "ICON_NAME": "FileText"
    }
}

# 5. Edit WC Claim Task Definition
EDIT_WC_CLAIM_DEFINITION = {
    "claim_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "TextInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "ID of the claim to edit",
        "ICON_NAME": "FileText"
    },
    "date_of_injury": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": "validate_date",
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "TextInput",
        "COMPONENT_PROPS": {"placeholder": "YYYY-MM-DD"},
        "DESCRIPTION": "Updated date of injury in YYYY-MM-DD format",
        "ICON_NAME": "Calendar"
    },
    "date_of_birth": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": "validate_date",
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "TextInput",
        "COMPONENT_PROPS": {"placeholder": "YYYY-MM-DD"},
        "DESCRIPTION": "Updated date of birth in YYYY-MM-DD format",
        "ICON_NAME": "Calendar"
    },
    "age_at_doi": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {"min": 0, "max": 120},
        "DESCRIPTION": "Updated age at the date of injury",
        "ICON_NAME": "Hash"
    },
    "occupational_code": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Updated occupational code",
        "ICON_NAME": "Briefcase"
    },
    "weekly_earnings": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "float",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {"step": 0.01, "min": 0},
        "DESCRIPTION": "Updated weekly earnings in dollars",
        "ICON_NAME": "DollarSign"
    },
    "applicant_name": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "TextInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Updated full name of the applicant",
        "ICON_NAME": "User"
    }
}

# 6. Edit WC Injury Task Definition
EDIT_WC_INJURY_DEFINITION = {
    "injury_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "TextInput",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "ID of the injury to edit",
        "ICON_NAME": "FileText"
    },
    "digit": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {"min": 0},
        "DESCRIPTION": "Updated digit impairment rating",
        "ICON_NAME": "Hash"
    },
    "wpi": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {"min": 0, "max": 100},
        "DESCRIPTION": "Updated whole person impairment percentage",
        "ICON_NAME": "Hash"
    },
    "le": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {"min": 0},
        "DESCRIPTION": "Updated lower extremity impairment rating",
        "ICON_NAME": "Hash"
    },
    "ue": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {"min": 0},
        "DESCRIPTION": "Updated upper extremity impairment rating",
        "ICON_NAME": "Hash"
    },
    "industrial": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {"min": 0, "max": 100},
        "DESCRIPTION": "Updated industrial apportionment percentage",
        "ICON_NAME": "Hash"
    },
    "pain": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {"min": 0},
        "DESCRIPTION": "Updated pain add-on rating",
        "ICON_NAME": "Hash"
    },
    "side": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": "validate_wc_side",
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Select",
        "COMPONENT_PROPS": {
            "options": [
                {"label": "Left", "value": "left"},
                {"label": "Right", "value": "right"},
                {"label": "Bilateral", "value": "bilateral"}
            ]
        },
        "DESCRIPTION": "Updated side of the injury (left, right, or bilateral)",
        "ICON_NAME": "ArrowLeftRight"
    }
}

CALIFORNIA_WORKER_COMP_SERVICE_DEFINITIONS = {
    "CREATE_WC_CLAIM": CREATE_WC_CLAIM_DEFINITION,
    "CREATE_WC_REPORT": CREATE_WC_REPORT_DEFINITION,
    "CREATE_WC_INJURY": CREATE_WC_INJURY_DEFINITION,
    "CALCULATE_WC_RATINGS": CALCULATE_WC_RATINGS_DEFINITION,
    "EDIT_WC_CLAIM": EDIT_WC_CLAIM_DEFINITION,
    "EDIT_WC_INJURY": EDIT_WC_INJURY_DEFINITION,
    "MIC_CHECK": MIC_CHECK_DEFINITION,
}

################### Scrape related content end #########################


MESSAGE_OBJECT_DEFINITION = {
    "id": {
        "REQUIRED": False,
        "DEFAULT": "",
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Key",
        "DESCRIPTION": "Enter the message id.",
    },
    "conversation_id": {
        "REQUIRED": False,
        "DEFAULT": "",
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Key",
        "DESCRIPTION": "Enter the conversation id.",
    },
    "content": {
        "REQUIRED": False,
        "DEFAULT": "",
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "textarea",
        "COMPONENT_PROPS": {
            "rows": 10,
        },
        "ICON_NAME": "Text",
        "DESCRIPTION": "Enter the message content.",
    },
    "role": {
        "REQUIRED": False,
        "DEFAULT": "",
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Select",
        "COMPONENT_PROPS": {
            "options": [
                {"label": "User", "value": "user"},
                {"label": "Assistant", "value": "assistant"},
                {"label": "System", "value": "system"},
                {"label": "Tool", "value": "tool"},
            ],
        },
        "ICON_NAME": "User",
        "DESCRIPTION": "Enter the message role. (user, assistant, system, tool)",
    },
    "type": {
        "REQUIRED": False,
        "DEFAULT": "",
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Select",
        "COMPONENT_PROPS": {
            "options": [
                {"label": "Text", "value": "text"},
                {"label": "Tool Call", "value": "tool_call"},
                {"label": "Mixed", "value": "mixed"},
            ],
        },
        "ICON_NAME": "Type",
        "DESCRIPTION": "Enter the message type. (text, tool_call, mixed)",
    },
    "files": {
        "REQUIRED": False,
        "DEFAULT": [],
        "VALIDATION": None,
        "DATA_TYPE": "array",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "MultiFileUpload",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Files",
        "DESCRIPTION": "Public urls for files to be associated with the message.",
    },
    "metadata": {
        "REQUIRED": False,
        "DEFAULT": {},
        "VALIDATION": None,
        "DATA_TYPE": "object",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "JsonEditor",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Metadata",
        "DESCRIPTION": "Metadata for the message.",
    },
}

AI_CHAT_DEFINITION = {
    "conversation_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Key",
        "DESCRIPTION": "Enter the conversation id.",
    },
    "message_object": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "object",
        "CONVERSION": "convert_message_object",
        "REFERENCE": MESSAGE_OBJECT_DEFINITION,
        "COMPONENT": "relatedObject",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Messages",
        "DESCRIPTION": "Enter the message object with message id, conversation id, content, role, type, and files.",
    },
}

PREP_CONVERSATION_DEFINITION = {
    "conversation_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Key",
        "DESCRIPTION": "Enter the ID of the conversation to be fetched, cached and ready for fast usage.",
    }
}


GET_NEEDED_RECIPE_BROKERS_DEFINITION = {
    "recipe_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the ID of the recipe to be fetched, cached and ready for fast usage.",
        "ICON_NAME": "Key",
        "TEST_VALUE": "e2049ce6-c340-4ff7-987e-deb24a977853",
    },
    "version": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Key",
        "DESCRIPTION": "Enter the version of the recipe or blank to get the latest version.",
    },
}

RUN_CHAT_RECIPE_DEFINITION = {
    "recipe_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the ID of the recipe to be fetched, cached and ready for fast usage.",
        "ICON_NAME": "Key",
        "TEST_VALUE": "e2049ce6-c340-4ff7-987e-deb24a977853"
    },
    "version": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Key",
        "DESCRIPTION": "Enter the version of the recipe or blank to get the latest version.",
    },
    "broker_values": {
        "REQUIRED": False,
        "DEFAULT": [],
        "VALIDATION": None,
        "DATA_TYPE": "array",
        "CONVERSION": "convert_broker_data",
        "REFERENCE": BROKER_DEFINITION,
        "COMPONENT": "relatedArrayObject",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the broker values to be used in the recipe.",
        "ICON_NAME": "Parentheses",
    },
    "user_id": {
        "REQUIRED": False,
        "DEFAULT": "socket_internal_user_id",
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "",
        "DESCRIPTION": "",
    },
    "prepare_for_next_call": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "FastForward ",
        "DESCRIPTION": "Determines if the results should be saved as a new conversation.",
    },
    "save_new_conversation": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Save",
        "DESCRIPTION": "Determines if the results should be saved as a new conversation.",
    },
    "include_classified_output": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Checkbox",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Shapes",
        "DESCRIPTION": "Determines if the classified output should be included in the response.",
    },
    "model_override": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Key",
        "DESCRIPTION": "Enter the ID of the AI Model or leave blank to use the default model.",
    },
    "tools_override": {
        "REQUIRED": False,
        "DEFAULT": [],
        "VALIDATION": None,
        "DATA_TYPE": "array",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "arrayField",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "PocketKnife",
        "DESCRIPTION": "Enter a list of tool names to be used in the call, which will override the tools defined in the recipe.",
    },
    "allow_default_values": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Checkbox",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "SwatchBook",
        "DESCRIPTION": "Determines if the default values can be used for brokers which are not provided or are not ready.",
    },
    "allow_removal_of_unmatched": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "BadgeX",
        "DESCRIPTION": "Determines if brokers which are not provided or are not ready should be removed from the input content prior to the call.",
    },
}

CHAT_CONFIG_DEFINITION = {
    "recipe_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Key",
        "TEST_VALUE": "e2049ce6-c340-4ff7-987e-deb24a977853",
        "DESCRIPTION": "Enter the ID of the recipe to be fetched, cached and ready for fast usage.",
    },
    "version": {
        "REQUIRED": False,
        "DEFAULT": "latest",
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Key",
        "TEST_VALUE": "latest",
        "DESCRIPTION": "Enter the version of the recipe or blank to get the latest version.",
    },
    "user_id": {
        "REQUIRED": False,
        "DEFAULT": "socket_internal_user_id",
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "",
        "DESCRIPTION": "",
    },
    "prepare_for_next_call": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Key",
        "DESCRIPTION": "Determines if the results should be saved as a new conversation.",
    },
    "save_new_conversation": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Key",
        "DESCRIPTION": "Determines if the results should be saved as a new conversation.",
    },
    "include_classified_output": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Checkbox",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Key",
        "DESCRIPTION": "Determines if the classified output should be included in the response.",
    },
    "model_override": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Key",
        "TEST_VALUE": "10168527-4d6b-456f-ab07-a889223ba3a9",
        "DESCRIPTION": "Enter the ID of the AI Model or leave blank to use the default model.",
    },
    "tools_override": {
        "REQUIRED": False,
        "DEFAULT": [],
        "VALIDATION": None,
        "DATA_TYPE": "array",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "arrayField",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "PocketKnife",
        "DESCRIPTION": "Enter a list of tool names to be used in the call, which will override the tools defined in the recipe.",
    },
    "allow_default_values": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Key",
        "DESCRIPTION": "Determines if the default values can be used for brokers which are not provided or are not ready.",
    },
    "allow_removal_of_unmatched": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Checkbox",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Key",
        "DESCRIPTION": "Determines if brokers which are not provided or are not ready should be removed from the input content prior to the call.",
    },
}

RECIPE_TO_CHAT_DEFINITION = {
    "chat_config": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "object",
        "CONVERSION": None,
        "REFERENCE": CHAT_CONFIG_DEFINITION,
        "COMPONENT": "relatedObject",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Settings",
        "DESCRIPTION": "Enter the chat config to be used in the recipe.",
    },
    "broker_values": {
        "REQUIRED": False,
        "DEFAULT": [],
        "VALIDATION": None,
        "DATA_TYPE": "array",
        "CONVERSION": "convert_broker_data",
        "REFERENCE": BROKER_DEFINITION,
        "COMPONENT": "relatedArrayObject",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the broker values to be used in the recipe.",
        "ICON_NAME": "Parentheses",
    },
}


BATCH_RECIPE_DEFINITION = {
    "chat_configs": {
        "REQUIRED": True,
        "DEFAULT": [],
        "VALIDATION": None,
        "DATA_TYPE": "array",
        "CONVERSION": None,
        "REFERENCE": CHAT_CONFIG_DEFINITION,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Key",
        "DESCRIPTION": "Enter the chat configs to be used in the recipe.",
    },
    "broker_values": {
        "REQUIRED": False,
        "DEFAULT": [],
        "VALIDATION": None,
        "DATA_TYPE": "array",
        "CONVERSION": "convert_broker_data",
        "REFERENCE": BROKER_DEFINITION,
        "COMPONENT": "relatedArrayObject",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the broker values to be used in the recipe.",
        "ICON_NAME": "Parentheses",
    },
    "max_count": {
        "REQUIRED": False,
        "DEFAULT": 3,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Sigma",
        "DESCRIPTION": "Enter the maximum number of chats to be created.",
    },
}

CONVERT_RECIPE_TO_CHAT_DEFINITION = {
    "chat_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Key",
        "DESCRIPTION": "Enter the ID of the chat to be converted to a recipe.",
    },
}

CONVERT_NORMALIZED_DATA_TO_USER_DATA_DEFINITION = {
    "data": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "object",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "JsonEditor",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Grid2x2Plus",
        "DESCRIPTION": "Enter a JSON object with normalized keys and values.",
    },
    "table_name": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Baseline",
        "DESCRIPTION": "Enter the name of the table to be created.",
    },
    "table_description": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Text",
        "DESCRIPTION": "Enter the description of the table to be created.",
    },
}

AI_CHAT_SERVICE_DEFINITIONS = {
    "RUN_RECIPE_TO_CHAT": RECIPE_TO_CHAT_DEFINITION,
    "RUN_BATCH_RECIPE": BATCH_RECIPE_DEFINITION,
    "PREPARE_BATCH_RECIPE": BATCH_RECIPE_DEFINITION,
    "CONVERT_NORMALIZED_DATA_TO_USER_DATA": CONVERT_NORMALIZED_DATA_TO_USER_DATA_DEFINITION,
    "MIC_CHECK": MIC_CHECK_DEFINITION,
}


CHAT_SERVICE_DEFINITIONS = {
    "AI_CHAT": AI_CHAT_DEFINITION,
    "PREP_CONVERSATION": PREP_CONVERSATION_DEFINITION,
    "GET_NEEDED_RECIPE_BROKERS": GET_NEEDED_RECIPE_BROKERS_DEFINITION,
    "RUN_CHAT_RECIPE": RUN_CHAT_RECIPE_DEFINITION,
    "MIC_CHECK": MIC_CHECK_DEFINITION,
}

COCKPIT_SERVICE_DEFINITIONS = {
    "COCKPIT_INSTANT": COCKPIT_INSTANT_DEFINITION,
    "RUN_RECIPE": RUN_RECIPE_DEFINITION,
    "RUN_COMPILED_RECIPE": RUN_COMPILED_RECIPE_DEFINITION,
    "ADD_RECIPE": ADD_RECIPE_DEFINITION,
    "GET_RECIPE": GET_RECIPE_DEFINITION,
    "GET_COMPILED_RECIPE": GET_COMPILED_RECIPE_DEFINITION,
    "GET_NEEDED_RECIPE_BROKERS": GET_NEEDED_RECIPE_BROKERS_DEFINITION,
    "RUN_CHAT_RECIPE": RUN_CHAT_RECIPE_DEFINITION,
    "MIC_CHECK": MIC_CHECK_DEFINITION,
}


SIMPLE_RECIPE_DEFINITIONS = {
    "RUN_RECIPE": RUN_RECIPE_DEFINITION,
    "CONVERT_RECIPE_TO_CHAT": CONVERT_RECIPE_TO_CHAT_DEFINITION,
}


SAMPLE_SERVICE_DEFINITIONS = {
    "SAMPLE_SERVICE": SAMPLE_SCHEMA_FIELDS,
}

# Service Definitions
READ_LOGS_DEFINITION = {
    "filename": {
        "REQUIRED": False,
        "DEFAULT": "application logs",
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Select",
        "COMPONENT_PROPS": {"options": [{"value": "application logs", "label": "Application Logs"}, {"value": "daphne logs", "label": "Daphne Logs"}, {"value": "local logs", "label": "Local Logs"}]},
        "ICON_NAME": "Document",
        "DESCRIPTION": "The log file to read (Application Logs, Daphne Logs, or Local Logs).",
    },
    "lines": {
        "REQUIRED": False,
        "DEFAULT": 100,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Number",
        "DESCRIPTION": "The number of lines to read from the log file (0 for all).",
    },
    "search": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Search",
        "DESCRIPTION": "A search term to filter log lines (case-insensitive).",
    },
}

TAIL_LOGS_DEFINITION = {
    "filename": {
        "REQUIRED": False,
        "DEFAULT": "application logs",
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Select",
        "COMPONENT_PROPS": {"options": [{"value": "application logs", "label": "Application Logs"}, {"value": "daphne logs", "label": "Daphne Logs"}, {"value": "local logs", "label": "Local Logs"}]},
        "ICON_NAME": "Document",
        "DESCRIPTION": "The log file to tail (Application Logs, Daphne Logs, or Local Logs).",
    },
    "interval": {
        "REQUIRED": False,
        "DEFAULT": 1.0,
        "VALIDATION": None,
        "DATA_TYPE": "float",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "NumberInput",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Clock",
        "DESCRIPTION": "The interval (in seconds) between checks for new log lines.",
    },
}

STOP_TAIL_LOGS_DEFINITION = {}

GET_LOG_FILES_DEFINITION = {}

GET_ALL_LOGS_DEFINITION = {
    "filename": {
        "REQUIRED": False,
        "DEFAULT": "application logs",
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Select",
        "COMPONENT_PROPS": {"options": [{"value": "application logs", "label": "Application Logs"}, {"value": "daphne logs", "label": "Daphne Logs"}, {"value": "local logs", "label": "Local Logs"}]},
        "ICON_NAME": "Document",
        "DESCRIPTION": "The log file to read all lines from (Application Logs, Daphne Logs, or Local Logs).",
    },
}


LOG_SERVICE_DEFINITIONS = {
    "READ_LOGS": READ_LOGS_DEFINITION,
    "TAIL_LOGS": TAIL_LOGS_DEFINITION,
    "STOP_TAIL_LOGS": STOP_TAIL_LOGS_DEFINITION,
    "GET_LOG_FILES": GET_LOG_FILES_DEFINITION,
    "GET_ALL_LOGS": GET_ALL_LOGS_DEFINITION,
}


SERVICE_DEFINITIONS = {
    "COCKPIT_SERVICE": COCKPIT_SERVICE_DEFINITIONS,
    "MARKDOWN_SERVICE": MARKDOWN_SERVICE_DEFINITIONS,
    "SCRAPER_SERVICE": SCRAPE_SERVICE_DEFINITIONS,
    "SCRAPER_SERVICE_V2": SCRAPER_SERVICE_V2_DEFINITIONS,
    "CALIFORNIA_WORKER_COMPENSATION_SERVICE": CALIFORNIA_WORKER_COMP_SERVICE_DEFINITIONS,
    "CHAT_SERVICE": CHAT_SERVICE_DEFINITIONS,
    "AI_CHAT_SERVICE": AI_CHAT_SERVICE_DEFINITIONS,
    "SAMPLE_SERVICE": SAMPLE_SERVICE_DEFINITIONS,
    "SIMPLE_RECIPE": SIMPLE_RECIPE_DEFINITIONS,
    "LOG_SERVICE": LOG_SERVICE_DEFINITIONS,
}

STANDARD_FIELD_DEFINITIONS = {
    "user_id": {
        "REQUIRED": False,
        "DEFAULT": "socket_internal_user_id",
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "CircleUser",
        "DESCRIPTION": "The ID of the user to be used in the recipe.",
    },
    "response_listener_event": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Zap",
        "DESCRIPTION": "The name of the event to be used in the recipe.",
    },
}


# Globally defined definitions (We should create more of these, as we have things which are used in multiple services)

GLOBAL_DEFINITIONS = ["BROKER_DEFINITION", "OVERRIDE_DEFINITION"]


def generate_typescript_interfaces(service_definitions):
    ts_output = []
    ts_interfaces = {}

    ts_type_map = {
        "string": "string",
        "integer": "number",
        "float": "number",
        "boolean": "boolean",
        "array": "any[]",
        "object": "Record<string, any>",  # Default for unknown objects
        None: "any",  # Default for unspecified types
    }

    def to_pascal_case(name):
        """Converts snake_case or lowercase names to PascalCase."""
        return "".join(word.capitalize() for word in name.split("_"))

    def parse_definition(name, definition, no_pascal_case=False):
        """
        Parses a Python schema definition and converts it into a TypeScript interface.
        """
        ts_interface_name = to_pascal_case(name) if not no_pascal_case else name
        ts_lines = [f"export interface {ts_interface_name} " + "{"]

        for field, props in definition.items():
            ts_type = ts_type_map.get(props["DATA_TYPE"], "any")

            if props["REFERENCE"]:
                ref_name = to_pascal_case(field)
                ts_interfaces[ref_name] = props["REFERENCE"]  # Store for later processing
                ts_type = ref_name

            # If it's an array, ensure it's properly formatted
            if props["DATA_TYPE"] == "array":
                ts_type = f"{ts_type}[]"

            # Optional fields
            required = "" if props["REQUIRED"] else "?"

            # Add TypeScript field declaration
            ts_lines.append(f"    {field}{required}: {ts_type};")

        ts_lines.append("}")
        return "\n".join(ts_lines)

    reversed_definitions = []

    for service, definitions in service_definitions.items():
        for definition_name, definition in definitions.items():
            reversed_definitions.insert(0, parse_definition(definition_name, definition))
            reversed_definitions.insert(0, "")

    for ref_name, ref_definition in ts_interfaces.items():
        reversed_definitions.insert(0, parse_definition(ref_name, ref_definition, no_pascal_case=True))
        reversed_definitions.insert(0, "")

    ts_output.extend(reversed_definitions)

    return "\n".join(ts_output)


def get_reference_names(definition):
    reference_names = {}

    for field, properties in definition.items():
        reference = properties.get("REFERENCE")
        if reference is not None:
            for var_name, var_value in globals().items():
                if var_value is reference:
                    reference_names[field] = var_name
                    break
            else:
                reference_names[field] = str(reference)
        else:
            reference_names[field] = None

    return reference_names


def topological_sort(all_defs, dependencies):
    # Kahn's algorithm
    in_degree = {k: 0 for k in all_defs}
    for deps in dependencies.values():
        for d in deps:
            in_degree[d] += 1

    # Start with nodes with in-degree 0
    queue = [k for k, v in in_degree.items() if v == 0]
    sorted_order = []
    while queue:
        node = queue.pop(0)
        sorted_order.append(node)
        for dep in dependencies[node]:
            in_degree[dep] -= 1
            if in_degree[dep] == 0:
                queue.append(dep)
    if len(sorted_order) != len(all_defs):
        raise Exception("Cycle detected in definitions")
    return sorted_order


def get_typescript_schema_interfaces():
    return """export interface SchemaField {
    REQUIRED: boolean;
    DEFAULT: any;
    VALIDATION: string | null;
    DATA_TYPE: string | null;
    CONVERSION: string | null;
    REFERENCE: any;
    ICON_NAME?: string;
    COMPONENT?: string;
    COMPONENT_PROPS?: Record<string, any>;
    DESCRIPTION?: string;
    TEST_VALUE?: any;
}

export interface Schema {
    [key: string]: SchemaField;
}"""


def get_typescript_task_builder():
    return """export const SOCKET_TASKS: { [key: string]: Schema } = Object.entries(SERVICE_TASKS).reduce(
    (acc, [_, serviceTasks]) => ({
        ...acc,
        ...serviceTasks,
    }),
    {}
);

const toTitleCase = (str: string): string => {
    return str
        .split("_")
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
        .join(" ");
};

export const getAvailableServices = (): Array<{ value: string; label: string }> => {
    return Object.keys(SERVICE_TASKS).map((key) => ({
        value: key,
        label: toTitleCase(key),
    }));
};

export const TASK_OPTIONS = Object.entries(SERVICE_TASKS).reduce((acc, [service, tasks]) => {
    acc[service] = Object.keys(tasks).map((task) => ({
        value: task,
        label: toTitleCase(task),
    }));
    return acc;
}, {} as Record<string, Array<{ value: string; label: string }>>);

export const getTasksForService = (service: string): Array<{ value: string; label: string }> => {
    return TASK_OPTIONS[service] || [];
};

export const getAvailableNamespaces = (): Array<{ value: string; label: string }> => {
    return Object.entries(AVAILABLE_NAMESPACES).map(([key, value]) => ({
        value: key,
        label: value,
    }));
};

export const getTaskSchema = (taskName: string): Schema | undefined => {
    return SOCKET_TASKS[taskName];
};

export const initializeTaskDataWithDefaults = (taskName: string): Record<string, any> => {
    const taskSchema = getTaskSchema(taskName);
    if (!taskSchema) {
        return {};
    }

    const taskData: Record<string, any> = {};

    Object.entries(taskSchema).forEach(([fieldName, fieldSpec]) => {
        if (fieldSpec.DEFAULT !== undefined) {
            taskData[fieldName] = fieldSpec.DEFAULT;
        }
    });

    return taskData;
};

export const validateTaskData = (taskName: string, taskData: Record<string, any>): { isValid: boolean; errors: string[] } => {
    const errors: string[] = [];
    const schema = getTaskSchema(taskName);

    if (!schema) {
        return { isValid: false, errors: [`No schema found for task '${taskName}'`] };
    }

    Object.entries(schema).forEach(([fieldName, fieldSpec]) => {
        const providedValue = taskData[fieldName];
        const isProvided = providedValue !== undefined && providedValue !== null;

        if (fieldSpec.REQUIRED && !isProvided) {
            errors.push(`Field '${fieldName}' is required but was not provided.`);
        }
    });

    return {
        isValid: errors.length === 0,
        errors,
    };
};

export const getFieldDefinition = (taskName: string, fieldPath: string, traverseNested: boolean = true): SchemaField | undefined => {
    const taskSchema = getTaskSchema(taskName);
    if (!taskSchema) {
        return undefined;
    }

    // Split the field path into parts (e.g., "broker_values.name" -> ["broker_values", "name"])
    const pathParts = fieldPath.split(".");

    // If not traversing nested fields, return the root field directly
    if (!traverseNested || pathParts.length === 1) {
        return taskSchema[pathParts[0]];
    }

    // Traverse the path for nested fields
    let currentSchema: Schema = taskSchema;
    let currentField: SchemaField | undefined;

    for (let i = 0; i < pathParts.length; i++) {
        const part = pathParts[i];
        currentField = currentSchema[part];
        if (!currentField) {
            return undefined; // Field not found
        }

        // If there's a REFERENCE and more parts to process, switch to the referenced schema
        if (currentField.REFERENCE && i < pathParts.length - 1) {
            if (!currentField.REFERENCE || typeof currentField.REFERENCE !== "object") {
                return undefined; // Invalid REFERENCE
            }
            currentSchema = currentField.REFERENCE as Schema;
        }
    }

    return currentField;
};

export const getAllFieldPaths = (taskName: string): string[] => {
    const taskSchema = getTaskSchema(taskName);
    if (!taskSchema) {
        return [];
    }

    const fieldPaths: string[] = [];

    const traverseSchema = (schema: Schema, prefix: string = "") => {
        Object.entries(schema).forEach(([fieldName, fieldDefinition]) => {
            const currentPath = prefix ? `${prefix}.${fieldName}` : fieldName;

            // Add the current field path
            fieldPaths.push(currentPath);

            // Handle nested objects via REFERENCE
            if (fieldDefinition.REFERENCE && typeof fieldDefinition.REFERENCE === "object") {
                if (fieldDefinition.DATA_TYPE === "array") {
                    // For arrays, append [index] to the path and traverse the referenced schema
                    const arrayItemPath = `${currentPath}[index]`;
                    traverseSchema(fieldDefinition.REFERENCE as Schema, arrayItemPath);
                } else {
                    // For non-array objects, traverse the referenced schema directly
                    traverseSchema(fieldDefinition.REFERENCE as Schema, currentPath);
                }
            }
        });
    };

    traverseSchema(taskSchema);
    return fieldPaths;
};

export interface FieldDefinitionInfo {
    path: string;
    dataType: string;
    defaultValue: any;
    reference?: Schema;
  }

  export const getFieldDefinitions = (taskName: string): FieldDefinitionInfo[] => {
    const taskSchema = getTaskSchema(taskName);
    if (!taskSchema) {
      return [];
    }

    const fieldDefinitions: FieldDefinitionInfo[] = [];

    const traverseSchema = (schema: Schema, prefix: string = "") => {
      Object.entries(schema).forEach(([fieldName, fieldDefinition]) => {
        const currentPath = prefix ? `${prefix}.${fieldName}` : fieldName;

        // Add field definition info
        fieldDefinitions.push({
          path: currentPath,
          dataType: fieldDefinition.DATA_TYPE,
          defaultValue: fieldDefinition.DEFAULT,
          reference: fieldDefinition.REFERENCE,
        });

        // Handle nested objects via REFERENCE
        if (fieldDefinition.REFERENCE && typeof fieldDefinition.REFERENCE === "object") {
          if (fieldDefinition.DATA_TYPE === "array") {
            const arrayItemPath = `${currentPath}[index]`;
            traverseSchema(fieldDefinition.REFERENCE as Schema, arrayItemPath);
          } else {
            traverseSchema(fieldDefinition.REFERENCE as Schema, currentPath);
          }
        }
      });
    };

    traverseSchema(taskSchema);
    return fieldDefinitions;
  };


// Define the eUUID function that was missing
const eUUID = (value: any): boolean => {
    // UUID regex pattern
    const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    return typeof value === 'string' && uuidPattern.test(value);
  };

export const validateTextLength = (value: any): boolean => {
    if (typeof value !== "string") {
        return false;
    }
    return value.length > 5;
};

export const validateMarkdown = (value: any): boolean => {
    if (typeof value !== "string") {
        return false;
    }
    // Check for common markdown patterns: headers, bold, italic, lists, links, or code
    const markdownRegex = /(#+\s|[-*+]\s|\*\*.*?\*\*|__.*?__|\*.*?\*|_.*?_|`.*?`|\[.*?\]\(.*?\))/;
    return markdownRegex.test(value);
};


export const validateWCSide = (value: any): boolean => {
    const validSides: WCSide[] = ["left", "right", "default"];
    return typeof value === "string" && validSides.includes(value as WCSide);
};

export const validateDate = (value: any): boolean => {
    if (typeof value !== "string") {
        return false;
    }

    const datePattern = /^\d{4}-\d{2}-\d{2}$/;
    if (!datePattern.test(value)) {
        return false;
    }

    try {
        const [year, month, day] = value.split("-").map(Number);
        const date = new Date(year, month - 1, day);
        return (
            date.getFullYear() === year &&
            date.getMonth() === month - 1 &&
            date.getDate() === day
        );
    } catch {
        return false;
    }
};

export const validToolNames = [
    "code_python_execute",
    "code_web_store_html",
    "code_fetcher_fetch",
    "api_news_fetch_headlines",
    "core_math_calculate",
    "core_web_search",
    "core_web_read_web_pages",
    "core_web_search_and_read",
    "data_sql_execute_query",
    "data_sql_list_tables",
    "data_sql_get_table_schema",
    "data_sql_create_user_generated_table_data",
    "text_analyze",
    "text_regex_extract",
];
export const validateToolNames = (value: any): boolean => {
    // Check if value is an array
    if (!Array.isArray(value)) {
        return false;
    }

    // Check if every item in the array is a string and exists in validToolNames
    return value.every((item) => typeof item === "string" && validToolNames.includes(item));
};

const validationFunctions: Record<string, (value: any) => boolean> = {
    eUUID,
    validateTextLength,
    validateMarkdown,
    validateToolNames,
};

export const isValidField = (taskName: string, fieldPath: string, value: any, traverseNested: boolean = true): { isValid: boolean; errorMessage: string } => {
    const fieldDefinition = getFieldDefinition(taskName, fieldPath, traverseNested);
    if (!fieldDefinition) {
      return { isValid: false, errorMessage: `Field definition not found for ${fieldPath}` };
    }

    const isEmpty = value === null || value === undefined;

    if (!fieldDefinition.REQUIRED && isEmpty) {
      console.log(`Field is not required and empty, returning true`);
      return { isValid: true, errorMessage: "" };
    }

    if (fieldDefinition.REQUIRED && isEmpty) {
      console.log(`Field is required but empty, returning false`);
      return { isValid: false, errorMessage: `${fieldPath} is required` };
    }

    const expectedType = fieldDefinition.DATA_TYPE;
    console.log(`Expected data type: ${expectedType}`);
    if (!isEmpty) {
      console.log(`Validating data type for value:`, value);
      switch (expectedType) {
        case "string":
          if (typeof value !== "string") {
            console.log(`Type mismatch: expected string, got ${typeof value}`);
            return { isValid: false, errorMessage: `Expected a string for ${fieldPath}, got ${typeof value}` };
          }
          break;
        case "number":
        case "integer": // Add integer type
          if (typeof value !== "number" || (expectedType === "integer" && !Number.isInteger(value))) {
            console.log(`Type mismatch: expected ${expectedType}, got ${typeof value}`);
            return { isValid: false, errorMessage: `Expected an ${expectedType} for ${fieldPath}, got ${typeof value}` };
          }
          break;
        case "boolean":
          if (typeof value !== "boolean") {
            console.log(`Type mismatch: expected boolean, got ${typeof value}`);
            return { isValid: false, errorMessage: `Expected a boolean for ${fieldPath}, got ${typeof value}` };
          }
          break;
        case "array":
          if (!Array.isArray(value)) {
            console.log(`Type mismatch: expected array, got ${typeof value}`);
            return { isValid: false, errorMessage: `Expected an array for ${fieldPath}, got ${typeof value}` };
          }
          break;
        case "object":
          if (typeof value !== "object" || value === null || Array.isArray(value)) {
            console.log(`Type mismatch: expected object, got ${typeof value}`);
            return { isValid: false, errorMessage: `Expected an object for ${fieldPath}, got ${typeof value}` };
          }
          break;
        default:
          console.log(`Unknown data type: ${expectedType}`);
          return { isValid: false, errorMessage: `Unknown data type ${expectedType} for ${fieldPath}` };
      }
      console.log(`Data type validation passed`);
    }

    if (!isEmpty && fieldDefinition.VALIDATION) {
      console.log(`Running validation function: ${fieldDefinition.VALIDATION}`);
      const validationFn = validationFunctions[fieldDefinition.VALIDATION];
      if (typeof validationFn === "function") {
        const validationResult = validationFn(value);
        console.log(`Validation function result: ${validationResult}`);
        if (!validationResult) {
          return { isValid: false, errorMessage: `Validation failed for ${fieldPath}: ${getValidationErrorMessage(fieldDefinition.VALIDATION, value)}` };
        }
        return { isValid: true, errorMessage: "" };
      }
      return { isValid: false, errorMessage: `Validation function ${fieldDefinition.VALIDATION} not found for ${fieldPath}` };
    }

    return { isValid: true, errorMessage: "" };
  };

  // Helper to provide specific error messages for validation failures
  const getValidationErrorMessage = (validationName: string, value: any): string => {
    switch (validationName) {
      case "eUUID":
        return `Expected a valid UUID, got "${value}"`;
      case "validateTextLength":
        return `Expected a string longer than 5 characters, got "${value}"`;
      case "validateMarkdown":
        return `Expected valid Markdown content, got "${value}"`;
      case "validateToolNames":
        return `Expected an array of valid tool names, got ${JSON.stringify(value)}`;
      default:
        return `Invalid value "${value}"`;
    }
  };

"""


def get_typescript_available_namespaces():
    return """export const AVAILABLE_NAMESPACES = {
    "/UserSession": "User Session",
    "/AdminSession": "Admin Session",
    "/Direct": "No Namespace",
    "/custom": "Custom Namespace",
} as const;

export type FieldType =
    | "input"
    | "textarea"
    | "switch"
    | "checkbox"
    | "slider"
    | "select"
    | "radiogroup"
    | "fileupload"
    | "multifileupload"
    | "jsoneditor";

export interface FieldOverride {
    type: FieldType;
    props?: Record<string, any>;
}

export type FieldOverrides = Record<string, FieldOverride>;

export const FIELD_OVERRIDES: FieldOverrides = {
    raw_markdown: {
        type: "textarea",
        props: {
            rows: 10,
        },
    },
};

"""


def generate_typescript_schemas(service_definitions):
    """
    Converts Python schema definitions into TypeScript schema objects.
    Ensures that referenced definitions come first (using topological sort).
    """
    ts_output = [get_typescript_schema_interfaces(), ""]
    reversed_definitions = []  # Collect definitions in reverse order

    # First, build a mapping of all definitions.
    all_definitions = {}
    # Add global definitions (BROKER_DEFINITION, OVERRIDE_DEFINITION, etc.)
    for var_name in GLOBAL_DEFINITIONS:
        if var_name in globals():
            all_definitions[var_name] = globals()[var_name]

    # Add definitions from service_definitions and their references.
    def collect_definitions(defs):
        for def_name, def_obj in defs.items():
            all_definitions[def_name.upper()] = def_obj
            # Check for nested references
            for field, props in def_obj.items():
                ref = props.get("REFERENCE")
                if ref is not None:
                    for var_name, var_value in globals().items():
                        if var_value is ref:
                            all_definitions[var_name] = ref
                            break

    for service, defs in service_definitions.items():
        collect_definitions(defs)

    # Build dependency graph: For each definition, find which definitions it references.
    dependencies = {name: set() for name in all_definitions}
    for name, def_obj in all_definitions.items():
        for field, props in def_obj.items():
            ref = props.get("REFERENCE")
            if ref is not None:
                # Look for a definition in all_definitions that matches by identity.
                for candidate_name, candidate_obj in all_definitions.items():
                    if candidate_obj is ref:
                        # "name" depends on candidate_name: candidate must come before name.
                        dependencies[name].add(candidate_name)
                        break

    # Now perform a topological sort so that referenced definitions come first.
    sorted_def_names = topological_sort(all_definitions, dependencies)

    # Function to format a value for TypeScript output.
    def format_value(value):
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, str):
            if value == "null":
                return "null"
            return f'"{value}"'
        if isinstance(value, dict):
            # Format dictionary as a JSON-like object
            items = [f'"{k}": {format_value(v)}' for k, v in value.items()]
            return "{" + ", ".join(items) + "}"
        if isinstance(value, list):
            # Format list with recursive formatting
            items = [format_value(item) for item in value]
            return "[" + ", ".join(items) + "]"
        return str(value)

    def parse_definition(name, definition):
        ts_lines = []
        ts_lines.append(f"export const {name}: Schema = " + "{")

        # Use get_reference_names to extract correct reference names for fields.
        ref_names = get_reference_names(definition)

        for field, props in definition.items():
            ts_lines.append(f"    {field}: " + "{")
            for key, value in props.items():
                formatted_value = format_value(value)
                if key == "REFERENCE" and ref_names.get(field) is not None:
                    # Use the reference name (without quotes) in TypeScript.
                    formatted_value = ref_names[field]
                ts_lines.append(f"        {key}: {formatted_value},")
            ts_lines.append("    },")
        ts_lines.append("};")
        return "\n".join(ts_lines)

    # Output definitions in topologically sorted order.
    for def_name in sorted_def_names:
        # Collect the parsed definitions in reverse order
        reversed_definitions.insert(0, parse_definition(def_name, all_definitions[def_name]))
        reversed_definitions.insert(0, "")  # Maintain spacing between definitions

    # Append reversed definitions to ts_output
    ts_output.extend(reversed_definitions)

    # Generate the SERVICE_TASKS registry grouped by service.
    ts_output.append("export const SERVICE_TASKS = {")
    for service, defs in service_definitions.items():
        service_key = f"{service.lower()}"
        ts_output.append(f"    {service_key}: {{")
        for def_name in defs.keys():
            task_name = def_name.lower().replace("_definition", "")
            ts_output.append(f"        {task_name}: {def_name.upper()},")
        ts_output.append("    },")
    ts_output.append("} as const;")
    ts_output.append("\n")
    ts_output.append(get_typescript_available_namespaces())
    ts_output.append("\n")
    ts_output.append(get_typescript_task_builder())

    return "\n".join(ts_output)


def generate_typescript_interfaces_and_schemas(definitions=None):
    if definitions is None:
        definitions = SERVICE_DEFINITIONS

    from matrx_utils.file_management.specific_handlers.code import CodeHandler
    from matrx_utils.schema_builder.helpers.configs import CODE_BASICS

    code_handler = CodeHandler(batch_print=False)

    typescript_interfaces = generate_typescript_interfaces(definitions)
    code_handler.generate_and_save_code_from_object(CODE_BASICS["socket_ts_interfaces"], main_code=typescript_interfaces)

    typescript_schemas = generate_typescript_schemas(definitions)
    code_handler.generate_and_save_code_from_object(CODE_BASICS["socket_ts_schemas"], main_code=typescript_schemas)


# New ========================================================


def generate_json_schemas(service_definitions: Dict[str, Any]) -> str:
    """
    Converts Python schema definitions into a JSON structure.
    Ensures that referenced definitions are included and ordered correctly.
    """
    # Collect all definitions
    all_definitions = {}

    # Add global definitions
    for var_name in globals().get("GLOBAL_DEFINITIONS", []):
        if var_name in globals():
            all_definitions[var_name] = globals()[var_name]

    # Add service definitions and their references
    def collect_definitions(defs: Dict[str, Any]):
        for def_name, def_obj in defs.items():
            all_definitions[def_name.upper()] = def_obj
            for field, props in def_obj.items():
                ref = props.get("REFERENCE")
                if ref is not None:
                    for var_name, var_value in globals().items():
                        if var_value is ref:
                            all_definitions[var_name] = ref
                            break

    for service, defs in service_definitions.items():
        collect_definitions(defs)

    # Build dependency graph
    dependencies = {name: set() for name in all_definitions}
    for name, def_obj in all_definitions.items():
        for field, props in def_obj.items():
            ref = props.get("REFERENCE")
            if ref is not None:
                for candidate_name, candidate_obj in all_definitions.items():
                    if candidate_obj is ref:
                        dependencies[name].add(candidate_name)
                        break

    # Perform topological sort
    sorted_def_names = topological_sort(all_definitions, dependencies)

    # Format values for JSON
    def format_value(value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value
        if isinstance(value, (int, float)):
            return value
        if isinstance(value, dict):
            return {k: format_value(v) for k, v in value.items()}
        if isinstance(value, list):
            return [format_value(item) for item in value]
        return str(value)

    # Parse definitions into JSON-compatible structure
    json_output = {}
    for def_name in sorted_def_names:
        definition = all_definitions[def_name]
        schema = {}
        ref_names = get_reference_names(definition)

        for field, props in definition.items():
            field_props = {}
            for key, value in props.items():
                if key == "REFERENCE" and ref_names.get(field):
                    field_props[key] = ref_names[field]
                else:
                    field_props[key] = format_value(value)
            schema[field] = field_props
        json_output[def_name] = schema

    # Generate SERVICE_TASKS equivalent
    service_tasks = {}
    for service, defs in service_definitions.items():
        service_key = service.lower()
        service_tasks[service_key] = {}
        for def_name in defs.keys():
            task_name = def_name.lower().replace("_definition", "")
            service_tasks[service_key][task_name] = def_name.upper()

    json_output["SERVICE_TASKS"] = service_tasks

    # Serialize to JSON string with proper formatting
    return json.dumps(json_output, indent=4, sort_keys=True)


def save_json_schemas(service_definitions: Dict[str, Any], output_file: str = "socket_schemas.json"):
    """
    Generates JSON schemas and saves them to a file in the same directory as this script.
    """
    json_schemas = generate_json_schemas(service_definitions)
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the full path using the script's directory
    output_path = os.path.join(script_dir, output_file)
    with open(output_path, "w") as f:
        f.write(json_schemas)
    print_link(output_path)


def generate_and_save_json_schemas():
    generate_typescript_interfaces_and_schemas()
    save_json_schemas(SERVICE_DEFINITIONS, "socket_schemas.json")


# There is an issue I need to fix with the scheme for typescript where I need to put the functions at the top of the file.


# if __name__ == "__main__":
#     os.system("cls")
#     # generate_typescript_interfaces_and_schemas()
#     generate_and_save_json_schemas()
#
#     # typescript_code = generate_typescript_interfaces(SERVICE_DEFINITIONS)
#     # print(typescript_code)
#     # print()
#     #
#     # typescript_code = generate_typescript_schemas(SERVICE_DEFINITIONS)
#     # print(typescript_code)
#
#     # save_json_schemas(SERVICE_DEFINITIONS)
#
