basic_config_defaults = {
    "project_name": "ai_matrix",
    "frontend_framework": "next_js_14",
    "backend_server": "python",
    "backend_framework": "django",
    "database": "supabase",
}

system_config_defaults = {
    "code_save_dir": "code_gen_saves/",
    "frontend_import_root": "@/",
}

framework_config_defaults = {
    "next_js_14": {
        "project_root": "@/",
        "app_dir": "app/",
        "api_dir": "app/api/",
        "config_files": [
            "next.config.js",
            "tsconfig.json",
            "jest.config.js",
        ],
        "components": "components/",
        "styles": "styles/",
        "utilities": "utils/",
        "services": "services/",
        "scripts": "scripts/",
        "db_ops": "db_ops/",
        "apis": "apis/",
        "custom": {},
    },
}


project_config_defaults = {
    "web_frontend": {
        "root": "@/",
        "components": "components",
        "styles": "styles",
        "utilities": "utils",
        "services": "services",
        "scripts": "scripts",
        "db_ops": "db_ops",
        "apis": "apis",
        "custom": {},
    },
    "web_backend": {
        "root": "/",
        "components": "components",
        "styles": "styles",
        "utilities": "utils",
        "services": "services",
        "scripts": "scripts",
        "db_ops": "db_ops",
        "apis": "apis",
        "custom": {},
    },
    "mobile": {
        "root": "@/",
        "components": "components",
        "styles": "styles",
        "utilities": "utils",
        "services": "services",
        "scripts": "scripts",
        "db_ops": "db_ops",
        "apis": "apis",
        "custom": {},
    },
    "desktop": {
        "root": "@/",
        "components": "components",
        "styles": "styles",
        "utilities": "utils",
        "services": "services",
        "scripts": "scripts",
        "db_ops": "db_ops",
        "apis": "apis",
        "custom": {},
    },
    "cloud_database": {
        "root": "/",
        "components": "",
        "styles": "",
        "utilities": "",
        "services": "",
        "scripts": "",
        "db_ops": "",
        "apis": "",
        "custom": {},
    },
    "local_database": {
        "root": "",
        "components": "",
        "styles": "",
        "utilities": "",
        "services": "",
        "scripts": "",
        "db_ops": "",
        "apis": "",
        "custom": {},
    },

    "cloud": {
        "root": "@/",
        "components": "components",
        "styles": "styles",
        "utilities": "utils",
        "services": "services",
        "scripts": "scripts",
        "db_ops": "db_ops",
        "apis": "apis",
        "custom": {},
    },
}

type_map_defaults = {
    "uuid": "string",
    "text": "string",
    "character varying": "string",
    "boolean": "boolean",
    "smallint": "number",
    "bigint": "number",
    "integer": "number",
    "real": "number",
    "double precision": "number",
    "numeric": "number",
    "jsonb": "Record<string, unknown>",
    "jsonb[]": "Record<string, unknown>[]",
    "json": "Record<string, unknown>",
    "data_type": "string",
    "data_source": "string",
    "data_destination": "string",
    "destination_component": "string",
    "function_role": "string",
    "broker_role": "string",
    "model_role": "string",
    "cognition_matrices": "string",
    "recipe_status": "string",
    "timestamp": "Date",
    "timestamp with time zone": "Date",
    "date": "Date",
    "time": "Date",
    "interval": "string",
    "bytea": "Uint8Array",
    "array": "any[]",
    "hstore": "Record<string, string>",
    "point": "{x: number, y: number}",
    "line": "{a: number, b: number, c: number}",
    "lseg": "{start: {x: number, y: number}, end: {x: number, y: number}}",
    "box": "{topRight: {x: number, y: number}, bottomLeft: {x: number, y: number}}",
    "path": "{points: {x: number, y: number}[], closed: boolean}",
    "polygon": "{x: number, y: number}[]",
    "circle": "{center: {x: number, y: number}, radius: number}",
    "cidr": "string",
    "inet": "string",
    "macaddr": "string",
    "tsvector": "string",
    "tsquery": "string",
    "uuid[]": "string[]",
    "text[]": "string[]",
    "integer[]": "number[]",
    "boolean[]": "boolean[]",
    "char[]": "string[]",
    "varchar[]": "string[]",
    "xml": "string",
    "money": "string",
    "bit": "string",
    "bit varying": "string",
    "timetz": "string",
    "timestamptz": "Date",
    "txid_snapshot": "string",
    "enum": "string"
}

