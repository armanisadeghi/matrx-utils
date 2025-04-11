import re
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
import pandas as pd
from database.client.postgres_connection import execute_sql_query
from common import vcprint


@dataclass
class ColumnBase:
    name: str = ""
    table_name: str = ""
    database_project: str = ""
    unique_column_id: str = ""
    position: int = 0
    data_type: str = ""
    full_type: str = ""
    base_type: str = ""
    domain_type: Optional[str] = None
    enum_labels: Optional[List[str]] = field(default_factory=list)
    is_array: bool = False
    is_nullable: bool = True
    is_required: bool = False
    default_value: Optional[str] = None
    default_generator_function: Optional[str] = None
    is_default_function: bool = False
    character_maximum_length: Optional[int] = None
    numeric_precision: Optional[int] = None
    numeric_scale: Optional[int] = None
    collation: Optional[str] = None
    is_identity: bool = False
    is_generated: bool = False
    is_primary_key: bool = False
    is_unique: bool = False
    has_index: bool = False
    check_constraints: List[str] = field(default_factory=list)
    foreign_key_reference: Dict[str, str] = field(default_factory=dict)
    fk_table: str = ""
    fk_column: str = ""
    description: str = ""
    comment: str = ""
    is_display_field: bool = False

    # Additional fields for code generation
    name_snake: str = ""
    name_camel: str = ""
    name_pascal: str = ""
    name_kebab: str = ""
    name_title: str = ""
    table_name_camel: str = ""

    # Component and UI related
    default_component: str = "INPUT"
    default_component_priority: int = -1
    component_props: Dict[str, Any] = field(default_factory=dict)
    component_props_priorities: Dict[str, int] = field(default_factory=dict)

    # Type system related
    typescript_type: str = ""
    matrx_schema_type: str = ""
    python_field_type: str = ""

    # Validation and rules
    validation_functions: List[str] = field(default_factory=list)
    exclusion_rules: List[str] = field(default_factory=list)
    max_field_length: Optional[int] = None
    type_reference: str = ""

    @staticmethod
    def analyze_default_value(
        default_expr: Optional[str],
    ) -> tuple[Optional[str], Optional[str], bool]:
        if not default_expr:
            return None, None, False

        function_patterns = [
            r"\w+\([^)]*\)",
            r"CURRENT_\w+",
            r"current_\w+",
            r"nextval\(",
            r"array\[.*\]",
            r"\w+::.*",
        ]
        is_function = any(re.search(pattern, default_expr) for pattern in function_patterns)
        if is_function:
            return default_expr, default_expr, True
        else:
            return default_expr, None, False


@dataclass
class RelationshipBase:
    foreign_keys: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    referenced_by: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    is_junction_table: bool = False
    connected_tables: List[Dict[str, Any]] = field(default_factory=list)
    constraint_name: str = ""
    column: str = ""
    foreign_column: str = ""
    target_table: str = ""
    source_table: str = ""
    relationship_type: str = ""
    is_required: bool = False
    cascade_delete: bool = False
    cascade_update: bool = False
    foreign_key_relationships: List[Dict[str, Any]] = field(default_factory=list)
    referenced_by_relationships: List[Dict[str, Any]] = field(default_factory=list)
    many_to_many_relationships: List[Dict[str, Any]] = field(default_factory=list)
    junction_table_name: str = ""
    left_table: str = ""
    right_table: str = ""
    left_column: str = ""
    right_column: str = ""


@dataclass
class ConstraintInfo:
    primary_key: List[str] = field(default_factory=list)
    unique: List[str] = field(default_factory=list)
    foreign_key: List[Dict[str, Any]] = field(default_factory=list)
    check: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TableMetadata:
    row_count: int = 0
    has_timestamps: bool = False
    has_soft_delete: bool = False
    last_analyzed: str = ""
    estimated_size: str = ""


@dataclass
class TriggerInfo:
    name: str = ""
    event: str = ""
    timing: str = ""
    statement: str = ""
    table: str = ""


@dataclass
class ExclusionConstraintInfo:
    name: str = ""
    definition: str = ""
    columns: List[str] = field(default_factory=list)


