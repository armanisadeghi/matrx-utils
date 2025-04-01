
def get_default_component_props():
    return {
        "subComponent": "default",
        "variant": "default",
        "section": "default",
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
        "min": "default",
        "max": "default",
        "step": "default",
        "numberType": "default",
        "options": "default",
    }

# Method to generate the AutomationSchema
def generate_automation_schema():  # TODO: Currently not used.
    lines = [
        "export type AutomationSchema = {",
        "    [tableName in AutomationTableName]: {",
        "        entityNameFormats: {",
        "            frontend: string;",
        "            backend: string;",
        "            database: string;",
        "            pretty: string;",
        "            component: string;",
        "            kebab: string;",
        "            [key: string]: string;",
        "        };",
        "        schemaType: 'table' | 'view' | 'dynamic' | 'other';",
        "        entityFields: {",
        "            [fieldName: string]: {",
        "                fieldNameFormats: {",
        "                    frontend: string;",
        "                    backend: string;",
        "                    database: string;",
        "                    pretty: string;",
        "                    component: string;",
        "                    kebab: string;",
        "                    [key: string]: string;",
        "                };",
        "                dataType: DataType;",
        "                isRequired?: boolean;",
        "                maxLength?: number | null;",
        "                isArray?: boolean;",
        "                defaultValue?: any;",
        "                isPrimaryKey?: boolean;",
        "                defaultGeneratorFunction?: string | null;",
        "                validationFunctions?: string[];",
        "                exclusionRules?: string[];",
        "                defaultComponent?: string;",
        "                structure: 'single' | 'array' | 'object' | 'foreignKey' | 'inverseForeignKey' | 'manyToMany';",
        "                isNative: boolean;",
        "                typeReference: TypeBrand<any>;",
        "                databaseTable: string;",
        "            };",
        "        };",
        "        defaultFetchStrategy: 'simple' | 'fk' | 'ifk' | 'm2m' | 'fkAndIfk' | 'm2mAndFk' | 'm2mAndIfk' | 'fkIfkAndM2M';",
        "        relationships: Array<{",
        "            relationshipType: 'foreignKey' | 'inverseForeignKey' | 'manyToMany';",
        "            column: string;",
        "            relatedTable: string;",
        "            relatedColumn: string;",
        "            junctionTable: string | null;",
        "        }>;",
        "    };",
        "};"
    ]

    return "\n".join(lines)

def get_relationship_data_model_types():
    ts_code_content = """
    
    import { AnyEntityDatabaseTable, EntityKeys } from "@/types";
    
    export type EntityRelationshipType =
        | "self-referential"
        | "one-to-one"
        | "one-to-many"
        | "many-to-one"
        | "many-to-many";
    
    export type ForeignKeyDetails = {
        foreignTable: AnyEntityDatabaseTable;
        foreignEntity: EntityKeys;
        column: string;
        fieldName: string;
        foreignField: string;
        foreignColumn: string;
        relationshipType: EntityRelationshipType;
        constraintName: string;
    };
    
    export type ReferencedByDetails = {
        foreignTable: AnyEntityDatabaseTable;
        foreignEntity: EntityKeys;
        field: string;
        column: string;
        foreignField: string;
        foreignColumn: string;
        constraintName: string;
    };
    
    export type RelationshipDetails = {
        entityName: EntityKeys;
        tableName: AnyEntityDatabaseTable;
        foreignKeys: Partial<Record<EntityKeys, ForeignKeyDetails>> | Record<string, never>;
        referencedBy: Partial<Record<EntityKeys, ReferencedByDetails>> | Record<string, never>;
    };
    
    export type FullEntityRelationships = {
        selfReferential: EntityKeys[];
        manyToMany: EntityKeys[];
        oneToOne: EntityKeys[];
        manyToOne: EntityKeys[];
        oneToMany: EntityKeys[];
        undefined: EntityKeys[];
        inverseReferences: EntityKeys[];
        relationshipDetails: RelationshipDetails;
    };
    
    export const asEntityRelationships = (data: any): Record<EntityKeys, FullEntityRelationships> => {
        return data as Record<EntityKeys, FullEntityRelationships>;
    };
    
    """
    return ts_code_content
