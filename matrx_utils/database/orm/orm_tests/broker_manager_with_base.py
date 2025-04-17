from database.orm.models import (
    DataBroker,
    MessageTemplate,
)
from common import vcprint
import asyncio
from database.orm.core.relations import ForeignKeyReference

info = True
debug = False
verbose = False


class BaseManager:
    def __init__(self, primary_model):
        self.primary_model = primary_model

        self.foreign_keys = self.primary_model._meta.foreign_keys
        self.foreign_key_references = {name: field for name, field in self.primary_model._fields.items() if isinstance(field, ForeignKeyReference)}
        self.inverse_foreign_keys = self.primary_model._meta.inverse_foreign_keys
        self.all_relationships = {
            **self.foreign_keys,
            **self.foreign_key_references,
            **self.inverse_foreign_keys,
        }

        self.related_models = self._get_related_models()
        self._active_items = set()

        vcprint(
            self.foreign_keys,
            title="Foreign Keys",
            color="yellow",
            verbose=debug,
            pretty=True,
        )
        vcprint(
            self.foreign_key_references,
            title="Foreign Key References",
            color="yellow",
            verbose=debug,
            pretty=True,
        )
        vcprint(
            self.inverse_foreign_keys,
            title="Inverse Foreign Keys",
            color="yellow",
            verbose=debug,
            pretty=True,
        )
        vcprint(
            self.all_relationships,
            title="All Relationships",
            color="yellow",
            verbose=debug,
            pretty=True,
        )
        vcprint(
            self.related_models,
            title="Related Models",
            color="yellow",
            verbose=debug,
            pretty=True,
        )

    def _get_related_models(self):
        related_models = set()

        for rel in self.foreign_keys.values():
            if hasattr(rel, "to_model"):
                related_models.add(rel.to_model)

        for rel in self.foreign_key_references.values():
            if hasattr(rel, "to_model"):
                related_models.add(rel.to_model)

        for rel in self.inverse_foreign_keys.values():
            if hasattr(rel, "from_model"):
                related_models.add(rel.from_model)

        return list(related_models)

    def add_active_item(self, item_id):
        self._active_items.add(item_id)

    async def load_item(self, item_id):
        item = await self.primary_model.get(id=item_id)

        item_dict = item.to_dict()
        print(item_dict)

        vcprint(item, title="Item", color="blue", verbose=info, pretty=True)
        if item:
            self._active_items.add(item_id)
            return item
        return None

    async def load_item_get_dict(self, item_id):
        item = await self.load_item(item_id)
        return item.to_dict() if item else None

    async def load_items(self, item_ids):
        return await asyncio.gather(*(self.load_item(item_id) for item_id in item_ids))

    async def load_items_get_dict(self, item_ids):
        items = await self.load_items(item_ids)
        return [item.to_dict() for item in items if item]

    async def get_active_items(self):
        items = await asyncio.gather(*(self.primary_model.get(id=item_id) for item_id in self._active_items))
        for item in items:
            if item:
                await item.fetch_related()
        return items

    async def get_active_items_dict(self):
        return [item.to_dict() for item in await self.get_active_items() if item]

    async def load_items_by_ids(self, item_ids, fetch_related=False):
        items = []
        for item_id in item_ids:
            item = await self.primary_model.get(id=item_id)
            if item:
                self._active_items.add(item_id)
                if fetch_related:
                    await item.fetch_related()
                items.append(item)
        return items

    async def load_items_by_ids_get_dict(self, item_ids, fetch_related=False):
        items = await self.load_items_by_ids(item_ids, fetch_related)
        return [item.to_dict() for item in items]

    async def create_item(self, **data):
        item = await self.primary_model.create(**data)
        self._active_items.add(item.id)
        return item

    async def create_item_get_dict(self, **data):
        item = await self.create_item(**data)
        return item.to_dict()

    async def update_item(self, item_id, **updates):
        item = await self.primary_model.get(id=item_id)
        if item:
            for key, value in updates.items():
                setattr(item, key, value)
            await item.save()
            await item.fetch_related()
        return item

    async def update_item_get_dict(self, item_id, **updates):
        item = await self.update_item(item_id, **updates)
        return item.to_dict() if item else None

    async def delete_item(self, item_id):
        item = await self.primary_model.get(id=item_id)
        if item:
            await item.delete()
            self._active_items.discard(item_id)
            return True
        return False

    async def deactivate_item(self, item_id):
        self._active_items.discard(item_id)

    async def deactivate_all(self):
        self._active_items.clear()

    async def exists(self, item_id):
        return bool(await self.primary_model.get(id=item_id))

    async def get_or_create(self, defaults=None, **kwargs):
        item = await self.primary_model.get(**kwargs)
        if not item and defaults:
            item = await self.create_item(**{**kwargs, **defaults})
        return item

    async def get_or_create_dict(self, defaults=None, **kwargs):
        item = await self.get_or_create(defaults, **kwargs)
        return item.to_dict() if item else None

    async def get_related_objects(self, item_id, related_name):
        item = await self.primary_model.get(id=item_id)
        if not item or not hasattr(item, related_name):
            return []
        return await getattr(item, related_name).all()

    async def get_foreign_key_related_object(self, item_id, fk_name):
        vcprint(
            f"Getting foreign key related object for {item_id} with relationship {fk_name}",
            color="yellow",
        )
        fk_relationships = self._get_foreign_key_relationships()
        vcprint(fk_relationships, title="FK Relationships", color="yellow", pretty=True)

        if fk_name not in fk_relationships:
            return None  # No such relationship

        item = await self.primary_model.get(id=item_id)
        vcprint(item, title="Item", color="yellow", pretty=True)
        if not item:
            return None

        fk_value = getattr(item, fk_name, None)
        vcprint(fk_value, title="FK Value", color="yellow", pretty=True)
        if not fk_value:
            return None  # No reference set

        fk_model = fk_relationships[fk_name]["to_model"]
        fk_field = fk_relationships[fk_name]["to_field"]
        vcprint(fk_model, title="FK Model", color="yellow", pretty=True)
        vcprint(fk_field, title="FK Field", color="yellow", pretty=True)
        vcprint(fk_value, title="FK Value", color="yellow", pretty=True)

        return await fk_model.get(**{fk_field: fk_value})

    async def get_inverse_related_objects(self, item_id, relationship_name):
        inverse_relationships = self._get_inverse_relationships()

        if relationship_name not in inverse_relationships:
            return []

        relationship = inverse_relationships[relationship_name]
        related_model = relationship["from_model"]
        related_field = relationship["from_field"]

        return await related_model.filter(**{related_field: item_id}).all()

    async def get_related_through_inverse(self, item_id, through_relationship, target_field, target_model):
        intermediary_objects = await self.get_inverse_related_objects(item_id, through_relationship)
        target_ids = [getattr(obj, target_field) for obj in intermediary_objects]
        return await target_model.filter(id__in=target_ids).all()

    async def get_related_objects_dict(self, item_id, related_name):
        objects = await self.get_related_objects(item_id, related_name)
        return [obj.to_dict() for obj in objects if obj]

    async def get_active_related_data(self):
        related_data = {}
        for item_id in self._active_items:
            related_data[item_id] = {model: await self.get_related_objects_dict(item_id, model) for model in self.related_models}
        return related_data

    async def get_through_relationship(self, item_id, through_model, from_field, to_field, target_model):
        related_items = await through_model.filter(**{from_field: item_id}).all()
        target_ids = [getattr(item, to_field) for item in related_items]
        return await target_model.filter(id__in=target_ids).all()

    async def get_active_through_relationship(self, through_model, from_field, to_field, target_model):
        all_related = await asyncio.gather(*(self.get_through_relationship(item_id, through_model, from_field, to_field, target_model) for item_id in self._active_items))
        return [item for sublist in all_related for item in sublist]

    @property
    def active_item_ids(self):
        return self._active_items.copy()