@dataclass
class TableBase:
    schema: str = ""
    name: str = ""
    oid: int = 0
    database_project: str = ""
    unique_table_id: str = ""
    type_: str = "table"
    database: str = ""
    owner: str = ""
    size_bytes: int = 0
    index_size_bytes: int = 0
    rows: int = 0
    last_vacuum: str = ""
    last_analyze: str = ""
    description: str = ""
    estimated_row_count: int = 0
    total_bytes: int = 0
    has_primary_key: bool = False
    index_count: int = 0
    columns: Dict[str, ColumnBase] = field(default_factory=dict)  # Changed from List to Dict
    relationships: RelationshipBase = field(default_factory=RelationshipBase)
    constraints: ConstraintInfo = field(default_factory=ConstraintInfo)
    metadata: TableMetadata = field(default_factory=TableMetadata)
    triggers: List[TriggerInfo] = field(default_factory=list)
    exclusion_constraints: List[ExclusionConstraintInfo] = field(default_factory=list)
    name_snake: str = ""
    name_camel: str = ""
    name_pascal: str = ""
    name_kebab: str = ""
    name_title: str = ""
    defaultFetchStrategy: str = "simple"
    schema_structure: Dict[str, Any] = field(
        default_factory=lambda: {
            "defaultFetchStrategy": "simple",
            "foreignKeys": [],
            "inverseForeignKeys": [],
            "manyToMany": [],
        }
    )
    display_field_metadata: Dict[str, Any] = field(default_factory=dict)
    unique_field_types: Set[str] = field(default_factory=set)
    unique_name_lookups: str = ""
    column_rel_entries: Dict[str, Any] = field(default_factory=dict)
    py_fields: List[str] = field(default_factory=list)


@dataclass
class DatabaseSchema:
    database_project: str = ""
    schema_name: str = ""
    tables: Dict[str, TableBase] = field(default_factory=dict)
    relationships: List[RelationshipBase] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
    version: str = "1.0"
    case_sensitive: bool = False
    enable_logging: bool = True
    debug_mode: bool = False


