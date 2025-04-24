import os

from matrx_utils import vcprint

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
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Input",
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
        "COMPONENT": "Slider",
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
        "COMPONENT": "Input",
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
        "COMPONENT": "Input",
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
        "COMPONENT": "Input",
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
        "COMPONENT": "Input",
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
        "COMPONENT": "Input",
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
        "COMPONENT": "Input",
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
        "COMPONENT": "relatedFieldsDisplay",
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
        "COMPONENT": "relatedFieldsDisplay",
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
        "COMPONENT": "Input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the id of the recipe to run.",
        "ICON_NAME": "Key",
    },
    "broker_values": {
        "REQUIRED": False,
        "DEFAULT": [],
        "VALIDATION": None,
        "DATA_TYPE": "array",
        "CONVERSION": "convert_broker_data",
        "REFERENCE": BROKER_DEFINITION,
        "COMPONENT": "relatedFieldsDisplay",
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
        "COMPONENT": "relatedFieldsDisplay",
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
        "COMPONENT": "Input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the id of the recipe to run.",
        "ICON_NAME": "Key",
    },
    "compiled_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Input",
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
        "COMPONENT": "Input",
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
        "COMPONENT": "Input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the id of the recipe to add.",
        "ICON_NAME": "Key",
    },
    "compiled_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Input",
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
        "COMPONENT": "Input",
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
        "COMPONENT": "Input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the id of the recipe to get.",
        "ICON_NAME": "Key",
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
        "COMPONENT": "Input",
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
        "COMPONENT": "Input",
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
        "COMPONENT": "Input",
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
        "COMPONENT": "Input",
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
        "COMPONENT": "Input",
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
        "COMPONENT": "Input",
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
        "COMPONENT": "Input",
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
        "COMPONENT": "Input",
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
        "COMPONENT": "Input",
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
        "COMPONENT": "Input",
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
        "COMPONENT": "Input",
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
        "COMPONENT": "Input",
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
        "COMPONENT": "Input",
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
        "COMPONENT": "Input",
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
        "COMPONENT": "Input",
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
        "COMPONENT": "Input",
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
        "COMPONENT": "Input",
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
        "COMPONENT": "Input",
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
        "COMPONENT": "Input",
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
        "COMPONENT": "Input",
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
        "COMPONENT": "Input",
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
        "COMPONENT": "Input",
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
        "COMPONENT": "Input",
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
        "COMPONENT": "ArrayField",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the urls to be scraped.",
        "ICON_NAME": "Link",
    },
    "clean_output": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Clean text formatting.",
        "ICON_NAME": "eraser",
    },
    "get_raw_json_content": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Get raw json content with results.",
        "ICON_NAME": "braces",
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
        "DESCRIPTION": "Enter the keywords to search for.",
        "ICON_NAME": "whole-word",
    },
    "country_code": {
        "REQUIRED": False,
        "DEFAULT": "all",
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the country code to get search results for.",
        "ICON_NAME": "flag",
    },
    "total_results_per_keyword": {
        "REQUIRED": False,
        "DEFAULT": 5,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Enter the number of results per keyword to get.",
        "ICON_NAME": "flag",
    },
    "search_type": {
        "REQUIRED": False,
        "DEFAULT": "all",
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Input",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Kind of search type to scrape, 'web', 'news', or 'all'.",
        "ICON_NAME": "rss",
    },
    "clean_output": {
        "REQUIRED": True,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Clean text formatting.",
        "ICON_NAME": "eraser",
    },
    "get_raw_json_content": {
        "REQUIRED": False,
        "DEFAULT": False,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Switch",
        "COMPONENT_PROPS": {},
        "DESCRIPTION": "Get raw json content with results.",
        "ICON_NAME": "braces",
    }
}


