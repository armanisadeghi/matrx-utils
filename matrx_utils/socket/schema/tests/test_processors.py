# from enum import Enum
import os
from matrx_utils.common import vcprint
from matrx_utils.socket.schema.schema_processor import ValidationSystem


sample_data = {
    "task": "run_chat_recipe",
    "index": 0,
    "stream": True,
    "taskData": {
        "recipe_id": "e2049ce6-c340-4ff7-987e-deb24a977853",
        "broker_values": [{"name": None, "id": "5d8c5ed2-5a84-476a-9258-6123a45f996a", "value": "My app helps kids make flashcards.", "ready": True}],
        "version": "17",
        "user_id": "user123",
        "save_new_conversation": True,
        # "custom_event_name": "my_new_event_name",
    },
}

if __name__ == "__main__":
    os.system("cls")

    result = ValidationSystem.validate(sample_data["taskData"], "chat_service", "run_chat_recipe", "user123")
    vcprint(result, title="Validation Result", color="gold")

    # event_name = "chat_service"
    # task_name = "run_chat_recipe"
    # schema = get_task_schema(event_name, task_name)
    # vcprint(schema, title=f"Task Schema for {task_name}", color="green")

    # event_name = "chat_service"
    # task_name = "prep_conversation"
    # schema = get_task_schema(event_name, task_name)
    # vcprint(schema, title=f"Task Schema for {task_name}", color="green")
