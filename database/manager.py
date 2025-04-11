import ast
from collections import defaultdict
import json
from datetime import datetime
import os

from common.utils.file_handlers.code_hanlder import CodeHandler
from common.utils.data_handlers.data_transformer import DataTransformer
from database.constants import (
    get_default_component_props,
    get_relationship_data_model_types,
)
from database.schema_builder.helpers.manager_helpers import generate_dto_and_manager
from database.python_sql.db_objects import get_db_objects
from common import vcprint
from database.schema_builder.helpers.manual_overrides import TABLE_ORDER_OVERRIDES

verbose = False
debug = False
info = True

utils = DataTransformer()

save_direct = True


class Relationship:
    def __init__(
        self,
        constraint_name,
        column,
        foreign_column,
        target_table=None,
        source_table=None,
    ):
        self.utils = utils
        self.constraint_name = constraint_name
        self.column = column
        self.foreign_column = foreign_column
        self.target_table = target_table  # Foreign key-related table
        self.source_table = source_table  # Inverse foreign key source table
        self.frontend_column = self.utils.to_camel_case(self.column)
        self.frontend_foreign_column = self.utils.to_camel_case(self.foreign_column)
        self.frontend_target_table = self.utils.to_camel_case(target_table.name) if target_table is not None else None
        self.frontend_source_table = self.utils.to_camel_case(source_table.name) if source_table is not None else None

        self.verbose = verbose
        self.debug = debug

        vcprint(
            self.to_dict(),
            title="Relationship initialized",
            pretty=True,
            verbose=self.verbose,
            color="yellow",
        )

    def __repr__(self):
        return f"<Relationship {self.constraint_name}: {self.column} -> {self.foreign_column}>"

    def to_dict(self):
        return {
            "constraint_name": self.constraint_name,
            "column": self.column,
            "foreign_column": self.foreign_column,
            "target_table": self.target_table,
            "source_table": self.source_table,
            "frontend_column": self.frontend_column,
            "frontend_foreign_column": self.frontend_foreign_column,
            "frontend_target_table": self.frontend_target_table,
            "frontend_source_table": self.frontend_source_table,
        }