class DatabaseAnalyzer:
    def __init__(
        self,
        schema: str,
        database_project: str,
        additional_schemas: Optional[List[str]] = None,
    ):
        self.schema = schema
        self.database_project = database_project
        self.schemas = [schema]
        if additional_schemas:
            self.schemas.extend(additional_schemas)
        self.analysis: Dict[str, TableBase] = {}

    def analyze_all(self) -> Dict[str, TableBase]:
        """
        Performs complete analysis of all tables in the specified schemas.
        """
        self._get_base_table_info()
        self._analyze_columns()
        self._analyze_relationships()
        self._analyze_constraints()
        self._analyze_triggers()  # Add new analysis
        self._analyze_exclusion_constraints()  # Add new analysis
        self._analyze_metadata()
        return self.analysis

    def _get_base_table_info(self):
        query = """
        SELECT DISTINCT 
            table_schema,
            table_name
        FROM information_schema.tables
        WHERE table_schema = ANY(%s)
            AND table_type = 'BASE TABLE';
        """
        results = execute_sql_query(query, (self.schemas,), self.database_project)
        df = pd.DataFrame(results)

        for _, row in df.iterrows():
            table_name = row["table_name"]
            self.analysis[table_name] = TableBase(
                schema=row["table_schema"],
                name=table_name,
                database_project=self.database_project,
                unique_table_id=f"{self.database_project}:{table_name}",
            )

    def _analyze_triggers(self):
        """
        Analyzes trigger information for all tables.
        """
        query = """
        SELECT 
            t.trigger_name,
            t.event_manipulation,
            t.event_object_table,
            t.action_timing,
            t.action_statement,
            t.action_orientation,
            t.action_reference_old_table,
            t.action_reference_new_table
        FROM information_schema.triggers t
        WHERE t.event_object_schema = ANY(%s)
        ORDER BY t.event_object_table, t.trigger_name;
        """
        results = execute_sql_query(query, (self.schemas,), self.database_project)
        df = pd.DataFrame(results)

        if not df.empty:
            for _, row in df.iterrows():
                table_name = row["event_object_table"]
                if table_name in self.analysis:
                    trigger = TriggerInfo(
                        name=row["trigger_name"],
                        event=row["event_manipulation"],
                        timing=row["action_timing"],
                        statement=row["action_statement"],
                        table=table_name,
                    )
                    self.analysis[table_name].triggers.append(trigger)

    def _analyze_exclusion_constraints(self):
        """
        Analyzes exclusion constraints for all tables.
        """
        query = """
        SELECT 
            t.relname as table_name,
            con.conname as constraint_name,
            pg_get_constraintdef(con.oid) as constraint_definition,
            array_agg(a.attname) as constraint_columns
        FROM pg_constraint con
        JOIN pg_class t ON t.oid = con.conrelid
        JOIN pg_namespace n ON n.oid = t.relnamespace
        JOIN pg_attribute a ON a.attrelid = t.oid 
        WHERE n.nspname = ANY(%s)
        AND con.contype = 'x'
        AND a.attnum = ANY(con.conkey)
        GROUP BY t.relname, con.conname, con.oid;
        """
        results = execute_sql_query(query, (self.schemas,), self.database_project)
        df = pd.DataFrame(results)

        if not df.empty:
            for _, row in df.iterrows():
                table_name = row["table_name"]
                if table_name in self.analysis:
                    exclusion = ExclusionConstraintInfo(
                        name=row["constraint_name"],
                        definition=row["constraint_definition"],
                        columns=row["constraint_columns"],
                    )
                    self.analysis[table_name].exclusion_constraints.append(exclusion)

    def _analyze_columns(self):
        """
        Analyzes column information for all tables with enhanced details.
        """
        query = """
        SELECT 
            c.relname AS table_name,
            a.attname AS name,
            a.attnum AS position,
            pg_catalog.format_type(a.atttypid, a.atttypmod) AS full_type,
            t.typname AS base_type,
            CASE WHEN t.typtype = 'd' THEN t.typname ELSE NULL END AS domain_type,
            CASE WHEN t.typtype = 'e' THEN (
                SELECT array_agg(enumlabel) FROM pg_enum WHERE enumtypid = t.oid
            ) ELSE NULL END AS enum_labels,
            a.attndims > 0 AS is_array,
            NOT a.attnotnull AS is_nullable,
            pg_get_expr(d.adbin, d.adrelid) AS default_value,
            CASE 
                WHEN a.atttypid = 1043 AND a.atttypmod > 0 THEN a.atttypmod - 4
                WHEN a.atttypid = 1043 AND a.atttypmod = -1 THEN NULL
                WHEN a.atttypid = 25 THEN NULL
                ELSE NULL 
            END AS character_maximum_length,
            CASE WHEN a.atttypid = 1700 THEN information_schema._pg_numeric_precision(a.atttypid, a.atttypmod) ELSE NULL END AS numeric_precision,
            CASE WHEN a.atttypid = 1700 THEN information_schema._pg_numeric_scale(a.atttypid, a.atttypmod) ELSE NULL END AS numeric_scale,
            CASE WHEN a.attcollation <> t.typcollation THEN col.collname ELSE NULL END AS collation,
            a.attidentity <> '' AS is_identity,
            a.attgenerated <> '' AS is_generated,
            EXISTS (
                SELECT 1 FROM pg_constraint p
                WHERE p.conrelid = a.attrelid AND p.contype = 'p' AND p.conkey @> ARRAY[a.attnum]
            ) AS is_primary_key,
            EXISTS (
                SELECT 1 FROM pg_constraint u
                WHERE u.conrelid = a.attrelid AND u.contype = 'u' AND u.conkey @> ARRAY[a.attnum]
            ) AS is_unique,
            EXISTS (
                SELECT 1 
                FROM pg_index i
                JOIN unnest(i.indkey) AS key ON key = a.attnum
                WHERE i.indrelid = a.attrelid AND i.indisprimary = false
            ) AS has_index,
            (
                SELECT array_agg(pg_get_constraintdef(con.oid))
                FROM pg_constraint con
                WHERE con.conrelid = a.attrelid AND con.contype = 'c' AND con.conkey @> ARRAY[a.attnum]
            ) AS check_constraints,
            (
                SELECT json_build_object(
                    'table', confrelid::regclass::text, 
                    'column', (SELECT attname FROM pg_attribute WHERE attrelid = confrelid AND attnum = conkey[1])
                )
                FROM pg_constraint fk
                WHERE fk.conrelid = a.attrelid AND fk.contype = 'f' AND fk.conkey[1] = a.attnum
            ) AS foreign_key_reference,
            col_description(a.attrelid, a.attnum) AS description,
            n.nspname AS schema_name
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        JOIN pg_attribute a ON a.attrelid = c.oid
        LEFT JOIN pg_attrdef d ON (a.attrelid, a.attnum) = (d.adrelid, d.adnum)
        LEFT JOIN pg_type t ON a.atttypid = t.oid
        LEFT JOIN pg_collation col ON col.oid = a.attcollation
        WHERE n.nspname = ANY(%s)
        AND a.attnum > 0 
        AND NOT a.attisdropped
        AND c.relkind = 'r'
        ORDER BY c.relname, a.attnum;
        """

        results = execute_sql_query(query, (self.schemas,), self.database_project)

        for row in results:
            table_name = row["table_name"]
            if table_name in self.analysis:
                # Calculate is_required (not nullable and no default)
                is_required = not row["is_nullable"] and row["default_value"] is None

                # Create unique column identifier
                unique_column_id = f"{self.database_project}_{row['schema_name']}:{table_name}:{row['name']}"

                default_expr = row["default_value"]
                default_value, default_generator_function, is_default_function = ColumnBase.analyze_default_value(default_expr)

                column_info = ColumnBase(
                    name=row["name"],
                    position=row["position"],
                    data_type=row["full_type"],
                    full_type=row["full_type"],
                    base_type=row["base_type"],
                    domain_type=row["domain_type"],
                    enum_labels=row["enum_labels"],
                    is_array=row["is_array"],
                    is_nullable=row["is_nullable"],
                    is_required=is_required,
                    default_value=default_value,
                    default_generator_function=default_generator_function,
                    is_default_function=is_default_function,
                    character_maximum_length=row["character_maximum_length"],
                    numeric_precision=row["numeric_precision"],
                    numeric_scale=row["numeric_scale"],
                    collation=row["collation"],
                    is_identity=row["is_identity"],
                    is_generated=row["is_generated"],
                    is_primary_key=row["is_primary_key"],
                    is_unique=row["is_unique"],
                    has_index=row["has_index"],
                    check_constraints=row["check_constraints"] if row["check_constraints"] else [],
                    foreign_key_reference=row["foreign_key_reference"],
                    fk_table=row["foreign_key_reference"]["table"] if row["foreign_key_reference"] else None,
                    fk_column=row["foreign_key_reference"]["column"] if row["foreign_key_reference"] else None,
                    description=row["description"],
                    table_name=table_name,
                    unique_column_id=unique_column_id,
                )

                self.analysis[table_name].columns[row["name"]] = column_info

    def _analyze_relationships(self):
        """
        Analyzes relationships between tables.
        """
        query = """
        SELECT
            tc.table_schema,
            tc.table_name,
            kcu.column_name,
            ccu.table_schema AS foreign_table_schema,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage ccu
            ON ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = ANY(%s);
        """
        results = execute_sql_query(query, (self.schemas,), self.database_project)
        df = pd.DataFrame(results)

        if not df.empty:
            for table_name in self.analysis:
                # Filter relationships for current table
                table_rels = df[df["table_name"] == table_name]

                for _, rel in table_rels.iterrows():
                    # Add foreign key information
                    self.analysis[table_name].relationships.foreign_keys[rel["column_name"]] = {
                        "referenced_table": rel["foreign_table_name"],
                        "referenced_column": rel["foreign_column_name"],
                        "referenced_schema": rel["foreign_table_schema"],
                    }

                # Find tables referencing this table
                referenced = df[df["foreign_table_name"] == table_name]
                for _, ref in referenced.iterrows():
                    self.analysis[table_name].relationships.referenced_by[ref["table_name"]] = {
                        "referencing_column": ref["column_name"],
                        "referenced_column": ref["foreign_column_name"],
                    }

    def _analyze_constraints(self):
        """
        Analyzes table constraints.
        """
        query = """
        SELECT
            tc.table_name,
            tc.constraint_type,
            kcu.column_name,
            tc.constraint_name,
            cc.check_clause
        FROM information_schema.table_constraints tc
        LEFT JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
        LEFT JOIN information_schema.check_constraints cc
            ON tc.constraint_name = cc.constraint_name
        WHERE tc.table_schema = ANY(%s)
        ORDER BY tc.table_name, tc.constraint_type;
        """
        results = execute_sql_query(query, (self.schemas,), self.database_project)
        df = pd.DataFrame(results)

        if not df.empty:
            grouped = df.groupby("table_name")
            for table_name, group in grouped:
                if table_name in self.analysis:
                    constraints = self.analysis[table_name].constraints

                    # Process each constraint type
                    for _, row in group.iterrows():
                        if row["constraint_type"] == "PRIMARY KEY":
                            constraints.primary_key.append(row["column_name"])
                        elif row["constraint_type"] == "UNIQUE":
                            constraints.unique.append(row["column_name"])
                        elif row["constraint_type"] == "FOREIGN KEY":
                            constraints.foreign_key.append(
                                {
                                    "column": row["column_name"],
                                    "name": row["constraint_name"],
                                }
                            )
                        elif row["constraint_type"] == "CHECK":
                            constraints.check.append(
                                {
                                    "name": row["constraint_name"],
                                    "definition": row["check_clause"],
                                }
                            )

    def _analyze_metadata(self):
        """
        Analyzes table metadata including row counts and other statistics.
        """
        query = """
        SELECT 
            schemaname,
            relname as table_name,
            n_live_tup as row_count,
            last_analyze::text,
            pg_size_pretty(pg_total_relation_size(quote_ident(schemaname) || '.' || quote_ident(relname))) as estimated_size
        FROM pg_stat_user_tables
        WHERE schemaname = ANY(%s);
        """
        results = execute_sql_query(query, (self.schemas,), self.database_project)
        df = pd.DataFrame(results)

        if not df.empty:
            for _, row in df.iterrows():
                table_name = row["table_name"]
                if table_name in self.analysis:
                    self.analysis[table_name].metadata = TableMetadata(
                        row_count=row["row_count"],
                        last_analyzed=row["last_analyze"],
                        estimated_size=row["estimated_size"],
                        # Updated to handle dictionary
                        has_timestamps=any(col.base_type == "timestamp" for col in self.analysis[table_name].columns.values()),
                        has_soft_delete=any(col.name in ["deleted_at", "is_deleted"] for col in self.analysis[table_name].columns.values()),
                    )


