BROKER_DEFINITION = {
    "name": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
    },
    "id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
    },
    "value": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
    },
    "ready": {
        "REQUIRED": False,
        "DEFAULT": True,
        "VALIDATION": None,
        "DATA_TYPE": "boolean",
        "CONVERSION": None,
        "REFERENCE": None,
    },
}

OVERRIDE_DEFINITION = {
    "model_override": {
        "REQUIRED": False,
        "DEFAULT": "",
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
    },
    "processor_overrides": {
        "REQUIRED": False,
        "DEFAULT": {},
        "VALIDATION": None,
        "DATA_TYPE": "object",
        "CONVERSION": None,
        "REFERENCE": None,
    },
    "other_overrides": {
        "REQUIRED": False,
        "DEFAULT": {},
        "VALIDATION": None,
        "DATA_TYPE": "object",
        "CONVERSION": None,
        "REFERENCE": None,
    },
}

definition = {
    "cockpit_id": {
        "REQUIRED": True,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
    },
    "broker_values": {
        "REQUIRED": True,
        "DEFAULT": [],
        "VALIDATION": None,
        "DATA_TYPE": "array",
        "CONVERSION": "convert_broker_data",
        "REFERENCE": BROKER_DEFINITION,
    },
    "overrides": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "object",
        "CONVERSION": None,
        "REFERENCE": OVERRIDE_DEFINITION,
    },
}


def get_reference_names(definition: dict) -> dict:
    reference_names = {}

    for field, properties in definition.items():
        reference = properties.get("REFERENCE")
        if reference is not None:
            for var_name, var_value in globals().items():
                if var_value is reference:
                    reference_names[field] = var_name
                    break
            else:
                reference_names[field] = str(reference)
        else:
            reference_names[field] = None

    return reference_names


print(get_reference_names(definition))