class Column:
    def __init__(
        self,
        database_project,
        table_name,
        unique_column_id,
        name,
        position,
        full_type,
        base_type,
        domain_type,
        enum_labels,
        is_array,
        nullable,
        default,
        character_maximum_length,
        numeric_precision,
        numeric_scale,
        collation,
        is_identity,
        is_generated,
        is_primary_key,
        is_unique,
        has_index,
        check_constraints,
        foreign_key_reference,
        comment,
        is_display_field=False,
    ):
        self.utils = utils
        self.database_project = database_project
        self.table_name = table_name
        self.unique_column_id = unique_column_id
        self.name = name
        self.position = position
        self.full_type = full_type
        self.base_type = base_type
        self.domain_type = domain_type
        self.enum_labels = enum_labels
        self.is_array = is_array
        self.nullable = nullable
        self.default = default
        self.character_maximum_length = character_maximum_length
        self.numeric_precision = numeric_precision
        self.numeric_scale = numeric_scale
        self.collation = collation
        self.is_identity = is_identity
        self.is_generated = is_generated
        self.is_primary_key = is_primary_key
        self.is_unique = is_unique
        self.has_index = has_index
        self.check_constraints = check_constraints
        self.comment = comment
        self.is_display_field = is_display_field
        self.has_enum_labels = True if self.enum_labels else False

        self.foreign_key_reference = (
            {
                "table": foreign_key_reference["table"],
                "column": foreign_key_reference["column"],
                "entity": self.utils.to_camel_case(foreign_key_reference["table"]),
                "field": self.utils.to_camel_case(foreign_key_reference["column"]),
            }
            if foreign_key_reference
            else None
        )

        self.table_name_camel = self.utils.to_camel_case(self.table_name)

        self.initialized = False

        self.verbose = verbose
        self.debug = debug

        self.name_snake = self.utils.to_snake_case(self.name)
        self.name_camel = self.utils.to_camel_case(self.name)
        self.name_pascal = self.utils.to_pascal_case(self.name)
        self.name_kebab = self.utils.to_kebab_case(self.name)
        self.name_title = self.utils.to_title_case(self.name)
        self.table_name_camel = self.utils.to_camel_case(self.table_name)

        self.default_component = "INPUT"
        self.default_component_priority = -1
        self.component_props = get_default_component_props()
        self.component_props_priorities = {key: -1 for key in self.component_props}

        self.is_required = "true" if not self.nullable else "false"

        self.ts_full_schema_entry = None
        self.ts_simple_schema_entry = None
        self.ts_field_lookup_entry = None

        self.json_schema_entry = {}
        self.py_field_entry = None

        self.initialize_code_generation()

        vcprint(
            self.to_dict(),
            title="Column initialized",
            pretty=True,
            verbose=self.verbose,
            color="cyan",
        )

        if self.enum_labels:
            self.has_enum_labels = True
            vcprint(f"Enum Labels: {self.enum_labels}", verbose=self.verbose, color="yellow")

    # Potential Additions: https://claude.ai/chat/e26ff11e-0cd5-46a5-b281-cfa359ed1fcd

    def __repr__(self):
        return f"<Column name={self.name}, type={self.base_type}>"

    def initialize_code_generation(self):
        if self.initialized:
            return
        self.set_typescript_enums()
        self.get_is_required()
        self.get_is_array()
        self.get_is_primary_key()

        self.clean_default = self.parse_default_value()
        self.typescript_type = self.utils.to_typescript_type_enums_to_string(self.base_type, self.has_enum_labels)
        self.matrx_schema_type = self.utils.to_matrx_schema_type(self.base_type)
        self.calc_default_value = self.get_default_value()
        self.calc_validation_functions = self.get_validation_functions()
        # self.calc_default_generator_functions = self.get_default_generator_function()
        self.calc_exclusion_rules = self.get_exclusion_rules()
        self.calc_max_length = self.get_max_field_length()
        self.type_reference = self.get_type_reference()

        self.python_field_type = self.utils.to_python_models_field(self.base_type)

        self.generate_unique_name_lookups()
        self.generate_name_variations()
        self.to_reverse_column_lookup_entry()
        self.generate_description()
        self.manage_data_type_impact()

        # self.calc_default_component = self.get_default_component()
        self.to_schema_entry()
        self.initialized = True

    def generate_unique_name_lookups(self):
        name_variations = {
            self.name,
            self.name_camel,
            self.name_snake,
            self.name_title,
            self.name_pascal,
            self.name_kebab,
            f"p_{self.name_snake}",
        }

        unique_names = set(name_variations)
        self.unique_name_lookups = {name: self.name_camel for name in unique_names}
        self.column_lookup_string = ",\n".join([f'"{key}": "{value}"' if " " in key or "-" in key else f'{key}: "{value}"' for key, value in self.unique_name_lookups.items()])

    def update_prop(self, prop, value, priority=0):
        if prop not in self.component_props_priorities:
            self.component_props_priorities[prop] = -1
            self.component_props[prop] = None

        current_priority = self.component_props_priorities[prop]
        if priority >= current_priority:
            self.component_props[prop] = value
            self.component_props_priorities[prop] = priority

    def update_component(self, component, priority=0):
        if priority > self.default_component_priority:
            self.default_component = component
            self.default_component_priority = priority

    def generate_name_variations(self):
        self.name_variations = {
            "frontend": self.name_camel,
            "backend": self.name_snake,
            "database": self.name_snake,
            "pretty": self.name_title,
            "component": self.name_pascal,
            "kebab": self.name_kebab,
            "sqlFunctionRef": f"p_{self.name_snake}",
            "RestAPI": self.name_camel,
            "GraphQL": self.name_camel,
            "custom": self.name_camel,
        }
        return self.name_variations

    def set_typescript_enums(self):
        if self.enum_labels:
            self.ts_enum_values = f"enumValues: {self.enum_labels} as const"
            self.default_component = "select"

            select_options = []
            for label in self.enum_labels:
                select_options.append({"label": self.utils.to_title_case(label), "value": label})

            self.update_component(component="SELECT", priority=10)

            self.update_prop(prop="options", value=select_options, priority=10)
            self.update_prop(prop="subComponent", value="enumSelect", priority=1)

            self.ts_enum_entry = f"enumValues: {self.enum_labels} as const"

        else:
            self.ts_enum_entry = "enumValues: null"

    def generate_description(self):
        if self.comment:
            self.description_frontend = self.comment
            self.description_backend = self.comment
        else:
            requirement_statement = "This is a required field." if not self.nullable else "This is an optional field."
            data_type_statement = f"Your entry must be an {self.matrx_schema_type} data type."

            array_statement = "You can enter one or more entries." if self.is_array else ""
            max_length_statement = f"Maximum Length: {self.character_maximum_length}" if self.character_maximum_length else ""
            unique_statement = "This must be a unique value." if self.is_unique else ""

            frontend_relation_statement = ""
            backend_relation_statement = ""

            if self.foreign_key_reference:
                related_entity = self.foreign_key_reference["entity"]
                related_table = self.foreign_key_reference["table"]
                frontend_relation_statement = f"This field is a reference to a {related_entity}."
                backend_relation_statement = f"This field is a foreign key reference to the {related_table} table."

                if self.name == "user_id":  # This is to avoid errors because "users" is not an entity at this time.
                    self.update_component(component="UUID_FIELD", priority=10)
                else:
                    self.update_component(component="FK_SELECT", priority=10)

            frontend_description_parts = [
                f'"{self.name_title}" field for {self.table_name_camel}.',
                requirement_statement,
                data_type_statement,
                array_statement,
                max_length_statement,
                unique_statement,
                frontend_relation_statement,
            ]
            backend_description_parts = [
                f'"{self.name_title}" field for the {self.table_name} table.',
                requirement_statement,
                data_type_statement,
                array_statement,
                max_length_statement,
                unique_statement,
                backend_relation_statement,
            ]

            self.description_frontend = " ".join(part for part in frontend_description_parts if part)
            self.description_backend = " ".join(part for part in backend_description_parts if part)

        self.description = {
            "frontend": self.description_frontend,
            "backend": self.description_backend,
        }

        return self.description

    def manage_data_type_impact(self):
        if self.full_type == "uuid":
            self.update_component(component="UUID_FIELD", priority=10)
            self.update_prop(prop="subComponent", value="default", priority=1)

        elif self.full_type == "uuid[]":
            self.update_component(component="UUID_ARRAY", priority=10)
            self.update_prop(prop="subComponent", value="default", priority=1)

        elif self.full_type == "character varying(255)":
            self.update_component(component="INPUT", priority=3)
            self.update_prop(prop="subComponent", value="default", priority=1)
            self.update_prop(prop="rows", value=3, priority=1)

        elif self.full_type == "character varying(50)":
            self.update_component(component="INPUT", priority=3)
            self.update_prop(prop="subComponent", value="default", priority=1)

        elif self.full_type == "character varying":
            self.update_component(component="INPUT", priority=3)
            self.update_prop(prop="subComponent", value="default", priority=1)
            self.update_prop(prop="rows", value=5, priority=1)

        elif self.full_type == "text":
            self.update_component(component="TEXTAREA", priority=5)
            self.update_prop(prop="subComponent", value="default", priority=1)
            self.update_prop(prop="rows", value=5, priority=1)

        elif self.full_type == "boolean":
            self.update_component(component="SWITCH", priority=8)
            self.update_prop(prop="subComponent", value="default", priority=1)

        elif self.full_type == "bigint":
            self.update_component(component="NUMBER_INPUT", priority=8)
            self.update_prop(prop="subComponent", value="default", priority=1)
            self.update_prop(prop="numberType", value="bigint", priority=5)

        elif self.full_type == "smallint":
            self.update_component(component="NUMBER_INPUT", priority=8)
            self.update_prop(prop="subComponent", value="default", priority=1)
            self.update_prop(prop="numberType", value="smallint", priority=5)

        elif self.full_type == "real":
            self.update_component(component="NUMBER_INPUT", priority=8)
            self.update_prop(prop="subComponent", value="default", priority=1)
            self.update_prop(prop="numberType", value="real", priority=5)

        elif self.full_type == "integer":
            self.update_component(component="NUMBER_INPUT", priority=8)
            self.update_prop(prop="subComponent", value="default", priority=1)
            self.update_prop(prop="numberType", value="integer", priority=5)

        elif self.full_type == "timestamp with time zone":
            self.update_component(component="DATE_PICKER", priority=8)
            self.update_prop(prop="subComponent", value=self.base_type, priority=5)

        elif self.full_type == "json":
            self.update_component(component="JSON_EDITOR", priority=8)
            self.update_prop(prop="subComponent", value="default", priority=1)

        elif self.full_type == "jsonb":
            self.update_component(component="JSON_EDITOR", priority=8)
            self.update_prop(prop="subComponent", value="default", priority=1)

        elif self.full_type == "jsonb[]":
            self.update_component(component="JSON_EDITOR", priority=8)
            self.update_prop(prop="subComponent", value="jsonArray", priority=5)

        elif self.full_type.lower() == "bytea":
            self.update_component(component="FILE_UPLOAD", priority=6)
            self.update_prop(prop="subComponent", value="binary", priority=5)

        elif self.full_type == "double precision":
            self.update_component(component="NUMBER_INPUT", priority=8)
            self.update_prop(prop="subComponent", value="default", priority=1)
            self.update_prop(prop="numberType", value="double", priority=5)

        elif self.full_type == "serial":
            self.update_component(component="NUMBER_INPUT", priority=8)
            self.update_prop(prop="subComponent", value="serial", priority=5)
            self.update_prop(prop="readOnly", value=True, priority=7)

        elif self.full_type == "bigserial":
            self.update_component(component="NUMBER_INPUT", priority=8)
            self.update_prop(prop="subComponent", value="bigserial", priority=5)
            self.update_prop(prop="readOnly", value=True, priority=7)

        elif self.full_type == "char":
            self.update_component(component="INPUT", priority=8)
            self.update_prop(prop="subComponent", value="fixed", priority=5)

        elif self.full_type == "time":
            self.update_component(component="TIME_PICKER", priority=8)
            self.update_prop(prop="subComponent", value="timeOnly", priority=5)

        elif self.full_type == "timetz":
            self.update_component(component="TIME_PICKER", priority=8)
            self.update_prop(prop="subComponent", value="timeWithZone", priority=5)

        elif self.full_type == "interval":
            self.update_component(component="INPUT", priority=8)
            self.update_prop(prop="subComponent", value="interval", priority=5)

        elif self.full_type == "bytea":
            self.update_component(component="FILE_UPLOAD", priority=8)
            self.update_prop(prop="subComponent", value="binary", priority=5)

        elif self.full_type == "inet":
            self.update_component(component="INPUT", priority=8)
            self.update_prop(prop="subComponent", value="ip", priority=5)

        elif self.full_type == "macaddr":
            self.update_component(component="INPUT", priority=8)
            self.update_prop(prop="subComponent", value="mac", priority=5)

        elif "time" in self.full_type.lower():
            self.update_component(component="TIME_PICKER", priority=6)
            self.update_prop(prop="subComponent", value="default", priority=1)

        elif "date" in self.full_type.lower():
            self.update_component(component="DATE_PICKER", priority=6)
            self.update_prop(prop="subComponent", value="default", priority=1)

        elif "numeric" in self.full_type.lower() or "decimal" in self.full_type.lower():
            self.update_component(component="NUMBER_INPUT", priority=6)
            self.update_prop(prop="subComponent", value="default", priority=1)
            self.update_prop(prop="numberType", value="decimal", priority=5)

        elif "serial" in self.full_type.lower():
            self.update_component(component="NUMBER_INPUT", priority=6)
            self.update_prop(prop="subComponent", value="default", priority=1)
            self.update_prop(prop="numberType", value="integer", priority=5)
        elif "character varying[]" in self.full_type.lower():
            self.update_component(component="TEXT_ARRAY", priority=6)
            self.update_prop(prop="subComponent", value="default", priority=1)
            self.update_prop(prop="rows", value=3, priority=1)

        else:
            if self.enum_labels:
                return
            else:
                self.update_component(component="INPUT", priority=1)
                vcprint(
                    data=self.full_type,
                    title="Unrecognized field type",
                    color="red",
                    verbose=True,
                )
                vcprint(
                    data=f" -Field: {self.name_camel}",
                    color="red",
                    verbose=True,
                    inline=True,
                )
                vcprint(
                    data=f" -Table: {self.table_name}",
                    color="red",
                    verbose=True,
                    inline=True,
                )

    def to_reverse_column_lookup_entry(self):
        self.reverse_column_lookup = {self.name_camel: self.name_variations}
        return self.reverse_column_lookup

    def to_ts_simple_schema_entry(self):
        # Compose the TypeScript schema entry
        self.ts_full_schema_entry = f"""{self.name_camel}: {{
            fieldNameFormats: {json.dumps(self.name_variations, indent=4)} as const,
            name: '{self.name_camel}',
            displayName: '{self.name_title}',
            dataType: '{self.matrx_schema_type}' as const,
            isRequired: {str(not self.nullable).lower()},
            maxLength: {self.calc_max_length},
            isArray: {str(self.is_array).lower()},
            defaultValue: "{self.clean_default['typescript']}" as const,
            isPrimaryKey: {str(self.is_primary_key).lower()},
            isDisplayField: {str(self.is_display_field).lower()},
            defaultGeneratorFunction: "{str(self.calc_default_generator_functions['typescript'])}",
            validationFunctions: [],
            exclusionRules: [],
            defaultComponent: '{self.default_component}' as const,
            componentProps: {json.dumps(self.component_props, indent=4)},
            structure: 'single' as const,
            isNative: true,
            typeReference: {{}} as TypeBrand<{self.type_reference['typescript']}>,
            {self.ts_enum_entry},
            entityName: '{self.table_name_camel}',
            databaseTable: '{self.table_name}',
            foreignKeyReference: {json.dumps(self.foreign_key_reference) if self.foreign_key_reference else 'null'},
            description: '{self.description_frontend}',
        }},"""
        return self.ts_full_schema_entry

    def to_schema_entry(self):
        # Compose the TypeScript schema entry
        self.ts_full_schema_entry = f"""{self.name_camel}: {{
            fieldNameFormats: {json.dumps(self.name_variations, indent=4)} as const,
            name: '{self.name_camel}',
            displayName: '{self.name_title}',

            uniqueColumnId: '{self.unique_column_id}',
            uniqueFieldId: '{self.database_project}:{self.table_name_camel}:{self.name_camel}',
            
            dataType: '{self.matrx_schema_type}' as const,
            isRequired: {self.calc_is_required['typescript']},
            maxLength: {self.calc_max_length},
            isArray: {self.calc_is_array['typescript']},
            defaultValue: "{self.clean_default['typescript']}" as const,
            isPrimaryKey: {self.calc_is_primary_key['typescript']},
            isDisplayField: {str(self.is_display_field).lower()},
            defaultGeneratorFunction: "{str(self.calc_default_generator_functions['typescript'])}",
            validationFunctions: {self.calc_validation_functions['typescript']},
            exclusionRules: {self.calc_exclusion_rules['typescript']},
            defaultComponent: '{self.default_component}' as const,
            componentProps: {json.dumps(self.component_props, indent=4)},
            structure: 'single' as const,
            isNative: true,
            typeReference: {{}} as TypeBrand<{self.type_reference['typescript']}>,
            {self.ts_enum_entry},
            entityName: '{self.table_name_camel}',
            databaseTable: '{self.table_name}',
            foreignKeyReference: {json.dumps(self.foreign_key_reference) if self.foreign_key_reference else 'null'},
            description: '{self.description_frontend}',
        }},"""

        enum_values_json = self.enum_labels if self.enum_labels else None

        # Compose the JSON schema entry
        self.json_schema_entry = {
            self.name_camel: {
                "fieldNameFormats": self.name_variations,
                "name": self.name_camel,
                "displayName": self.name_title,
                "uniqueColumnId": self.unique_column_id,
                "uniqueFieldId": f"{self.database_project}:{self.table_name_camel}:{self.name_camel}",
                "dataType": self.matrx_schema_type,
                "isRequired": not self.nullable,
                "maxLength": self.calc_max_length,
                "isArray": self.is_array,
                "defaultValue": self.clean_default["json"],
                "isPrimaryKey": self.is_primary_key,
                "isDisplayField": self.is_display_field,
                "defaultGeneratorFunction": None,
                "validationFunctions": [],
                "exclusionRules": [],
                "defaultComponent": self.default_component,
                "componentProps": self.component_props,
                "structure": "single",
                "isNative": True,
                "typeReference": self.type_reference["json"],
                "enumValues": enum_values_json,
                "entityName": self.table_name_camel,
                "databaseTable": self.table_name,
                "foreignKeyReference": self.foreign_key_reference,
                "description": self.description,
            }
        }

        return self.ts_full_schema_entry, self.json_schema_entry

    def parse_default_value(self):
        # Define static outcomes at the top
        outcomes = {
            None: {"default": {"blank": "", "generator": ""}},
            "gen_random_uuid()": {
                "python": {"blank": "", "generator": "uuid.uuid4()"},
                "database": {"blank": "null", "generator": "gen_random_uuid()"},
                "json": {"blank": "", "generator": "get_uuid"},
                "typescript": {"blank": "", "generator": "getUUID()"},
            },
            "uuid_generate_v4()": {
                "python": {"blank": "", "generator": "uuid.uuid4()"},
                "database": {"blank": "null", "generator": "gen_random_uuid()"},
                "json": {"blank": "", "generator": "get_uuid"},
                "typescript": {"blank": "", "generator": "getUUID()"},
            },
            "extensions.uuid_generate_v4()": {
                "python": {"blank": "", "generator": "uuid.uuid4()"},
                "database": {"blank": "null", "generator": "gen_random_uuid()"},
                "json": {"blank": "", "generator": "get_uuid"},
                "typescript": {"blank": "", "generator": "getUUID()"},
            },
            "now()": {
                "python": {"blank": "", "generator": "datetime.now()"},
                "database": {"blank": "null", "generator": "now()"},
                "json": {"blank": "", "generator": "get_current_time"},
                "typescript": {"blank": "", "generator": "getCurrentTime()"},
            },
            "null": {"default": {"blank": "null", "generator": ""}},
            "true": {"default": {"blank": "true", "generator": ""}},
            "false": {"default": {"blank": "false", "generator": ""}},
            "'[]'::jsonb": {"default": {"blank": "[]", "generator": ""}},
        }

        callable_outcomes = {
            "::smallint": lambda value: {
                "blank": str(int(value.split("'")[1].strip())),  # Extract smallint value
                "generator": "",
            },
            "::integer": lambda value: {
                "blank": str(int(value.split("'")[1].strip())),  # Extract integer value
                "generator": "",
            },
            "::bigint": lambda value: {
                "blank": str(int(value.split("'")[1].strip())),  # Extract bigint value
                "generator": "",
            },
            "::real": lambda value: {
                "blank": value.split("'")[1].strip(),  # Extract the real value
                "generator": "",
            },
            "::double precision": lambda value: {
                "blank": str(float(value.split("'")[1].strip())),  # Extract double value
                "generator": "",
            },
            "::numeric": lambda value: {
                "blank": value.split("'")[1].strip(),  # Extract numeric value
                "generator": "",
            },
            "::character varying": lambda value: {
                "blank": value.split("'")[1].strip(),  # Extract the text value
                "generator": "",
            },
            "::text": lambda value: {
                "blank": value.split("'")[1].strip(),  # Extract the text value
                "generator": "",
            },
            "::boolean": lambda value: {
                "blank": value.split("'")[1].strip(),  # Extract true/false
                "generator": "",
            },
            "::timestamptz": lambda value: {
                "blank": value.split("'")[1].strip(),  # Extract the date value
                "generator": "formatTimestamptz()",
            },
            "::date": lambda value: {
                "blank": value.split("'")[1].strip(),  # Extract the date value
                "generator": "formatDate()",
            },
            "::timestamp without time zone": lambda value: {
                "blank": value.split("'")[1].strip(),  # Extract timestamp
                "generator": "formatTimestamp()",
            },
            "::timestamp with time zone": lambda value: {
                "blank": value.split("'")[1].strip(),  # Extract timestamp with timezone
                "generator": "formatTimestamptz()",
            },
            "::uuid": lambda uuid_value: {
                "blank": uuid_value.split("'")[1].strip() if "'" in uuid_value else uuid_value.strip(),
                "generator": "",
            },
            "::jsonb": lambda value: {
                "blank": json.loads(value.split("'")[1].strip().replace("'", '"')),
                "generator": "",
            },
            "empty_jsonb": lambda value: {
                "blank": "{}",  # Handle empty JSON object
                "generator": "",
            },
            "enum": {
                "default_enum": lambda enum_value: {
                    "blank": enum_value,
                    "generator": "",
                },
                "prompt_enum": lambda readable_base_type: {
                    "blank": f"Select {readable_base_type}",
                    "generator": "",
                },
            },
            "timestamptz": lambda value: {
                "blank": value.strip(),
                "generator": "formatTimestamptz()",
            },
            "timestamp": lambda value: {
                "blank": value.strip(),
                "generator": "formatTimestamp()",
            },
            "date": lambda value: {"blank": value.strip(), "generator": "formatDate()"},
            "time": lambda value: {"blank": value.strip(), "generator": "formatTime()"},
            "default": lambda value: {"blank": value.strip(), "generator": ""},
        }

        def clean_value(value, context):
            """
            Returns a string representation based on the provided value and context.
            """
            # Handle None type
            if value is None:
                return outcomes[None]["default"]

            # Handle UUID special cases
            if value in [
                "gen_random_uuid()",
                "uuid_generate_v4()",
                "extensions.uuid_generate_v4()",
            ]:
                return outcomes[value].get(context, callable_outcomes["default"](value))

            # Handle UUID and timestamp special cases
            if value in ["now()"]:
                if self.verbose:
                    vcprint(data=value, verbose=self.verbose, color="blue")
                    vcprint(data=self.base_type, verbose=self.verbose, color="yellow")

                return outcomes[value].get(context, callable_outcomes[self.base_type](value))

            # Handle specific cases with static entries
            elif value == "null":
                return outcomes["null"]["default"]

            elif value in ["true", "false"]:
                return outcomes[value]["default"]

            elif value == "'[]'::jsonb":
                return outcomes["'[]'::jsonb"]["default"]

            # Handle empty JSONB
            elif value == "'{}'::jsonb":
                return callable_outcomes["empty_jsonb"](value)

            # Handle nextval (PostgreSQL sequence values)
            elif value.startswith("nextval("):
                sequence_name = value.split("'")[1]  # Extract the sequence name
                return callable_outcomes.get("nextval", callable_outcomes["default"])(sequence_name)

            # Explicit handling for PostgreSQL types
            if value.endswith("::smallint"):
                return callable_outcomes["::smallint"](value)

            if value.endswith("::integer"):
                return callable_outcomes["::integer"](value)

            if value.endswith("::bigint"):
                return callable_outcomes["::bigint"](value)

            if value.endswith("::real"):
                return callable_outcomes["::real"](value)

            if value.endswith("::double precision"):
                return callable_outcomes["::double precision"](value)

            if value.endswith("::numeric"):
                return callable_outcomes["::numeric"](value)

            if value.endswith("::character varying"):
                return callable_outcomes["::character varying"](value)

            if value.endswith("::text"):
                return callable_outcomes["::text"](value)

            if value.endswith("::boolean"):
                return callable_outcomes["::boolean"](value)

            if value.endswith("::timestamptz"):
                vcprint(data=value, color="green")
                return callable_outcomes["::timestamptz"](value)

            if value.endswith("::date"):
                vcprint(data=value, color="green")
                return callable_outcomes["::date"](value)

            if value.endswith("::timestamp without time zone"):
                vcprint(data=value, color="blue")
                return callable_outcomes["::timestamp without time zone"](value)

            if value.endswith("::timestamp with time zone"):
                vcprint(data=value, color="red")
                return callable_outcomes["::timestamp with time zone"](value)

            if value.endswith("::uuid"):
                uuid_value = value.split("::")[0].strip("'")  # Extract UUID without validation
                return callable_outcomes["::uuid"](uuid_value)

            if value.endswith("::jsonb"):
                return callable_outcomes["::jsonb"](value)

            # Handle enums
            if "::" in value and hasattr(self, "enum_labels"):
                enum_value = value.split("::")[0].strip("'")
                if enum_value in self.enum_labels:
                    return callable_outcomes["enum"]["default_enum"](enum_value)
                else:
                    readable_base_type = self.base_type.replace("_", " ").title()
                    return callable_outcomes["enum"]["prompt_enum"](readable_base_type)

            # Default case for unhandled values
            vcprint(
                data=self.to_dict(),
                title=f"Default value not handled: {value}",
                pretty=True,
                verbose=True,
                color="red",
            )
            return callable_outcomes["default"](value)

        # Handling the case where self.default is None
        if self.default is None:
            self.clean_default = {
                "python": None,
                "database": "null",
                "json": "null",
                "typescript": "",
            }
            self.calc_default_generator_functions = {
                "python": "",
                "database": "",
                "json": "",
                "typescript": "",
            }
            return

        # Parse the default value for each context and store them as strings
        self.clean_default = {
            "python": str(clean_value(self.default, "python")["blank"]),
            "database": str(clean_value(self.default, "database")["blank"]),
            "json": str(clean_value(self.default, "json")["blank"]),
            "typescript": str(clean_value(self.default, "typescript")["blank"]) or "",
        }

        self.calc_default_generator_functions = {
            "python": clean_value(self.default, "python")["generator"] or "",
            "database": clean_value(self.default, "database")["generator"] or "",
            "json": clean_value(self.default, "json")["generator"] or "",
            "typescript": clean_value(self.default, "typescript")["generator"] or "",
        }

        return self.clean_default

    def get_default_value(self):
        # TODO: Update this to always directly give the properly formatted empty value as well: None, [], {}, etc.

        self.calc_default_value = self.parse_default_value()
        return self.calc_default_value

    def get_type_reference(self):
        if self.enum_labels:
            ts_type_reference = " | ".join([f'"{label}"' for label in self.enum_labels]) + " | undefined"
            json_type_reference = self.enum_labels
        else:
            ts_type_reference = self.typescript_type
            json_type_reference = self.typescript_type

        self.type_reference = {
            "database": self.full_type,
            "python": self.full_type,  # Temporary
            "typescript": ts_type_reference,
            "json": json_type_reference,
        }

        return self.type_reference

    def get_is_required(self):
        if not self.nullable:
            self.calc_is_required = {
                "python": None,
                "database": None,
                "json": None,
                "typescript": "true",
            }
            self.update_prop(prop="required", value=True, priority=5)

        else:
            self.calc_is_required = {
                "python": None,
                "database": None,
                "json": None,
                "typescript": "false",
            }
            self.update_prop(prop="required", value=False, priority=5)

        return self.calc_is_required

    def get_is_array(self):
        if self.is_array:
            self.calc_is_array = {
                "python": None,
                "database": None,
                "json": None,
                "typescript": "true",
            }
        else:
            self.calc_is_array = {
                "python": None,
                "database": None,
                "json": None,
                "typescript": "false",
            }
        return self.calc_is_array

    def get_is_primary_key(self):
        if self.is_primary_key:
            self.calc_is_primary_key = {
                "python": None,
                "database": None,
                "json": None,
                "typescript": "true",
            }
            self.update_prop(prop="required", value=True, priority=10)

        else:
            self.calc_is_primary_key = {
                "python": None,
                "database": None,
                "json": None,
                "typescript": "false",
            }
        return self.calc_is_primary_key

    def get_default_generator_function(self):
        self.calc_default_generator_functions = {
            "python": None,
            "database": None,
            "json": None,
            "typescript": "null",
        }

        return self.calc_default_generator_functions

    def get_validation_functions(self):
        self.calc_validation_functions = {
            "python": None,
            "database": None,
            "json": None,
            "typescript": "[]",
        }

        return self.calc_validation_functions

    def get_exclusion_rules(self):
        self.calc_exclusion_rules = {
            "python": None,
            "database": None,
            "json": None,
            "typescript": "[]",
        }

        return self.calc_exclusion_rules

    def get_max_field_length(self):
        self.calc_max_length = self.character_maximum_length if self.character_maximum_length is not None else "null"
        return self.calc_max_length

    def to_python_model_field(self):
        field_options = []
        if self.is_primary_key:
            field_options.append("primary_key=True")
        if not self.nullable:
            field_options.append("null=False")
        if self.clean_default is not None:
            python_default = self.clean_default["python"]
            if python_default:
                if isinstance(python_default, (dict, list)):  # Proper JSON-like structure
                    field_options.append(f"default={python_default}")  # No quotes!
                elif isinstance(python_default, str):
                    try:
                        parsed_default = ast.literal_eval(python_default)
                        if isinstance(parsed_default, (dict, list)):  # Confirm it's valid JSON-like structure
                            field_options.append(f"default={parsed_default}")
                        else:
                            field_options.append(f"default='{python_default}'")
                    except (ValueError, SyntaxError):
                        field_options.append(f"default='{python_default}'")  # Keep as string if parsing fails

        if self.character_maximum_length:
            field_options.append(f"max_length={self.character_maximum_length}")
        if self.is_unique:
            field_options.append("unique=True")

        options_str = ", ".join(field_options)

        if self.foreign_key_reference:
            related_model = self.utils.to_pascal_case(self.foreign_key_reference["table"])
            if related_model == self.utils.to_pascal_case(self.table_name):
                field_def = f"{self.name} = ForeignKey(to_model='{related_model}', to_column='{self.foreign_key_reference['column']}', {options_str})"
            else:
                field_def = f"{self.name} = ForeignKey(to_model={related_model}, to_column='{self.foreign_key_reference['column']}', {options_str})"
        elif self.python_field_type == "ObjectField":
            field_def = f"{self.name} = ObjectField({options_str})"
        else:
            field_def = f"{self.name} = {self.python_field_type}({options_str})"

        return field_def

    def to_dict(self):
        return {
            "name": self.name,
            "position": self.position,
            "full_type": self.full_type,
            "base_type": self.base_type,
            "domain_type": self.domain_type,
            "enum_labels": self.enum_labels,
            "is_array": self.is_array,
            "nullable": self.nullable,
            "default": self.default,
            "character_maximum_length": self.character_maximum_length,
            "numeric_precision": self.numeric_precision,
            "numeric_scale": self.numeric_scale,
            "collation": self.collation,
            "is_identity": self.is_identity,
            "is_generated": self.is_generated,
            "is_primary_key": self.is_primary_key,
            "is_unique": self.is_unique,
            "has_index": self.has_index,
            "check_constraints": self.check_constraints,
            "foreign_key_reference": self.foreign_key_reference,
            "comment": self.comment,
        }


