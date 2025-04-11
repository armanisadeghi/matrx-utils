import os
from dotenv import load_dotenv

load_dotenv()


class DatabaseConfigError(Exception):
    """Custom exception for database configuration errors"""

    pass


database_project = {
    "supabase_automation_matrix": {
        "host": os.environ.get("SUPABASE_MATRIX_HOST"),
        "port": os.environ.get("SUPABASE_MATRIX_PORT"),
        "database_name": os.environ.get("SUPABASE_MATRIX_DATABASE_NAME"),
        "user": os.environ.get("SUPABASE_MATRIX_USER"),
        "password": os.environ.get("SUPABASE_MATRIX_PASSWORD"),
    },
    "supabase_ai-matrix": {
        "host": os.environ.get("SUPABASE_AI_MATRIX_HOST"),
        "port": os.environ.get("SUPABASE_AI_MATRIX_PORT"),
        "database_name": os.environ.get("SUPABASE_AI_MATRIX_DATABASE_NAME"),
        "user": os.environ.get("SUPABASE_AI_MATRIX_USER"),
        "password": os.environ.get("SUPABASE_AI_MATRIX_PASSWORD"),
    },
    "supabase_sample_matrix": {
        "host": os.environ.get("SUPABASE_SAMPLE_MATRIX_HOST"),
        "port": os.environ.get("SUPABASE_SAMPLE_MATRIX_PORT"),
        "database_name": os.environ.get("SUPABASE_SAMPLE_MATRIX_DATABASE_NAME"),
        "user": os.environ.get("SUPABASE_SAMPLE_MATRIX_USER"),
        "password": os.environ.get("SUPABASE_SAMPLE_MATRIX_PASSWORD"),
    },
    "supabase_matrix_django": {
        "host": os.environ.get("SUPABASE_MATRIX_DJANGO_HOST"),
        "port": os.environ.get("SUPABASE_MATRIX_DJANGO_PORT"),
        "database_name": os.environ.get("SUPABASE_MATRIX_DJANGO_DATABASE_NAME"),
        "user": os.environ.get("SUPABASE_MATRIX_DJANGO_USER"),
        "password": os.environ.get("SUPABASE_MATRIX_DJANGO_PASSWORD"),
    },
}


def get_database_config(config_name: str) -> dict:
    try:
        config = database_project[config_name]
    except KeyError:
        raise DatabaseConfigError(f"Configuration '{config_name}' not found in database_project")

    required_fields = ["host", "port", "database_name", "user", "password"]
    missing_fields = [field for field in required_fields if not config.get(field)]

    if missing_fields:
        raise DatabaseConfigError(f"Missing required configuration fields for '{config_name}': " f"{', '.join(missing_fields)}. Please check your environment variables.")

    return config


def get_connection_string(config_name: str) -> str:
    config = get_database_config(config_name)
    connection_string = f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database_name']}"
    return connection_string
