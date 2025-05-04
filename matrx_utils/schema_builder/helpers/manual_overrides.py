# matrx_utils\schema_builder\helpers\manual_overrides.py
# Add the table you want to MOVE UP in the file.
# Use TABLE NAME, not the "Model" name. (Lowercase snake case)

TABLE_ORDER_OVERRIDES = {
    "ai_provider": 2,
    "data_input_component": 1,
    "data_output_component": 2,
    "projects": 1,
    "scrape_job": 3,
    "scrape_cache_policy": 3,
    "scrape_cycle_tracker": 1,
    "scrape_path_pattern": 1,
    "scrape_path_pattern_cache_policy": 2,
    "category": 1

}

SYSTEM_OVERRIDES_ENTITIES = {
    "recipe": {
        "defaultFetchStrategy": '"fkAndIfk"',
    },
    "broker": {
        "displayFieldMetadata": '{ fieldName: "displayName", databaseFieldName: "display_name" }',
    },
    "aiModel": {
        "displayFieldMetadata": '{ fieldName: "commonName", databaseFieldName: "common_name" }',
    },
    "messageTemplate": {
        "displayFieldMetadata": '{ fieldName: "role", databaseFieldName: "role" }',
    },
}

recipe_field_overrides = {"tags": {"componentProps": {"subComponent": "tagsManager"}}}

data_input_component_field_overrides = {"options": {"componentProps": {"subComponent": "optionsManager"}}}

broker_field_overrides = {
    "name": """{
        isDisplayField: false,
        isRequired: null,
        maxLength: null,
        defaultValue: null,
        defaultGeneratorFunction: null,
        validationFunctions: null,
        exclusionRules: null,
        defaultComponent: null,
        componentProps: null,
        foreignKeyReference: null,
        description: null,
        fieldNameFormats: null
    }""",
    "displayName": """{
        isDisplayField: true,
        isRequired: null,
        maxLength: null,
        defaultValue: null,
        defaultGeneratorFunction: null,
        validationFunctions: null,
        exclusionRules: null,
        defaultComponent: null,
        componentProps: null,
        foreignKeyReference: null,
        description: null,
        fieldNameFormats: null
    }""",
}

message_template_field_overrides = {
    "role": """{
        isDisplayField: true
    }""",
    "type": """{
        isDisplayField: false
    }""",
}

ai_settings_field_overrides = {
    "temperature": {
        "defaultComponent": "SPECIAL",
        "componentProps": {
            "subComponent": "SLIDER",
            "className": "w-full",
            "min": 0,
            "max": 2,
            "step": 0.01,
            "numberType": "real",
        },
    },
    "maxTokens": {
        "defaultComponent": "SPECIAL",
        "componentProps": {
            "subComponent": "SLIDER",
            "className": "w-full",
            "min": 0,
            "max": 5000,
            "step": 1,
            "numberType": "smallint",
        },
    },
    "stream": {
        "defaultComponent": "SPECIAL",
        "componentProps": {
            "subComponent": "SWITCH",
            "variant": "geometric",
            "width": "w-28",
            "height": "h-7",
            "labels": {"on": "Steam", "off": "Direct"},
        },
    },
    "responseFormat": {
        "defaultComponent": "SPECIAL",
        "componentProps": {
            "subComponent": "MULTI_SWITCH",
            "variant": "geometric",
            "preset": "RESPONSE_FORMATS",
            "width": "w-24",
            "height": "h-7",
            "rows": 5,
        },
    },
    "tools": {
        "defaultComponent": "SPECIAL",
        "componentProps": {
            "subComponent": "TOOL_CONTROL",
            "variant": "geometric",
            "placeholder": "Select tools...",
            "width": "w-48",
            "height": "h-7",
            "primaryControlOptions": "toolAssistOptions",
            "toolOptions": "aiTools",
        },
    },
}

# Combining all into SYSTEM_OVERRIDES_FIELDS
SYSTEM_OVERRIDES_FIELDS = {
    "recipe": recipe_field_overrides,
    "dataInputComponent": data_input_component_field_overrides,
    "broker": broker_field_overrides,
    "messageTemplate": message_template_field_overrides,
    "aiSettings": ai_settings_field_overrides,
}
