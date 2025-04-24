from database.orm.models import (
    DataBroker,
    DataInputComponent,
    MessageBroker,
    MessageTemplate,
)
from common import vcprint
import asyncio


class BrokerManager:
    def __init__(self):
        self._active_brokers = set()

    async def load_broker(self, broker_id):
        broker = await DataBroker.get(id=broker_id)
        if broker:
            self._active_brokers.add(broker_id)
        return broker

    async def load_broker_with_related(self, broker_id):
        broker = await DataBroker.get(id=broker_id)
        if broker:
            self._active_brokers.add(broker_id)
            await broker.get_related()
        return broker

    async def load_brokers_by_ids(self, broker_ids):
        brokers = []
        for bid in broker_ids:
            broker = await DataBroker.get(id=bid)
            if broker:
                self._active_brokers.add(bid)
                brokers.append(broker)
        return brokers

    async def load_brokers_by_ids_with_related(self, broker_ids):
        brokers = []
        for bid in broker_ids:
            broker = await DataBroker.get(id=bid)
            if broker:
                self._active_brokers.add(bid)
                await broker.get_related()
                brokers.append(broker)
        return brokers

    async def create_broker(self, **data):
        broker = await DataBroker.create(**data)
        self._active_brokers.add(broker.id)
        return broker

    async def load_brokers(self, **filters):
        brokers = await DataBroker.filter(**filters).all()
        self._active_brokers.update(b.id for b in brokers)
        for broker in brokers:
            await broker.get_related()
        return brokers

    async def get_active_brokers(self):
        brokers = [await DataBroker.get(id=bid) for bid in self._active_brokers]
        for broker in brokers:
            await broker.get_related()
        return brokers

    async def get_active_brokers_data(self):
        brokers = await self.get_active_brokers()
        return [b.to_dict() for b in brokers]

    async def deactivate_broker(self, broker_id):
        self._active_brokers.discard(broker_id)

    async def deactivate_all(self):
        self._active_brokers.clear()

    async def update_broker(self, broker_id, **updates):
        broker = await DataBroker.get(id=broker_id)
        if broker:
            for key, value in updates.items():
                setattr(broker, key, value)
            await broker.save()
            await broker.get_related()
        return broker

    async def delete_broker(self, broker_id):
        broker = await DataBroker.get(id=broker_id)
        if broker:
            await broker.delete()
            self._active_brokers.discard(broker_id)
            return True
        return False

    async def count_active(self):
        return len(self._active_brokers)

    async def exists(self, broker_id):
        return bool(await DataBroker.get(id=broker_id))

    async def get_or_create(self, defaults=None, **kwargs):
        broker = await DataBroker.get(**kwargs)
        if not broker and defaults:
            broker = await self.create_broker(**{**kwargs, **defaults})
        return broker

    @property
    def active_broker_ids(self):
        return self._active_brokers.copy()

    async def get_input_component(self, broker_id):
        broker = await DataBroker.get(id=broker_id)
        if broker and broker.default_component:
            return await DataInputComponent.get(id=broker.default_component)
        return None

    async def get_message_brokers(self, broker_id):
        return await MessageBroker.filter(broker_id=broker_id).all()

    async def get_messages(self, broker_id):
        message_brokers = await self.get_message_brokers(broker_id)
        messages = []
        for mb in message_brokers:
            message = await MessageTemplate.get(id=mb.message_id)
            if message:
                messages.append(message)
        return messages

    async def get_active_input_component_ids(self):
        brokers = await self.get_active_brokers()
        return [b.default_component for b in brokers if b.default_component]

    async def get_active_input_components(self):
        component_ids = await self.get_active_input_component_ids()
        return await asyncio.gather(*(DataInputComponent.get(id=cid) for cid in component_ids))

    async def get_active_input_components_dict(self):
        components = await self.get_active_input_components()
        return [component.to_dict() for component in components]

    async def get_active_message_broker_ids(self):
        message_brokers = await asyncio.gather(*(self.get_message_brokers(bid) for bid in self._active_brokers))
        return [mb.id for mbs in message_brokers for mb in mbs]

    async def get_active_message_brokers(self):
        return await asyncio.gather(*(self.get_message_brokers(bid) for bid in self._active_brokers))

    async def get_active_message_brokers_dict(self):
        message_brokers = await self.get_active_message_brokers()
        return [broker.to_dict() for brokers in message_brokers for broker in brokers]

    async def get_active_message_ids(self):
        messages = await asyncio.gather(*(self.get_messages(bid) for bid in self._active_brokers))
        return [m.id for msgs in messages for m in msgs]

    async def get_active_messages(self):
        return await asyncio.gather(*(self.get_messages(bid) for bid in self._active_brokers))

    async def get_active_messages_dict(self):
        messages = await self.get_active_messages()
        return [message.to_dict() for msgs in messages for message in msgs]

    async def get_active_related_data(self):
        components = await self.get_active_input_components_dict()
        message_brokers = await self.get_active_message_brokers_dict()
        messages = await self.get_active_messages_dict()

        return {
            "input_components": components,
            "message_brokers": message_brokers,
            "messages": messages,
        }


if __name__ == "__main__":

    async def main():
        broker_manager = BrokerManager()
        broker = await broker_manager.load_broker("130a553d-235f-4476-b39e-0dfcb1972553")
        await broker_manager.load_broker("109e838c-f285-48fc-91ad-39bc41261eeb")

        messages = await broker_manager.get_messages(broker.id)
        vcprint(
            [m.to_dict() for m in messages],
            title="Related Messages",
            color="green",
            pretty=True,
        )

        related_data = await broker_manager.get_active_related_data()
        vcprint(related_data, title="Related Data", color="green", pretty=True)

    asyncio.run(main())
