# matrx_utils\schema_builder\individual_managers\schema.py
from collections import defaultdict
import json
from matrx_utils import vcprint
from matrx_utils.schema_builder.helpers.configs import CODE_BASICS
from matrx_utils.schema_builder.individual_managers.common import (
    schema_builder_verbose,
    schema_builder_debug,
    schema_builder_info,
    schema_builder_utils,
)
from matrx_utils.file_management.specific_handlers.code import CodeHandler
from matrx_utils.schema_builder.helpers.manual_overrides import (
    SYSTEM_OVERRIDES_ENTITIES,
    SYSTEM_OVERRIDES_FIELDS,
    TABLE_ORDER_OVERRIDES,
)
from matrx_utils.schema_builder.parts_generators.entity_field_override_generator import (
    generate_full_typescript_file,
)
from matrx_utils.schema_builder.parts_generators.entity_main_hook_generator import (
    generate_all_entity_main_hooks,
)
from matrx_utils.schema_builder.parts_generators.entity_override_generator import (
    generate_multiple_entities,
)
import re

LOCAL_DEBUG_MODE = False


def format_ts_object(ts_object_str):
    """
    Formats a JSON-like string to remove quotes from keys for TypeScript compatibility.
    Ensures TypeScript-style object notation.
    """
    return re.sub(r'"(\w+)"\s*:', r"\1:", ts_object_str)


