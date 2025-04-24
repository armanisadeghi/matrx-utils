import os
from database.orm.models import CompiledRecipeManager
from database.orm.core.managed_models import DataBrokerManager
import asyncio

verbose = False

if verbose:
    from common.utils.fancy_prints import vcprint


def pretty_log(data, title, color="blue"):
    if verbose:
        vcprint(data, title, verbose=verbose, color=color, pretty=True)


def line_log(data, title, color="green"):
    if verbose:
        vcprint(data, title, verbose=verbose, color=color, pretty=False)


def log_message(message):
    if verbose:
        print("\n--------------------------------")
        print("ROLE: ", message.get("role"))
        print("TYPE: ", message.get("type"))
        print()
        vcprint(message.get("content"), color="bright_gold")
        print("--------------------------------\n")


def log_intermediate_message(message, index):
    if verbose:
        print("\n" + "=" * 100)
        print(
            "MESSAGE NUMBER: ",
            index,
            "ROLE: ",
            message.get("role"),
            "TYPE: ",
            message.get("type"),
            "\n",
        )
        vcprint(message.get("content"), color="bright_gold")
        print("\n" + "=" * 100)


def log_final_message(message, index):
    from common.utils.fancy_prints import vcprint

    verbose = True
    if verbose:
        print("\n" + "=" * 100)
        print(
            "MESSAGE NUMBER: ",
            index,
            "ROLE: ",
            message.get("role"),
            "TYPE: ",
            message.get("type"),
            "\n",
        )
        vcprint(message.get("content"), color="bright_gold")
        print("\n" + "=" * 100)


async def compiled_recipe_manager_test(compiled_recipe_id):
    compiled_recipe_manager = CompiledRecipeManager()

    compiled_recipe = await compiled_recipe_manager.load_item(id=compiled_recipe_id)
    pretty_log(compiled_recipe, "Compiled Recipe Data")

    return compiled_recipe, compiled_recipe_manager


async def data_broker_manager_test(data_broker_id):
    broker_manager = DataBrokerManager()

    broker = await broker_manager.get_item_dict(item_id=data_broker_id)

    pretty_log(broker, "Broker Data", color="blue")
    return broker, broker_manager


async def orchestrator_manager_test(data):
    compiled_recipe_id = data["compiled_recipe_id"]
    data_broker_id = data["data_broker_id"]

    compiled_recipe, compiled_recipe_manager = await compiled_recipe_manager_test(compiled_recipe_id)
    broker, broker_manager = await data_broker_manager_test(data_broker_id)

    pretty_log(compiled_recipe, "Compiled Recipe Data")
    pretty_log(broker, "Broker Data")

    final_structure = compiled_recipe.runtime.dto.get_final_structure()
    pretty_log(final_structure, "Final Structure")

    ready_messages = compiled_recipe.runtime.dto.ready_messages
    for message in ready_messages:
        log_message(message)

    await compiled_recipe_manager.add_broker(compiled_recipe_id, broker)

    new_final_structure = await compiled_recipe_manager.get_final_structure(compiled_recipe_id)
    pretty_log(new_final_structure, "New Final Structure")

    final_messages = new_final_structure.get("messages")
    for index, message in enumerate(final_messages, start=1):
        log_intermediate_message(message, index)

    # compiled_recipe_id: str, broker_id: str, value: str
    broker_id_to_update = "790ea0c3-8472-4127-b134-77b42da44e2f"
    value = "New Updated Value 1"
    print("-" * 100)
    await compiled_recipe_manager.update_broker_value(compiled_recipe_id, broker_id_to_update, value)
    print("-" * 100)

    # batch_broker_values = [
    #     {"id": "790ea0c3-8472-4127-b134-77b42da44e2f", "value": "New Updated Value 2"},
    #     {"id": "0f4505ca-bc96-47fb-8efd-c2d1a2dabfde", "value": "New Updated Value 3"}
    # ]
    # await compiled_recipe_manager.update_broker_values(compiled_recipe_id, batch_broker_values)

    new_final_structure = await compiled_recipe_manager.get_final_structure(compiled_recipe_id)
    pretty_log(new_final_structure, "Structure After Updatig Broker Value")

    final_messages = new_final_structure.get("messages")
    for index, message in enumerate(final_messages, start=1):
        log_final_message(message, index)


if __name__ == "__main__":
    os.system("cls")

    compiled_recipe_id = "6f373a7a-522b-4c4e-bdc9-17081ea1736f"  # "db3e1b4e-c197-493d-b594-f98d17e6bb68"
    data_broker_id = "2b09cd3d-1a22-4bee-bc1b-7aa4ad4a1cd4"

    data = {"compiled_recipe_id": compiled_recipe_id, "data_broker_id": data_broker_id}

    asyncio.run(orchestrator_manager_test(data))