class Table:
    def __init__(
        self,
        oid,
        database_project,
        unique_table_id,
        name,
        type_,
        schema,
        database,
        owner,
        size_bytes,
        index_size_bytes,
        rows,
        last_vacuum,
        last_analyze,
        description,
        estimated_row_count,
        total_bytes,
        has_primary_key,
        index_count,
        columns=None,
        junction_analysis_ts=None,
    ):
        self.utils = utils
        self.oid = oid
        self.database_project = database_project
        self.unique_table_id = unique_table_id
        self.name = name
        self.type = type_
        self.schema = schema
        self.database = database
        self.owner = owner
        self.size_bytes = size_bytes
        self.index_size_bytes = index_size_bytes
        self.rows = rows
        self.last_vacuum = last_vacuum
        self.last_analyze = last_analyze
        self.description = description
        self.estimated_row_count = estimated_row_count
        self.total_bytes = total_bytes
        self.has_primary_key = has_primary_key
        self.index_count = index_count
        self.columns = [Column(**col) for col in columns]
        self.junction_analysis_ts = junction_analysis_ts

        self.identify_display_column()
        self.defaultFetchStrategy = "simple"

        self.all_table_instances = {}
        # Existing collections
        self.foreign_keys = {}
        self.referenced_by = {}
        self.many_to_many = []

        # New collections for relationship instances
        self.foreign_key_relationships = []
        self.referenced_by_relationships = []
        self.many_to_many_relationships = []

        self.schema_structure = {
            "defaultFetchStrategy": "simple",
            "foreignKeys": [],
            "inverseForeignKeys": [],
            "manyToMany": [],
        }
        self.display_field_metadata = None

        self.verbose = verbose
        self.debug = debug
        self.initialized = False

        self.name_snake = self.utils.to_snake_case(self.name)
        self.name_camel = self.utils.to_camel_case(self.name)
        self.name_pascal = self.utils.to_pascal_case(self.name)
        self.name_kebab = self.utils.to_kebab_case(self.name)
        self.name_title = self.utils.to_title_case(self.name)

        self.unique_entity_id = f"{self.database_project}:{self.name_camel}"

        self.py_fields = []
        self.unique_field_types = set()
        self.unique_name_lookups = ""
        self.column_rel_entries = {}  # Temp solution to get fk/ifk for reverse field lookup
        self.Field_name_groups = {}

        vcprint(self.junction_analysis_ts, pretty=True, verbose=self.verbose, color="blue")
        vcprint(
            self.to_dict(),
            title="Table initialized",
            pretty=True,
            verbose=self.verbose,
            color="cyan",
        )

    def add_column(self, column_data):
        column = Column(**column_data)
        column.initialize_code_generation()
        self.columns.append(column)

    def identify_display_column(self):
        # TODO: Figure out how to make the timing on this work because right now, it won't work.
        # Reset all columns' display status initially to ensure only one display field is set
        for col in self.columns:
            col.is_display_field = False

        # Define the layers of matching logic
        exact_priority_names = ["name", "title", "label"]
        containment_keywords = ["name", "title", "label"]
        extended_candidates = [
            "description",
            "full_name",
            "username",
            "display_name",
            "subject",
        ]
        last_resort_candidates = ["matrx", "broker", "type"]

        # Layer 1: Exact match with priority names
        for column in self.columns:
            if column.name.lower() in exact_priority_names:
                column.is_display_field = True
                self.display_field_metadata = {
                    "fieldName": column.name_camel,
                    "databaseFieldName": column.name,
                }
                return  # Exit as soon as one display field is set

        # Layer 2: Check for containment of keywords within column names
        for column in self.columns:
            if any(keyword in column.name.lower() for keyword in containment_keywords):
                column.is_display_field = True
                self.display_field_metadata = {
                    "fieldName": column.name_camel,
                    "databaseFieldName": column.name,
                }
                return  # Stop after setting the first containment match

        # Layer 3: Extended candidates matching
        for column in self.columns:
            if column.name.lower() in extended_candidates:
                column.is_display_field = True
                self.display_field_metadata = {
                    "fieldName": column.name_camel,
                    "databaseFieldName": column.name,
                }
                return  # Stop after setting the first extended match

        # Layer 4: Last resort candidates matching
        for column in self.columns:
            if column.name.lower() in last_resort_candidates:
                column.is_display_field = True
                self.display_field_metadata = {
                    "fieldName": column.name_camel,
                    "databaseFieldName": column.name,
                }
                return  # Stop after setting the first last resort match

        # Layer 5: Fallback to primary key if no match found
        for column in self.columns:
            if column.is_primary_key:
                column.is_display_field = True
                self.display_field_metadata = {
                    "fieldName": column.name_camel,
                    "databaseFieldName": column.name,
                }
                return  # Stop after setting the primary key

    def get_display_field_metadata(self):
        if self.display_field_metadata is None:
            self.display_ts_field_metadata = "null"
            self.display_json_field_metadata = None
        else:
            field_name = self.display_field_metadata["fieldName"]
            database_field_name = self.display_field_metadata["databaseFieldName"]

            self.display_ts_field_metadata = f"{{ fieldName: '{field_name}', " f"databaseFieldName: '{database_field_name}' }}"

            self.display_json_field_metadata = {
                "fieldName": field_name,
                "databaseFieldName": database_field_name,
            }

    def add_foreign_key(self, target_table, relationship):
        # Maintain existing behavior
        self.foreign_keys[target_table] = relationship
        self.schema_structure["foreignKeys"].append(
            {
                "column": relationship.column,
                "relatedTable": target_table,
                "relatedColumn": relationship.foreign_column,
            }
        )
        # Add to new collection
        self.foreign_key_relationships.append(relationship)
        self._update_fetch_strategy()

    def get_relationship_mapping(self):
        return {relationship.target_table: relationship.foreign_column for relationship in self.foreign_key_relationships}

    def add_referenced_by(self, source_table, relationship):
        # Maintain existing behavior
        self.referenced_by[source_table] = relationship
        self.schema_structure["inverseForeignKeys"].append({"relatedTable": source_table, "relatedColumn": relationship.column})
        # Add to new collection
        self.referenced_by_relationships.append(relationship)
        self._update_fetch_strategy()

    def add_many_to_many(self, junction_table, related_table):
        # Maintain existing behavior
        many_to_many_entry = {
            "junction_table": junction_table,
            "related_table": related_table,
        }
        self.many_to_many.append(many_to_many_entry)
        self.schema_structure["manyToMany"].append({"junctionTable": junction_table.name, "relatedTable": related_table.name})
        # Add to new collection
        self.many_to_many_relationships.append(many_to_many_entry)
        self._update_fetch_strategy()

    def _update_fetch_strategy(self):
        """
        Updates the fetch strategy based on the relationships present.
        """
        has_fk = bool(self.schema_structure["foreignKeys"])
        has_ifk = bool(self.schema_structure["inverseForeignKeys"])
        has_m2m = bool(self.schema_structure["manyToMany"])

        # Check for all combinations
        if has_m2m and has_fk and has_ifk:
            self.defaultFetchStrategy = "fkIfkAndM2M"
        elif has_m2m and has_fk:
            self.defaultFetchStrategy = "m2mAndFk"
        elif has_m2m and has_ifk:
            self.defaultFetchStrategy = "m2mAndIfk"
        elif has_m2m:
            self.defaultFetchStrategy = "m2m"
        elif has_fk and has_ifk:
            self.defaultFetchStrategy = "fkAndIfk"
        elif has_fk:
            self.defaultFetchStrategy = "fk"
        elif has_ifk:
            self.defaultFetchStrategy = "ifk"
        else:
            self.defaultFetchStrategy = "simple"

    def get_column(self, column_name):
        for column in self.columns:
            if column.name == column_name:
                return column
        return None

    def get_foreign_key(self, target_table):
        return self.foreign_keys.get(target_table)

    def get_referenced_by(self, source_table):
        return self.referenced_by.get(source_table)

    def get_foreign_key_column(self, target_table):
        fk = self.get_foreign_key(target_table)
        return fk.column if fk else None

    def get_referenced_by_column(self, source_table):
        ref = self.get_referenced_by(source_table)
        return ref.column if ref else None

    def get_all_columns(self):
        return self.columns

    def get_all_foreign_keys(self):
        return self.foreign_keys

    def get_all_referenced_by(self):
        return self.referenced_by

    def get_column_names(self):
        return [column.name for column in self.columns]

    def __repr__(self):
        return self.name

    def initialize_code_generation(self):
        if self.initialized:
            return
        for column in self.columns:
            if not column.initialized:
                column.initialize_code_generation()

        self.generate_unique_field_types()
        self.generate_name_variations()
        self.generate_unique_name_lookups()
        self.generate_component_props()  # TODO: Needs update
        self.get_fieldNames_in_groups()

        self.identify_display_column()
        self.get_display_field_metadata()

    def finalize_initialization(self):
        self.to_reverse_field_name_lookup()
        self.to_reverse_table_lookup_entry()

        self.initialized = True

    def get_primary_key_field(self) -> str:
        primary_key_columns = [column.name_camel for column in self.columns if column.is_primary_key]

        if len(primary_key_columns) == 1:
            return primary_key_columns[0]
        elif len(primary_key_columns) > 1:
            return ", ".join(primary_key_columns)

        return "null"

    def get_fieldNames_in_groups(self):
        self.Field_name_groups["nativeFields"] = [column.name_camel for column in self.columns]
        self.Field_name_groups["primaryKeyFields"] = [column.name_camel for column in self.columns if column.is_primary_key]
        self.Field_name_groups["nativeFieldsNoPk"] = [column.name_camel for column in self.columns if not column.is_primary_key]
        return self.Field_name_groups

    def get_primary_key_fields_list(self):
        database_columns = []
        frontend_fields = []
        for column in self.columns:
            if column.is_primary_key:
                database_columns.append(column.name)
                frontend_fields.append(column.name_camel)

        pk_entry = {
            "frontend_name": database_columns,
            "database_name": frontend_fields,
        }
        return pk_entry

    def get_column_default_components(self):
        self.column_default_components = [column.calc_default_component for column in self.columns]
        return self.column_default_components

    def get_primary_key_metadata(self) -> dict:
        """
        Generates comprehensive primary key metadata including:
        - Frontend field names
        - Database field names
        - Query template structure
        - Type information
        """
        primary_key_columns = [
            {
                "frontend_name": column.name_camel,
                "database_name": column.name,
                "type": column.type_reference,
                "is_required": column.is_required,
            }
            for column in self.columns
            if column.is_primary_key
        ]

        if not primary_key_columns:
            return {
                "type": "none",
                "fields": [],
                "database_fields": [],
                "where_template": {},
            }

        # Create the where clause template with database field names
        where_template = {col["database_name"]: None for col in primary_key_columns}

        return {
            "type": "composite" if len(primary_key_columns) > 1 else "single",
            "fields": [col["frontend_name"] for col in primary_key_columns],
            "database_fields": [col["database_name"] for col in primary_key_columns],
            "where_template": where_template,
        }

    def generate_unique_name_lookups(self):
        name_variations = set(self.name_variations.values())
        formatted_unique_names = {f'"{name}"' if " " in name or "-" in name else name: self.name_camel for name in name_variations}
        self.unique_name_lookups = formatted_unique_names

    def generate_unique_field_types(self):
        # Initialize the lookup structure (no need for table name here, it's done when aggregating)
        lookup_structure = f"{{\n"

        # Add the fields for each column in the table, properly formatted
        for idx, column in enumerate(self.columns):
            column_entry = column.column_lookup_string

            # Add commas only between entries (not after the last one)
            if idx < len(self.columns) - 1:
                lookup_structure += f"    {column_entry},\n"
            else:
                lookup_structure += f"    {column_entry}\n"

        # Close the lookup structure (no extra comma at the end)
        lookup_structure += "}"

        # Store the properly formatted structure
        self.field_name_lookup_structure = lookup_structure

    def to_foreign_key_entry(self, target_table):
        self.component_props = {
            "subComponent": "default",
            "variant": "default",
            "placeholder": "default",
            "size": "default",
            "textSize": "default",
            "textColor": "default",
            "rows": "default",
            "animation": "default",
            "fullWidthValue": "default",
            "fullWidth": "default",
            "disabled": "default",
            "className": "default",
            "type": "default",
            "onChange": "default",
            "onBlur": "default",
            "formatString": "default",
            "minDate": "default",
            "maxDate": "default",
            "numberType": "default",
        }

        if target_table == "self_reference":
            target_table = self.name

        frontend_name = f"{self.utils.to_camel_case(target_table)}Reference"
        entityName = f"{self.utils.to_camel_case(target_table)}"

        uniqueColumnId = f"{self.database_project}:{target_table}:{self.get_primary_key_field()}"
        uniqueFieldId = f"{self.database_project}:{entityName}:{self.utils.to_camel_case(self.get_primary_key_field())}"

        vcprint(uniqueFieldId, verbose=self.verbose, color="yellow")

        # Generate the name variations based on the target table
        table_variations = {
            "frontend": f"{self.utils.to_camel_case(target_table)}Reference",
            "backend": f"{self.utils.to_snake_case(target_table)}_reference",
            "database": f"ref_{target_table}",
            "pretty": f"{self.utils.to_title_case(target_table)} Reference",
            "component": f"{self.utils.to_pascal_case(target_table)}Reference",
            "kebab": f"{self.utils.to_kebab_case(target_table)}Reference",
            "sqlFunctionRef": f"p_ref_{target_table}",
            "RestAPI": f"{self.utils.to_camel_case(target_table)}Reference",
            "GraphQL": f"{self.utils.to_camel_case(target_table)}Reference",
            "custom": f"{self.utils.to_camel_case(target_table)}Reference",
        }

        self.column_rel_entries[frontend_name] = table_variations

        relationship_map = self.get_relationship_mapping()

        # TypeScript structure
        ts_structure = (
            f"{table_variations['frontend']}: {{\n"
            f"    fieldNameFormats: {json.dumps(table_variations, indent=4)} as const,\n"
            f"    uniqueColumnId: '{uniqueColumnId}',\n"
            f"    uniqueFieldId: '{uniqueFieldId}',\n"
            f"    name: '{frontend_name}',\n"
            f"    displayName: '{table_variations['pretty']}',\n"
            f"    dataType: 'object' as const,\n"
            f"    isRequired: false,\n"
            f"    maxLength: null,\n"
            f"    isArray: true,\n"
            f"    defaultValue: [],\n"
            f"    isPrimaryKey: false,\n"
            f"    defaultGeneratorFunction: null,\n"
            f"    validationFunctions: ['isValidDatabaseEntry'],\n"
            f"    exclusionRules: ['notCoreField'],\n"
            f"    defaultComponent: 'ACCORDION_VIEW_ADD_EDIT' as const,\n"
            f"    structure: 'foreignKey' as const,\n"
            f"    isNative: false,\n"
            f"    typeReference: {{}} as TypeBrand<TableSchemaStructure['{entityName}'][]>,\n"
            f"    entityName: '{entityName}',\n"
            f"    databaseTable: '{target_table}',\n"
            f"    relationshipMap: {relationship_map},\n"
            f"}},"
        )

        const_ts_structure = (
            f"{table_variations['frontend']}: {{\n"
            f"    fieldNameFormats: {json.dumps(table_variations, indent=4)} as const,\n"
            f"    uniqueColumnId: '{uniqueColumnId}',\n"
            f"    uniqueFieldId: '{uniqueFieldId}',\n"
            f"    name: '{frontend_name}',\n"
            f"    displayName: '{table_variations['pretty']}',\n"
            f"    dataType: 'object' as const,\n"
            f"    isRequired: false,\n"
            f"    maxLength: null,\n"
            f"    isArray: true,\n"
            f"    defaultValue: [],\n"
            f"    isPrimaryKey: false,\n"
            f"    defaultGeneratorFunction: null,\n"
            f"    validationFunctions: ['isValidDatabaseEntry'],\n"
            f"    exclusionRules: ['notCoreField'],\n"
            f"    defaultComponent: 'ACCORDION_VIEW_ADD_EDIT' as const,\n"
            f"    structure: 'foreignKey' as const,\n"
            f"    isNative: false,\n"
            f"    typeReference: {{}} as TypeBrand<AutomationEntity<'{entityName}'>[]>,\n"
            f"    entityName: '{entityName}',\n"
            f"    databaseTable: '{target_table}',\n"
            f"    relationshipMap: {relationship_map},\n"
            f"}},"
        )

        # JSON structure
        json_structure = {
            f"{table_variations['frontend']}": {
                "fieldNameFormats": table_variations,
                "uniqueColumnId": uniqueColumnId,
                "uniqueFieldId": uniqueFieldId,
                "type": "object",
                "format": "single",
                "defaultComponent": "ACCORDION_VIEW_ADD_EDIT",
                "structure": {
                    "structure": "foreignKey",
                    "databaseTable": target_table,
                    "typeReference": f"TypeBrand<AutomationEntity<'{entityName}'>[]>",
                },
            }
        }

        return ts_structure, json_structure, const_ts_structure

    def to_inverse_foreign_key_entry(self, source_table):
        self.component_props = {
            "subComponent": "default",
            "variant": "default",
            "placeholder": "default",
            "size": "default",
            "textSize": "default",
            "textColor": "default",
            "rows": "default",
            "animation": "default",
            "fullWidthValue": "default",
            "fullWidth": "default",
            "disabled": "default",
            "className": "default",
            "type": "default",
            "onChange": "default",
            "onBlur": "default",
            "formatString": "default",
            "minDate": "default",
            "maxDate": "default",
            "numberType": "default",
        }

        frontend_name = f"{self.utils.to_camel_case(source_table)}Inverse"
        entityName = f"{self.utils.to_camel_case(source_table)}"
        uniqueTableId = f"{self.database_project}:{source_table}"
        uniqueEntityId = f"{self.database_project}:{entityName}"

        # referenceTo = f"{self.utils.to_camel_case(source_table)}" #comeback

        table_variations = {
            "frontend": f"{self.utils.to_camel_case(source_table)}Inverse",
            "backend": f"{self.utils.to_snake_case(source_table)}_Inverse",
            "database": f"ifk_{source_table}",
            "pretty": f"{self.utils.to_title_case(source_table)} Inverse",
            "component": f"{self.utils.to_pascal_case(source_table)}Inverse",
            "kebab": f"{self.utils.to_kebab_case(source_table)}Inverse",
            "sqlFunctionRef": f"p_ifk_{source_table}",
            "RestAPI": f"{self.utils.to_camel_case(source_table)}Inverse",
            "GraphQL": f"{self.utils.to_camel_case(source_table)}Inverse",
            "custom": f"{self.utils.to_camel_case(source_table)}Inverse",
        }
        self.column_rel_entries[frontend_name] = table_variations

        # TypeScript structure
        ts_structure = (
            f"{table_variations['frontend']}: {{\n"
            f"    fieldNameFormats: {json.dumps(table_variations, indent=4)} as const,\n"
            f"    uniqueTableId: '{uniqueTableId}',\n"
            f"    uniqueEntityId: '{uniqueEntityId}',\n"
            f"    name: '{frontend_name}',\n"
            f"    displayName: '{self.utils.to_title_case(source_table)} Inverse',\n"
            f"    dataType: 'object' as const,\n"
            f"    isRequired: false,\n"
            f"    maxLength: null,\n"
            f"    isArray: true,\n"
            f"    defaultValue: [],\n"
            f"    isPrimaryKey: false,\n"
            f"    defaultGeneratorFunction: null,\n"
            f"    validationFunctions: ['isValidDatabaseEntry'],\n"
            f"    exclusionRules: ['notCoreField'],\n"
            f"    defaultComponent: 'ACCORDION_VIEW_ADD_EDIT' as const,\n"
            f"    structure: 'inverseForeignKey' as const,\n"
            f"    isNative: false,\n"
            f"    typeReference: {{}} as TypeBrand<TableSchemaStructure['{entityName}'][]>,\n"
            f"    entityName: '{entityName}',\n"
            f"    databaseTable: '{source_table}',\n"
            f"}},"
        )
        const_ts_structure = (
            f"{table_variations['frontend']}: {{\n"
            f"    fieldNameFormats: {json.dumps(table_variations, indent=4)} as const,\n"
            f"    uniqueTableId: '{uniqueTableId}',\n"
            f"    uniqueEntityId: '{uniqueEntityId}',\n"
            f"    name: '{frontend_name}',\n"
            f"    displayName: '{self.utils.to_title_case(source_table)} Inverse',\n"
            f"    dataType: 'object' as const,\n"
            f"    isRequired: false,\n"
            f"    maxLength: null,\n"
            f"    isArray: true,\n"
            f"    defaultValue: [],\n"
            f"    isPrimaryKey: false,\n"
            f"    defaultGeneratorFunction: null,\n"
            f"    validationFunctions: ['isValidDatabaseEntry'],\n"
            f"    exclusionRules: ['notCoreField'],\n"
            f"    defaultComponent: 'ACCORDION_VIEW_ADD_EDIT' as const,\n"
            f"    structure: 'inverseForeignKey' as const,\n"
            f"    isNative: false,\n"
            f"    typeReference: {{}} as TypeBrand<AutomationEntity<'{entityName}'>[]>,\n"
            f"    entityName: '{entityName}',\n"
            f"    databaseTable: '{source_table}',\n"
            f"}},"
        )

        # JSON structure
        json_structure = {
            f"{table_variations['frontend']}": {
                "fieldNameFormats": table_variations,
                "uniqueTableId": uniqueTableId,
                "uniqueEntityId": uniqueEntityId,
                "type": "array",
                "format": "array",
                "defaultComponent": "ACCORDION_VIEW_ADD_EDIT",
                "structure": {
                    "structure": "inverseForeignKey",
                    "entityName": entityName,
                    "databaseTable": source_table,
                    "typeReference": f"TypeBrand<AutomationEntity<'{entityName}'>[]>",
                },
            }
        }

        return ts_structure, json_structure, const_ts_structure

    def to_json_inverse_foreign_keys(self):
        entries = []
        for ifk in self.referenced_by.values():
            entries.append(
                {
                    "relatedTable": ifk.source_table,
                    "relatedColumn": ifk.column,
                    "mainTableColumn": ifk.foreign_column,  # Include the main table column being referenced
                }
            )
        return entries

    def to_json_foreign_keys(self):
        entries = []
        for fk in self.schema_structure["foreignKeys"]:
            entries.append(
                {
                    "column": fk["column"],
                    "relatedTable": fk["relatedTable"],
                    "relatedColumn": fk["relatedColumn"],
                }
            )
        return entries

    def to_json_many_to_many(self):
        entries = []
        for mm in self.many_to_many:
            junction_table = mm["junction_table"]  # Junction table is a Table instance
            related_table = mm["related_table"]  # Related table is a Table instance

            # Retrieve the foreign key columns from the junction table
            main_table_column = None
            related_table_column = None

            # Loop through the foreign keys in the junction table
            for fk in junction_table.foreign_keys.values():
                if fk.target_table == self.name:  # Check if the target_table is the main table (Table 1)
                    main_table_column = fk.column
                elif fk.target_table == related_table.name:  # Check if the target_table is the related table (Table 3)
                    related_table_column = fk.column

            if main_table_column and related_table_column:
                entries.append(
                    {
                        "junctionTable": junction_table.name,
                        "relatedTable": related_table.name,
                        "mainTableColumn": main_table_column,
                        "relatedTableColumn": related_table_column,
                    }
                )
        return entries

    def to_ts_foreign_keys(self):
        entries = []
        for fk in self.schema_structure["foreignKeys"]:
            entry = (
                f"{{ relationshipType: 'foreignKey', "
                f"column: '{fk['column']}', "
                f"relatedTable: '{fk['relatedTable']}', "
                f"relatedColumn: '{fk['relatedColumn']}', "  # TODO make sure this exists
                f"junctionTable: null }}"
            )
            entries.append(entry)
        return entries

    def to_ts_inverse_foreign_keys(self):
        entries = []
        for ifk in self.referenced_by.values():
            entry = (
                f"{{ relationshipType: 'inverseForeignKey', "
                f"column: '{ifk.foreign_column}', "
                f"relatedTable: '{ifk.source_table}', "
                f"relatedColumn: '{ifk.column}', "
                f"junctionTable: null }}"
            )
            entries.append(entry)
        return entries

    def to_ts_many_to_many(self):
        entries = []
        for mm in self.many_to_many:
            junction_table = mm["junction_table"]  # Junction table is a Table instance
            related_table = mm["related_table"]  # Related table is a Table instance

            # Retrieve the foreign key columns from the junction table
            main_table_column = None
            related_table_column = None

            # Loop through the foreign keys in the junction table
            for fk in junction_table.foreign_keys.values():
                if fk.target_table == self.name:  # Check if the target_table is the main table (Table 1)
                    main_table_column = fk.column
                elif fk.target_table == related_table.name:  # Check if the target_table is the related table (Table 3)
                    related_table_column = fk.column

            if main_table_column and related_table_column:
                entry = (
                    f"{{ relationshipType: 'manyToMany', "
                    f"column: '{main_table_column}', "
                    f"relatedTable: '{related_table.name}', "
                    f"relatedColumn: '{related_table_column}', "
                    f"junctionTable: '{junction_table.name}' }}"
                )
                entries.append(entry)
        return entries

    def to_schema_structure_entry(self):
        # TypeScript structure generation (as string entries for ts)
        ts_entries = []

        foreign_keys = self.to_ts_foreign_keys()
        inverse_foreign_keys = self.to_ts_inverse_foreign_keys()
        many_to_many = self.to_ts_many_to_many()

        # Add non-empty entries to the TypeScript structure list
        if foreign_keys:
            ts_entries.extend(foreign_keys)
        if inverse_foreign_keys:
            ts_entries.extend(inverse_foreign_keys)
        if many_to_many:
            ts_entries.extend(many_to_many)

        # Create the final TypeScript structure string
        ts_structure = ",\n        ".join(ts_entries)

        # JSON structure generation
        json_entries = []

        foreign_keys_json = self.to_json_foreign_keys()
        inverse_foreign_keys_json = self.to_json_inverse_foreign_keys()
        many_to_many_json = self.to_json_many_to_many()

        # Add non-empty entries to the JSON structure list
        if foreign_keys_json:
            json_entries.extend(foreign_keys_json)
        if inverse_foreign_keys_json:
            json_entries.extend(inverse_foreign_keys_json)
        if many_to_many_json:
            json_entries.extend(many_to_many_json)

        # Return the final TypeScript and JSON structures as lists of entries
        return ts_structure, json_entries

    def generate_name_variations(self):
        self.name_variations = {
            "frontend": self.name_camel,
            "backend": self.name_snake,
            "database": self.name_snake,
            "pretty": self.name_title,
            "component": self.name_pascal,
            "kebab": self.name_kebab,
            "sqlFunctionRef": f"p_{self.name_snake}",
            "RestAPI": self.name_camel,
            "GraphQL": self.name_camel,
            "custom": self.name_camel,
        }
        return self.name_variations

    def generate_component_props(self):  # TODO: Needs update
        self.component_props = {
            "subComponent": "default",
            "variant": "default",
            "placeholder": "default",
            "size": "default",
            "textSize": "default",
            "textColor": "default",
            "rows": "default",
            "animation": "default",
            "fullWidthValue": "default",
            "fullWidth": "default",
            "disabled": "default",
            "className": "default",
            "type": "default",
            "onChange": "default",
            "onBlur": "default",
            "formatString": "default",
            "minDate": "default",
            "maxDate": "default",
            "numberType": "default",
        }
        return self.component_props

    def to_reverse_table_lookup_entry(self):
        self.reverse_table_lookup = {self.name_camel: self.name_variations}
        return self.reverse_table_lookup

    def to_reverse_field_name_lookup(self):  # comeback
        self.reverse_field_name_lookup = {self.name_camel: {}}

        for column in self.columns:
            self.reverse_field_name_lookup[self.name_camel].update(column.reverse_column_lookup)

        if self.column_rel_entries:
            self.reverse_field_name_lookup[self.name_camel].update(self.column_rel_entries)

        return self.reverse_field_name_lookup

    def to_schema_entry(self):
        ts_fields = []
        const_ts_fields = []
        json_fields = {}

        for column in self.columns:
            ts_field, json_field = column.to_schema_entry()
            ts_fields.append(ts_field)
            const_ts_fields.append(ts_field)
            json_fields.update(json_field)

        for target_table, relationship in self.get_all_foreign_keys().items():
            ts_fk, json_fk, const_ts_fk = self.to_foreign_key_entry(target_table)
            ts_fields.append(ts_fk)
            const_ts_fields.append(const_ts_fk)
            json_fields.update(json_fk)

        for source_table, relationship in self.get_all_referenced_by().items():
            ts_ifk, json_ifk, const_ts_ifk = self.to_inverse_foreign_key_entry(source_table)
            ts_fields.append(ts_ifk)
            const_ts_fields.append(const_ts_ifk)
            json_fields.update(json_ifk)

        joined_ts_fields = "\n            ".join(ts_fields)
        const_joined_ts_fields = "\n            ".join(const_ts_fields)

        relationship_ts, relationship_json = self.to_schema_structure_entry()
        name_variations = json.dumps(self.generate_name_variations(), indent=4)
        component_props = json.dumps(self.generate_component_props(), indent=4)  # TODO: Needs update

        primary_key_info = self.get_primary_key_metadata()
        primary_key_json = json.dumps(primary_key_info, indent=4)

        entity_structure = (
            f"        schemaType: 'table' as const,\n"
            f"        entityName: '{self.name_camel}',\n"
            f"        displayName: '{self.name_title}',\n"
            f"        uniqueTableId: '{self.unique_table_id}',\n"
            f"        uniqueEntityId: '{self.unique_entity_id}',\n"
            f"        primaryKey: '{self.get_primary_key_field()}',\n"
            f"        primaryKeyMetadata: {primary_key_json},\n"
            f"        displayFieldMetadata: {self.display_ts_field_metadata},\n"
            f"        defaultFetchStrategy: '{self.defaultFetchStrategy}',\n"
            f"        componentProps: {component_props},\n"
            f"        entityFields: {{\n"
            f"            {joined_ts_fields}\n"
            f"        }},\n"
            f"        entityNameFormats: {name_variations},\n"
            f"        relationships: [\n"
            f"            {relationship_ts}\n"
            f"        ],\n"
        )
        const_entity_structure = (
            f"        schemaType: 'table' as const,\n"
            f"        entityName: '{self.name_camel}',\n"
            f"        displayName: '{self.name_title}',\n"
            f"        uniqueTableId: '{self.unique_table_id}',\n"
            f"        uniqueEntityId: '{self.unique_entity_id}',\n"
            f"        primaryKey: '{self.get_primary_key_field()}',\n"
            f"        primaryKeyMetadata: {primary_key_json},\n"
            f"        displayFieldMetadata: {self.display_ts_field_metadata},\n"
            f"        defaultFetchStrategy: '{self.defaultFetchStrategy}',\n"
            f"        componentProps: {component_props},\n"
            f"        entityFields: {{\n"
            f"            {const_joined_ts_fields}\n"
            f"        }},\n"
            f"        entityNameFormats: {name_variations},\n"
            f"        relationships: [\n"
            f"            {relationship_ts}\n"
            f"        ],\n"
        )

        self.ts_structure = f"    {self.name_camel}: {{\n" f"{entity_structure}" f"    }}"

        self.const_ts_structure = f"export const {self.name_camel} = {{\n" f"{const_entity_structure}" f"    }} as const;"

        self.json_structure = {
            self.name_camel: {
                "schemaType": "table",
                "entityName": self.name_camel,
                "uniqueTableId": self.unique_table_id,
                "uniqueEntityId": self.unique_entity_id,
                "primaryKey": self.get_primary_key_field(),
                "primaryKeyMetadata": primary_key_info,
                "displayFieldMetadata": self.display_json_field_metadata,
                "defaultFetchStrategy": self.defaultFetchStrategy,
                "componentProps": self.generate_component_props(),  # TODO: Needs update
                "entityFields": json_fields,
                "entityNameFormats": self.generate_name_variations(),
                "relationships": relationship_json,
            }
        }

        self.finalize_initialization()
        return self.ts_structure, self.json_structure, self.const_ts_structure

    def to_python_foreign_key_field(self, target_table, relationship):
        field_name = self.utils.to_snake_case(f"{target_table}_reference")
        target_model = self.utils.to_pascal_case(target_table)
        return f"{field_name} = ForeignKeyReference(to_model={target_model}, related_name='{self.name}')"

    def to_python_inverse_foreign_key_field(self, source_table, relationship):
        """
        Creates a dictionary for inverse foreign key relationships.
        """
        source_model = self.utils.to_pascal_case(source_table)
        relationship_name = f"{source_table}s"

        return {
            relationship_name: {
                "from_model": source_model,
                "from_field": relationship.column,
                "referenced_field": relationship.foreign_column,
                "related_name": relationship_name,
            }
        }

    def to_python_model(self):
        """
        Builds the Python class model string with dynamic foreign keys.
        """
        py_fields = []
        self.unique_field_types = set()

        # Process regular fields for the model
        for column in self.columns:
            py_field = column.to_python_model_field()
            py_fields.append(py_field)
            self.unique_field_types.add(column.python_field_type)

        # Process inverse foreign keys and collect them
        inverse_foreign_keys = {}
        for source_table, relationship in self.get_all_referenced_by().items():
            ifk_field = self.to_python_inverse_foreign_key_field(source_table, relationship)
            inverse_foreign_keys.update(ifk_field)

        # Add _inverse_foreign_keys to the model fields
        py_fields.append(f"_inverse_foreign_keys = {inverse_foreign_keys}")

        # Join the fields and build the class structure
        joined_py_fields = "\n    ".join(py_fields)
        py_structure = f"class {self.name_pascal}(Model):\n" f"    {joined_py_fields}\n"

        return py_structure

    def to_python_manager_string(self):
        return generate_dto_and_manager(self.name, self.name_pascal)

    def to_dict(self):
        return {
            "oid": self.oid,
            "name": self.name,
            "database_project": self.database_project,
            "unique_table_id": self.unique_table_id,
            "unique_entity_id": self.unique_entity_id,
            "type": self.type,
            "schema": self.schema,
            "database": self.database,
            "owner": self.owner,
            "size_bytes": self.size_bytes,
            "index_size_bytes": self.index_size_bytes,
            "rows": self.rows,
            "last_vacuum": self.last_vacuum,
            "last_analyze": self.last_analyze,
            "description": self.description,
            "estimated_row_count": self.estimated_row_count,
            "total_bytes": self.total_bytes,
            "has_primary_key": self.has_primary_key,
            "index_count": self.index_count,
            "columns": [column.to_dict() for column in self.columns],
            "foreign_keys": {k: v.to_dict() for k, v in self.foreign_keys.items()},
            "referenced_by": {k: v.to_dict() for k, v in self.referenced_by.items()},
            "many_to_many": self.many_to_many,
        }


