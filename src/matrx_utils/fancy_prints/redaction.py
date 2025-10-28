def is_sensitive(key, additional_keys=None):
    """Check if a key suggests sensitive data."""
    sensitive_patterns = [
        'password', 'secret', 'key', 'token', 'auth', 'credential',
        'private', 'pass', 'pwd', 'api_key', 'access_key', 'secret_key'
    ]
    if additional_keys:
        sensitive_patterns.extend(additional_keys)
    key_lower = key.lower()
    return any(pattern in key_lower for pattern in sensitive_patterns)

def redact_object(obj, redact_keys=None):
    """Recursively redact sensitive data in an object."""
    def redact_value(value):
        str_value = str(value)
        length = len(str_value)
        if length <= 4:
            return '*' * length
        elif length <= 8:
            return str_value[0] + '*' * (length - 2) + str_value[-1]
        elif length <= 16:
            return str_value[:2] + '*' * (length - 4) + str_value[-2:]
        else:
            return str_value[:3] + '*' * (length - 6) + str_value[-3:]

    if isinstance(obj, dict):
        return {
            k: redact_object(v, redact_keys) if not is_sensitive(k, redact_keys)
            else redact_value(v) if not isinstance(v, (dict, list))
            else redact_object(v, redact_keys)
            for k, v in obj.items()
        }
    elif isinstance(obj, list):
        return [redact_object(item, redact_keys) for item in obj]
    return obj

def redact_string(value):
    """Redact a string value directly."""
    str_value = str(value)
    length = len(str_value)
    if length <= 4:
        return '*' * length
    elif length <= 8:
        return str_value[0] + '*' * (length - 2) + str_value[-1]
    elif length <= 16:
        return str_value[:2] + '*' * (length - 4) + str_value[-2:]
    else:
        return str_value[:3] + '*' * (length - 6) + str_value[-3:]
