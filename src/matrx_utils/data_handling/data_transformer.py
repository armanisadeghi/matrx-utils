import inspect
import random
import re
import json
import datetime
import uuid
import decimal
from matrx_utils import vcprint
from matrx_utils.data_handling.validation.validators import URLValidator, validate_email
import inflect
from .utils import get_random_text_entry

random_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")


class SingletonMeta(type):
    """A metaclass for creating a Singleton base class."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class DataTransformer(metaclass=SingletonMeta):
    def __init__(self):
        self.inflect_engine = inflect.engine()
        # self.code_handler = CodeHandler() # Not used anywhere.
        self.verbose = False
        self.debug = False
        self.info = False
        self.enum_list = []
        self.sql_to_typescript_types = {
            "uuid": "string",
            "text": "string",
            "_text": "string[]",
            "_varchar": "string[]",
            "character varying": "string",
            "varchar": "string",
            "bool": "boolean",
            "int2": "number",
            "int4": "number",
            "int8": "number",
            "float4": "number",
            "float8": "number",
            "_uuid": "string[]",
            "_jsonb": "Record<string, unknown>[]",
            "jsonb": "Record<string, unknown>",
            "json": "Record<string, unknown>",
            "boolean": "boolean",
            "smallint": "number",
            "bigint": "number",
            "integer": "number",
            "real": "number",
            "double precision": "number",
            "numeric": "number",
            "jsonb[]": "Record<string, unknown>[]",
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
            "_text": "string[]",
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
            "enum": "string",
            "ARRAY": "any[]",
            "USER-DEFINED": "string",
        }
        self.sql_to_python_types = {
            "uuid": "str",
            "text": "str",
            "character varying": "str",
            "boolean": "bool",
            "smallint": "int",
            "bigint": "int",
            "integer": "int",
            "real": "float",
            "double precision": "float",
            "numeric": "Decimal",
            "jsonb": "Dict[str, Any]",
            "jsonb[]": "List[Dict[str, Any]]",
            "json": "Dict[str, Any]",
            "data_type": "str",
            "data_source": "str",
            "data_destination": "str",
            "destination_component": "str",
            "function_role": "str",
            "broker_role": "str",
            "model_role": "str",
            "cognition_matrices": "str",
            "recipe_status": "str",
            "timestamp": "datetime",
            "timestamp with time zone": "datetime",
            "date": "date",
            "time": "time",
            "interval": "timedelta",
            "bytea": "bytes",
            "array": "List[Any]",
            "hstore": "Dict[str, str]",
            "point": "Tuple[float, float]",
            "line": "Tuple[float, float, float]",
            "lseg": "Tuple[Tuple[float, float], Tuple[float, float]]",
            "box": "Tuple[Tuple[float, float], Tuple[float, float]]",
            "path": "List[Tuple[float, float]]",
            "polygon": "List[Tuple[float, float]]",
            "circle": "Tuple[Tuple[float, float], float]",
            "cidr": "str",
            "inet": "str",
            "macaddr": "str",
            "tsvector": "str",
            "tsquery": "str",
            "uuid[]": "List[str]",
            "text[]": "List[str]",
            "integer[]": "List[int]",
            "boolean[]": "List[bool]",
            "char[]": "List[str]",
            "varchar[]": "List[str]",
            "xml": "str",
            "money": "Decimal",
            "bit": "str",
            "bit varying": "str",
            "timetz": "time",
            "timestamptz": "datetime",
            "txid_snapshot": "str",
            "enum": "str",
        }
        self.sql_to_matrx_schema = {
            "uuid": "uuid",
            "text": "string",
            "_text": "string[]",
            "character varying": "string",
            "varchar": "string",
            "_varchar": "string[]",
            "bool": "boolean",
            "int2": "number",
            "int4": "number",
            "int8": "number",
            "float4": "number",
            "float8": "number",
            "_uuid": "uuid",
            "_jsonb": "object",  # Updated from 'Record<string, unknown>[]' to 'object[]'
            "jsonb": "object",  # Updated from 'Record<string, unknown>' to 'object'
            "json": "object",  # Updated from 'Record<string, unknown>' to 'object'
            "boolean": "boolean",
            "smallint": "number",
            "bigint": "number",
            "integer": "number",
            "real": "number",
            "double precision": "number",
            "numeric": "number",
            "jsonb[]": "objectArray",  # Updated from 'Record<string, unknown>[]' to 'object[]'
            "data_type": "string",
            "data_source": "string",
            "data_destination": "string",
            "destination_component": "string",
            "function_role": "string",
            "broker_role": "string",
            "model_role": "string",
            "cognition_matrices": "string",
            "recipe_status": "string",
            "timestamp": "date",  # Updated to 'date' from 'Date'
            "timestamp with time zone": "date",  # Updated to 'date' from 'Date'
            "date": "date",  # Updated to 'date' from 'Date'
            "time": "string",  # Kept as 'string' since 'time' isn't defined
            "interval": "string",
            "bytea": "any",  # Uint8Array isn't part of DataType, so using 'any'
            "array": "any[]",
            "hstore": "object",  # Updated from 'Record<string, string>' to 'object'
            "point": "tuple",  # Updated to 'tuple' to represent coordinate tuples
            "line": "tuple",  # Updated to 'tuple' to represent line tuples
            "lseg": "tuple",  # Updated to 'tuple' to represent segment tuples
            "box": "tuple",  # Updated to 'tuple' to represent box tuples
            "path": "array",  # Updated to 'array' since it's an array of points
            "polygon": "array",  # Updated to 'array' for array of coordinates
            "circle": "object",  # Updated to 'object' for circle structure
            "cidr": "string",
            "inet": "string",
            "macaddr": "string",
            "tsvector": "string",
            "tsquery": "string",
            "uuid[]": "stringArray",
            "text[]": "stringArray",
            "integer[]": "number[]",
            "boolean[]": "boolean[]",
            "char[]": "stringArray",
            "varchar[]": "stringArray",
            "xml": "string",
            "money": "string",
            "bit": "string",
            "bit varying": "string",
            "timetz": "string",
            "timestamptz": "date",  # Updated to 'date' from 'Date'
            "txid_snapshot": "string",
            "enum": "enum",  # Updated to 'enum'
            "ARRAY": "array",  # Updated to 'array'
            "USER-DEFINED": "string",  # Kept as 'string' for user-defined types
        }
        self.sql_to_python_models_field = {
            "uuid": "UUIDField",
            "text": "TextField",
            "_text": "JSONBField",
            "_varchar": "JSONBField",
            "character varying": "CharField",
            "varchar": "CharField",
            "bool": "BooleanField",
            "int2": "SmallIntegerField",
            "int4": "IntegerField",
            "int8": "BigIntegerField",
            "float4": "FloatField",
            "float8": "FloatField",
            "_uuid": "UUIDArrayField",
            "_jsonb": "JSONBArrayField",  # Array of JSONB objects using JSONBArrayField
            "jsonb": "JSONBField",
            "json": "JSONField",
            "boolean": "BooleanField",
            "smallint": "SmallIntegerField",
            "bigint": "BigIntegerField",
            "integer": "IntegerField",
            "real": "FloatField",
            "double precision": "FloatField",
            "numeric": "DecimalField",  # DecimalField for numeric/decimal types
            "jsonb[]": "JSONBArrayField",  # Using JSONBArrayField for arrays of JSONB
            "data_type": "CharField",
            "data_source": "CharField",
            "data_destination": "CharField",
            "destination_component": "CharField",
            "function_role": "CharField",
            "broker_role": "CharField",
            "model_role": "CharField",
            "cognition_matrices": "CharField",
            "recipe_status": "CharField",
            "timestamp": "DateTimeField",  # Mapping timestamp to DateTimeField
            "timestamp with time zone": "DateTimeField",
            "date": "DateField",
            "time": "TimeField",  # Kept as TimeField
            "interval": "TimeDeltaField",  # Using TimeDeltaField for interval
            "bytea": "BinaryField",  # Mapping bytea to BinaryField
            "array": "PrimitiveArrayField",  # Using PrimitiveArrayField for generic array types
            "hstore": "HStoreField",  # Mapping hstore to HStoreField
            "point": "PointField",  # Using PointField for geometric data
            "line": "PrimitiveArrayField",  # No LineField, using array fallback
            "lseg": "PrimitiveArrayField",  # No LsegField, using array fallback
            "box": "PrimitiveArrayField",  # No BoxField, using array fallback
            "path": "ArrayField",  # Using ArrayField for arrays of points
            "polygon": "ArrayField",  # Using ArrayField for array of coordinates
            "circle": "PrimitiveArrayField",  # No CircleField, using array fallback
            "cidr": "IPNetworkField",  # Using IPNetworkField for CIDR
            "inet": "IPAddressField",  # Using general IPAddressField for both IPv4 and IPv6
            "macaddr": "MacAddressField",  # Mapping macaddr to MacAddressField
            "tsvector": "TextField",  # Mapping tsvector to TextField
            "tsquery": "TextField",  # Mapping tsquery to TextField
            "uuid[]": "UUIDArrayField",  # Array of UUIDs to UUIDArrayField
            "text[]": "TextArrayField",  # Using TextArrayField for array of text
            "integer[]": "IntegerArrayField",  # Array of integers to IntegerArrayField
            "boolean[]": "BooleanArrayField",  # Array of booleans to BooleanArrayField
            "char[]": "ArrayField",  # Using ArrayField for array of char
            "varchar[]": "ArrayField",  # Using ArrayField for array of varchar
            "xml": "TextField",  # Mapping XML to TextField
            "money": "MoneyField",  # Mapping money to MoneyField
            "bit": "CharField",  # Using CharField for bit type
            "bit varying": "CharField",  # Using CharField for varying bit
            "timetz": "TimeField",  # Mapping timetz to TimeField
            "timestamptz": "DateTimeField",  # Mapping timestamptz to DateTimeField
            "txid_snapshot": "CharField",  # Mapping txid_snapshot to CharField
            "enum": "EnumField",  # Mapping enum to EnumField
            "ARRAY": "ArrayField",  # Generic ARRAY mapped to ArrayField
            "USER-DEFINED": "CharField",  # User-defined types mapped to CharField
        }

    def set_enum_list(self, enum_list):
        vcprint(data=enum_list, title="Enum list updated with the following values", verbose=self.verbose,
                color="yellow")
        self.enum_list = enum_list

    def set_and_update_ts_enum_list(self, enum_list):
        vcprint(data=enum_list, title="Enum list updated with the following values", verbose=self.verbose,
                color="yellow")
        self.enum_list = enum_list
        self.update_transformation_list_with_enums()

    def get_enum_list(self):
        return self.enum_list

    def update_transformation_list_with_enums(self):
        """
        Updates various type mapping dictionaries to include enum types.
        Each dictionary gets its own specific mapping type for enums.
        Logs any unhandled mapping cases.
        """
        # Define known mapping dictionaries and their enum type values
        mapping_configs = {
            'sql_to_typescript_types': 'string',
            'sql_to_python_types': 'str',
            'sql_to_matrx_schema': 'string',
            'sql_to_python_models_field': 'CharField'
        }

        # Update each mapping dictionary if it exists
        for enum in self.enum_list:
            for mapping_name, enum_type in mapping_configs.items():
                mapping_dict = getattr(self, mapping_name, None)

                if mapping_dict is not None:
                    mapping_dict[enum] = enum_type
                else:
                    from matrx_utils import vcprint
                    vcprint(
                        data={
                            'error': f'Missing mapping dictionary',
                            'mapping_name': mapping_name,
                            'enum': enum
                        },
                        title='Enum Mapping Error',
                        color='red'
                    )

        # Check if there are any other mapping dictionaries that start with 'sql_to_'
        for attr_name in dir(self):
            if attr_name.startswith('sql_to_') and attr_name not in mapping_configs:
                mapping_dict = getattr(self, attr_name)
                if isinstance(mapping_dict, dict):
                    # Log that we're defaulting to 'string' for this mapping
                    from matrx_utils import vcprint
                    for enum in self.enum_list:
                        mapping_dict[enum] = 'string'
                        vcprint(
                            data={
                                'warning': 'Using default string mapping',
                                'mapping_name': attr_name,
                                'enum': enum,
                                'default_value': 'string'
                            },
                            title='Default Enum Mapping',
                            pretty=True,
                            color='red'
                        )

    def method_name(self):
        return inspect.currentframe().f_back.f_code.co_name

    def to_rdx_model_format(self, value, data_type):
        if value is None:
            return "null"
        elif data_type == "USER-DEFINED":
            if value is None or (isinstance(value, str) and value.lower() == "none"):
                return "null"
            else:
                return f"'{value}'"
        elif isinstance(value, bool) or data_type == "boolean":
            return str(value).lower()
        elif isinstance(value, str):
            if value == "":
                return "''"
            elif value == "gen_random_uuid()":
                return "uuidv4()"
            elif value.lower() == "none":
                return "null"
            elif value == "[]" or data_type == "ARRAY":
                return value
            elif (value.startswith("{") and value.endswith("}")) or data_type in ["json", "jsonb"]:
                try:
                    json_obj = json.loads(value)
                    return json.dumps(json_obj)
                except json.JSONDecodeError:
                    return f"'{value}'"
            elif data_type in ["bigint", "smallint", "integer", "real"]:
                return value
            elif data_type in ["text", "character varying", "uuid"]:
                return f"'{value}'"
            else:
                return f"'{value}'"
        else:
            return str(value)

    def normalize_to_snake_case(self, s):
        if isinstance(s, str):
            s = re.sub(r'(?<!^)(?=[A-Z])', '_', s)
            s = re.sub(r'[^a-zA-Z0-9]+', '_', s)
            s = s.lower()
        return s

    def to_lower_case(self, s):
        if isinstance(s, str):
            return s.lower()
        return None

    def to_upper_case(self, s):
        if isinstance(s, str):
            return s.upper()
        return None

    def to_snake_case(self, s):
        if isinstance(s, str):
            normalized = self.normalize_to_snake_case(s)
            return normalized
        return None

    def to_kebab_case(self, s):
        if isinstance(s, str):
            normalized = self.normalize_to_snake_case(s)
            return normalized.replace('_', '-')
        return None

    def to_camel_case(self, s):
        if isinstance(s, str):
            normalized = self.normalize_to_snake_case(s)
            components = normalized.split('_')
            return components[0].lower() + ''.join(x.title() for x in components[1:])
        return None

    def to_pascal_case(self, s):
        if isinstance(s, str):
            normalized = self.normalize_to_snake_case(s)
            components = normalized.split('_')
            return ''.join(x.title() for x in components)
        return None

    def to_title_case(self, s):
        if isinstance(s, str):
            normalized = self.normalize_to_snake_case(s)
            components = normalized.split('_')
            return ' '.join(x.title() for x in components)
        return None

    def to_space_case(self, s):
        if isinstance(s, str):
            normalized = self.normalize_to_snake_case(s)
            components = normalized.split('_')
            return ' '.join(x.lower() for x in components)
        return None

    def to_plural(self, s):
        if isinstance(s, str):
            return self.inflect_engine.plural(s)
        return None

    def to_singular(self, s):
        if isinstance(s, str):
            return self.inflect_engine.singular_noun(s) or s
        return None

    def to_constant_case(self, s):
        if isinstance(s, str):
            return self.normalize_to_snake_case(s).upper()
        return None

    def to_dot_notation(self, s):
        if isinstance(s, str):
            return self.normalize_to_snake_case(s).replace('_', '.')
        return None

    def to_acronym(self, s):
        if isinstance(s, str):
            words = re.findall(r'\b\w', s.replace('_', ' '))
            return ''.join(words).upper()
        return None

    def remove_special_characters(self, s):
        if isinstance(s, str):
            return re.sub(r'[^a-zA-Z0-9_]', '', s)
        return None

    def to_valid_identifier(self, s):
        if isinstance(s, str):
            s = self.remove_special_characters(s)
            if s and s[0].isdigit():
                s = '_' + s
            return s
        return None

    def to_quoted_string(self, s):
        if isinstance(s, str):
            return f'"{s}"'
        return None

    def to_typescript_type(self, s):
        if s in self.sql_to_typescript_types:
            return self.sql_to_typescript_types[s]

        if s in self.sql_to_typescript_types.values():
            return s

        if s == "column_name":
            return s

        vcprint(f"ERROR! Typescript Type Not Found! Original Value: {s}", color="red")
        return f"any // ERROR! Original Value: {s} Type Not Found!"

    def to_typescript_type_enums_to_string(self, s, has_enum_labels=False):
        if has_enum_labels:
            return s
        if s in self.sql_to_typescript_types:
            return self.sql_to_typescript_types[s]

        if s in self.sql_to_typescript_types.values():
            return s

        if s == "column_name":
            return s

        vcprint(f"ERROR! Typescript Type Not Found! Original Value: {s}", color="red")
        return f"any // ERROR! Original Value: {s} Type Not Found!"

    def to_matrx_schema_type(self, s):
        if s in self.sql_to_matrx_schema:
            return self.sql_to_matrx_schema[s]

        if s in self.sql_to_matrx_schema.values():
            return s

        if s == "column_name":
            return s

        vcprint(f"ERROR! Matrx Schema Type Not Found! Original Value: {s}", color="red")
        return f"any // ERROR! Original Value: {s} Type Not Found!"

    def to_python_models_field(self, s):
        # Check if the SQL type exists in the mapping dictionary
        if s in self.sql_to_python_models_field:
            return self.sql_to_python_models_field[s]

        # If it's already one of the Python field types, return it as is
        if s in self.sql_to_python_models_field.values():
            return s

        # Special case for "column_name", assuming it's a direct pass-through
        if s == "column_name":
            return s

        # Error handling for cases where the SQL type is not found
        vcprint(f"ERROR! Python Model Field Not Found! Original Value: {s}", color="red")
        return f"Any # ERROR! Original Value: {s} Field Not Found!"

    def to_union_enum(self, values, for_enum=False):
        if values == "column_enum_options" or "":
            return None

        if self.debug:
            print("-" * 30 + "Debug Print: DataTransformer.to_union_enum" + "-" * 30)
            print(values)
        if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
            raise ValueError("Input must be a list of strings")

        formatted_values = [f'"{self.to_valid_identifier(v)}"' for v in values if v]

        if not formatted_values:
            return ""

        if for_enum:
            return ", ".join(formatted_values)
        else:
            return " | ".join(formatted_values)

    def backup_to_typescript_type(self, s):
        if isinstance(s, str):
            vcprint(s, "converting sql type to typescript type", color="yellow")
            value = self.sql_to_typescript_types.get(s.lower())

            vcprint(value, "typescript type", color="yellow")
            # return self.sql_to_typescript_types.get(s.lower(), 'any')
            return value
        return None

    def to_python_type(self, s):
        if isinstance(s, str):
            return self.sql_to_python_types.get(s.lower(), 'Any')
        return None

    def to_type_annotation(self, s, language='typescript'):
        if isinstance(s, str):
            if language.lower() == 'typescript':
                return self.sql_to_typescript_types.get(s.lower(), 'any')
            elif language.lower() == 'python':
                return self.sql_to_python_types.get(s.lower(), 'Any')
            else:
                return 'Unknown language'
        return None

    def to_comment(self, s, language='python'):
        if isinstance(s, str):
            comment_styles = {
                'python': f'# {s}',
                'javascript': f'// {s}',
                'html': f'<!-- {s} -->',
                'css': f'/* {s} */'
            }
            return comment_styles.get(language.lower(), f'# {s}')
        return None

    def to_url_safe(self, s):
        if isinstance(s, str):
            s = s.lower()
            s = re.sub(r'[^a-z0-9]+', '-', s)
            return s.strip('-')
        return None

    def convert_value_to_data_type(self, value, data_type):
        special_pattern = re.compile(r'^\{.*\}!$')
        if value in (None, "", "null", "NULL"):
            return None
        if special_pattern.match(str(value)):
            return str(value)
        try:
            if not data_type or data_type.lower() in ['blank', 'null', 'any', 'unknown', '']:
                return str(value)
            elif data_type == 'int':
                return int(value)
            elif data_type == 'float':
                return float(value)
            elif data_type == 'bool':
                return value.lower() in ['true', '1', 't', 'y', 'yes'] if isinstance(value, str) else bool(value)
            elif data_type in ['dict', 'json']:
                return json.loads(value) if isinstance(value, str) else (
                    value if isinstance(value, dict) else json.dumps(value))
            elif data_type == 'list':
                return json.loads(value) if isinstance(value, str) else (
                    value if isinstance(value, list) else json.dumps(value))
            elif data_type == 'str':
                return str(value)
            elif data_type == 'datetime':
                return datetime.datetime.fromisoformat(value)
            elif data_type == 'uuid':
                return uuid.UUID(value)
            elif data_type == 'decimal':
                return decimal.Decimal(value)
            elif data_type == 'url':
                validate = URLValidator()
                validate(value)
                return value
            elif data_type == 'email':
                validate_email(value)
                return value
            elif data_type == 'binary':
                return value.encode()
            else:
                return str(value)

        except Exception as e:
            print(f"Error converting value to data type: {e}")
            print(f"Value: {value}, Data Type: {data_type}")
            print(f"Returning value as string and proceeding...")
            return str(value)

    @property
    def class_name(self):
        return self.prettify_name(self.__class__.__name__)

    @property
    def class_id(self):
        return f"[MATRIX {self.class_name}]"

    @property
    def method_id(self):
        method_name = self.prettify_name(self.get_caller_method_name())
        return f"[MATRIX {self.class_name} {method_name}]: "

    def prettify_name(self, name: str) -> str:
        name = name.replace('_', ' ')
        name = re.sub(r'(?<!^)(?=[A-Z])', ' ', name)
        name = name.title()
        return name

    def get_caller_method_name(self):
        return inspect.stack()[3].function

    def print_method_name(self):
        print(f"This method is {self.method_id}")

    def print_class(self):
        print(f"This class is: {self.class_id}")

    def find_keys_without_terms(self, data, terms):
        def check_key_or_value(key_or_value):
            return not any(term in key_or_value for term in terms)

        def recursive_search(obj):
            values_without_terms = []

            if isinstance(obj, dict):
                for k, v in obj.items():
                    if check_key_or_value(k):
                        values_without_terms.append(k)
                    if isinstance(v, (dict, list)):
                        values_without_terms.extend(recursive_search(v))
                    elif check_key_or_value(str(v)):
                        values_without_terms.append(v)
            elif isinstance(obj, list):
                for item in obj:
                    if isinstance(item, (dict, list)):
                        values_without_terms.extend(recursive_search(item))
                    elif check_key_or_value(str(item)):
                        values_without_terms.append(item)

            return values_without_terms

        return recursive_search(data)

    def get_column_test_values(self, data_type, options):
        random_text = get_random_text_entry()
        test_value = f"{random_text}_{random_time}"
        random_key = random.choice(["some_key", "another_key", "last_key"])

        if options:
            return f'"{options[0]}"'

        elif data_type in ['text', 'character varying']:
            random_text = get_random_text_entry()
            return f'"{random_text}_{random_time}"'

        elif data_type == 'uuid':
            return f'"{uuid.uuid4()}"'

        elif data_type == 'bigint':
            return str(random.randint(5, 500))

        elif data_type.startswith('jsonb'):
            return f"jsonb_build_object('{random_key}', '{random_text}')"

        elif data_type.endswith('[]'):
            return f"ARRAY[jsonb_build_object('{random_key}', '{random_text}')]::jsonb[]"

        elif data_type == 'boolean':
            return str(random.choice([True, False]))

        else:
            return f"ERROR DATA TRANSFORMER DOES NOT HAVE DATA TYPE: {data_type}"

    def replace_dict_keys(self, data, key_map, replace_in_lists=True):
        """
        Recursively replaces keys in a dictionary (including nested dictionaries and lists) based on a given key mapping.

        Args:
            data (dict or list): The input dictionary (or nested structure) to process.
            key_map (dict): A mapping of keys to their replacement values.
            replace_in_lists (bool): Whether to apply key replacements inside lists. Defaults to True.

        Returns:
            dict or list: A new dictionary or list with keys replaced as per the mapping.
        """
        if isinstance(data, dict):
            new_dict = {}
            for key, value in data.items():
                new_key = key_map.get(key, key)
                new_dict[new_key] = self.replace_dict_keys(value, key_map, replace_in_lists)
            return new_dict

        elif isinstance(data, list) and replace_in_lists:
            return [self.replace_dict_keys(item, key_map, replace_in_lists) for item in data]

        else:
            return data

    def convert_keys_to_camel_case(self, data, replace_in_lists=True):
        """
        Recursively converts keys in a dictionary (including nested dictionaries and lists) from snake_case to camelCase.

        Args:
            data (dict or list): The input dictionary (or nested structure) to process.
            replace_in_lists (bool): Whether to apply key conversions inside lists. Defaults to True.

        Returns:
            dict or list: A new dictionary or list with keys converted to camelCase.
        """
        if isinstance(data, dict):
            new_dict = {}
            for key, value in data.items():
                new_key = self.to_camel_case(key)  # Convert key to camelCase
                new_dict[new_key] = self.convert_keys_to_camel_case(value, replace_in_lists)
            return new_dict

        elif isinstance(data, list) and replace_in_lists:
            return [self.convert_keys_to_camel_case(item, replace_in_lists) for item in data]

        else:
            return data

    def python_dict_to_ts(self, obj, indent=0):
        if isinstance(obj, dict):
            ts_obj = []
            for key, value in obj.items():
                formatted_key = key if key.isidentifier() else f'"{key}"'
                formatted_value = self.python_dict_to_ts(value, indent + 4)
                ts_obj.append(f"{formatted_key}: {formatted_value}")
            return "{\n" + " " * (indent + 4) + (",\n" + " " * (indent + 4)).join(ts_obj) + "\n" + " " * indent + "}"
        elif isinstance(obj, list):
            formatted_items = [self.python_dict_to_ts(item, indent + 4) for item in obj]
            return "[\n" + " " * (indent + 4) + (",\n" + " " * (indent + 4)).join(
                formatted_items) + "\n" + " " * indent + "]"
        elif isinstance(obj, str):
            return f'"{obj}"'
        else:
            return json.dumps(obj)

    def python_dict_to_ts_with_updates(self, name, obj, keys_to_camel=True, export=True, as_const=False, ts_type=None,
                                       indent=0):
        if keys_to_camel:
            obj = self.convert_keys_to_camel_case(obj)

        ts_declaration = ""

        # Add export if required
        if export:
            ts_declaration += "export "

        # Add the variable name and type
        ts_declaration += f"const {name}"
        if ts_type:
            ts_declaration += f": {ts_type}"

        # Convert the Python dictionary to TypeScript format
        ts_declaration += f" = {self.python_dict_to_ts(obj, indent)}"

        # Append `as const` if required
        if as_const:
            ts_declaration += " as const"

        # End the declaration with a semicolon
        ts_declaration += ";\n"

        return ts_declaration


# Test the transformations
if __name__ == "__main__":
    transformer = DataTransformer()
    test_string = "Ai Matrix"

    print(f"Original: {test_string}")
    print(f"to_plural: {transformer.to_plural(test_string)}")
    print(f"to_singular: {transformer.to_singular(test_string)}")
    print(f"to_constant_case: {transformer.to_constant_case(test_string)}")
    print(f"to_dot_notation: {transformer.to_dot_notation(test_string)}")
    print(f"to_acronym: {transformer.to_acronym(test_string)}")
    print(f"remove_special_characters: {transformer.remove_special_characters(test_string)}")
    print(f"to_valid_identifier: {transformer.to_valid_identifier(test_string)}")
    print(f"to_quoted_string: {transformer.to_quoted_string(test_string)}")
    print(f"to_type_annotation (Python): {transformer.to_type_annotation('integer', 'python')}")
    print(f"to_type_annotation (TypeScript): {transformer.to_type_annotation('integer', 'typescript')}")
    print(f"to_comment: {transformer.to_comment(test_string)}")
    print(f"to_url_safe: {transformer.to_url_safe(test_string)}")

    print(f"to_lower_case: {transformer.to_lower_case(test_string)}")
    print(f"to_upper_case: {transformer.to_upper_case(test_string)}")
    print(f"to_snake_case: {transformer.to_snake_case(test_string)}")
    print(f"to_kebab_case: {transformer.to_kebab_case(test_string)}")
    print(f"to_camel_case: {transformer.to_camel_case(test_string)}")
    print(f"to_pascal_case: {transformer.to_pascal_case(test_string)}")
    print(f"to_title_case: {transformer.to_title_case(test_string)}")
    print(f"to_space_case: {transformer.to_space_case(test_string)}")

    # Test SQL to TypeScript and Python type conversions
    sql_types = ["integer", "text", "timestamp", "jsonb", "boolean[]", "point", "interval"]
    print("\nSQL to TypeScript and Python type conversions:")
    for sql_type in sql_types:
        print(f"SQL: {sql_type}")
        print(f"  TypeScript: {transformer.to_type_annotation(sql_type, 'typescript')}")
        print(f"  Python: {transformer.to_type_annotation(sql_type, 'python')}")