class View:
    def __init__(
        self,
        oid,
        name,
        type_,
        schema,
        database,
        owner,
        size_bytes,
        description,
        view_definition,
        column_data,
    ):
        self.utils = utils
        self.oid = oid
        self.name = name
        self.type = type_
        self.schema = schema
        self.database = database
        self.owner = owner
        self.size_bytes = size_bytes
        self.description = description
        self.view_definition = view_definition
        self.column_data = column_data
        self.verbose = verbose
        self.debug = debug
        self.initialized = False

        self.name_snake = self.utils.to_snake_case(self.name)
        self.name_camel = self.utils.to_camel_case(self.name)
        self.name_pascal = self.utils.to_pascal_case(self.name)
        self.name_kebab = self.utils.to_kebab_case(self.name)
        self.name_title = self.utils.to_title_case(self.name)

        self.unique_name_lookups = None
        vcprint(
            self.to_dict(),
            title="View initialized",
            pretty=True,
            verbose=self.verbose,
            color="cyan",
        )

    def __repr__(self):
        return f"<View name={self.name}>"

    def initialize_code_generation(self):
        if self.initialized:
            return
        self.generate_unique_name_lookups()
        self.initialized = True

    def generate_unique_name_lookups(self):
        name_variations = {
            self.name,
            self.name_camel,
            self.name_snake,
            self.name_title,
            self.name_pascal,
            self.name_kebab,
            f"p_{self.name_snake}",
        }

        unique_names = set(name_variations)

        formatted_unique_names = {f'"{name}"' if " " in name or "-" in name else name: self.name_camel for name in unique_names}

        self.unique_name_lookups = formatted_unique_names

    def to_dict(self):
        return {
            "oid": self.oid,
            "name": self.name,
            "type": self.type,
            "schema": self.schema,
            "database": self.database,
            "owner": self.owner,
            "size_bytes": self.size_bytes,
            "description": self.description,
            "view_definition": self.view_definition,
            "column_data": self.column_data,
        }


