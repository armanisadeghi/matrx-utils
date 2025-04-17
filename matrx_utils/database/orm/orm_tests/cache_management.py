import asyncio

from common import vcprint
from database.orm.models import DataBroker
from database.state import StateManager


# Add to your test script
async def test_cache_management():
    vcprint("\nTesting Cache Management:", color="yellow")

    # Get initial state
    broker = await DataBroker.get(id="331fd73e-2619-44d5-afaa-f9a567c2d509")

    # Force cache eviction
    await StateManager.remove(DataBroker, broker)

    # Verify it's gone
    cached_broker = await StateManager.get(DataBroker, id=broker.id)
    vcprint(cached_broker is None, "Broker removed from cache", color="blue")

    # Fetch again - should hit database
    refetched_broker = await DataBroker.get(id=broker.id)
    vcprint(refetched_broker is not None, "Broker refetched", color="blue")


if __name__ == "__main__":
    asyncio.run(test_cache_management())