technology_config_defaults = {
    "typescript_types": {
        "project_type": "web_frontend",
        "name_format": "pascal_case",
        "name_prefix": "",
        "name_suffix": "Types",
        "save_dir": "typescript/types/",
        "tech_dir": "types/",
        "filename_prefix": "",
        "filename_suffix": "Types",
        "file_extension": "ts",
        "custom_configs": {},
    },
    "typescript_helpers": {
        "name_format": "camel_case",
        "name_prefix": "",
        "name_suffix": "Helper",
        "save_dir": "typescript/helpers/",
        "tech_dir": "typescript/helpers/",
        "filename_prefix": "",
        "filename_suffix": "Helper",
        "file_extension": "ts",
        "custom_configs": {},
        "project_type": "web_frontend"
    },
    "typescript_utils": {
        "name_format": "camel_case",
        "name_prefix": "",
        "name_suffix": "Util",
        "save_dir": "typescript/utils/",
        "tech_dir": "",
        "filename_prefix": "",
        "filename_suffix": "Util",
        "file_extension": "ts",
        "custom_configs": {},
        "project_type": "web_frontend"
    },
    "redux_models": {
        "name_format": "pascal_case",
        "name_prefix": "",
        "name_suffix": "Model",
        "save_dir": "redux/models/",
        "tech_dir": "redux/models/",
        "filename_prefix": "",
        "filename_suffix": "Models",
        "file_extension": "ts",
        "custom_configs": {},
        "project_type": "web_frontend"
    },
    "redux_selectors": {
        "name_format": "camel_case",
        "name_prefix": "",
        "name_suffix": "Selector",
        "save_dir": "redux/selectors/",
        "tech_dir": "redux/selectors/",
        "filename_prefix": "",
        "filename_suffix": "Selectors",
        "file_extension": "ts",
        "custom_configs": {},
        "project_type": "web_frontend"
    },
    "redux_slices": {
        "name_format": "pascal_case",
        "name_prefix": "",
        "name_suffix": "Slice",
        "save_dir": "redux/slices/",
        "tech_dir": "redux/slice/",
        "filename_prefix": "",
        "filename_suffix": "Slice",
        "file_extension": "ts",
        "custom_configs": {},
        "project_type": "web_frontend"
    },
    "redux_services": {
        "name_format": "pascal_case",
        "name_prefix": "",
        "name_suffix": "Service",
        "save_dir": "redux/services/",
        "tech_dir": "redux/services/",
        "filename_prefix": "",
        "filename_suffix": "Service",
        "file_extension": "ts",
        "custom_configs": {},
        "project_type": "web_frontend"
    },
    "redux_middlewares": {
        "name_format": "camel_case",
        "name_prefix": "",
        "name_suffix": "Middleware",
        "save_dir": "redux/middlewares/",
        "tech_dir": "redux/middlewares/",
        "filename_prefix": "",
        "filename_suffix": "Middleware",
        "file_extension": "ts",
        "custom_configs": {},
        "project_type": "web_frontend"
    },
    "redux_reducers": {
        "name_format": "camel_case",
        "name_prefix": "",
        "name_suffix": "Reducer",
        "save_dir": "redux/reducers/",
        "tech_dir": "redux/reducers/",
        "filename_prefix": "",
        "filename_suffix": "Reducer",
        "file_extension": "ts",
        "custom_configs": {},
        "project_type": "web_frontend"
    },
    "redux_actions": {
        "name_format": "camel_case",
        "name_prefix": "",
        "name_suffix": "Action",
        "save_dir": "redux/actions/",
        "tech_dir": "redux/actions/",
        "filename_prefix": "",
        "filename_suffix": "Actions",
        "file_extension": "ts",
        "custom_configs": {},
        "project_type": "web_frontend"
    },
    "react_components": {
        "name_format": "pascal_case",
        "name_prefix": "",
        "name_suffix": "Component",
        "save_dir": "react/components/",
        "tech_dir": "components/",
        "filename_prefix": "",
        "filename_suffix": "Component",
        "file_extension": "tsx",
        "custom_configs": {},
        "project_type": "web_frontend"
    },
    "react_hooks": {
        "name_format": "camel_case",
        "name_prefix": "use",
        "name_suffix": "Hook",
        "save_dir": "react/hooks/",
        "tech_dir": "",
        "filename_prefix": "",
        "filename_suffix": "Hook",
        "file_extension": "tsx",
        "custom_configs": {},
        "project_type": "web_frontend"
    },
    "react_utils": {
        "name_format": "camel_case",
        "name_prefix": "",
        "name_suffix": "Util",
        "save_dir": "react/utils/",
        "tech_dir": "",
        "filename_prefix": "",
        "filename_suffix": "Util",
        "file_extension": "tsx",
        "custom_configs": {},
        "project_type": "web_frontend"
    },
    "mantine_ui_components": {
        "name_format": "pascal_case",
        "name_prefix": "Mantine",
        "name_suffix": "Component",
        "save_dir": "react/components/mantine/",
        "tech_dir": "",
        "filename_prefix": "Mantine",
        "filename_suffix": "Component",
        "file_extension": "tsx",
        "custom_configs": {},
        "project_type": "web_frontend"
    },
    "shadcn_ui_components": {
        "name_format": "pascal_case",
        "name_prefix": "Shadcn",
        "name_suffix": "Component",
        "save_dir": "react/components/shadcn/",
        "tech_dir": "",
        "filename_prefix": "Shadcn",
        "filename_suffix": "Component",
        "file_extension": "tsx",
        "custom_configs": {},
        "project_type": "web_frontend"
    },
    "tailwind_css": {
        "name_format": "kebab_case",
        "name_prefix": "",
        "name_suffix": "",
        "save_dir": "react/styles/tailwind/",
        "tech_dir": "",
        "filename_prefix": "",
        "filename_suffix": "",
        "file_extension": "css",
        "custom_configs": {},
        "project_type": "web_frontend"
    },
    "supabase_ts_services": {
        "name_format": "pascal_case",
        "name_prefix": "",
        "name_suffix": "Service",
        "save_dir": "services/supabase/",
        "tech_dir": "",
        "filename_prefix": "",
        "filename_suffix": "Service",
        "file_extension": "ts",
        "custom_configs": {},
        "project_type": "web_frontend"
    },
    "supabase_ts_rpc_services": {
        "name_format": "pascal_case",
        "name_prefix": "",
        "name_suffix": "RpcService",
        "save_dir": "services/supabase/",
        "tech_dir": "",
        "filename_prefix": "",
        "filename_suffix": "RpcService",
        "file_extension": "ts",
        "custom_configs": {},
        "project_type": "web_frontend"
    },
    "supabase_ts_db_ops": {
        "name_format": "camel_case",
        "name_prefix": "",
        "name_suffix": "DbOp",
        "save_dir": "services/supabase/",
        "tech_dir": "",
        "filename_prefix": "",
        "filename_suffix": "DbOp",
        "file_extension": "ts",
        "custom_configs": {},
        "project_type": "backend_server"
    },
    "supabase_py_services": {
        "name_format": "pascal_case",
        "name_prefix": "",
        "name_suffix": "Service",
        "save_dir": "services/supabase/",
        "tech_dir": "",
        "filename_prefix": "",
        "filename_suffix": "Service",
        "file_extension": "ts",
        "custom_configs": {},
        "project_type": "backend_server"
    },
    "supabase_py_rpc_services": {
        "name_format": "pascal_case",
        "name_prefix": "",
        "name_suffix": "RpcService",
        "save_dir": "services/supabase/",
        "tech_dir": "",
        "filename_prefix": "",
        "filename_suffix": "RpcService",
        "file_extension": "ts",
        "custom_configs": {},
        "project_type": "backend_server"
    },
    "supabase_py_db_ops": {
        "name_format": "camel_case",
        "name_prefix": "",
        "name_suffix": "DbOp",
        "save_dir": "services/supabase/",
        "tech_dir": "",
        "filename_prefix": "",
        "filename_suffix": "DbOp",
        "file_extension": "ts",
        "custom_configs": {},
        "project_type": "web_backend"
    },
    "javascript_helpers": {
        "name_format": "camel_case",
        "name_prefix": "",
        "name_suffix": "Helper",
        "save_dir": "lib/helpers/",
        "tech_dir": "",
        "filename_prefix": "",
        "filename_suffix": "Helper",
        "file_extension": "js",
        "custom_configs": {},
        "project_type": "web_frontend"
    },
    "javascript_utils": {
        "name_format": "camel_case",
        "name_prefix": "",
        "name_suffix": "Util",
        "save_dir": "lib/utils/",
        "tech_dir": "",
        "filename_prefix": "",
        "filename_suffix": "Util",
        "file_extension": "js",
        "custom_configs": {},
        "project_type": "web_frontend"
    },
    "sql_procedures": {
        "name_format": "snake_case",
        "name_prefix": "",
        "name_suffix": "_procedure",
        "save_dir": "sql/procedures/",
        "tech_dir": "",
        "filename_prefix": "",
        "filename_suffix": "_procedure",
        "file_extension": "sql",
        "custom_configs": {},
        "project_type": "cloud_database"
    },
    "sql_triggers": {
        "name_format": "snake_case",
        "name_prefix": "",
        "name_suffix": "_trigger",
        "save_dir": "sql/triggers/",
        "tech_dir": "",
        "filename_prefix": "",
        "filename_suffix": "_trigger",
        "file_extension": "sql",
        "custom_configs": {},
        "project_type": "cloud_database"
    },
    "sql_views": {
        "name_format": "snake_case",
        "name_prefix": "",
        "name_suffix": "_view",
        "save_dir": "sql/views/",
        "tech_dir": "",
        "filename_prefix": "",
        "filename_suffix": "_view",
        "file_extension": "sql",
        "custom_configs": {},
        "project_type": "cloud_database"
    },
    "sql_schemas": {
        "name_format": "snake_case",
        "name_prefix": "",
        "name_suffix": "_schema",
        "save_dir": "sql/schemas/",
        "tech_dir": "",
        "filename_prefix": "",
        "filename_suffix": "_schema",
        "file_extension": "sql",
        "custom_configs": {},
        "project_type": "cloud_database"
    },
    "python_services": {
        "name_format": "snake_case",
        "name_prefix": "",
        "name_suffix": "_service",
        "save_dir": "python/services/",
        "tech_dir": "",
        "filename_prefix": "",
        "filename_suffix": "_service",
        "file_extension": "py",
        "custom_configs": {},
        "project_type": "backend_server"
    },
    "python_helpers": {
        "name_format": "snake_case",
        "name_prefix": "",
        "name_suffix": "_helper",
        "save_dir": "python/helpers/",
        "tech_dir": "",
        "filename_prefix": "",
        "filename_suffix": "_helper",
        "file_extension": "py",
        "custom_configs": {},
        "project_type": "backend_server"
    },
    "python_utils": {
        "name_format": "snake_case",
        "name_prefix": "",
        "name_suffix": "_util",
        "save_dir": "python/utils/",
        "tech_dir": "",
        "filename_prefix": "",
        "filename_suffix": "_util",
        "file_extension": "py",
        "custom_configs": {},
        "project_type": "backend_server"
    },
    "python_models": {
        "name_format": "snake_case",
        "name_prefix": "",
        "name_suffix": "_model",
        "save_dir": "python/models/",
        "tech_dir": "",
        "filename_prefix": "",
        "filename_suffix": "_model",
        "file_extension": "py",
        "custom_configs": {},
        "project_type": "backend_server"
    },
    "python_sql": {
        "name_format": "snake_case",
        "name_prefix": "",
        "name_suffix": "_sql",
        "save_dir": "python/sql/",
        "tech_dir": "",
        "filename_prefix": "",
        "filename_suffix": "_sql",
        "file_extension": "py",
        "custom_configs": {},
        "project_type": "backend_server"
    },
    "python_tests": {
        "name_format": "snake_case",
        "name_prefix": "",
        "name_suffix": "_test",
        "save_dir": "python/tests/",
        "tech_dir": "",
        "filename_prefix": "",
        "filename_suffix": "_test",
        "file_extension": "py",
        "custom_configs": {},
        "project_type": "backend_server"
    },
    "python_functions": {
        "name_format": "snake_case",
        "name_prefix": "",
        "name_suffix": "_function",
        "save_dir": "python/functions/",
        "tech_dir": "",
        "filename_prefix": "",
        "filename_suffix": "_function",
        "file_extension": "py",
        "custom_configs": {},
        "project_type": "backend_server"
    },
    "python_classes": {
        "name_format": "pascal_case",
        "name_prefix": "",
        "name_suffix": "Class",
        "save_dir": "python/classes/",
        "tech_dir": "",
        "filename_prefix": "",
        "filename_suffix": "Class",
        "file_extension": "py",
        "custom_configs": {},
        "project_type": "backend_server"
    },
    "python_modules": {
        "name_format": "snake_case",
        "name_prefix": "",
        "name_suffix": "_module",
        "save_dir": "python/modules/",
        "tech_dir": "",
        "filename_prefix": "",
        "filename_suffix": "_module",
        "file_extension": "py",
        "custom_configs": {},
        "project_type": "backend_server"
    }
}