class Schema:
    def __init__(self, name="public", database_project="supabase_automation_matrix"):
        self.utils = utils
        self.code_handler = CodeHandler()
        self.name = name
        self.database_project = database_project
        self.tables = {}
        self.views = {}
        self.relationships = []
        self.verbose = verbose
        self.debug = debug
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
            "export type ExpandRecursively<T> = T extends object\n  ? T extends infer O\n    ? { [K in keyof O]: ExpandRecursively<O[K]> }\n    : never\n  : T;"
        )

        return ts_tables_type, ts_views_type, ts_entities_type

    def generate_primary_key_object(self):
        ts_schema_code_temp_path = "entityPrimaryKeys.ts"
        result = "export const primaryKeys = {\n"

        for table in self.tables.values():
            table_name = table.name_camel  # Assuming `name_camel` gives the camelCase table name
            pk_entry = table.get_primary_key_fields_list()  # Dictionary with frontend and database fields

            # Formatting the frontend and database fields
            frontend_keys = ", ".join(f"'{key}'" for key in pk_entry["frontend_name"])
            database_keys = ", ".join(f"'{key}'" for key in pk_entry["database_name"])

            # Adding the formatted entry for this table
            result += f"  {table_name}: {{\n" f"    frontendFields: [{frontend_keys}],\n" f"    databaseColumns: [{database_keys}],\n" f"  }},\n"

        result += "};\n"

        self.code_handler.save_code_file(ts_schema_code_temp_path, result)

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
        ts_lookup_code_temp_path = "lookupSchema.ts"

        import_lines = self.get_import_statements("lookup_schema_file")

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

            ts_field_name_lookup.append(f"    {table.name_camel}: {table.field_name_lookup_structure},")
            ts_reverse_table_name_lookup.append(f"    {table.name_camel}: {json.dumps(table.reverse_table_lookup[table.name_camel], indent=4)},")
            ts_reverse_field_name_lookup.append(f"    {table.name_camel}: {json.dumps(table.reverse_field_name_lookup[table.name_camel], indent=4)},")

        for view in self.views.values():
            for key, value in view.unique_name_lookups.items():
                ts_view_name_lookup.append(f'    {key}: "{value}",')

        ts_table_name_lookup_code = "\n".join([ts_table_name_lookup_line_1] + ts_table_name_lookup + [ts_common_close])
        ts_field_name_lookup_code = "\n".join([ts_field_name_lookup_line_1] + ts_field_name_lookup + [ts_common_close])
        ts_reverse_table_name_lookup_code = "\n".join([ts_reverse_table_name_lookup_line_1] + ts_reverse_table_name_lookup + [ts_common_close])
        ts_reverse_field_name_lookup_code = "\n".join([ts_reverse_field_name_lookup_line_1] + ts_reverse_field_name_lookup + [ts_common_close])
        ts_view_name_lookup_code = "\n".join([ts_view_name_lookup_line_1] + ts_view_name_lookup + [ts_common_close])

        ts_code_content = (
            f"{import_lines}\n\n"
            f"{ts_table_name_lookup_code}\n\n"
            f"{ts_field_name_lookup_code}\n\n"
            f"{ts_reverse_table_name_lookup_code}\n\n"
            f"{ts_reverse_field_name_lookup_code}\n\n"
            f"{ts_view_name_lookup_code}\n\n"
        )

        self.code_handler.save_code_file(ts_lookup_code_temp_path, ts_code_content)

    def generate_schema_file(self):
        ts_schema_code_temp_path = "initialSchemas.ts"
        file_location = self.get_file_location("schema_file")
        import_line_1 = self.get_import_statements("schema_file")

        ts_individual_table_schemas = "initialTableSchemas.ts"
        ts_individual_file_location = self.get_file_location("table_schema_file")
        ts_individual_import_line_1 = self.get_import_statements("table_schema_file")

        ts_structure, const_structure = self.generate_schema_structure()
        table_schema_structure = self.generate_static_ts_Initial_table_schema()

        # Combine everything into the final schema file content
        ts_code_content = f"{file_location}\n\n" f"{import_line_1}\n\n" f"{ts_structure}\n\n" f"{table_schema_structure}\n\n"

        ts_code_const = f"{ts_individual_file_location}\n\n" f"{ts_individual_import_line_1}\n\n" f"{const_structure}\n\n"

        # Save the schema file
        self.code_handler.save_code_file(ts_schema_code_temp_path, ts_code_content)
        self.code_handler.save_code_file(ts_individual_table_schemas, ts_code_const)

    # Method to generate and save the types file (AutomationSchemaTypes.ts)
    def generate_types_file(self):
        ts_types_code_temp_path = "AutomationSchemaTypes.ts"

        # Get all the components for the types file
        file_location = self.get_file_location("types_file")
        import_line_1 = self.get_import_statements("types_file")
        ts_tables_type, ts_views_type, ts_entities_type = self.generate_typescript_list_tables_and_views()
        data_type_entry = self.generate_data_type()
        data_structure_entry = self.generate_data_structure()
        fetch_strategy_entry = self.generate_fetch_strategy()
        generate_name_formats = self.generate_name_formats()
        automation_dynamic_names = self.generate_automation_dynamic_name()
        automation_custom_names = self.generate_automation_custom_name()
        type_inference_entries = self.generate_type_inference_entries()
        type_brand_util = self.generate_type_brand_util()
        # automation_schema = generate_automation_schema() # Currently not used.

        # Combine everything into the final types file content
        ts_code_content = (
            f"{file_location}\n\n"
            f"{import_line_1}\n\n"
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
            # f"{automation_schema}\n\n"
        )

        # Save the types file
        self.code_handler.save_code_file(ts_types_code_temp_path, ts_code_content)

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
        ts_entity_field_temp_path = "entityFieldNames.ts"
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

        # Convert the entity_field_names dictionary into a TypeScript-compatible string
        entity_field_names_ts = (
            "'use client';\n\n"
            "import { EntityAnyFieldKey, EntityKeys } from '@/types';\n"
            "export type FieldGroups = {\n"
            "    nativeFields: EntityAnyFieldKey<EntityKeys>[];\n"
            "    primaryKeyFields: EntityAnyFieldKey<EntityKeys>[];\n"
            "    nativeFieldsNoPk: EntityAnyFieldKey<EntityKeys>[];\n"
            "};\n\n"
            "export type EntityFieldNameGroupsType = Record<EntityKeys, FieldGroups>;\n\n"
            "export const entityFieldNameGroups: EntityFieldNameGroupsType = " + self.convert_to_typescript(entity_field_names) + ";"
        )

        # Save the TypeScript file
        self.code_handler.save_code_file(ts_entity_field_temp_path, entity_field_names_ts)

        return entity_field_names

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

    def generate_models_old(self):
        py_code_temp_path = "models.py"

        file_location = "# File: database/orm/models.py"
        import_lines = [
            "from database.orm.core.fields import (CharField, TextField, IntegerField, FloatField, BooleanField, DateTimeField, UUIDField, JSONField, DecimalField, BigIntegerField, SmallIntegerField, JSONBField, UUIDArrayField, JSONBArrayField, ForeignKey)",
            "from database.orm.core.registry import model_registry" "from database.orm.core.base import Model",
        ]

        reference_count = defaultdict(int)

        # Step 1: Count how many times each table is referenced by checking referenced_by_relationships
        for table_name, table in self.tables.items():
            # Count how many times this table is referenced by others
            reference_count[table_name] = len(table.referenced_by_relationships)

        # Step 2: Sort tables: those with more references first, those with no references last
        sorted_tables = sorted(
            self.tables.keys(),
            key=lambda table_name: reference_count[table_name],
            reverse=True,
        )

        # Step 3: Generate Python code for each table in sorted order
        py_structure = []
        for table_name in sorted_tables:
            table = self.tables[table_name]
            py_table_entry = table.to_python_model()
            py_structure.append(py_table_entry)

        py_manager_structure = []
        for table_name in sorted_tables:
            table = self.tables[table_name]
            py_manager_entry = table.to_python_manager_string()
            vcprint(py_manager_entry, verbose=self.verbose, color="green")
            py_manager_structure.append(py_manager_entry)

        py_code_content = f"{file_location}\n\n{chr(10).join(import_lines)}\n\n{chr(10).join(py_structure)}\n\n{chr(10).join(py_manager_structure)}"

        self.code_handler.save_code_file(py_code_temp_path, py_code_content)

        return py_code_content

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
        py_code_temp_path = "models.py"

        file_location = "# File: database/orm/models.py"
        import_lines = [
            "from database.orm.core.fields import (CharField, DateField, TextField, IntegerField, FloatField, BooleanField, DateTimeField, UUIDField, JSONField, DecimalField, BigIntegerField, SmallIntegerField, JSONBField, UUIDArrayField, JSONBArrayField, ForeignKey)",
            "from database.orm.core.base import Model",
            "from database.orm.core.registry import model_registry",
            "from recipes.compiled.new_utils import update_content_with_runtime_brokers",
            "from common import vcprint",
            "from dataclasses import dataclass",
            "from database.orm.core.extended import BaseDTO, BaseManager",
            "\n\nverbose = False",
            "debug = False",
            "info = True",
        ]

        reference_count = defaultdict(int)
        for table_name, table in self.tables.items():
            reference_count[table_name] = len(table.referenced_by_relationships)

        # MANUAL OVERRIDE OF TABLE ORDER
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
        for table_name in sorted_tables:
            table = self.tables[table_name]
            py_manager_entry = table.to_python_manager_string()
            py_manager_structure.append(py_manager_entry)

        py_structure.append(self.get_string_model_registry())

        py_code_content = f"{file_location}\n\n{chr(10).join(import_lines)}\n\n{chr(10).join(py_structure)}\n\n{chr(10).join(py_manager_structure)}"

        self.code_handler.save_code_file(py_code_temp_path, py_code_content)

        return py_code_content

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


