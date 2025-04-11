import ipaddress
import json
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal


class TypeConverter:
    @staticmethod
    def to_python(value, field_type):
        if value is None:
            return None

        if field_type == "int":
            return int(value)
        elif field_type == "float":
            return float(value)
        elif field_type == "bool":
            return bool(value)
        elif field_type == "str":
            return str(value)
        elif field_type == "datetime":
            return datetime.fromisoformat(value) if isinstance(value, str) else value
        elif field_type == "date":
            return date.fromisoformat(value) if isinstance(value, str) else value
        elif field_type == "uuid":
            return UUID(value) if isinstance(value, str) else value
        elif field_type == "json":
            return json.loads(value) if isinstance(value, str) else value
        elif field_type == "decimal":
            return Decimal(value) if isinstance(value, (str, int, float)) else value
        elif field_type.startswith("array"):
            item_type = field_type.split(":")[1]
            return [TypeConverter.to_python(item, item_type) for item in value]
        else:
            return value

    @staticmethod
    def get_db_prep_value(value, field_type):
        if value is None:
            return None

        if field_type in ["int", "float", "bool", "str"]:
            return value
        elif field_type in ["datetime", "date"]:
            return value.isoformat()
        elif field_type == "uuid":
            return str(value)
        elif field_type == "json":
            return json.dumps(value)
        elif field_type == "decimal":
            return str(value)
        elif field_type.startswith("array"):
            item_type = field_type.split(":")[1]
            return [TypeConverter.get_db_prep_value(item, item_type) for item in value]
        else:
            return value


class CustomTypeConverter(TypeConverter):
    custom_converters = {}

    @classmethod
    def register_converter(cls, python_type, to_db_func, to_python_func):
        cls.custom_converters[python_type] = (to_db_func, to_python_func)

    @classmethod
    def to_python(cls, value, field_type):
        if field_type in cls.custom_converters:
            return cls.custom_converters[field_type][1](value)
        return super().to_python(value, field_type)

    @classmethod
    def get_db_prep_value(cls, value, field_type):
        if field_type in cls.custom_converters:
            return cls.custom_converters[field_type][0](value)
        return super().get_db_prep_value(value, field_type)


# Usage
CustomTypeConverter.register_converter("ipaddress", lambda ip: str(ip), lambda ip_str: ipaddress.ip_address(ip_str))


# Usage
def convert_query_results(results, model):
    converted = []
    for row in results:
        converted_row = {}
        for field_name, field in model._fields.items():
            if field_name in row:
                converted_row[field_name] = TypeConverter.to_python(row[field_name], field.field_type)
        converted.append(converted_row)
    return converted


def prepare_query_params(params, model):
    prepared = {}
    for field_name, value in params.items():
        if field_name in model._fields:
            prepared[field_name] = TypeConverter.get_db_prep_value(value, model._fields[field_name].field_type)
    return prepared
