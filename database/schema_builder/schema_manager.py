from datetime import datetime
import os
from common import vcprint

from database.schema_builder.individual_managers.common import schema_builder_verbose, schema_builder_debug, \
    schema_builder_info, schema_builder_utils
from database.schema_builder.individual_managers.schema import Schema
from database.schema_builder.individual_managers.tables import Table
from database.schema_builder.individual_managers.views import View
from database.schema_builder.individual_managers.relationships import Relationship

from database.constants import get_relationship_data_model_types
from database.python_sql.db_objects import get_db_objects


class SchemaManager:
    def __init__(self, database="postgres", schema="public", database_project="supabase_automation_matrix",
                 additional_schemas=None, save_direct=False):
        if additional_schemas is None:
            additional_schemas = ["auth"]

        # Ensure utils and Schema are properly imported or defined
        self.utils = schema_builder_utils  # Define or import `utils` properly
        self.database = database
        self.schema = Schema(name=schema, database_project=database_project,
                             save_direct=save_direct)  # Define or import `Schema`
        self.additional_schemas = additional_schemas
        self.database_project = database_project
        self.processed_objects = None
        self.full_relationships = None
        self.full_junction_analysis = None
        self.all_enum_base_types = None
        self.overview_analysis = None
        self.frontend_full_relationships = []
        self.initialized = False
        self.save_direct = save_direct
        self.verbose = schema_builder_verbose
        self.debug = schema_builder_debug
        self.info = schema_builder_info

    def initialize(self):
        """Orchestrates the initialization of the SchemaManager."""
        self.set_all_schema_data()
        self.load_objects()
        self.load_table_relationships()
        self.initialized = True
        self.analyze_schema()
        self.get_full_relationship_analysis()

    def execute_all_initit_level_1(self):
        pass

    def execute_all_initit_level_2(self):
        pass

    def execute_all_initit_level_3(self):
        pass

    def execute_all_initit_level_4(self):
        pass

    def execute_all_initit_level_5(self):
        pass

    def execute_all_initit_level_6(self):
        pass

    def set_all_schema_data(self):
        (self.processed_objects, self.full_relationships, self.full_junction_analysis, self.all_enum_base_types,
         self.overview_analysis) = (
            get_db_objects(self.schema.name, self.database_project)
        )

        self.utils.set_and_update_ts_enum_list(self.all_enum_base_types)

        vcprint(self.full_relationships, title="Full relationships", pretty=True, verbose=self.verbose, color="yellow")
        vcprint(self.processed_objects, title="Processed objects", pretty=True, verbose=self.verbose, color="green")
        vcprint(self.overview_analysis, title="Relationship Overview analysis", pretty=True, verbose=self.verbose,
                color="green")

    def load_objects(self):
        """Loads all database objects (tables and views) into the schema."""
        vcprint(f"Loaded {len(self.processed_objects)} objects from {self.database_project}.", verbose=self.verbose,
                color="blue")

        for obj in self.processed_objects:
            if obj["type"] == "table":
                self.load_table(obj)
            elif obj["type"] == "view":
                self.load_view(obj)

        self.schema.add_all_table_instances()

        vcprint(f"Loaded {len(self.schema.tables)} tables.", verbose=self.verbose, color="blue")
        vcprint(f"Loaded {len(self.schema.views)} views.", verbose=self.verbose, color="green")

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
            table_columns=obj["table_columns"],
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
            vcprint(f"Loaded relationships for {len(self.full_relationships)} tables.", color="green")

    def detect_many_to_many_relationships(self):
        """Detects and sets many-to-many relationships."""
        for table in self.schema.tables.values():
            if len(table.foreign_keys) == 2 and len(table.referenced_by) == 0:
                related_tables = list(table.foreign_keys.keys())
                for related_table_name in related_tables:
                    related_table = self.schema.get_table(related_table_name)
                    if related_table:
                        other_table = self.schema.get_table(
                            related_tables[1] if related_tables[0] == related_table_name else related_tables[0]
                        )
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
                [(table.name, len(table.referenced_by)) for table in self.schema.tables.values()], key=lambda x: x[1],
                reverse=True
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
                    default_component_count[column.default_component] = default_component_count.get(
                        column.default_component, 0) + 1

                if "typescript" in column.calc_validation_functions:
                    validation_function = column.calc_validation_functions["typescript"]
                    calc_validation_functions_count[validation_function] = calc_validation_functions_count.get(
                        validation_function, 0) + 1

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
            "most_common_column_types": dict(
                sorted(column_type_count.items(), key=lambda item: item[1], reverse=True)[:10]),
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
        return (
            self.schema.tables[table_name].columns[column_name]
            if table_name in self.schema.tables and column_name in self.schema.tables[table_name].columns
            else None
        )

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

        vcprint(transformed, title="Transformed Foreign Keys", verbose=self.debug, pretty=True, color="yellow")
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

        vcprint(self.frontend_full_relationships, title="Frontend Full Relationships", pretty=True,
                verbose=self.verbose, color="yellow")
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
            name="entityRelationships", obj=self.full_relationship_analysis, keys_to_camel=True, export=True,
            as_const=True, ts_type=None
        )

        ts_code_content = ts_types_string + ts_code_content
        self.schema.code_handler.save_code_file("fullRelationships.ts", ts_code_content)

        vcprint(self.full_relationship_analysis, title="Full Relationship Analysis", pretty=True, verbose=self.verbose,
                color="blue")

    def get_frontend_junction_analysis(self):
        frontend_junction_analysis = {}

        for table_key, table_value in self.full_junction_analysis.items():
            table_instance = self.schema.tables.get(table_key)
            entity_name = table_instance.name_camel if table_instance else table_key

            updated_table = {"entityName": entity_name, "schema": table_value["schema"], "connectedTables": [],
                             "additionalFields": []}

            for connected_table in table_value["connected_tables"]:
                connected_instance = self.schema.tables.get(connected_table["table"])
                updated_table["connectedTables"].append(
                    {
                        "schema": connected_table["schema"],
                        "entity": connected_instance.name_camel if connected_instance else connected_table["table"],
                        "connectingColumn": self.schema.tables[table_key].columns[
                            connected_table["connecting_column"]].name_camel
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


generator_verbose = False
generator_debug = False
generator_info = True


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
                    "junctionTable": mm[
                        "junction_table"
                    ],  # The junction table that joins the two tables
                    "localColumn": mm[
                        "local_column"
                    ],  # Column in the junction table for the current table
                    "relatedColumn": mm[
                        "related_column"
                    ],  # Column in the junction table for the related table
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
        schema_structure["defaultFetchStrategy"] = (
            "simple"  # No relationships, basic fetch
        )

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
        verbose=generator_verbose,
        color="cyan",
    )

    example_view = schema_manager.get_view(
        "view_registered_function_all_rels"
    ).to_dict()
    vcprint(
        example_view,
        title="Full Registered Function View",
        pretty=True,
        verbose=generator_verbose,
        color="yellow",
    )

    example_table = schema_manager.get_table("registered_function").to_dict()
    vcprint(
        example_table,
        title="Flashcard History Table",
        pretty=True,
        verbose=generator_verbose,
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