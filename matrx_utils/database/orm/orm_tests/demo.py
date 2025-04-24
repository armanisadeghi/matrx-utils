# database\orm\demo.py
import asyncio

from common import vcprint
from common.utils.fancy_prints import cool_print
from database.orm.models import DataBroker, DataInputComponent, DataOutputComponent
from database.orm.orm_tests.additional_tests import final_message, type_sentence
import time
import os


# Run this file to see the ORM in action
# It's best to run it once and read the output
# Then, go through it section by section to learn the basics

# NOTE: This demo only covers basic read operations, but you can check the rest of C_UD in the code.

# UPDATE: Now, you're down to just _ _ U _ because I added Create and Delete to this tutorial as well. Not the fancy versions, but just the basics for now.

# ANOTHER UPDATE: We are down to _ _ _ _ yay!!! All basic CRUD completed. (But bulk operations and things like that may or may not work. haha)


def clear_terminal():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


async def basic_operations_demo(broker_id):
    async def wait_for_enter():
        cool_print(
            "\nPress Enter to continue to the next section...",
            color="white",
            style="bold",
        )
        await asyncio.get_event_loop().run_in_executor(None, input)

    # Clear the terminal at the start
    clear_terminal()
    cool_print(
        "Welcome to the Database Operations Demo!\n\n Please make your terminal nice and big so you can see and read everything. \n\n",
        color="white",
        style="bold",
    )
    await wait_for_enter()

    vcprint(
        "\n =============== Use vcprint to Print the Model Itself to see fields and metadata  ===============\n",
        color="yellow",
    )

    cool_print(
        "\n --> vcprint(DataBroker, title='DataBroker', color='yellow', pretty=True) \n",
        color="white",
        style="bold",
    )

    vcprint(DataBroker, title="DataBroker", color="yellow", pretty=True)

    vcprint(
        "\n =============== =============== =============== =============== ===============  ===============\n",
        color="yellow",
    )
    await wait_for_enter()

    vcprint(
        "\n =============== Using get_by_id & Directly Print the data for the instance  ===============\n",
        color="green",
    )

    cool_print(
        "\n --> broker = await DataBroker.get_by_id(broker_id) \n",
        color="white",
        style="bold",
    )

    broker = await DataBroker.get_by_id(broker_id)

    vcprint(broker, title="Broker", color="green", pretty=True)

    vcprint(
        "\n =============== =============== =============== =============== ===============  ===============\n",
        color="green",
    )
    await wait_for_enter()

    vcprint(
        "\n =============== Using fetch_fk to directly fetch data for tables with a foreign key reference  ===============\n",
        color="blue",
    )

    cool_print(
        "\n --> input_component_object = await broker.fetch_fk('input_component') \n",
        color="white",
        style="bold",
    )

    input_component_object = await broker.fetch_fk("input_component")
    vcprint(input_component_object, title="Input Component", color="blue", pretty=True)

    type_sentence("\n\nWe just 'reached through' the broker to get the input component. Notice that we did not need to get the other model. It's just there!!!\n\n")

    vcprint(
        "\n =============== =============== =============== =============== ===============  ===============\n",
        color="blue",
    )
    await wait_for_enter()

    vcprint(
        "\n =============== No fk value. No problem. No Errors.  ===============\n",
        color="bright_purple",
    )

    cool_print(
        "\n --> output_component_object = await broker.fetch_fk('output_component') \n",
        color="white",
        style="bold",
    )

    output_component_object = await broker.fetch_fk("output_component")
    vcprint(
        output_component_object,
        title="Output Component",
        color="bright_purple",
        pretty=True,
    )

    type_sentence("\n\nSince we cannot possibly know (I guess we could) if there is actually an entry, trying to get it will not cause errors.\n\n")

    vcprint(
        "\n =============== =============== =============== =============== ===============  ===============\n",
        color="bright_purple",
    )
    await wait_for_enter()

    vcprint(
        "\n =============== Using fetch_ifk to directly fetch data for tables that reference the current table  ===============\n",
        color="bright_orange",
    )

    cool_print(
        "\n --> broker_values = await broker.fetch_ifk('broker_values') \n",
        color="white",
        style="bold",
    )
    cool_print(
        "\n --> message_brokers = await broker.fetch_ifk('message_brokers') \n",
        color="white",
        style="bold",
    )

    type_sentence(
        "\n\n Now, this part is kind of magical so get ready for it... We are about to not only have 'knowledge' of the tables that reference the current table, but we are also going to fetch the data for them.\n\n"
    )

    await wait_for_enter()

    broker_values = await broker.fetch_ifk("broker_values")
    vcprint(broker_values, title="Broker Values", color="bright_orange", pretty=True)

    message_brokers = await broker.fetch_ifk("message_brokers")
    vcprint(message_brokers, title="Message Brokers", color="bright_orange", pretty=True)

    first_message_broker = message_brokers[0]

    first_message = await first_message_broker.fetch_fk("message_id")

    vcprint(first_message, title="First Message", color="bright_orange", pretty=True)

    type_sentence("\n\n All of that was just done without any information about the models or their relationships! \n\n")
    type_sentence("\n\n We also have automated features that can just fetch them all by default, but you have to be careful. \n\n")
    type_sentence("\n\n If you did this with a table for 'tags' for example, you would fetch hundreds of unwanted records. \n\n")

    vcprint(
        "\n =============== =============== =============== =============== ===============  ===============\n",
        color="bright_orange",
    )
    await wait_for_enter()

    vcprint(
        "\n =============== Now, we are going to take this to the next level, and reach through the related table and get the tables it points to!  ===============\n",
        color="yellow",
    )

    type_sentence(
        "\n\n Since you aren't familiar with this table, think about what we're doing. Messages have 'message_brokers' which connect messages to brokers. We are in Brokers right now, so we're two steps removed from messages and we're sort of pointing in the 'wrong' direction as far as most other ORMs see it. \n\n"
    )

    await wait_for_enter()

    all_messages_for_all_message_brokers = await asyncio.gather(*[mb.fetch_fk("message_id") for mb in message_brokers])

    vcprint(
        all_messages_for_all_message_brokers,
        title="All Messages for All Message Brokers",
        color="yellow",
        pretty=True,
    )

    vcprint(
        "\n =============== =============== =============== =============== ===============  ===============\n",
        color="yellow",
    )
    await wait_for_enter()

    vcprint(
        "\n =============== Using get or get_by_id to fetch data from the database  ===============\n",
        color="green",
    )

    cool_print(
        "\n --> cached_broker = await DataBroker.get(id=broker_id) \n",
        color="white",
        style="bold",
    )

    cached_broker = await DataBroker.get(id=broker_id)

    vcprint(cached_broker.to_dict(), title="Cached Broker", color="green", pretty=True)

    vcprint(
        "\n =============== =============== =============== =============== ===============  ===============\n",
        color="green",
    )
    await wait_for_enter()

    vcprint(
        "\n =============== Using Filter to conduct a 'search' for whatever fields and values you want to match  ===============\n",
        color="bright_teal",
    )

    cool_print(
        "\n --> brokers = await DataBroker.filter(name='New Broker').all() \n",
        color="white",
        style="bold",
    )

    cool_print(
        "\n --> brokers_dicts = [b.to_dict() for b in brokers] \n",
        color="white",
        style="bold",
    )
    brokers = await DataBroker.filter(name="New Broker").all()

    vcprint(f"Found {len(brokers)} brokers with data_type='str'", color="bright_teal")

    brokers_dicts = [b.to_dict() for b in brokers]

    vcprint(brokers_dicts, title="Brokers", color="bright_teal", pretty=True)

    vcprint(
        "\n =============== =============== =============== =============== ===============  ===============\n",
        color="bright_teal",
    )
    await wait_for_enter()

    vcprint(
        "\n =============== Listing all brokers in cache  ===============\n",
        color="bright_lavender",
    )

    vcprint(
        f"Broker cache policy: {DataBroker._cache_policy}",
        color="bright_lavender",
        inline=True,
    )

    vcprint(
        "\n--> Import placed here to show you never need to think about the cache or state",
        color="bright_lavender",
    )
    from database.state import StateManager

    cool_print(
        "\n --> in_cache = bool(await StateManager.get(DataBroker, id=broker_id)) \n",
        color="white",
        style="bold",
    )

    in_cache = bool(await StateManager.get(DataBroker, id=broker_id))

    vcprint(
        in_cache,
        title="--> Checking if the broker is in cache... Is it????",
        color="bright_lavender",
        inline=True,
    )

    cool_print(
        "\n --> cache_count = await StateManager.count(DataBroker) \n",
        color="white",
        style="bold",
    )

    cache_count = await StateManager.count(DataBroker)

    vcprint(f"--> Total brokers in cache: {cache_count}", color="bright_lavender")

    vcprint(
        "\n =============== =============== =============== =============== ===============  ===============\n",
        color="bright_lavender",
    )
    await wait_for_enter()

    vcprint(
        "\n =============== Cached Brokers Dictionaries  ===============\n",
        color="bright_pink",
    )

    cool_print(
        "\n --> cached_brokers = await StateManager.get_all(DataBroker) \n",
        color="white",
        style="bold",
    )

    cool_print(
        "\n --> cached_broker_dicts = [broker.to_dict() for broker in cached_brokers] \n",
        color="white",
        style="bold",
    )
    cached_brokers = await StateManager.get_all(DataBroker)

    cached_broker_dicts = [broker.to_dict() for broker in cached_brokers]

    vcprint(
        cached_broker_dicts,
        title="All Cached Brokers",
        color="bright_pink",
        pretty=True,
    )

    vcprint(
        "\n =============== =============== =============== =============== ===============  ===============\n",
        color="bright_pink",
    )
    await wait_for_enter()

    vcprint(
        "\n =============== Override Cache and Get a fresh instance  ===============\n",
        color="cyan",
    )

    broker = await DataBroker.get(id=broker_id, bypass_cache=True)

    vcprint(broker, title="Broker", color="cyan", pretty=True)

    vcprint(
        "\n =============== =============== =============== =============== ===============  ===============\n",
        color="cyan",
    )
    await wait_for_enter()

    vcprint(
        "\n =============== ORM Tutorial: CRUD Operations Demo ===============\n",
        color="bright_lime",
    )

    # Create operation demo
    vcprint("\n1. Creating a New Broker", color="bright_lime")
    type_sentence("First, let's create a new broker with minimal fields. Note that fields like data_type and color have defaults.")

    test_broker = {
        "name": "New Unique TestBroker",
        "default_value": "This is my default value. I'm a test so if you see me, please delete me.",
    }

    broker = await DataBroker.create(**test_broker)
    vcprint(broker, title="Newly Created Broker", color="bright_lime", pretty=True)

    vcprint(
        "\n =============== =============== =============== =============== ===============  ===============\n",
        color="bright_lime",
    )
    await wait_for_enter()

    # Update demos
    vcprint("\n2. Different Ways to Update a Broker", color="bright_lime")

    # Method 1: Direct attribute update and save
    vcprint("\nMethod 1: Update attribute directly and save\n", color="cyan")
    type_sentence("This is the most straightforward way to update a single field\n")

    basic_select_component = await DataInputComponent.filter(name="Simple Select Dropdown").first()
    broker.input_component = basic_select_component.id
    await broker.save()

    updated_broker = await DataBroker.get(id=broker.id, bypass_cache=True)
    vcprint(
        updated_broker,
        title="Broker Updated with Input Component",
        color="bright_lime",
        pretty=True,
    )

    vcprint(
        "\n =============== =============== =============== =============== ===============  ===============\n",
        color="bright_lime",
    )
    await wait_for_enter()

    # Method 2: Update using update() method
    vcprint("\nMethod 2: Using the update() method", color="cyan")
    type_sentence("This method allows updating multiple fields in one call")

    basic_chat_component = await DataOutputComponent.filter(component_type="chatResponse").first()

    cool_print(
        "\n --> updated_broker = await broker.update( your updates here )\n",
        color="white",
        style="bold",
    )

    updated_broker = await broker.update(
        output_component=basic_chat_component.id,
        data_type="int",  # Changing from default 'str' to 'int'
        color="red",  # Changing from default 'blue' to 'red'
    )

    updated_broker = await DataBroker.get(id=broker.id, bypass_cache=True)
    vcprint(
        updated_broker,
        title="Broker Updated with Multiple Fields",
        color="bright_lime",
        pretty=True,
    )

    vcprint(
        "\n =============== =============== =============== =============== ===============  ===============\n",
        color="bright_lime",
    )
    await wait_for_enter()

    # Method 3: Using update_fields class method
    vcprint("\nMethod 3: Using update_fields class method", color="cyan")
    type_sentence("This method is useful when you want to update an instance by ID")

    cool_print(
        "\n --> updated_broker = await DataBroker.update_fields(broker.id, your updates here)\n",
        color="white",
        style="bold",
    )

    updated_broker = await DataBroker.update_fields(broker.id, data_type="list", color="green")
    vcprint(
        updated_broker,
        title="Broker Updated Using update_fields",
        color="bright_lime",
        pretty=True,
    )

    vcprint(
        "\n =============== =============== =============== =============== ===============  ===============\n",
        color="bright_lime",
    )
    await wait_for_enter()

    # Delete and verify
    vcprint("\n3. Deleting and Verifying Deletion", color="bright_lime")
    type_sentence("Now we'll delete the broker and verify it's gone")

    cool_print("\n --> await broker.delete() \n", color="white", style="bold")

    await broker.delete()

    # Try to find by name
    broker_by_name = await DataBroker.filter(name="New Unique TestBroker").first()
    vcprint(
        broker_by_name,
        title="Attempt to Find Deleted Broker by Name",
        color="bright_lime",
        pretty=True,
    )

    vcprint(
        "\n =============== =============== =============== =============== ===============  ===============\n",
        color="bright_lime",
    )
    await wait_for_enter()

    cool_print(
        "\n --> broker_by_id = await DataBroker.get_or_none(id=broker.id) \n",
        color="white",
        style="bold",
    )

    type_sentence("\n\nAlthough you don't need to do this, we can be explicit about 'getting one or none' \n\n")

    await wait_for_enter()

    broker_by_id = await DataBroker.get_or_none(id=broker.id)
    vcprint(
        broker_by_id,
        title="Attempt to Find Deleted Broker by ID",
        color="bright_lime",
        pretty=True,
    )

    type_sentence("\n\nWhen was the last time you got an error that was that easy to understand and so PRETTY?!?!?\n\n")

    vcprint(
        "\n =============== That covers the basics of CRUD, but a few more things... ===============\n",
        color="bright_lime",
    )
    await wait_for_enter()

    vcprint(
        "\n #################### LAZY DEVELOPER GRAND FINALE ####################\n",
        color="bright_gold",
    )

    vcprint(
        " --> Too Lazy to type this really REALLY long and confusing filter?\n",
        color="bright_gold",
    )
    vcprint(
        "  brokers = await DataBroker.filter(name='New Broker').all()",
        color="bright_gold",
    )

    vcprint(
        "\n =======> Me too! So don't. Just do this instead and get the same result:\n",
        color="bright_gold",
    )

    type_sentence("\n I don't know who came up with the idea of something.something_else().anotherthing().blahBlach but I don't liek it!!!\n")
    await wait_for_enter()

    vcprint("brokers = await DataBroker.get_many(name='New Broker')", color="bright_gold")

    start_time = time.perf_counter()

    filtered_brokers = await DataBroker.get_many(name="My Favorite Broker")

    duration_ms = (time.perf_counter() - start_time) * 1000

    vcprint(filtered_brokers, title="Filtered Brokers", color="bright_gold", pretty=True)

    vcprint(
        f"\nQuery execution time: {duration_ms:.3f}ms (These were not cached)",
        color="bright_gold",
    )

    vcprint(
        "\n =============== =============== =============== =============== ===============  ===============\n",
        color="bright_gold",
    )

    final_message()


if __name__ == "__main__":
    broker_id = "109e838c-f285-48fc-91ad-39bc41261eeb"
    asyncio.run(basic_operations_demo(broker_id))