def get_comprehensive_analysis(schema: str, database_project: str, additional_schemas: Optional[List[str]] = None) -> Dict[str, TableBase]:
    """
    Main function to get comprehensive analysis of all tables.
    """
    analyzer = DatabaseAnalyzer(schema, database_project, additional_schemas)
    return analyzer.analyze_all()


def convert_table_analysis_to_dict_with_columns(table_analysis: TableBase) -> dict:
    """
    Converts a TableBase object to a plain dictionary with comprehensive column information.
    """
    column_list = list(table_analysis.columns.keys())

    return {
        "schema": table_analysis.schema,
        "name": table_analysis.name,
        "column_list": column_list,
        "relationships": {
            "foreign_keys": table_analysis.relationships.foreign_keys,
            "referenced_by": table_analysis.relationships.referenced_by,
            "is_junction_table": table_analysis.relationships.is_junction_table,
            "connected_tables": table_analysis.relationships.connected_tables,
        },
        "constraints": {
            "primary_key": table_analysis.constraints.primary_key,
            "unique": table_analysis.constraints.unique,
            "foreign_key": table_analysis.constraints.foreign_key,
            "check": table_analysis.constraints.check,
        },
        "metadata": {
            "row_count": table_analysis.metadata.row_count,
            "has_timestamps": table_analysis.metadata.has_timestamps,
            "has_soft_delete": table_analysis.metadata.has_soft_delete,
            "last_analyzed": table_analysis.metadata.last_analyzed,
            "estimated_size": table_analysis.metadata.estimated_size,
        },
        "triggers": [
            {
                "name": trigger.name,
                "event": trigger.event,
                "timing": trigger.timing,
                "statement": trigger.statement,
                "table": trigger.table,
            }
            for trigger in table_analysis.triggers
        ],
        "exclusion_constraints": [
            {
                "name": constraint.name,
                "definition": constraint.definition,
                "columns": constraint.columns,
            }
            for constraint in table_analysis.exclusion_constraints
        ],
        "columns": {
            name: {
                "name": col.name,
                "position": col.position,
                "data_type": col.data_type,
                "full_type": col.full_type,
                "base_type": col.base_type,
                "domain_type": col.domain_type,
                "enum_labels": col.enum_labels,
                "is_array": col.is_array,
                "is_nullable": col.is_nullable,
                "is_required": col.is_required,
                "default_value": col.default_value,
                "default_generator_function": col.default_generator_function,
                "is_default_function": col.is_default_function,
                "character_maximum_length": col.character_maximum_length,
                "numeric_precision": col.numeric_precision,
                "numeric_scale": col.numeric_scale,
                "collation": col.collation,
                "is_identity": col.is_identity,
                "is_generated": col.is_generated,
                "is_primary_key": col.is_primary_key,
                "is_unique": col.is_unique,
                "has_index": col.has_index,
                "check_constraints": col.check_constraints,
                "foreign_key_reference": col.foreign_key_reference,
                "fk_table": col.fk_table,
                "fk_column": col.fk_column,
                "description": col.description,
                "table_name": col.table_name,
                "unique_column_id": col.unique_column_id,
            }
            for name, col in table_analysis.columns.items()
        },
    }


