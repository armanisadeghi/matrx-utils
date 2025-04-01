import re

def to_camel_case(snake_str):
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

def to_pascal_case(snake_str):
    components = snake_str.split('_')
    return ''.join(x.title() for x in components)

def generate_import_statement(module, imports):
    imports_str = ', '.join(imports)
    return f"import {{ {imports_str} }} from '{module}';"

def generate_ts_type(table):
    type_name = to_pascal_case(table.table_name)
    fields = []
    for column in table.schema:
        field_name = column.column_name
        field_type = column.data_type  # This will need to be mapped to TypeScript types
        fields.append(f"    {field_name}: {field_type};")
    fields_str = '\n'.join(fields)
    return f"export type {type_name} = {{\n{fields_str}\n}};"

def generate_ts_types(schema_manager):
    ts_types = []
    for table in schema_manager.tables:
        ts_type = generate_ts_type(table)
        ts_types.append(ts_type)
    return ts_types

# Example usage:
schema_manager = SchemaManager()
schema_manager.load_schema()
schema_manager.initialize()
ts_types = generate_ts_types(schema_manager)
for ts_type in ts_types:
    print(ts_type)