class Schema:
    def __init__(
        self,
        name="public",
        database_project="supabase_automation_matrix",
        save_direct=False,
    ):
        self.utils = schema_builder_utils
        self.code_handler = CodeHandler(save_direct=save_direct)
        self.name = name
        self.database_project = database_project
        self.tables = {}
        self.views = {}
        self.relationships = []
        self.verbose = schema_builder_verbose
        self.debug = schema_builder_debug
        self.info = schema_builder_info
        self.save_direct = save_direct
        self.initialized = False

        vcprint(
            self.to_dict(),
            title="Schema started",
            pretty=True,
            verbose=self.verbose,
            color="cyan",
        )

    def add_table(self, table):
        self.tables[table.name] = table

    def add_all_table_instances(self):
        """Assigns each table an instance of every other table in the schema."""
        for table in self.tables.values():
            table.all_table_instances = {name: tbl for name, tbl in self.tables.items() if name != table.name}

    def add_view(self, view):
        self.views[view.name] = view

    def get_table(self, table_name):
        return self.tables.get(table_name)

    def get_view(self, view_name):
        return self.views.get(view_name)

    def get_related_tables(self, table_name):
        table = self.get_table(table_name)
        related_tables = set()
        if table:
            for target_table, rel in table.foreign_keys.items():
                related_tables.add(target_table)
            for source_table, rel in table.referenced_by.items():
                related_tables.add(source_table)
        return list(related_tables)

    def __repr__(self):
        return f"<Schema name={self.name}, tables={len(self.tables)}, views={len(self.views)}>"

    def initialize_code_generation(self):
        if self.initialized:
            return
        for table in self.tables.values():
            table.initialize_code_generation()
        for view in self.views.values():
            view.initialize_code_generation()

        self.initialized = True
        vcprint(
            self.to_dict(),
            title="Schema started",
            pretty=True,
            verbose=self.verbose,
            color="cyan",
        )

    # Method to get file location based on the code version (schema or types)
    def get_file_location(self, code_version):
        if code_version == "schema_file":
            return "// File: lib/initialSchemas.ts"
        elif code_version == "types_file":
            return "// File: types/AutomationSchemaTypes.ts"
        elif code_version == "table_schema_file":
            return "// File: lib/initialTableSchemas.ts"
        else:
            return ""

    # Method to get import statements based on the code version (schema or types)
    def get_import_statements(self, code_version):
        if code_version == "schema_file":
            return (
                "import {AutomationTableName,DataStructure,FetchStrategy,NameFormat,FieldDataOptionsType} from '@/types/AutomationSchemaTypes';"
                "\nimport {AutomationEntity, EntityData, EntityDataMixed, EntityDataOptional, EntityDataWithKey, ProcessedEntityData} from '@/types/entityTypes';"
            )
        elif code_version == "types_file":
            return "import {AutomationEntity, EntityData, EntityDataMixed, EntityDataOptional, EntityDataWithKey, ProcessedEntityData} from '@/types/entityTypes';"
        elif code_version == "table_schema_file":
            return "import {AutomationEntity, TypeBrand} from '@/types/entityTypes';"

        elif code_version == "lookup_schema_file":
            return "import {EntityNameToCanonicalMap,FieldNameToCanonicalMap,EntityNameFormatMap,FieldNameFormatMap} from '@/types/entityTypes';"

        else:
            return ""

    def generate_schema_structure(self):
        ts_structure = "export const initialAutomationTableSchema = {\n"
        table_entries = []
        const_structure = ""
        const_entries = []

        for table in self.tables.values():
            ts_table_entry, _, const_ts_structure = table.to_schema_entry()
            table_entries.append(ts_table_entry.strip())
            const_entries.append(const_ts_structure.strip())

        ts_structure += ",\n".join(table_entries)
        ts_structure += "\n} as const;"

        const_structure = "\n\n".join(const_entries)

        return ts_structure, const_structure

    # Method to handle type inference entries for types file
    # export type MessageRecordMap = Record<MatrxRecordId, MessageData>;
    def generate_type_inference_entries(self):
        infer_entries = []
        for table in self.tables.values():
            table_infer_entry = (
                f'export type {table.name_pascal}Type = AutomationEntity<"{table.name_camel}">;\n'
                f'export type {table.name_pascal}DataRequired = Expand<EntityData<"{table.name_camel}">>;\n'
                f'export type {table.name_pascal}DataOptional = Expand<EntityDataOptional<"{table.name_camel}">>;\n'
                f'export type {table.name_pascal}RecordWithKey = Expand<EntityDataWithKey<"{table.name_camel}">>;\n'
                f'export type {table.name_pascal}Processed = Expand<ProcessedEntityData<"{table.name_camel}">>;\n'
                f'export type {table.name_pascal}Data = Expand<EntityDataMixed<"{table.name_camel}">>;\n'
                f'export type {table.name_pascal}State = EntityStateType<"{table.name_camel}">;\n'
                f'export type {table.name_pascal}RecordMap = Record<"{table.name_camel}RecordId", {table.name_pascal}Data>;\n'
            )
            infer_entries.append(table_infer_entry)
        return "\n".join(infer_entries)

    def generate_initial_type_inference_entries(self):
        infer_entries = []
        for table in self.tables.values():
            table_infer_entry = f'export type {table.name_pascal}InitialType = ExpandedInitialTableType<"{table.name_camel}">;'
            infer_entries.append(table_infer_entry)
        return "\n".join(infer_entries)

    # Method to generate TypeScript declarations for tables, views, and combined entities
    def generate_typescript_list_tables_and_views(self):
        ts_tables = []
        ts_views = []
        ts_entities = []

        for table in self.tables.values():
            ts_tables.append(table.name_camel)

        for view in self.views.values():
            ts_views.append(view.name_camel)

        ts_entities.extend(ts_tables)
        ts_entities.extend(ts_views)

        ts_tables_type = "export type AutomationTableName =\n    '" + "'\n    | '".join(ts_tables) + "';"
        ts_views_type = "export type AutomationViewName =\n    '" + "'\n    | '".join(ts_views) + "';"
        ts_entities_type = (
            "export type AutomationEntityName = AutomationTableName | AutomationViewName;\n\n"
            "// export type ProcessedSchema = ReturnType<typeof initializeTableSchema>;\n\n// export type UnifiedSchemaCache = ReturnType<typeof initializeSchemaSystem>\n\n"
            "// export type SchemaEntityKeys = keyof ProcessedSchema;\n\n"
            "export type Expand<T> = T extends infer O ? { [K in keyof O]: O[K] } : never;\n\n"
            "export type ExpandRecursively<T> = T extends object ? (T extends infer O ? { [K in keyof O]: ExpandRecursively<O[K]> } : never) : T;"
            "export type ExpandExcept<T, KeysToExclude extends string[] = []> = T extends object\n    ? {\n   [K in keyof T]: K extends KeysToExclude[number] ? T[K] : ExpandExcept<T[K], KeysToExclude>;\n} : T;\n\n"
            'export type EntityStateType<TEntity extends EntityKeys> = ExpandExcept<EntityState<TEntity>, ["entityFields", "relationships", "unsavedRecords", "primaryKeyMetadata", "primaryKeyValues", "metadata"]>;'
        )

        return ts_tables_type, ts_views_type, ts_entities_type

    def generate_primary_key_object(self):
        result = "export const primaryKeys = {\n"
        for table in self.tables.values():
            table_name = table.name_camel
            pk_entry = table.get_primary_key_fields_list()

            frontend_keys = ", ".join(f"'{key}'" for key in pk_entry["frontend_name"])
            database_keys = ", ".join(f"'{key}'" for key in pk_entry["database_name"])

            result += f"  {table_name}: {{\n" f"    frontendFields: [{frontend_keys}],\n" f"    databaseColumns: [{database_keys}],\n" f"  }},\n"
        result += "};\n"

        main_code = result
        self.code_handler.generate_and_save_code_from_object(CODE_BASICS["primary_keys"], main_code)

    # Method to generate TypeBrand utility type
    def generate_type_brand_util(self):
        return "export type TypeBrand<T> = { _typeBrand: T };"

    # Method to generate the DataType declaration
    def generate_data_type(self, data_types=None):
        # Default list of values for DataType
        if data_types is None:
            data_types = [
                "string",
                "number",
                "boolean",
                "array",
                "object",
                "json",
                "null",
                "undefined",
                "any",
                "function",
                "symbol",
                "union",
                "bigint",
                "date",
                "map",
                "set",
                "tuple",
                "enum",
                "intersection",
                "literal",
                "void",
                "never",
                "uuid",
                "email",
                "url",
                "phone",
                "datetime",
            ]

        # Generating the TypeScript type definition using the list
        return "export type FieldDataOptionsType =\n" + "    | '" + "'\n    | '".join(data_types) + "';"

    def generate_data_structure(self, data_structures=None):
        # Default list of values for DataStructure
        if data_structures is None:
            data_structures = [
                "single",
                "array",
                "object",
                "foreignKey",
                "inverseForeignKey",
                "manyToMany",
            ]

        # Generating the TypeScript type definition using the list
        return "export type DataStructure =\n" + "    | '" + "'\n    | '".join(data_structures) + "';"

    def generate_fetch_strategy(self, fetch_strategies=None):
        # Default list of values for FetchStrategy
        if fetch_strategies is None:
            fetch_strategies = [
                "simple",
                "fk",
                "ifk",
                "m2m",
                "fkAndIfk",
                "m2mAndFk",
                "m2mAndIfk",
                "fkIfkAndM2M",
                "none",
            ]

        # Generating the TypeScript type definition using the list
        return "export type FetchStrategy =\n" + "    | '" + "'\n    | '".join(fetch_strategies) + "';"

    def generate_name_formats(self):
        return (
            "export type RequiredNameFormats =\n"
            "    'frontend' |\n"
            "    'backend' |\n"
            "    'database' |\n"
            "    'pretty' |\n"
            "    'component'|\n"
            "    'kebab' |\n"
            "    'sqlFunctionRef';\n\n"
            "export type OptionalNameFormats =\n"
            "    'RestAPI' |\n"
            "    'GraphQL' |\n"
            "    'custom';\n\n"
            "export type NameFormat = RequiredNameFormats | OptionalNameFormats;"
        )

    def generate_automation_dynamic_name(self, dynamic_names=None):
        # Default list of values for AutomationDynamicName
        if dynamic_names is None:
            dynamic_names = [
                "dynamicAudio",
                "dynamicImage",
                "dynamicText",
                "dynamicVideo",
                "dynamicSocket",
                "anthropic",
                "openai",
                "llama",
                "googleAi",
            ]

        # Generating the TypeScript type definition using the list
        return "export type AutomationDynamicName =\n" + "    | '" + "'\n    | '".join(dynamic_names) + "';"

    def generate_automation_custom_name(self, custom_names=None):
        # Default list of values for AutomationCustomName
        if custom_names is None:
            custom_names = ["flashcard", "mathTutor", "scraper"]

        # Generating the TypeScript type definition using the list
        return "export type AutomationCustomName =\n" + "    | '" + "'\n    | '".join(custom_names) + "';"

    def generate_static_ts_Initial_table_schema(self):
        ts_structure = (
            "export type TypeBrand<DataType> = { _typeBrand: DataType };\n"
            "export type EnumValues<T> = T extends TypeBrand<infer U> ? U : never;\n"
            "export type ExtractType<T> = T extends TypeBrand<infer U> ? U : T;\n\n"
            "export type InitialTableSchema = {\n"
            "    schemaType: 'table';\n"
            "    entityName: string;\n"
            "    displayName: string;\n"
            "    uniqueTableId: string;\n"
            "    uniqueEntityId: string;\n"
            "    primaryKey: string[];\n"
            "    primaryKeyMetadata: {\n"
            "        type: 'single' | 'composite';\n"
            "        fields: string[];\n"
            "        database_fields: string[];\n"
            "        where_template: Record<string, any>;\n"
            "    };\n"
            "    displayFieldMetadata: {\n"
            "        fieldName: string;\n"
            "        databaseFieldName: string;\n"
            "    };\n"
            "    defaultFetchStrategy: FetchStrategy;\n"
            "    componentProps: Record<string, any>;\n"
            "    entityNameFormats: {\n"
            "        [key in NameFormat]?: string;\n"
            "    };\n"
            "    entityFields: {\n"
            "        [fieldName: string]: {\n"
            "            fieldNameFormats: {\n"
            "                [key in NameFormat]?: string;\n"
            "            };\n"
            "            dataType: FieldDataOptionsType;\n"
            "            isRequired: boolean;\n"
            "            maxLength: number | null;\n"
            "            isArray: boolean;\n"
            "            defaultValue: any;\n"
            "            isPrimaryKey: boolean;\n"
            "            isDisplayField?: boolean;\n"
            "            defaultGeneratorFunction: string | null;\n"
            "            validationFunctions: readonly string[];\n"
            "            exclusionRules: readonly string[];\n"
            "            defaultComponent?: string;\n"
            "            componentProps?: Record<string, unknown>;\n"
            "            structure: DataStructure;\n"
            "            isNative: boolean;\n"
            "            typeReference: TypeBrand<any>;\n"
            "            enumValues: readonly string[];\n"
            "            entityName: string;\n"
            "            databaseTable: string;\n"
            "            description: string;\n"
            "        };\n"
            "    };\n"
            "    relationships: Array<{\n"
            "        relationshipType: 'foreignKey' | 'inverseForeignKey' | 'manyToMany';\n"
            "        column: string;\n"
            "        relatedTable: string;\n"
            "        relatedColumn: string;\n"
            "        junctionTable: string | null;\n"
            "    }>;\n"
            "};\n\n"
            "export type TableSchemaStructure = {\n"
            "    [entityName in AutomationTableName]: InitialTableSchema;\n"
            "};\n"
        )

        return ts_structure

    def generate_ts_lookup_file(self):
        ts_table_name_lookup = []
        ts_field_name_lookup = []
        ts_reverse_table_name_lookup = []
        ts_reverse_field_name_lookup = []
        ts_view_name_lookup = []

        ts_table_name_lookup_line_1 = "export const entityNameToCanonical: EntityNameToCanonicalMap = {"
        ts_field_name_lookup_line_1 = "export const fieldNameToCanonical: FieldNameToCanonicalMap = {"
        ts_reverse_table_name_lookup_line_1 = "export const entityNameFormats: EntityNameFormatMap = {"
        ts_reverse_field_name_lookup_line_1 = "export const fieldNameFormats: FieldNameFormatMap = {"
        ts_view_name_lookup_line_1 = "export const viewNameLookup: Record<string, string> = {"

        ts_common_close = "};"

        for table in self.tables.values():
            for key, value in table.unique_name_lookups.items():
                ts_table_name_lookup.append(f'    {key}: "{value}",')

            # Properly format field name lookup to prevent double brackets
            field_lookup_data = table.field_name_lookup_structure
            if isinstance(field_lookup_data, dict):
                formatted_field_lookup = json.dumps(field_lookup_data, indent=4)[1:-1]  # Removes outer {}
                formatted_field_lookup = format_ts_object(formatted_field_lookup)  # Remove unnecessary quotes
                formatted_field_lookup = f"{{\n{formatted_field_lookup}\n}}"  # Ensure correct brackets
            else:
                formatted_field_lookup = str(field_lookup_data)

            ts_field_name_lookup.append(f"    {table.name_camel}: {formatted_field_lookup},")

            # Convert to JSON and remove quotes from keys
            formatted_reverse_table_lookup = format_ts_object(json.dumps(table.reverse_table_lookup[table.name_camel], indent=4))
            formatted_reverse_field_lookup = format_ts_object(json.dumps(table.reverse_field_name_lookup[table.name_camel], indent=4))

            ts_reverse_table_name_lookup.append(f"    {table.name_camel}: {formatted_reverse_table_lookup},")
            ts_reverse_field_name_lookup.append(f"    {table.name_camel}: {formatted_reverse_field_lookup},")

        for view in self.views.values():
            for key, value in view.unique_name_lookups.items():
                ts_view_name_lookup.append(f'    {key}: "{value}",')

        ts_table_name_lookup_code = "\n".join([ts_table_name_lookup_line_1] + ts_table_name_lookup + [ts_common_close])
        ts_field_name_lookup_code = "\n".join([ts_field_name_lookup_line_1] + ts_field_name_lookup + [ts_common_close])
        ts_reverse_table_name_lookup_code = "\n".join([ts_reverse_table_name_lookup_line_1] + ts_reverse_table_name_lookup + [ts_common_close])
        ts_reverse_field_name_lookup_code = "\n".join([ts_reverse_field_name_lookup_line_1] + ts_reverse_field_name_lookup + [ts_common_close])
        ts_view_name_lookup_code = "\n".join([ts_view_name_lookup_line_1] + ts_view_name_lookup + [ts_common_close])

        main_code = (
            f"{ts_table_name_lookup_code}\n\n"
            f"{ts_field_name_lookup_code}\n\n"
            f"{ts_reverse_table_name_lookup_code}\n\n"
            f"{ts_reverse_field_name_lookup_code}\n\n"
            f"{ts_view_name_lookup_code}"
        )

        self.code_handler.generate_and_save_code_from_object(CODE_BASICS["typescript_lookup"], main_code)

    def generate_entity_typescript_types_file(self):
        ts_type_entries = []
        for table in self.tables.values():
            ts_type_entries.append(table.to_typescript_type_entry())

        main_code = "\n".join(ts_type_entries)
        self.code_handler.generate_and_save_code_from_object(CODE_BASICS["entity_typescript_types"], main_code)

    def generate_schema_file(self):
        ts_structure, const_structure = self.generate_schema_structure()
        table_schema_structure = self.generate_static_ts_Initial_table_schema()
        ts_code_content = f"{ts_structure}\n\n{table_schema_structure}"

        self.code_handler.generate_and_save_code_from_object(CODE_BASICS["typescript_schema"], ts_code_content)

        self.code_handler.generate_and_save_code_from_object(CODE_BASICS["typescript_individual_table_schemas"], const_structure)

    # Method to generate and save the types file (AutomationSchemaTypes.ts)
    def generate_types_file(self):
        ts_tables_type, ts_views_type, ts_entities_type = self.generate_typescript_list_tables_and_views()
        data_type_entry = self.generate_data_type()
        data_structure_entry = self.generate_data_structure()
        fetch_strategy_entry = self.generate_fetch_strategy()
        generate_name_formats = self.generate_name_formats()
        automation_dynamic_names = self.generate_automation_dynamic_name()
        automation_custom_names = self.generate_automation_custom_name()
        type_inference_entries = self.generate_type_inference_entries()
        type_brand_util = self.generate_type_brand_util()

        ts_code_content = (
            f"{type_brand_util}\n\n"
            f"{data_type_entry}\n\n"
            f"{data_structure_entry}\n\n"
            f"{fetch_strategy_entry}\n\n"
            f"{generate_name_formats}\n\n"
            f"{automation_dynamic_names}\n\n"
            f"{automation_custom_names}\n\n"
            f"{ts_tables_type}\n\n"
            f"{ts_views_type}\n\n"
            f"{ts_entities_type}\n\n"
            f"{type_inference_entries}\n\n"
        )

        self.code_handler.generate_and_save_code_from_object(CODE_BASICS["typescript_types"], ts_code_content)

        self.generate_field_name_list()

    def convert_to_typescript(self, python_dict):
        def format_key(key):
            # Ensure keys are not strings in the final TypeScript output
            return key if key.isidentifier() else f'"{key}"'

        def dict_to_ts(d):
            ts_lines = []
            for k, v in d.items():
                if isinstance(v, dict):
                    ts_lines.append(f"{format_key(k)}: {dict_to_ts(v)}")
                elif isinstance(v, list):
                    ts_lines.append(f"{format_key(k)}: {json.dumps(v)}")
                else:
                    ts_lines.append(f"{format_key(k)}: {json.dumps(v)}")
            return "{\n  " + ",\n  ".join(ts_lines) + "\n}"

        # Convert the Python dictionary to TypeScript object syntax
        return dict_to_ts(python_dict)

    def generate_field_name_list(self):
        entity_field_names = {}
        for table in self.tables.values():
            entity_name = table.name_camel
            vcprint(f"Processing entity: {entity_name}", verbose=self.verbose, color="blue")
            entity_field_names[entity_name] = table.Field_name_groups
            vcprint(
                f"Field names: {entity_field_names[entity_name]}",
                verbose=self.verbose,
                color="green",
            )

        main_code = self.convert_to_typescript(entity_field_names)

        self.code_handler.generate_and_save_code_from_object(CODE_BASICS["typescript_entity_fields"], main_code)

        self.generate_entity_overrides()

    def generate_entity_overrides(self):
        entity_names = []
        for table in self.tables.values():
            entity_names.append(table.name_camel)

        overrides_code = generate_multiple_entities(entity_names, SYSTEM_OVERRIDES_ENTITIES)

        self.code_handler.generate_and_save_code_from_object(CODE_BASICS["typescript_entity_overrides"], overrides_code)

        self.generate_entity_main_hooks()
        self.generate_entity_field_overrides()

    def generate_entity_main_hooks(self):
        all_table_snake_names = [table.name for table in self.tables.values()]
        main_hook_code = generate_all_entity_main_hooks(all_table_snake_names)
        self.code_handler.generate_and_save_code_from_object(CODE_BASICS["typescript_entity_main_hooks"], main_hook_code)

    def generate_entity_field_overrides(self):
        entity_names = []
        for table in self.tables.values():
            entity_names.append(table.name_camel)

        overrides_code = generate_full_typescript_file(entity_names, SYSTEM_OVERRIDES_FIELDS)

        self.code_handler.generate_and_save_code_from_object(CODE_BASICS["typescript_entity_field_overrides"], overrides_code)

        self.generate_entity_typescript_types_file()

    # Main orchestrator method that generates both schema and types files, and JSON
    def generate_schema_files(self):
        self.initialize_code_generation()  # Initialize code generation for all tables and views
        self.generate_schema_file()  # Generate and save schema file
        self.generate_types_file()  # Generate and save types file
        self.generate_ts_lookup_file()
        self.generate_primary_key_object()

        # Generate and save JSON structure for schema data
        json_code_temp_path = "initialSchemas.json"
        json_structure = {}
        for table in self.tables.values():
            _, json_table_entry, _ = table.to_schema_entry()
            json_structure.update(json_table_entry)

        self.code_handler.write_to_json(json_code_temp_path, json_structure, clean=True)

    def get_string_user_model(self):
        # Returns the string for the Users model
        users_model = """class Users(Model):
        id = UUIDField(primary_key=True, null=False)
        email = CharField(null=False)\n\n"""
        return users_model

    def get_string_model_registry(self):
        # Generates the model_registry string for all models
        all_models = [table.name_pascal for table in self.tables.values()]
        all_models.append("Users")  # Always include the Users model

        # Join the models into a string with appropriate formatting
        model_registry_string = "\nmodel_registry.register_all(\n[\n        " + ",\n        ".join(all_models) + "\n    ]\n)"

        return model_registry_string

    def generate_models(self):
        reference_count = defaultdict(int)
        for table_name, table in self.tables.items():
            reference_count[table_name] = len(table.referenced_by_relationships)

        boost_models = TABLE_ORDER_OVERRIDES
        for model_name in reference_count:
            if model_name in boost_models:
                reference_count[model_name] += boost_models[model_name]

        sorted_tables = sorted(
            self.tables.keys(),
            key=lambda table_name: reference_count[table_name],
            reverse=True,
        )

        py_structure = [self.get_string_user_model()]
        for table_name in sorted_tables:
            table = self.tables[table_name]
            py_table_entry = table.to_python_model()
            py_structure.append(py_table_entry)

        py_manager_structure = []
        py_base_manager_structure = []
        py_auto_config_structure = []

        for table_name in sorted_tables:
            table = self.tables[table_name]
            py_manager_entry = table.to_python_manager_string()
            py_manager_structure.append(py_manager_entry)

            py_auto_config_entry = table.base_class_auto_config
            py_auto_config_string = f"{table.name}_auto_config = {repr(py_auto_config_entry)}\n\n"
            py_auto_config_structure.append(py_auto_config_string)  # Append as valid Python code

            py_base_manager_entry = table.model_base_class_str
            py_base_manager_structure.append(py_base_manager_entry)

        py_structure.append(self.get_string_model_registry())

        main_code = "\n".join(py_structure)
        additional_code = "\n".join(py_manager_structure)

        if LOCAL_DEBUG_MODE:
            print("DEBUG.....")
            print("python_models", CODE_BASICS["python_models"])
            print("-----------------------------\n")

        self.code_handler.generate_and_save_code_from_object(CODE_BASICS["python_models"], main_code, additional_code)

        py_base_manager_code = "\n".join(py_base_manager_structure)
        py_auto_config_code = "\n".join(py_auto_config_structure)

        self.code_handler.generate_and_save_code_from_object(CODE_BASICS["python_base_manager"], py_base_manager_code)
        self.code_handler.generate_and_save_code_from_object(CODE_BASICS["python_auto_config"], py_auto_config_code)

    def save_analysis_json(self, analysis_dict):
        json_code_temp_path = "schemaAnalysis.json"
        self.code_handler.write_to_json(json_code_temp_path, analysis_dict, clean=True)

    def save_frontend_full_relationships_json(self, analysis_dict):
        json_code_temp_path = "fullRelationships.json"
        self.code_handler.write_to_json(json_code_temp_path, analysis_dict, clean=True)

    def save_frontend_junction_analysis_json(self, analysis_dict):
        json_code_temp_path = "junctionAnalysis.json"
        self.code_handler.write_to_json(json_code_temp_path, analysis_dict, clean=True)

    def to_dict(self):
        return {
            "name": self.name,
            "tables": {k: v.to_dict() for k, v in self.tables.items()},
            "views": {k: v.to_dict() for k, v in self.views.items()},
        }