def convert_table_analysis_to_dict(table_analysis: TableBase) -> dict:
    """
    Converts a TableBase object to a plain dictionary with focus on save operation requirements.
    """
    # Get column names as a simple list
    column_list = list(table_analysis.columns.keys())

    # Extract foreign key dependencies with their rules
    foreign_key_details = {}
    for col_name, fk_info in table_analysis.relationships.foreign_keys.items():
        foreign_key_details[col_name] = {
            "referenced_table": fk_info["referenced_table"],
            "referenced_column": fk_info["referenced_column"],
            # Additional important aspects for save operations:
            "on_delete": fk_info.get("on_delete", "NO ACTION"),  # CASCADE, SET NULL, etc.
            "on_update": fk_info.get("on_update", "NO ACTION"),
            "deferrable": fk_info.get("deferrable", False),
        }

    triggers_info = [
        {
            "name": trigger.name,
            "event": trigger.event,
            "timing": trigger.timing,
            "statement": trigger.statement,
        }
        for trigger in table_analysis.triggers
    ]

    # Add exclusion constraints
    exclusion_info = [{"name": exc.name, "definition": exc.definition, "columns": exc.columns} for exc in table_analysis.exclusion_constraints]

    return {
        "schema": table_analysis.schema,
        "name": table_analysis.name,
        "column_list": column_list,
        "save_operation_rules": {
            "has_identity": any(col.data_type in ["serial", "bigserial"] for col in table_analysis.columns.values()),
            "has_default_values": [name for name, col in table_analysis.columns.items() if col.default_value is not None],
            "required_columns": [name for name, col in table_analysis.columns.items() if not col.is_nullable and col.default_value is None],
            "unique_constraints": table_analysis.constraints.unique,
            "primary_key": table_analysis.constraints.primary_key,
            "foreign_keys": foreign_key_details,
            "check_constraints": table_analysis.constraints.check,
            "triggers": triggers_info,
            "generated_columns": [name for name, col in table_analysis.columns.items() if "generated" in (col.default_value or "").lower()],
            "exclusion_constraints": exclusion_info,
        },
        "metadata": {
            "row_count": table_analysis.metadata.row_count,
            "has_timestamps": table_analysis.metadata.has_timestamps,
            "has_soft_delete": table_analysis.metadata.has_soft_delete,
        },
    }


