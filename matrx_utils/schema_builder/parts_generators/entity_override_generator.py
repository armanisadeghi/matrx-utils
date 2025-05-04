# matrx_utils\schema_builder\parts_generators\entity_override_generator.py
from matrx_utils.schema_builder.helpers.manual_overrides import SYSTEM_OVERRIDES_ENTITIES


def generate_imports():
    #     return """import { EntityKeys } from '@/types';
    # import { EntityOverrides } from './overrideTypes';
    # """
    return ""


def generate_typescript_entity(entity_name, overrides=None):
    overrides = overrides or {}
    ts_template = f"""
const {entity_name}EntityOverrides: EntityOverrides<'{entity_name}'> = {{
    schemaType: {overrides.get('schemaType', 'null')},
    entityName: {overrides.get('entityName', 'null')},
    uniqueTableId: {overrides.get('uniqueTableId', 'null')},
    uniqueEntityId: {overrides.get('uniqueEntityId', 'null')},
    primaryKey: {overrides.get('primaryKey', 'null')},
    primaryKeyMetadata: {overrides.get('primaryKeyMetadata', 'null')},
    displayFieldMetadata: {overrides.get('displayFieldMetadata', 'null')},
    defaultFetchStrategy: {overrides.get('defaultFetchStrategy', 'null')},
    componentProps: {overrides.get('componentProps', 'null')},
    entityNameFormats: {overrides.get('entityNameFormats', 'null')},
    relationships: {overrides.get('relationships', 'null')},
    entityFields: {overrides.get('entityFields', 'null')}
}};
"""
    return ts_template


def generate_multiple_entities(entity_names, system_overrides):
    imports = generate_imports()
    entities_code = "\n\n".join(generate_typescript_entity(name, system_overrides.get(name, {})) for name in entity_names)

    entity_overrides_list = "\n".join(f"    {name}: {name}EntityOverrides," for name in entity_names)

    entity_overrides_block = f"""

export const ENTITY_OVERRIDES: Record<EntityKeys, EntityOverrides<EntityKeys>> = {{
{entity_overrides_list}
}};
"""

    return imports + "\n" + entities_code + entity_overrides_block


if __name__ == "__main__":
    entity_names = ["projects", "recipe", "wc_impairment_definition"]
    ts_code = generate_multiple_entities(entity_names, SYSTEM_OVERRIDES_ENTITIES)
    print(ts_code)
