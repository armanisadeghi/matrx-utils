# from matrx_utils import vcprint
# from matrx_utils.conf import settings
# from matrx_utils.schema_builder.helpers.git_checker import check_git_status
#
# def create_schema():
#     schema = "public"
#     database_project = "supabase_automation_matrix"
#     additional_schemas = ["auth"]
#     save_direct = True
#
#     if settings.SAVE_DIRECT_SCHEMA:
#         check_git_status(settings.SAVE_DIRECT_SCHEMA)
#         vcprint(
#             "\n[MATRX UTILS AUTOMATED SCHEMA GENERATOR] WARNING!! save_direct is True. Proceed with caution.\n",
#             color="red",
#         )
#         input("WARNING: This will overwrite the existing schema files. Press Enter to continue...")
#
#     schema_manager = SchemaManager(
#         schema=schema,
#         database_project=database_project,
#         additional_schemas=additional_schemas,
#         save_direct=save_direct,
#     )
#     schema_manager.initialize()
#
#     matrx_schema_entry = schema_manager.schema.generate_schema_files()
#
#     matrx_models = schema_manager.schema.generate_models()
#
#     analysis = schema_manager.analyze_schema()
#     vcprint(
#         data=analysis,
#         title="Schema Analysis",
#         pretty=True,
#         verbose=False,
#         color="yellow",
#     )
#     schema_manager.schema.code_handler.print_all_batched()
