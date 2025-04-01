# config.py

import os

from aidream.settings import BASE_DIR, TEMP_DIR


CONFIG = {
    "directories": {
        "react_dir": os.path.join(TEMP_DIR, "codeGenReact"),
        "typescript_dir": "types",
        "selectors_dir": "selectors",
        "models_dir": "models",
        "slice_dir": "slices",
        "service_dir": "services",
        "middleware_dir": "middlewares",
        "reducers_dir": "reducers",
        "actions_dir": "actions",
        "components_dir": "components",
        "redux_dir": "redux",
    },
    "naming_conventions": {
        "filename_format": "{table_name}{suffix}",  # Correct format
        "type_suffix": "Type.ts",
        "model_suffix": "Model.ts",
        "slice_suffix": "Slice.ts",
        "reducer_suffix": "Reducer.ts",
        "selector_suffix": "Selectors.ts",
        "service_suffix": "Service.ts",
        "middleware_suffix": "Middleware.ts",
        "component_suffix": "Component.tsx",
        "action_creators_suffix": "ActionCreators.ts",
        "store_suffix": ".ts"
    },
    "typescript_type_mappings": {
        "id": "number",
        "endsWithId": "number",
        "createdAt": "Date",
        "updatedAt": "Date",
        "startsWithIs": "boolean",
        "default": "string",
    },
    "imports": {
        "redux_imports": "import { createSlice, PayloadAction } from '@reduxjs/toolkit';",
        "orm_imports": "import { createSelector } from 'redux-orm';\nimport orm from '@/redux/orm';",
        "supabase_imports": "import supabase from '@/utils/supabase/client';\nimport { SupabaseClient } from '@supabase/supabase-js';",
        "redux_orm_model_imports": "import { Model, attr, fk, many } from 'redux-orm';",
        "react_imports": "import React, { useState } from 'react';\nimport { useSelector, useDispatch } from 'react-redux';",
        "mantine_imports": "import { Table, Button, Modal, TextInput, Group, List, Divider } from '@mantine/core';",
    },
    "type_map": {
        "uuid": "string",
        "text": "string",
        "character varying": "string",
        "boolean": "boolean",
        "smallint": "number",
        "bigint": "number",
        "integer": "number",
        "real": "number",
        "jsonb": "any",
        "jsonb[]": "any[]",
        "json": "any",
        "data_type": "string",
        "data_source": "string",
        "data_destination": "string",
        "destination_component": "string",
        "function_role": "string",
        "broker_role": "string",
        "model_role": "string",
        "cognition_matrices": "string",
        "recipe_status": "string"
    }
}

def get_config():
    return CONFIG
