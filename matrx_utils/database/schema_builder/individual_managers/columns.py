import ast
import json
from matrx_utils.common import vcprint
from matrx_utils.database.schema_builder.individual_managers.common import (
    DEBUG_SETTINGS,
    schema_builder_verbose,
    schema_builder_debug,
    schema_builder_info,
    schema_builder_utils,
)
from matrx_utils.database.constants import get_default_component_props
import keyword
import re


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
        parent_table_instance,
        is_display_field=False,
    ):
        self.utils = schema_builder_utils
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
        self.parent_table_instance = parent_table_instance
        self.is_display_field = is_display_field
        self.has_enum_labels = True if self.enum_labels else False

        self.verbose = schema_builder_verbose
        self.debug = schema_builder_debug
        self.info = schema_builder_info

        self.pre_initialized = False
        self.initialized = False

        self.initit_level_1()

        self.is_debug = False
        if self.parent_table_instance.is_debug:
            if self.name in DEBUG_SETTINGS["columns"]:
                self.is_debug = True

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

        self.pre_initialize()

        self.table_name_camel = self.utils.to_camel_case(self.table_name)

        self.default_component = "INPUT"
        self.default_component_priority = -1
        self.component_props = get_default_component_props()
        self.component_props_priorities = {key: -1 for key in self.component_props}

        self.is_required = "true" if not self.nullable else "false"

        self.ts_full_schema_entry = None
        self.ts_simple_schema_entry = None
        self.ts_field_lookup_entry = None

        self.py_enum_entry = None

        self.json_schema_entry = {}
        self.py_field_entry = None

        self.initialization_attempts = 0

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

    def initit_level_1(self):
        self.generate_core_name_variations()

    def initit_level_2(self):
        pass

    def initit_level_3(self):
        pass

    def initit_level_4(self):
        pass

    def initit_level_5(self):
        pass

    def initit_level_6(self):
        pass

    def generate_core_name_variations(self):
        self.name_snake = self.utils.to_snake_case(self.name)
        self.name_snake = self.utils.to_snake_case(self.name)
        self.name_camel = self.utils.to_camel_case(self.name)
        self.name_pascal = self.utils.to_pascal_case(self.name)
        self.name_kebab = self.utils.to_kebab_case(self.name)
        self.name_title = self.utils.to_title_case(self.name)

    def pre_initialize(self):
        if self.pre_initialized:
            return

        if not self.parent_table_instance.pre_initialized:
            self.parent_table_instance.pre_initialize()

        self.generate_basic_info()

        self.pre_initialized = True

    def generate_basic_info(self):
        self.table_python_model_name = self.parent_table_instance.python_model_name
        self.table_ts_entity_name = self.parent_table_instance.ts_entity_name
        self.table_react_component_name = self.parent_table_instance.react_component_name
        self.set_python_enum_entry()

    def initialize_code_generation(self):
        self.initialization_attempts += 1
        if self.is_debug:
            print(f"---------------- Initializing Column Attempt {self.table_name} {self.name}: {self.initialization_attempts} ----------------")

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
        self.set_is_default_filter_field()
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

    def set_is_default_filter_field(self):
        self.is_default_filter_field = False

        if self.is_display_field:
            self.is_default_filter_field = True
        if self.has_enum_labels:
            self.is_default_filter_field = True
        if self.foreign_key_reference:
            self.is_default_filter_field = True
        if self.is_array:
            self.is_default_filter_field = True

    def set_python_enum_entry(self):
        if self.enum_labels:
            type_name = self.utils.to_pascal_case(self.base_type)

            py_enum_entries = []
            for label in self.enum_labels:
                # Convert label to a valid Python identifier
                valid_label = re.sub(r"\W+", "_", label)  # Replace non-alphanumeric chars with _
                valid_label = valid_label.upper()

                # Prevent leading numbers
                if valid_label[0].isdigit():
                    valid_label = f"_{valid_label}"

                # Handle Python reserved keywords
                if keyword.iskeyword(valid_label):
                    valid_label += "_"

                py_enum_entry = f'{valid_label} = "{label}"'
                py_enum_entries.append(py_enum_entry)

            py_enum_entries_string = "\n    ".join(py_enum_entries)

            self.py_enum_entry = f"class {type_name}(str, Enum):\n    {py_enum_entries_string}"
        else:
            self.py_enum_entry = None

        return self.py_enum_entry

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

        elif self.full_type == "character varying(100)":
            self.update_component(component="INPUT", priority=3)
            self.update_prop(prop="subComponent", value="default", priority=1)

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

    def to_typescript_type_entry(self):
        if self.nullable:
            self.ts_type_entry = f"    {self.name_camel}?: {self.type_reference['typescript']};"
        else:
            self.ts_type_entry = f"    {self.name_camel}: {self.type_reference['typescript']};"

        return self.ts_type_entry

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


            # Handle plain integer values for integer columns
            if isinstance(value, (int, str)) and self.full_type in ["integer", "int4"]:
                try:
                    int_value = int(value)  # Ensure it's a valid integer
                    return callable_outcomes["::integer"](f"'{int_value}'::integer")
                except ValueError:
                    pass  # Not a valid integer, fall through

            # Default case for unhandled values
            vcprint(f"Table Name: {self.table_name}", color="yellow")
            vcprint(f"Value: {value}", color="yellow")
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
                    if python_default == "false":  # Existing fix for 'false'
                        field_options.append("default=False")
                    elif python_default == "true":  # New surgical fix for 'true'
                        field_options.append("default=True")
                    else:
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
        elif self.has_enum_labels:
            enum_class = self.utils.to_pascal_case(self.base_type)
            field_def = f"{self.name} = EnumField(enum_class={enum_class}, {options_str})"
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