class SchemaManager:
    def __init__(
        self,
        database="postgres",
        schema="public",
        database_project="supabase_automation_matrix",
        additional_schemas=None,
    ):
        if additional_schemas is None:
            additional_schemas = ["auth"]

        # Ensure utils and Schema are properly imported or defined
        self.utils = utils  # Define or import `utils` properly
        self.database = database
        self.schema = Schema(name=schema, database_project=database_project)  # Define or import `Schema`
        self.additional_schemas = additional_schemas
        self.database_project = database_project
        self.processed_objects = None
        self.full_relationships = None
        self.full_junction_analysis = None
        self.all_enum_base_types = None
        self.overview_analysis = None
        self.frontend_full_relationships = []
        self.initialized = False
        self.verbose = verbose
        self.debug = debug

    def initialize(self):
        """Orchestrates the initialization of the SchemaManager."""
        self.set_all_schema_data()
        self.load_objects()
        self.load_table_relationships()
        self.initialized = True
        self.analyze_schema()
        self.get_full_relationship_analysis()

    def set_all_schema_data(self):
        (
            self.processed_objects,
            self.full_relationships,
            self.full_junction_analysis,
            self.all_enum_base_types,
            self.overview_analysis,
        ) = get_db_objects(self.schema.name, self.database_project)

        self.utils.set_and_update_ts_enum_list(self.all_enum_base_types)

        vcprint(
            self.full_relationships,
            title="Full relationships",
            pretty=True,
            verbose=self.verbose,
            color="yellow",
        )
        vcprint(
            self.processed_objects,
            title="Processed objects",
            pretty=True,
            verbose=self.verbose,
            color="green",
        )
        vcprint(
            self.overview_analysis,
            title="Relationship Overview analysis",
            pretty=True,
            verbose=self.verbose,
            color="green",
        )

    def load_objects(self):
        """Loads all database objects (tables and views) into the schema."""
        vcprint(
            f"Loaded {len(self.processed_objects)} objects from {self.database_project}.",
            verbose=self.verbose,
            color="blue",
        )

        for obj in self.processed_objects:
            if obj["type"] == "table":
                self.load_table(obj)
            elif obj["type"] == "view":
                self.load_view(obj)

        self.schema.add_all_table_instances()

        vcprint(
            f"Loaded {len(self.schema.tables)} tables.",
            verbose=self.verbose,
            color="blue",
        )
        vcprint(
            f"Loaded {len(self.schema.views)} views.",
            verbose=self.verbose,
            color="green",
        )

    def load_table(self, obj):
        table = Table(
            oid=obj["oid"],
            database_project=obj["database_project"],
            unique_table_id=obj["unique_table_id"],
            name=obj["name"],
            type_=obj["type"],
            schema=obj["schema"],
            database=obj["database"],
            owner=obj["owner"],
            size_bytes=obj["size_bytes"],
            index_size_bytes=obj["index_size_bytes"],
            rows=obj["rows"],
            last_vacuum=obj["last_vacuum"],
            last_analyze=obj["last_analyze"],
            description=obj["description"],
            estimated_row_count=obj["estimated_row_count"],
            total_bytes=obj["total_bytes"],
            has_primary_key=obj["has_primary_key"],
            index_count=obj["index_count"],
            columns=obj["table_columns"],
            junction_analysis_ts=obj["junction_analysis_ts"],
        )
        self.schema.add_table(table)

    def load_view(self, obj):
        view = View(
            oid=obj["oid"],
            name=obj["name"],
            # database_project=self.database_project,
            type_=obj["type"],
            schema=obj["schema"],
            database=obj["database"],
            owner=obj["owner"],
            size_bytes=obj["size_bytes"],
            description=obj["description"],
            view_definition=obj["view_definition"],
            column_data=obj["columns"],
        )
        self.schema.add_view(view)

    def load_table_relationships(self):
        """Loads relationship information for tables."""

        # Remove self-references from referenced_by
        for table_data in self.full_relationships:
            if table_data["referenced_by"] and table_data["referenced_by"] != "None":
                table_data["referenced_by"].pop(table_data["table_name"], None)

        for table_data in self.full_relationships:
            table_name = table_data["table_name"]
            table = self.schema.get_table(table_name)
            if table:
                # Process foreign keys
                if table_data["foreign_keys"] and table_data["foreign_keys"] != "None":
                    for target_table_name, fk_data in table_data["foreign_keys"].items():
                        target_table_instance = self.schema.get_table(target_table_name)
                        relationship = Relationship(
                            fk_data["constraint_name"],
                            fk_data["column"],
                            fk_data["foreign_column"],
                            target_table=target_table_instance,
                            source_table=table,
                        )
                        # Important: Use table_name as key to maintain backward compatibility
                        table.add_foreign_key(target_table_name, relationship)

                # Process referenced_by
                if table_data["referenced_by"] and table_data["referenced_by"] != "None":
                    for source_table_name, ref_data in table_data["referenced_by"].items():
                        source_table_instance = self.schema.get_table(source_table_name)
                        relationship = Relationship(
                            ref_data["constraint_name"],
                            ref_data["column"],
                            ref_data["foreign_column"],
                            target_table=table,
                            source_table=source_table_instance,
                        )
                        # Important: Use table_name as key to maintain backward compatibility
                        table.add_referenced_by(source_table_name, relationship)

        # Detect many-to-many relationships
        self.detect_many_to_many_relationships()
        if self.verbose:
            vcprint(
                f"Loaded relationships for {len(self.full_relationships)} tables.",
                color="green",
            )

    def detect_many_to_many_relationships(self):
        """Detects and sets many-to-many relationships."""
        for table in self.schema.tables.values():
            if len(table.foreign_keys) == 2 and len(table.referenced_by) == 0:
                related_tables = list(table.foreign_keys.keys())
                for related_table_name in related_tables:
                    related_table = self.schema.get_table(related_table_name)
                    if related_table:
                        other_table = self.schema.get_table(related_tables[1] if related_tables[0] == related_table_name else related_tables[0])
                        if other_table:
                            related_table.add_many_to_many(table, other_table)
                            table.add_many_to_many(table, other_table)

    def analyze_relationships(self):
        """Analyzes relationships in the schema."""
        analysis = {
            "tables_with_foreign_keys": sum(1 for table in self.schema.tables.values() if table.foreign_keys),
            "tables_referenced_by_others": sum(1 for table in self.schema.tables.values() if table.referenced_by),
            "many_to_many_relationships": sum(len(table.many_to_many) for table in self.schema.tables.values()) // 2,
            "most_referenced_tables": sorted(
                [(table.name, len(table.referenced_by)) for table in self.schema.tables.values()],
                key=lambda x: x[1],
                reverse=True,
            )[:5],
        }
        return analysis

    def get_table(self, table_name):
        """Returns a specific table."""
        return self.schema.get_table(table_name)

    def get_view(self, view_name):
        """Returns a specific view."""
        return self.schema.get_view(view_name)

    def get_column(self, table_name, column_name):
        """Returns a specific column."""
        table = self.get_table(table_name)
        if table:
            for column in table.columns:
                if column.name == column_name:
                    return column
        return None

    def get_related_tables(self, table_name):
        """Returns tables related to a specific table."""
        return self.schema.get_related_tables(table_name)

    def get_all_tables(self):
        """Returns all tables."""
        return list(self.schema.tables.values())

    def get_all_views(self):
        """Returns all views."""
        return list(self.schema.views.values())

    def analyze_schema(self):
        """Performs a comprehensive analysis of the schema."""
        table_fetch_strategy = {}  # A dictionary of fetch strategies with their corresponding tables
        primary_key_count = 0
        tables_with_fk = 0
        tables_with_ifk = 0
        tables_with_m2m = 0
        no_primary_key_tables = []
        column_type_count = {}
        unique_column_types = set()
        default_component_count = {}
        calc_validation_functions_count = {}
        calc_exclusion_rules_count = {}
        sub_component_props_count = {}
        estimated_row_counts = {}
        foreign_key_relationships_total = 0
        referenced_by_relationships_total = 0
        many_to_many_relationships_total = 0

        for table in self.schema.tables.values():
            # Fetch strategy analysis
            strategy = table.schema_structure.get("defaultFetchStrategy", "simple")
            if strategy == "simple":
                table_fetch_strategy["simple"] = table_fetch_strategy.get("simple", 0) + 1
            else:
                if strategy not in table_fetch_strategy:
                    table_fetch_strategy[strategy] = []
                table_fetch_strategy[strategy].append(table.name)

            # Count tables with primary keys
            if table.has_primary_key:
                primary_key_count += 1
            else:
                no_primary_key_tables.append(table.name)

            # Count tables with foreign keys
            if table.foreign_keys:
                tables_with_fk += 1

            # Count tables with inverse foreign keys
            if table.referenced_by:
                tables_with_ifk += 1

            # Count tables with many-to-many relationships
            if table.many_to_many:
                tables_with_m2m += 1

            # Total relationships
            foreign_key_relationships_total += len(table.foreign_key_relationships)
            referenced_by_relationships_total += len(table.referenced_by_relationships)
            many_to_many_relationships_total += len(table.many_to_many_relationships)

            # Estimated row count
            estimated_row_counts[table.name] = table.estimated_row_count

            # Analyze column data
            for column in table.columns:
                col_type = column.base_type
                column_type_count[col_type] = column_type_count.get(col_type, 0) + 1
                unique_column_types.add(col_type)

                if column.default_component:
                    default_component_count[column.default_component] = default_component_count.get(column.default_component, 0) + 1

                if "typescript" in column.calc_validation_functions:
                    validation_function = column.calc_validation_functions["typescript"]
                    calc_validation_functions_count[validation_function] = calc_validation_functions_count.get(validation_function, 0) + 1

                if "typescript" in column.calc_exclusion_rules:
                    exclusion_rule = column.calc_exclusion_rules["typescript"]
                    calc_exclusion_rules_count[exclusion_rule] = calc_exclusion_rules_count.get(exclusion_rule, 0) + 1

                if "sub_component" in column.component_props:
                    sub_component = column.component_props["sub_component"]
                    sub_component_props_count[sub_component] = sub_component_props_count.get(sub_component, 0) + 1

        # General analysis summary
        analysis = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "table_count": len(self.schema.tables),
            "view_count": len(self.schema.views),
            "tables_with_primary_key": primary_key_count,
            "tables_without_primary_key": len(no_primary_key_tables),
            "no_primary_key_tables": no_primary_key_tables,
            "total_columns": sum(len(table.columns) for table in self.schema.tables.values()),
            "unique_column_types": list(unique_column_types - set(self.all_enum_base_types)),  # Exclude enums
            "most_common_column_types": dict(sorted(column_type_count.items(), key=lambda item: item[1], reverse=True)[:10]),
            "all_enum_base_types": list(self.all_enum_base_types),
            "tables_by_size": sorted(self.schema.tables.values(), key=lambda t: t.size_bytes, reverse=True)[:5],
            "views_by_size": sorted(self.schema.views.values(), key=lambda v: v.size_bytes, reverse=True)[:5],
            "fetch_strategies": table_fetch_strategy,
            "tables_with_foreign_keys": tables_with_fk,
            "tables_with_inverse_foreign_keys": tables_with_ifk,
            "tables_with_many_to_many": tables_with_m2m,
            "default_component_count": default_component_count,
            "calc_validation_functions_count": calc_validation_functions_count,
            "calc_exclusion_rules_count": calc_exclusion_rules_count,
            "sub_component_props_count": sub_component_props_count,
            "estimated_row_counts": dict(sorted(estimated_row_counts.items(), key=lambda x: x[1], reverse=True)),
            "foreign_key_relationships_total": foreign_key_relationships_total,
            "referenced_by_relationships_total": referenced_by_relationships_total,
            "many_to_many_relationships_total": many_to_many_relationships_total,
            "database_table_names": [table.name for table in self.schema.tables.values()],
            "database_view_names": [view.name for view in self.schema.views.values()],
            "allEntities": [table.name_camel for table in self.schema.tables.values()],
        }
        self.schema.save_analysis_json(analysis)
        return analysis

    def get_table_instance(self, table_name):
        return self.schema.tables[table_name] if table_name in self.schema.tables else None

    def get_view_instance(self, view_name):
        return self.schema.views[view_name] if view_name in self.schema.views else None

    def get_column_instance(self, table_name, column_name):
        return self.schema.tables[table_name].columns[column_name] if table_name in self.schema.tables and column_name in self.schema.tables[table_name].columns else None

    def get_table_frontend_name(self, table_name):
        return self.get_table_instance(table_name).name_camel if table_name in self.schema.tables else table_name

    def get_view_frontend_name(self, view_name):
        return self.get_view_instance(view_name).name_camel if view_name in self.schema.views else view_name

    def get_column_frontend_name(self, table_name, column_name):
        return (
            self.get_column_instance(table_name, column_name).name_camel
            if table_name in self.schema.tables and column_name in self.schema.tables[table_name].columns
            else self.utils.to_camel_case(column_name)
        )

    def transform_foreign_keys(self, main_table_name, entry):
        if not entry:
            return {}
        transformed = {}
        for key, fk_data in (entry.get("foreign_keys") or {}).items():
            transformed[self.get_table_frontend_name(key)] = {
                "foreign_table": key,
                "foreign_entity": self.get_table_frontend_name(key),
                "column": fk_data["column"],
                "fieldName": self.get_column_frontend_name(main_table_name, fk_data["column"]),
                "foreign_field": self.get_column_frontend_name(key, fk_data["foreign_column"]),
                "foreign_column": fk_data["foreign_column"],
                "relationship_type": fk_data["relationship_type"],
                "constraint_name": fk_data["constraint_name"],
            }

        vcprint(
            transformed,
            title="Transformed Foreign Keys",
            verbose=debug,
            pretty=True,
            color="yellow",
        )
        return transformed

    def transform_referenced_by(self, table_name, entry):
        if not entry:
            return {}
        transformed = {}
        for key, ref_data in (entry.get("referenced_by") or {}).items():
            transformed[self.get_table_frontend_name(key)] = {
                "foreign_table": key,
                "foreign_entity": self.get_table_frontend_name(key),
                "field": self.get_column_frontend_name(key, ref_data["column"]),
                "column": ref_data["column"],
                "foreign_field": self.get_column_frontend_name(table_name, ref_data["foreign_column"]),
                "foreign_column": ref_data["foreign_column"],
                "constraint_name": ref_data["constraint_name"],
            }
        return transformed

    def get_frontend_full_relationships(self):
        self.frontend_full_relationships = []

        for info_object in self.full_relationships:
            database_table = info_object["table_name"]
            entity_name = self.get_table_frontend_name(database_table)

            transformed_foreign_keys = self.transform_foreign_keys(database_table, info_object)
            transformed_referenced_by = self.transform_referenced_by(database_table, info_object)

            updated_relationship = {
                "entityName": entity_name,
                "table_name": database_table,
                "foreignKeys": transformed_foreign_keys,
                "referencedBy": transformed_referenced_by,
            }
            self.frontend_full_relationships.append(updated_relationship)

        vcprint(
            self.frontend_full_relationships,
            title="Frontend Full Relationships",
            pretty=True,
            verbose=self.verbose,
            color="yellow",
        )
        return self.frontend_full_relationships

    def get_full_relationship_analysis(self):
        frontend_relationships = self.get_frontend_full_relationships()
        relationship_details = {rel["table_name"]: rel for rel in frontend_relationships}

        self.full_relationship_analysis = {}

        for table_name, analysis in self.overview_analysis.items():
            frontend_name = self.get_table_frontend_name(table_name)

            transformed_analysis = {
                "selfReferential": [self.get_table_frontend_name(name) for name in analysis["self-referential"]],
                "manyToMany": [self.get_table_frontend_name(name) for name in analysis["many-to-many"]],
                "oneToOne": [self.get_table_frontend_name(name) for name in analysis["one-to-one"]],
                "manyToOne": [self.get_table_frontend_name(name) for name in analysis["many-to-one"]],
                "oneToMany": [self.get_table_frontend_name(name) for name in analysis["one-to-many"]],
                "undefined": [self.get_table_frontend_name(name) for name in analysis["undefined"]],
                "inverseReferences": [self.get_table_frontend_name(name) for name in analysis["inverse_references"]],
                "relationshipDetails": relationship_details.get(table_name, {}),
            }

            self.full_relationship_analysis[frontend_name] = transformed_analysis

        self.schema.save_frontend_full_relationships_json(self.full_relationship_analysis)

        ts_types_string = get_relationship_data_model_types()

        ts_code_content = self.utils.python_dict_to_ts_with_updates(
            name="entityRelationships",
            obj=self.full_relationship_analysis,
            keys_to_camel=True,
            export=True,
            as_const=True,
            ts_type=None,
        )

        ts_code_content = ts_types_string + ts_code_content
        self.schema.code_handler.save_code_file("fullRelationships.ts", ts_code_content)

        vcprint(
            self.full_relationship_analysis,
            title="Full Relationship Analysis",
            pretty=True,
            verbose=self.verbose,
            color="blue",
        )

    def get_frontend_junction_analysis(self):
        frontend_junction_analysis = {}

        for table_key, table_value in self.full_junction_analysis.items():
            table_instance = self.schema.tables.get(table_key)
            entity_name = table_instance.name_camel if table_instance else table_key

            updated_table = {
                "entityName": entity_name,
                "schema": table_value["schema"],
                "connectedTables": [],
                "additionalFields": [],
            }

            for connected_table in table_value["connected_tables"]:
                connected_instance = self.schema.tables.get(connected_table["table"])
                updated_table["connectedTables"].append(
                    {
                        "schema": connected_table["schema"],
                        "entity": connected_instance.name_camel if connected_instance else connected_table["table"],
                        "connectingColumn": self.schema.tables[table_key].columns[connected_table["connecting_column"]].name_camel
                        if table_instance and connected_table["connecting_column"] in table_instance.columns
                        else connected_table["connecting_column"],
                        "referencedColumn": connected_instance.columns[connected_table["referenced_column"]].name_camel
                        if connected_instance and connected_table["referenced_column"] in connected_instance.columns
                        else connected_table["referenced_column"],
                    }
                )

            for field in table_value["additional_fields"]:
                field_instance = table_instance.columns.get(field) if table_instance else None
                updated_table["additionalFields"].append(field_instance.name_camel if field_instance else field)

            frontend_junction_analysis[entity_name] = updated_table

        self.schema.save_frontend_junction_analysis_json(frontend_junction_analysis)
        return frontend_junction_analysis

    def __repr__(self):
        return f"<SchemaManager database={self.database}, schema={self.schema.name}, initialized={self.initialized}>"