SCRAPER_SERVICE_V2_DEFINITIONS = {
    "QUICK_SCRAPE": QUICK_SCRAPE_V2_DEFINITION,
    "SEARCH_AND_SCRAPE": SEARCH_AND_SCRAPE_DEFINITION,
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
    },
    "date_of_birth": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": "validate_date",
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
    },
    "age_at_doi": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
    },
    "occupational_code": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
    },
    "weekly_earnings": {
        "REQUIRED": False,
        "DEFAULT": 290.0,
        "VALIDATION": None,
        "DATA_TYPE": "float",
        "CONVERSION": None,
        "REFERENCE": None,
    },
    "applicant_name": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
    },
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
    },
    "impairment_definition_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
    },
    "digit": {
        "REQUIRED": False,
        "DEFAULT": 0,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
    },
    "wpi": {
        "REQUIRED": False,
        "DEFAULT": 0,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
    },
    "le": {
        "REQUIRED": False,
        "DEFAULT": 0,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
    },
    "ue": {
        "REQUIRED": False,
        "DEFAULT": 0,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
    },
    "industrial": {
        "REQUIRED": False,
        "DEFAULT": 100,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
    },
    "pain": {
        "REQUIRED": False,
        "DEFAULT": 0,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
    },
    "side": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": "validate_wc_side",
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
    },
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
    },
    "date_of_injury": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": "validate_date",
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
    },
    "date_of_birth": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": "validate_date",
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
    },
    "age_at_doi": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
    },
    "occupational_code": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
    },
    "weekly_earnings": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "float",
        "CONVERSION": None,
        "REFERENCE": None,
    },
    "applicant_name": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
    },
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
    },
    "digit": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
    },
    "wpi": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
    },
    "le": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
    },
    "ue": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
    },
    "industrial": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
    },
    "pain": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
    },
    "side": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": "validate_wc_side",
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
    },
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
        "COMPONENT": "Input",
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
        "COMPONENT": "Input",
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
        "COMPONENT": "TextArea",
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
        "COMPONENT": "Input",
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
        "COMPONENT": "relatedFieldsDisplay",
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
        "COMPONENT": "Input",
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
        "COMPONENT": "Input",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Key",
        "DESCRIPTION": "Enter the ID of the recipe to be fetched, cached and ready for fast usage.",
    },
    "version": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Input",
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
        "COMPONENT": "Input",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Key",
        "DESCRIPTION": "Enter the ID of the recipe to be fetched, cached and ready for fast usage.",
    },
    "version": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Input",
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
        "COMPONENT": "relatedFieldsDisplay",
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
        "COMPONENT": "Input",
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
        "COMPONENT": "Input",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Key",
        "TEST_VALUE": "e2049ce6-c340-4ff7-987e-deb24a977853",
        "DESCRIPTION": "Enter the ID of the recipe to be fetched, cached and ready for fast usage.",
    },
    "version": {
        "REQUIRED": False,
        "DEFAULT": "latest",
        "VALIDATION": None,
        "DATA_TYPE": "integer",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "Input",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Key",
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
        "COMPONENT": "Input",
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
        "COMPONENT": "Input",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Key",
        "DESCRIPTION": "Enter the chat config to be used in the recipe.",
    },
    "broker_values": {
        "REQUIRED": False,
        "DEFAULT": [],
        "VALIDATION": None,
        "DATA_TYPE": "array",
        "CONVERSION": "convert_broker_data",
        "REFERENCE": BROKER_DEFINITION,
        "COMPONENT": "relatedFieldsDisplay",
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
        "COMPONENT": "Input",
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
        "COMPONENT": "relatedFieldsDisplay",
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
        "COMPONENT": "Input",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Key",
        "DESCRIPTION": "Enter the ID of the chat to be converted to a recipe.",
    },
}


AI_CHAT_SERVICE_DEFINITIONS = {
    "RUN_RECIPE_TO_CHAT": RECIPE_TO_CHAT_DEFINITION,
    "RUN_BATCH_RECIPE": BATCH_RECIPE_DEFINITION,
    "PREPARE_BATCH_RECIPE": BATCH_RECIPE_DEFINITION,
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
        "COMPONENT_PROPS": {
            "options": [
                {"value": "application logs", "label": "Application Logs"},
                {"value": "daphne logs", "label": "Daphne Logs"},
                {"value": "local logs", "label": "Local Logs"}
            ]
        },
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
        "COMPONENT": "Input",
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
        "COMPONENT_PROPS": {
            "options": [
                {"value": "application logs", "label": "Application Logs"},
                {"value": "daphne logs", "label": "Daphne Logs"},
                {"value": "local logs", "label": "Local Logs"}
            ]
        },
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
        "COMPONENT_PROPS": {
            "options": [
                {"value": "application logs", "label": "Application Logs"},
                {"value": "daphne logs", "label": "Daphne Logs"},
                {"value": "local logs", "label": "Local Logs"}
            ]
        },
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
        "COMPONENT": "Input",
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
        "COMPONENT": "Input",
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

"""


def get_typescript_available_namespaces():
    return """export const AVAILABLE_NAMESPACES = {
    "/UserSession": "User Session",
    "/AdminSession": "Admin Session",
    "/Direct": "No Namespace",
    "/custom": "Custom Namespace",
} as const;

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

    from matrx_utils.common.file_management.specific_handlers.code import CodeHandler
    from matrx_utils.database.schema_builder.helpers.configs import CODE_BASICS

    code_handler = CodeHandler(batch_print=False)

    typescript_interfaces = generate_typescript_interfaces(definitions)
    code_handler.generate_and_save_code_from_object(CODE_BASICS["socket_ts_interfaces"], main_code=typescript_interfaces)

    typescript_schemas = generate_typescript_schemas(definitions)
    code_handler.generate_and_save_code_from_object(CODE_BASICS["socket_ts_schemas"], main_code=typescript_schemas)


if __name__ == "__main__":
    os.system("cls")
    generate_typescript_interfaces_and_schemas()
    # typescript_code = generate_typescript_interfaces(SERVICE_DEFINITIONS)
    # print(typescript_code)
    # print()
    #
    # typescript_code = generate_typescript_schemas(SERVICE_DEFINITIONS)
    # print(typescript_code)