class BrokerManager(BaseManager):
    def __init__(self):
        super().__init__(DataBroker)

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


if __name__ == "__main__":

    async def main():
        broker_manager = BrokerManager()
        # await broker_manager.load_broker("331fd73e-2619-44d5-afaa-f9a567c2d509")
        await broker_manager.load_broker("109e838c-f285-48fc-91ad-39bc41261eeb")

        # broker_data_dict = await broker_manager.load_broker_get_dict("4c09a4a9-f991-4848-bd45-519cd07c836e")
        # vcprint(broker_data_dict, title="Broker Data Dict", color="blue", pretty=True)

        # active_brokers_dict = await broker_manager.get_active_brokers_dict()
        # vcprint(active_brokers_dict, title="Active Brokers Dict", color="green", pretty=True)

        # active_input_components_dict = await broker_manager.get_active_input_components_dict()
        # vcprint(active_input_components_dict, title="Active Input Components Dict", color="cyan", pretty=True)

        # active_message_brokers_dict = await broker_manager.get_active_message_brokers_dict()
        # active_messages_dict = await broker_manager.get_active_messages_dict()

        # related_data = await broker_manager.get_active_related_data()

        # vcprint(active_message_brokers_dict, title="Active Message Brokers Dict", color="magenta", pretty=True)
        # vcprint(active_messages_dict, title="Active Messages Dict", color="red", pretty=True)
        # vcprint(related_data, title="Related Data", color="yellow", pretty=True)

    asyncio.run(main())