def generate_schema_structure(schema_manager, table_name):
    """
    Generates the schema structure with defaultFetchStrategy, foreignKeys, inverseForeignKeys, and manyToMany relationships.

    :param schema_manager: The schema manager object that holds the schema details
    :param table_name: The name of the table for which the schema is being generated
    :return: A dictionary representing the schema structure
    """
    table = schema_manager.get_table(table_name)

    if not table:
        print(f"Table '{table_name}' not found.")
        return None

    schema_structure = {
        "defaultFetchStrategy": None,  # This will be determined based on the relationships present
        "foreignKeys": [],  # List of foreign key relationships
        "inverseForeignKeys": [],  # List of tables that reference the current table
        "manyToMany": [],  # List of many-to-many relationships
    }

    # Populate foreign keys
    if table.foreign_keys:
        for target, rel in table.foreign_keys.items():
            schema_structure["foreignKeys"].append(
                {
                    "column": rel.local_column,  # Assuming local_column holds the FK column in the current table
                    "relatedTable": target,  # Target is the related table name
                    "relatedColumn": rel.related_column,  # Assuming related_column is the column in the target table
                }
            )

    # Populate inverse foreign keys (tables that reference this table)
    if table.referenced_by:
        for source, rel in table.referenced_by.items():
            schema_structure["inverseForeignKeys"].append(
                {
                    "relatedTable": source,  # Source is the table that references the current table
                    "relatedColumn": rel.local_column,  # Assuming local_column holds the FK column in the source table
                }
            )

    # Populate many-to-many relationships
    if table.many_to_many:
        for mm in table.many_to_many:
            schema_structure["manyToMany"].append(
                {
                    "relatedTable": mm["related_table"],  # The related table
                    "junctionTable": mm["junction_table"],  # The junction table that joins the two tables
                    "localColumn": mm["local_column"],  # Column in the junction table for the current table
                    "relatedColumn": mm["related_column"],  # Column in the junction table for the related table
                }
            )

    # Determine fetch strategy based on available relationships
    if schema_structure["manyToMany"]:
        schema_structure["defaultFetchStrategy"] = "m2m"
    elif schema_structure["foreignKeys"] and schema_structure["inverseForeignKeys"]:
        schema_structure["defaultFetchStrategy"] = "fkAndIfk"
    elif schema_structure["foreignKeys"]:
        schema_structure["defaultFetchStrategy"] = "fk"
    elif schema_structure["inverseForeignKeys"]:
        schema_structure["defaultFetchStrategy"] = "ifk"
    else:
        schema_structure["defaultFetchStrategy"] = "simple"  # No relationships, basic fetch

    return schema_structure


