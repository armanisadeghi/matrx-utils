from database.schema_builder.helpers.field_processor.dataclass_generator import generate_complete_code
from common import vcprint, print_link
from typing import Dict, Any

FIELD_DEFINITIONS = {
    "recipe_id": {"always_include": True, "default": "", "type": str},
    "recipe_ids": {"always_include": True, "default": [], "type": list, "list_type": str},
    "planEnabled": {"always_include": True, "default": False, "type": bool},
    "audioEnabled": {"always_include": True, "default": False, "type": bool},
    "thinking_settings": {"always_include": True, "default": None, "type": dict},
    "count": {"always_include": True, "default": 1, "type": int},
    "config": {"always_include": True, "default": {}, "type": dict},
    "scores": {"always_include": True, "default": [], "type": list, "list_type": int},
    "flags": {"always_include": False, "default": [], "type": list, "list_type": bool},
}

AI_SETTINGS_DATA_FIELD_DEFINITIONS = {
    "ai_model": {"type": str, "always_include": False, "default": None},
    "temperature": {"type": int, "always_include": False, "default": None},
    "max_tokens": {"type": int, "always_include": False, "default": None},
    "top_p": {"type": int, "always_include": False, "default": 1},
    "frequency_penalty": {"type": int, "always_include": False, "default": None},
    "presence_penalty": {"type": int, "always_include": False, "default": None},
    "stream": {"type": bool, "always_include": True, "default": True},
    "response_format": {"type": str, "always_include": True, "default": "text"},
    "size": {"type": str, "always_include": False, "default": None},
    "quality": {"type": str, "always_include": False, "default": None},
    "count": {"type": int, "always_include": False, "default": 1},
    "audio_voice": {"type": str, "always_include": False, "default": None},
    "audio_format": {"type": str, "always_include": False, "default": None},
    "modalities": {"type": dict, "always_include": False, "default": {}},
    "tools": {"type": dict, "always_include": False, "default": {}},
    "preset_name": {"type": str, "always_include": False, "default": None},
    "system_message_override": {"type": str, "always_include": False, "default": None},
    "reasoning": {"type": dict, "always_include": False, "default": {}},
}

AI_SETTINGS_DATA_FIELD_MAP = {}


AI_SETTINGS_ARGS = {
    "class_name": "AISettingsData",
    "fields_spec": AI_SETTINGS_DATA_FIELD_DEFINITIONS,
    "additional_imports": "",
    "path_from_base": "matrix/compiled_recipes/utils/ai_settings_util.py",
    "field_map": AI_SETTINGS_DATA_FIELD_MAP,
}


BROKER_OBJECT_FIELD_DEFINITIONS = {
    "id": {"type": str, "always_include": True, "default": None},
    "name": {"type": str, "always_include": True, "default": None},
    "default_value": {"type": str, "always_include": False, "default": None},
    "ready": {"type": bool, "always_include": True, "default": False},
    "data_type": {"type": str, "always_include": True, "default": "str"},
}

BROKER_OBJECT_FIELD_MAP = {
    "broker_id": "id",
    "broker_ready": "ready",
}


BROKER_OBJECT_ARGS = {
    "class_name": "BrokerObject",
    "fields_spec": BROKER_OBJECT_FIELD_DEFINITIONS,
    "additional_imports": "",
    "path_from_base": "matrix/compiled_recipes/utils/ai_settings_util_broker_object.py",
    "field_map": BROKER_OBJECT_FIELD_MAP,
}


CHAT_CONFIG_FIELD_DEFINITIONS = {
    "allow_default_values": {"type": bool, "always_include": True, "default": False},
    "allow_removal_of_unmatched": {"type": bool, "always_include": True, "default": False},
    "include_classified_output": {"type": bool, "always_include": True, "default": False},
    "model_override": {"type": str, "always_include": False, "default": None},
    "tools_override": {"type": list, "always_include": False, "default": None},
    "recipe_id": {"type": str, "always_include": False, "default": None},
    "version": {"type": Any, "always_include": True, "default": "latest"},
    "user_id": {"type": str, "always_include": False, "default": None},
    "prepare_for_next_call": {"type": bool, "always_include": True, "default": False},
    "save_new_conversation": {"type": bool, "always_include": True, "default": False},
}

CHAT_CONFIG_FIELD_MAP = {
    "model_id": "model_override",
    "tools": "tools_override",
}

CHAT_CONFIG_ARGS = {
    "class_name": "ChatConfig",
    "fields_spec": CHAT_CONFIG_FIELD_DEFINITIONS,
    "additional_imports": "",
    "path_from_base": "matrix/utils/chat_config_util.py",
    "field_map": CHAT_CONFIG_FIELD_MAP,
}


def generate_code_by_args(args: Dict[str, Any]) -> str:
    complete_code, file_path = generate_complete_code(**args)
    vcprint(f"\n=================== {args['class_name']} GENERATED CODE ===================\n", color="green")
    vcprint(complete_code, "Complete code", color="blue")
    vcprint("\n========================================================\n", color="green")
    if file_path:
        print()
        print_link(file_path)
    return complete_code, file_path


if __name__ == "__main__":
    # generate_code_by_args(AI_SETTINGS_ARGS)
    # generate_code_by_args(BROKER_OBJECT_ARGS)
    generate_code_by_args(CHAT_CONFIG_ARGS)
    # pass
