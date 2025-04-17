# relationship_trials.py
import asyncio
from common import vcprint
from database.orm.models import DataBroker, DataInputComponent, MessageBroker
from database.state import StateManager


async def relationship_trial():
    # 1. Test Forward Foreign Key Relationships
    vcprint("\nTesting Forward Foreign Key Relationships:", color="yellow")
    broker = await DataBroker.get(id="331fd73e-2619-44d5-afaa-f9a567c2d509")

    # Get the related DataInputComponent
    vcprint("\nFetching default component:", color="yellow")
    default_component_id = broker.default_component
    if default_component_id:
        component = await DataInputComponent.get(id=default_component_id)
        vcprint(
            component.to_dict(),
            title="Related DataInputComponent",
            color="green",
            pretty=True,
        )

        # Verify it's in cache
        cached_component = await StateManager.get(DataInputComponent, id=default_component_id)
        vcprint("Component in cache:", bool(cached_component), color="blue")

    # 2. Test Inverse Foreign Key Relationships
    vcprint("\nTesting Inverse Foreign Key Relationships:", color="yellow")

    # Get all message brokers that reference this data broker
    message_brokers = await MessageBroker.filter(broker_id=broker.id).all()
    vcprint(f"Found {len(message_brokers)} related message brokers", color="blue")

    if message_brokers:
        broker_dicts = [mb.to_dict() for mb in message_brokers]
        vcprint(broker_dicts, title="Related Message Brokers", color="green", pretty=True)

    # 3. Test Bulk Related Data Loading
    vcprint("\nTesting Bulk Related Data Loading:", color="yellow")
    await broker.fetch_related()

    # Check if related data is cached
    has_component_cache = hasattr(broker, "_default_component_cache")
    has_message_brokers_cache = hasattr(broker, "_message_brokers_cache")

    vcprint(
        {
            "Component Cached": has_component_cache,
            "Message Brokers Cached": has_message_brokers_cache,
        },
        title="Cache Status",
        color="green",
        pretty=True,
    )

    # 4. Test Relationship Navigation
    vcprint("\nTesting Relationship Navigation:", color="yellow")
    if message_brokers:
        first_message_broker = message_brokers[0]
        # Navigate back to the data broker
        related_broker = await DataBroker.get(id=first_message_broker.broker_id)
        vcprint(
            "Relationship navigation successful:",
            broker.id == related_broker.id,
            color="blue",
        )

    # Test Cache Coherency
    vcprint("\nTesting Cache Coherency:", color="yellow")
    if message_brokers:
        mb = message_brokers[0]
        original_value = mb.default_value
        test_value = "Test Update Value"

        try:
            # Update with new value
            mb.default_value = test_value
            await mb.save()

            # Verify cache update
            cached_mb = await StateManager.get(MessageBroker, id=mb.id)
            vcprint(
                {
                    "Original Value": original_value,
                    "Updated Value": cached_mb.default_value if cached_mb else None,
                    "Cache Updated": cached_mb.default_value == test_value if cached_mb else False,
                },
                title="Cache Update Check",
                color="green",
                pretty=True,
            )
        finally:
            # Always restore original value
            mb.default_value = original_value
            await mb.save()


if __name__ == "__main__":
    asyncio.run(relationship_trial())
