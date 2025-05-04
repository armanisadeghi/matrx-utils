# matrx_utils\database\orm\core\managed_models.py
import asyncio
from common.utils.fancy_prints import vcprint
from database.orm.models import MessageTemplate
from database.orm.models import DataBrokerManager


class BrokerManager(DataBrokerManager):
    def __init__(self):
        super().__init__()
        all_attributes = vars(self)
        vcprint(all_attributes, title="All Attributes", color="blue", pretty=True)

    async def load_broker(self, id):
        return await self.load_item(id)

    async def load_broker_get_dict(self, id):
        return await self.load_item_get_dict(id)

    async def load_brokers(self, broker_ids):
        return await self.load_items(broker_ids)

    async def load_brokers_get_dict(self, broker_ids):
        return await self.load_items_get_dict(broker_ids)

    async def create_broker(self, **data):
        return await self.create_item(**data)

    async def create_broker_get_dict(self, **data):
        return await self.create_item_get_dict(**data)

    async def update_broker(self, id, **updates):
        return await self.update_item(id, **updates)

    async def update_broker_get_dict(self, id, **updates):
        return await self.update_item_get_dict(id, **updates)

    async def get_active_brokers(self):
        return await self.get_active_items()

    async def get_active_brokers_dict(self):
        return await self.get_active_items_dict()

    async def get_input_component(self, id):
        return await self.get_foreign_key_related_object(id, "default_component")

    async def get_input_component_dict(self, id):
        component = await self.get_input_component(id)
        return component.to_dict() if component else None

    async def get_active_input_components(self):
        return await asyncio.gather(*(self.get_input_component(bid) for bid in self._active_items))

    async def get_active_input_components_dict(self):
        return await asyncio.gather(*(self.get_input_component_dict(bid) for bid in self._active_items))

    async def get_message_brokers(self, id):
        return await self.get_inverse_related_objects(id, "message_brokers_inverse")

    async def get_message_brokers_dict(self, id):
        return [broker.to_dict() for broker in await self.get_message_brokers(id)]

    async def get_active_message_brokers(self):
        return await asyncio.gather(*(self.get_message_brokers(bid) for bid in self._active_items))

    async def get_active_message_brokers_dict(self):
        return await asyncio.gather(*(self.get_message_brokers_dict(bid) for bid in self._active_items))

    async def get_messages(self, id):
        return await self.get_related_through_inverse(id, "message_brokers_inverse", "message_id", MessageTemplate)

    async def get_messages_dict(self, id):
        return [msg.to_dict() for msg in await self.get_messages(id)]

    async def get_active_messages(self):
        return await asyncio.gather(*(self.get_messages(bid) for bid in self._active_items))

    async def get_active_messages_dict(self):
        return await asyncio.gather(*(self.get_messages_dict(bid) for bid in self._active_items))

    async def get_active_related_data(self):
        return {
            "input_components": await self.get_active_input_components_dict(),
            "message_brokers": await self.get_active_message_brokers_dict(),
            "messages": await self.get_active_messages_dict(),
        }


async def main():
    broker_manager = BrokerManager()

    # await broker_manager.load_broker("109e838c-f285-48fc-91ad-39bc41261eeb")

    broker_data_dict = await broker_manager.load_broker_get_dict("4c09a4a9-f991-4848-bd45-519cd07c836e")
    vcprint(broker_data_dict, title="Broker Data Dict", color="blue", pretty=True)

    active_brokers_dict = await broker_manager.get_active_brokers_dict()
    vcprint(active_brokers_dict, title="Active Brokers Dict", color="green", pretty=True)

    active_input_components_dict = await broker_manager.get_active_input_components_dict()
    vcprint(
        active_input_components_dict,
        title="Active Input Components Dict",
        color="cyan",
        pretty=True,
    )

    # active_message_brokers_dict = await broker_manager.get_active_message_brokers_dict()
    # active_messages_dict = await broker_manager.get_active_messages_dict()

    # related_data = await broker_manager.get_active_related_data()

    # vcprint(active_message_brokers_dict, title="Active Message Brokers Dict", color="magenta", pretty=True)
    # vcprint(active_messages_dict, title="Active Messages Dict", color="red", pretty=True)
    # vcprint(related_data, title="Related Data", color="yellow", pretty=True)


if __name__ == "__main__":
    asyncio.run(main())
