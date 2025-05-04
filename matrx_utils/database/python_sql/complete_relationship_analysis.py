# matrx_utils\database\python_sql\complete_relationship_analysis.py
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from database.client.postgres_connection import execute_sql_query
from common import vcprint


@dataclass
class ColumnInfo:
    name: str
    data_type: str
    is_nullable: bool
    default_value: Optional[str] = None
    description: Optional[str] = None
    is_primary_key: bool = False
    is_foreign_key: bool = False
    is_unique: bool = False


@dataclass
class RelationshipInfo:
    foreign_keys: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    referenced_by: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    is_junction_table: bool = False
    connected_tables: List[Dict[str, Any]] = field(default_factory=list)


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
    last_analyzed: Optional[str] = None
    estimated_size: Optional[str] = None


@dataclass
class TableAnalysis:
    schema: str
    name: str
    columns: Dict[str, ColumnInfo] = field(default_factory=dict)
    relationships: RelationshipInfo = field(default_factory=RelationshipInfo)
    constraints: ConstraintInfo = field(default_factory=ConstraintInfo)
    metadata: TableMetadata = field(default_factory=TableMetadata)


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
        self.analysis: Dict[str, TableAnalysis] = {}

    def analyze_all(self) -> Dict[str, TableAnalysis]:
        """
        Performs complete analysis of all tables in the specified schemas.
        """
        self._get_base_table_info()
        self._analyze_columns()
        self._analyze_relationships()
        self._analyze_constraints()
        self._analyze_metadata()
        return self.analysis

    def _get_base_table_info(self):
        """
        Gets basic information about all tables in the specified schemas.
        """
        query = """
        SELECT DISTINCT 
            table_schema,
            table_name
        FROM information_schema.tables
        WHERE table_schema = ANY(%s)
            AND table_type = 'BASE TABLE';
        """
        results = execute_sql_query(query, (self.schemas,), self.database_project)

        for row in results:
            table_name = row["table_name"]
            self.analysis[table_name] = TableAnalysis(schema=row["table_schema"], name=table_name)

    def _analyze_columns(self):
        """
        Analyzes column information for all tables.
        """
        query = """
        SELECT 
            c.table_name,
            c.column_name,
            c.data_type,
            c.is_nullable = 'YES' as is_nullable,
            c.column_default,
            pgd.description,
            EXISTS (
                SELECT 1 FROM information_schema.key_column_usage kcu
                JOIN information_schema.table_constraints tc 
                    ON tc.constraint_name = kcu.constraint_name
                WHERE kcu.column_name = c.column_name 
                    AND kcu.table_name = c.table_name
                    AND tc.constraint_type = 'PRIMARY KEY'
            ) as is_primary_key,
            EXISTS (
                SELECT 1 FROM information_schema.key_column_usage kcu
                JOIN information_schema.table_constraints tc 
                    ON tc.constraint_name = kcu.constraint_name
                WHERE kcu.column_name = c.column_name 
                    AND kcu.table_name = c.table_name
                    AND tc.constraint_type = 'FOREIGN KEY'
            ) as is_foreign_key,
            EXISTS (
                SELECT 1 FROM information_schema.key_column_usage kcu
                JOIN information_schema.table_constraints tc 
                    ON tc.constraint_name = kcu.constraint_name
                WHERE kcu.column_name = c.column_name 
                    AND kcu.table_name = c.table_name
                    AND tc.constraint_type = 'UNIQUE'
            ) as is_unique
        FROM information_schema.columns c
        LEFT JOIN pg_description pgd 
            ON pgd.objoid = (quote_ident(c.table_schema) || '.' || quote_ident(c.table_name))::regclass
            AND pgd.objsubid = c.ordinal_position
        WHERE c.table_schema = ANY(%s)
        ORDER BY c.table_name, c.ordinal_position;
        """
        results = execute_sql_query(query, (self.schemas,), self.database_project)

        for row in results:
            table_name = row["table_name"]
            if table_name in self.analysis:
                self.analysis[table_name].columns[row["column_name"]] = ColumnInfo(
                    name=row["column_name"],
                    data_type=row["data_type"],
                    is_nullable=row["is_nullable"],
                    default_value=row["column_default"],
                    description=row["description"],
                    is_primary_key=row["is_primary_key"],
                    is_foreign_key=row["is_foreign_key"],
                    is_unique=row["is_unique"],
                )

    def _analyze_relationships(self):
        """
        Analyzes relationships between tables.
        """
        # Implementation of relationship analysis
        # This would include foreign key relationships and junction table analysis
        pass

    def _analyze_constraints(self):
        """
        Analyzes table constraints.
        """
        # Implementation of constraint analysis
        pass

    def _analyze_metadata(self):
        """
        Analyzes table metadata including row counts and other statistics.
        """
        # Implementation of metadata analysis
        pass


def get_comprehensive_analysis(schema: str, database_project: str, additional_schemas: Optional[List[str]] = None) -> Dict[str, TableAnalysis]:
    """
    Main function to get comprehensive analysis of all tables.

    Args:
        schema: Primary schema to analyze
        database_project: Database configuration name
        additional_schemas: Optional additional schemas to include

    Returns:
        Dictionary mapping table names to their complete analysis
    """
    analyzer = DatabaseAnalyzer(schema, database_project, additional_schemas)
    return analyzer.analyze_all()


if __name__ == "__main__":
    # For testing purposes only
    schema = "public"
    database_project = "supabase_automation_matrix"
    additional_schemas = ["auth"]

    analysis = get_comprehensive_analysis(
        schema=schema,
        database_project=database_project,
        additional_schemas=additional_schemas,
    )

    vcprint(data=analysis, title="Comprehensive Table Analysis", pretty=True, verbose=True)