def example_usage(schema_manager):
    table = schema_manager.get_table("flashcard_data")
    print()
    if table:
        vcprint(f"Table: {table.name}")
        vcprint("Foreign Keys:")
        for target, rel in table.foreign_keys.items():
            vcprint(f"  - {target}: {rel}")
        vcprint("Referenced By:")
        for source, rel in table.referenced_by.items():
            vcprint(f"  - {source}: {rel}")
        vcprint("Many-to-Many Relationships:")
        for mm in table.many_to_many:
            vcprint(f"  - {mm['related_table']} (via {mm['junction_table']})")

    example_column = schema_manager.get_column("flashcard_data", "id").to_dict()
    vcprint(
        example_column,
        title="Flashcard ID Column",
        pretty=True,
        verbose=verbose,
        color="cyan",
    )

    example_view = schema_manager.get_view("view_registered_function_all_rels").to_dict()
    vcprint(
        example_view,
        title="Full Registered Function View",
        pretty=True,
        verbose=verbose,
        color="yellow",
    )

    example_table = schema_manager.get_table("registered_function").to_dict()
    vcprint(
        example_table,
        title="Flashcard History Table",
        pretty=True,
        verbose=verbose,
        color="cyan",
    )

    # full_schema = schema_manager.schema.to_dict()
    # vcprint(full_schema, title="Full Schema", pretty=True, verbose=verbose, color="cyan")


def get_full_schema_object(schema, database_project):
    schema_manager = SchemaManager(schema=schema, database_project=database_project)
    schema_manager.initialize()
    matrx_schema_entry = schema_manager.schema.generate_schema_files()
    matrx_models = schema_manager.schema.generate_models()
    analysis = schema_manager.analyze_schema()

    full_schema_object = {
        "schema": matrx_schema_entry,
        "models": matrx_models,
        "analysis": analysis,
    }
    return full_schema_object


def clear_terminal():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


if __name__ == "__main__":
    clear_terminal()

    schema = "public"
    database_project = "supabase_automation_matrix"
    # database_project = "supabase_matrix_django"
    additional_schemas = ["auth"]

    schema_manager = SchemaManager(
        schema=schema,
        database_project=database_project,
        additional_schemas=additional_schemas,
    )
    schema_manager.initialize()

    # Claude with some familiarity with the structure, especially the json: https://claude.ai/chat/05e6e654-2574-4cdf-9f26-61f6a26ad631
    # Potential Additions: https://claude.ai/chat/e26ff11e-0cd5-46a5-b281-cfa359ed1fcd

    # example_usage(schema_manager)

    # # Access tables, views, or columns as needed
    # vcprint(schema_manager.schema.tables, title="Tables", pretty=True, verbose=verbose, color="blue")
    # vcprint(schema_manager.schema.views, title="Views", pretty=True, verbose=verbose, color="green")
    #
    # # Example: Get a specific table and its columns
    # table = schema_manager.get_table('flashcard_history').to_dict()
    # vcprint(table, title="Flashcard History Table", pretty=True, verbose=verbose, color="cyan")

    matrx_schema_entry = schema_manager.schema.generate_schema_files()

    matrx_models = schema_manager.schema.generate_models()

    # # Example: Get a specific column from a table
    # column = schema_manager.get_column('flashcard_history', 'id').to_dict()
    # vcprint(column, title="Flashcard ID Column", pretty=True, verbose=verbose, color="magenta")
    #
    # # Example: Get a specific view...
    # view = schema_manager.get_view('view_registered_function_all_rels').to_dict()
    # vcprint(view, title="Full Registered Function View", pretty=True, verbose=verbose, color="yellow")
    #
    analysis = schema_manager.analyze_schema()
    vcprint(
        data=analysis,
        title="Schema Analysis",
        pretty=True,
        verbose=False,
        color="yellow",
    )
    #
    # relationship_analysis = schema_manager.analyze_relationships()
    # vcprint(data=relationship_analysis, title="Relationship Analysis", pretty=True, verbose=True, color="green")
    #
    # related_tables = schema_manager.schema.get_related_tables("flashcard_data")
    # vcprint(f"Tables related to 'flashcard_data': {related_tables}", verbose=verbose, color="cyan")
    #
    schema_manager.schema.code_handler.print_all_batched()

    # Not sure exactly what this is returning so we'll need to make updates for it to return the full data we need for react.
    # full_schema_object = get_full_schema_object(schema, database_project)
    # vcprint(full_schema_object, title="Full Schema Object", pretty=True, verbose=True, color="cyan")
