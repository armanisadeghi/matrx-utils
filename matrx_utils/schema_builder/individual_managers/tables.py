# matrx_utils\schema_builder\individual_managers\tables.py
import json
from matrx_utils import vcprint
from matrx_utils.schema_builder.helpers.configs import MANAGER_CONFIG_OVERRIDES
from matrx_utils.schema_builder.helpers.manager_dto_creator import generate_manager_class
from matrx_utils.schema_builder.individual_managers.columns import Column
from matrx_utils.schema_builder.individual_managers.common import (
    DEBUG_SETTINGS,
    schema_builder_verbose,
    schema_builder_debug,
    schema_builder_info,
    schema_builder_utils,
)
from matrx_utils.schema_builder.helpers.manager_helpers import generate_dto_and_manager


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
        table_columns=None,
        junction_analysis_ts=None,
    ):
        self.utils = schema_builder_utils

        self.pre_initialized = False
        self.initialized = False

        self.is_debug = False
        if name in DEBUG_SETTINGS["tables"]:
            self.is_debug = True

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
        self.junction_analysis_ts = junction_analysis_ts

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

        self.python_model_name = None

        self.verbose = schema_builder_verbose
        self.debug = schema_builder_debug
        self.info = schema_builder_info

        self.name_snake = self.utils.to_snake_case(self.name)
        self.name_camel = self.utils.to_camel_case(self.name)
        self.name_pascal = self.utils.to_pascal_case(self.name)
        self.name_kebab = self.utils.to_kebab_case(self.name)
        self.name_title = self.utils.to_title_case(self.name)
        self.name_plural = self.utils.to_plural(self.name)

        self.unique_entity_id = f"{self.database_project}:{self.name_camel}"

        self.py_fields = []
        self.unique_field_types = set()
        self.unique_name_lookups = ""
        self.column_rel_entries = {}  # Temp solution to get fk/ifk for reverse field lookup
        self.Field_name_groups = {}

        self.columns = [Column(**col, parent_table_instance=self) for col in (table_columns or [])]

        self.identify_display_column()

        self.pre_initialize()

        vcprint(self.junction_analysis_ts, pretty=True, verbose=self.verbose, color="blue")
        vcprint(
            self.to_dict(),
            title="Table initialized",
            pretty=True,
            verbose=self.verbose,
            color="cyan",
        )

    def pre_initialize(self):
        if self.pre_initialized:
            return

        self.generate_basic_info()

        self.pre_initialized = True

    def generate_basic_info(self):
        self.python_model_name = f"{self.name_pascal}"
        self.ts_entity_name = self.name_camel
        self.react_component_name = self.name_pascal

    # ============= Commented out because I don't think it's used ===============
    # def add_column(self, column_data):
    #     column = Column(**column_data)
    #     column.initialize_code_generation()
    #     self.columns.append(column)

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

    def get_all_relations(self):
        fks = self.foreign_keys
        ifks = self.referenced_by
        relations = {**fks, **ifks}
        return relations

    def get_all_relations_list(self):
        relations = self.get_all_relations()
        return list(relations.keys())

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
        lookup_structure = "{\n"

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

    def to_typescript_type_entry(self):
        self.ts_type_entry = f"export type {self.name_pascal} = {{\n" + "\n".join([column.to_typescript_type_entry() for column in self.columns]) + "\n}\n"
        return self.ts_type_entry

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
            "component": self.react_component_name,
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
        py_enum_classes = []
        seen_enum_names = set()  # Track unique enum names

        # Process regular fields for the model
        for column in self.columns:
            py_field = column.to_python_model_field()
            py_fields.append(py_field)
            self.unique_field_types.add(column.python_field_type)

            if column.has_enum_labels:
                py_enum_entry = column.set_python_enum_entry()
                enum_name = self.utils.to_pascal_case(column.base_type)  # Extract enum class name

                if py_enum_entry and enum_name not in seen_enum_names:  # Only add unique enums
                    py_enum_classes.append(py_enum_entry)
                    seen_enum_names.add(enum_name)  # Mark this enum as added

        # Process inverse foreign keys and collect them
        inverse_foreign_keys = {}
        for source_table, relationship in self.get_all_referenced_by().items():
            ifk_field = self.to_python_inverse_foreign_key_field(source_table, relationship)
            inverse_foreign_keys.update(ifk_field)

        # Add _inverse_foreign_keys to the model fields
        py_fields.append(f"_inverse_foreign_keys = {inverse_foreign_keys}")

        if py_enum_classes:
            enum_string = "\n\n".join(py_enum_classes)
            enum_entry = f"\n\n{enum_string}\n\n"
        else:
            enum_entry = ""

        # Join the fields and build the class structure
        joined_py_fields = "\n    ".join(py_fields)
        py_structure = f"{enum_entry}class {self.python_model_name}(Model):\n    {joined_py_fields}\n"

        return py_structure

    def to_python_manager_string(self):
        relations = self.get_all_relations_list()
        filter_fields = [column.name for column in self.columns if column.is_default_filter_field]

        # Default configuration with all options explicitly set
        base_config = {
            "model_pascal": self.python_model_name,
            "model_name": self.name,
            "model_name_plural": self.name_plural,
            "model_name_snake": self.name_snake,
            "relations": relations,
            "filter_fields": filter_fields,
            "include_core_relations": True,
            "include_active_relations": False,
            "include_filter_fields": True,
            "include_active_methods": False,
            "include_or_not_methods": False,
            "include_to_dict_methods": False,
            "include_to_dict_relations": False,
        }

        # Apply overrides if they exist
        if self.name in MANAGER_CONFIG_OVERRIDES:
            model_overrides = MANAGER_CONFIG_OVERRIDES[self.name]
            base_config.update(model_overrides)

        self.base_class_auto_config = base_config
        self.model_base_class_str = generate_manager_class(**self.base_class_auto_config)

        return generate_dto_and_manager(self.name, self.python_model_name)

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
