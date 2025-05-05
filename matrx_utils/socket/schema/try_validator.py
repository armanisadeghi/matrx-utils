from matrx_utils.socket.schema.schema_processor import get_validator


validator = get_validator()


event = "ai_chat_service"
task = "run_recipe_to_chat"
user_id = "jatin-123"

data = {
        "chat_config": {
            "recipe_id": "e2049ce6-c340-4ff7-987e-deb24a977853",
            "version": "latest",
            "user_id": "socket_internal_user_id",
            "prepare_for_next_call": False,
            "save_new_conversation": False,
            "include_classified_output": False,
            "model_override": "10168527-4d6b-456f-ab07-a889223ba3a9",
            "allow_default_values": False,
            "allow_removal_of_unmatched": False
        },
        "broker_values": [
            {
                "name": None,
                "id": "",
                "value": "",
                "ready": True
            },
            {
                "name": None,
                "id": None,
                "value": "",
                "ready": False
            }
        ]
    }

from matrx_utils import vcprint

vcprint(validator.validate(data, event, task, user_id))