if __name__ == "__main__":
    import json
    import os
    from datetime import datetime
    from aidream.settings import BASE_DIR
    from common import print_link

    try:
        full_directory_path = os.path.join(BASE_DIR, "database/python_sql/temp_data")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_no_columns = f"{full_directory_path}/rel_nc_{timestamp}.json"
        filename_with_columns = f"{full_directory_path}/rel_wc_{timestamp}.json"

        schema = "public"
        database_project = "supabase_automation_matrix"
        additional_schemas = ["auth"]

        # Get the analysis
        analysis = get_comprehensive_analysis(
            schema=schema,
            database_project=database_project,
            additional_schemas=additional_schemas,
        )

        # Extract and print registered_function table data
        if "registered_function" in analysis:
            registered_function_dict = convert_table_analysis_to_dict(analysis["registered_function"])
            vcprint(
                data=registered_function_dict,
                title="Registered Function Table Analysis",
                pretty=True,
                verbose=True,
                color="yellow",
            )

        if "registered_function" in analysis:
            registered_function_dict = convert_table_analysis_to_dict_with_columns(analysis["registered_function"])
            vcprint(
                data=registered_function_dict,
                title="Registered Function Table Analysis",
                pretty=True,
                verbose=True,
                color="blue",
            )

        # Create temp_data directory if it doesn't exist
        os.makedirs(full_directory_path, exist_ok=True)

        # Convert all analysis to dict and save
        analysis_dict_without_columns = {table_name: convert_table_analysis_to_dict_with_columns(table_analysis) for table_name, table_analysis in analysis.items()}

        with open(filename_with_columns, "w") as f:
            json.dump(analysis_dict_without_columns, f, indent=2)

        print_link(filename_with_columns)

        full_analysis_dict = {table_name: convert_table_analysis_to_dict(table_analysis) for table_name, table_analysis in analysis.items()}

        with open(filename_no_columns, "w") as f:
            json.dump(full_analysis_dict, f, indent=2)

        print_link(filename_no_columns)

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise
