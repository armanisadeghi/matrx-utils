from pydantic import BaseModel
from typing import Dict, List, Union

class FieldAlts(BaseModel):
    frontend: str
    backend: str
    database: str
    db_p: str
    pretty: str
    component: str
    kebab: str

class FieldStructure(BaseModel):
    structure: str
    typeReference: Union[str, List[str]]  # Can include simple types or lists of types

class BaseField(BaseModel):
    alts: FieldAlts
    type: str
    format: str
    structure: FieldStructure

class SimpleField(BaseField):
    pass  # This can be used for fields like boolean, string, etc.

class RelationshipField(BaseField):
    relationship_type: str  # e.g., "foreignKey", "inverseForeignKey"
    related_model: str  # Name of the related model

class TableFieldSchema(BaseModel):
    fields: Dict[str, Union[SimpleField, RelationshipField]]  # Fields can be simple or relationship types

class TableSchema(BaseModel):
    name: Dict[str, str]
    schemaType: str
    fields: TableFieldSchema

class DatabaseSchema(BaseModel):
    __root__: Dict[str, TableSchema]  # Represents all tables

# Example of how to create a database schema
schema_data = {
    "action": {
        "name": {
            "frontend": "action",
            "backend": "action",
            "database": "action",
            "pretty": "Action"
        },
        "schemaType": "table",
        "fields": {
            "includeOther": {
                "alts": {
                    "frontend": "includeOther",
                    "backend": "include_other",
                    "database": "include_other",
                    "db_p": "p_include_other",
                    "pretty": "Include Other",
                    "component": "IncludeOther",
                    "kebab": "include-other"
                },
                "type": "boolean",
                "format": "single",
                "structure": {
                    "structure": "simple",
                    "typeReference": "boolean"
                }
            },
            "automationMatrixReference": {
                "alts": {
                    "frontend": "automationMatrixReference",
                    "backend": "automation_matrix_reference",
                    "database": "ref_automation_matrix",
                    "db_p": "p_ref_automation_matrix",
                    "pretty": "Automation Matrix Reference",
                    "component": "AutomationMatrixReference",
                    "kebab": "automation-matrixReference"
                },
                "type": "string",
                "format": "single",
                "structure": {
                    "structure": "foreignKey",
                    "typeReference": "AutomationMatrixType"
                },
                "relationship_type": "foreignKey",
                "related_model": "AutomationMatrix"
            }
        }
    }
}

# Instantiate the schema
db_schema = DatabaseSchema.parse_obj(schema_data)

# Example: Accessing the fields of a specific table
action_fields = db_schema.action.fields
print(action_fields)
