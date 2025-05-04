# matrx_utils\schema_builder\generate_schema.py
from matrx_utils import vcprint
from matrx_utils.schema_builder.schema_manager import SchemaManager

def generate_all():
    schema = "public"
    database_project = "supabase_automation_matrix"
    additional_schemas = ["auth"]
    save_direct = True

    schema_manager = SchemaManager(
        schema=schema,
        database_project=database_project,
        additional_schemas=additional_schemas,
        save_direct=save_direct,
    )
    schema_manager.initialize()

    matrx_schema_entry = schema_manager.schema.generate_schema_files()
    matrx_models = schema_manager.schema.generate_models()

    analysis = schema_manager.analyze_schema()
    vcprint(
        data=analysis,
        title="Schema Analysis",
        pretty=True,
        verbose=False,
        color="yellow",
    )
    schema_manager.schema.code_handler.print_all_batched()
