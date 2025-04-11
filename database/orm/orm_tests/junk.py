from database.orm.core.base import Model
from database.orm.core.fields import DateTimeField, UUIDField, CharField, TextField
from database.orm.core.relations import ForeignKey


# https://claude.ai/chat/c307841f-89f9-4347-a885-a0640e3968f5


class DataBroker(Model):
    # Actual database fields
    id = UUIDField(is_native=True, primary_key=True, null=False)
    name = CharField(is_native=True, null=False)
    data_type = CharField(is_native=True, default="str")
    default_value = TextField(is_native=True)
    default_component = ForeignKey(
        is_native=True,
        to_model="DataInputComponent",
        to_field="id",
        default="6463aae0-9480-4c4c-90b8-e3ce9c11a103",
    )
    color = CharField(is_native=True, default="blue")

    class Meta:
        # Who points to us
        inverse_relationships = {
            "message_brokers": {
                "from_model": "MessageBroker",
                "from_field": "broker_id",
                "to_field": "id",
                "relationship_type": "one_to_one",
            }
        }

        # How to traverse through intermediaries
        cross_relationships = {
            "related_messages": {
                "through_relationship_type": "inverse_relationships",
                "through_model": "message_brokers",
                "via_field": "message_id",
                "target_model": "MessageTemplate",
                "target_field": "id",
            }
        }


class MessageTemplate(Model):
    id = UUIDField(primary_key=True, null=False)
    role = CharField(null=False, default="user")
    type = CharField(null=False, default="text")
    created_at = DateTimeField(null=False)
    content = TextField()

    class Meta:
        inverse_relationships = {
            "message_brokers": {
                "from_model": "MessageBroker",
                "from_field": "message_id",
                "to_field": "id",
                "relationship_type": "one_to_one",
            },
            "recipe_messages": {
                "from_model": "RecipeMessage",
                "from_field": "message_id",
                "to_field": "id",
                "relationship_type": "one_to_one",
            },
        }

        cross_relationships = {
            "related_brokers": {
                "through_relationship_type": "inverse_relationships",
                "through_model": "message_brokers",
                "via_field": "broker_id",
                "target_model": "DataBroker",
                "target_field": "id",
            },
            "related_recipes": {
                "through_relationship_type": "inverse_relationships",
                "through_model": "recipe_messages",
                "via_field": "recipe_id",
                "target_model": "Recipe",
                "target_field": "id",
            },
        }


class MessageBroker(Model):
    id = UUIDField(primary_key=True, null=False)
    message_id = ForeignKey(to_model="MessageTemplate", null=False)
    broker_id = ForeignKey(to_model="DataBroker", null=False)
    default_value = TextField()
    default_component_override = ForeignKey(
        to_model="DataInputComponent",
    )
    data_broker_reference = ForeignKey(to_model="DataBroker", related_name="message_broker")
    data_input_component_reference = ForeignKey(to_model="DataInputComponent", related_name="message_broker")
    message_template_reference = ForeignKey(to_model="MessageTemplate", related_name="message_broker")
