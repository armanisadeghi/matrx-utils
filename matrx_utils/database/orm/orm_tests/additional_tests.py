import asyncio
import time

from common import vcprint
from common.utils.fancy_prints import cool_print
from database.orm.models import DataBroker, MessageBroker
from common import vcprint
from database.orm.models import DataBroker


def type_sentence(sentence):
    for char in sentence:
        print(char, end="", flush=True)
        time.sleep(0.02)


def final_message():
    print("\n")
    type_sentence("If only all libraries were this easy to use and this fun to learn!\n")
    type_sentence("\n")
    type_sentence("At the same time, as much as I would love to waste the rest of my day doing stupid shit like this, I actually have some real programminng to do.\n")
    type_sentence("\n")
    type_sentence("By the way... If you find any bugs in this ORM, it's not because it's a bug, it's because you're clearly doing it wrong! Haha. just kidding.\n")
    type_sentence("\n")
    type_sentence("I'm sure there are TONS AND TONS of bugs. I've only tested about 10% of the features so far.\n")
    type_sentence("\n")
    type_sentence(
        "But I hope you appreciate the REALLY REALLY UNIQUE features, such as the inverse foreign key relationships, and the ability to 'reach through' a relationship to get other related objects.\n"
    )
    type_sentence("\n")
    type_sentence(
        "And I think the caching is really cool as well and allows you to have full caching, without thinking about it. But we have to be very careful about using it and properly set cache policies.\n"
    )
    type_sentence("\n")
    last_message()


def last_message():
    print("\n")
    cool_print(
        "=============== =============== =============== ===============  ===============",
        color="bright_purple",
        style="bold",
    )
    time.sleep(0.08)
    cool_print(
        "=============== =============== =============== ===============  ===============",
        color="bright_purple",
        style="bold",
    )
    time.sleep(0.08)
    cool_print(
        "=============== ===============                 ===============  ===============",
        color="bright_purple",
        style="bold",
    )
    time.sleep(0.08)
    cool_print(
        "=============== ===============   Matrx Nexus   ===============  ===============",
        color="bright_purple",
        style="bold",
    )
    time.sleep(0.08)
    cool_print(
        "=============== ===============       ORM       ===============  ===============",
        color="bright_purple",
        style="bold",
    )
    time.sleep(0.08)
    cool_print(
        "=============== =============== =============== ===============  =======@=======",
        color="bright_purple",
        style="bold",
    )
    time.sleep(0.08)
    cool_print(
        "=============== =============== =============== ===============  ===============",
        color="bright_purple",
        style="bold",
    )
    print("\n")
    type_sentence("The '@' is there to remind you that there will be bugs. Please be part of the solution ;)\n\n\n")


async def test_bulk_operations():
    vcprint("\nTesting Bulk Operations:", color="yellow")

    # Get multiple brokers with their relationships
    brokers = await DataBroker.filter(data_type="str").all()
    vcprint(f"Found {len(brokers)} brokers", color="blue")

    # Bulk fetch related data
    for broker in brokers:
        await broker.fetch_related()

    # Verify all relations are cached - convert UUIDs to strings
    relation_stats = {
        str(broker.id): {  # Convert UUID to string
            "has_component": hasattr(broker, "_default_component_cache"),
            "has_messages": hasattr(broker, "_message_brokers_cache"),
        }
        for broker in brokers
    }
    vcprint(relation_stats, title="Relation Cache Status", color="green", pretty=True)

    # Show the actual related data counts
    for broker in brokers:
        vcprint(f"\nBroker {broker.id}:", color="blue")
        if hasattr(broker, "_default_component_cache"):
            component = getattr(broker, "_default_component_cache")
            vcprint(
                f"- Default component: {component.id if component else None}",
                color="blue",
            )
        if hasattr(broker, "_message_brokers_cache"):
            messages = getattr(broker, "_message_brokers_cache")
            vcprint(f"- Message count: {len(messages) if messages else 0}", color="blue")


async def test_complex_query():
    vcprint("\nTesting Complex Queries:", color="yellow")

    # Find brokers that have message brokers with specific values
    brokers = await DataBroker.filter(data_type="str").order_by("name").all()

    # Limit the number of brokers processed to 10
    for i, broker in enumerate(brokers):
        if i >= 10:
            break  # Exit after processing 10 brokers

        message_brokers = await MessageBroker.filter(broker_id=broker.id).all()
        vcprint(f"Broker {broker.id} has {len(message_brokers)} messages", color="blue")


async def test_error_handling():
    vcprint("\nTesting Error Handling:", color="yellow")

    try:
        # Try to get non-existent broker
        await DataBroker.get(id="00000000-0000-0000-0000-000000000000")
    except Exception as e:
        vcprint(f"Expected error caught: {str(e)}", color="green")

    try:
        # Try to update with invalid field
        broker = await DataBroker.get(id="331fd73e-2619-44d5-afaa-f9a567c2d509")
        broker.nonexistent_field = "test"
        await broker.save()
    except Exception as e:
        vcprint(f"Invalid field error caught: {str(e)}", color="green")


async def test_all():
    await test_bulk_operations()
    await test_complex_query()
    await test_error_handling()


if __name__ == "__main__":
    asyncio.run(test_all())
