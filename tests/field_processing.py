from matrx_utils import clear_terminal, vcprint
from matrx_utils.field_processing import (process_batch_field_definitions,
                                          process_object_field_definitions)

field_defs = {
    "name": {"type": str, "always_include": True, "default": "===default value==="},
    "age": {"type": int, "always_include": False},
    "scores": {"type": list, "list_type": int, "always_include": False},
    "user_name": {"type": str, "always_include": True, "default": "===default value==="},
    "primary_email": {"type": str, "always_include": True, "default": "===default value==="},
    "secondary_email": {"type": str, "always_include": True, "default": "===default value==="},
    "first_name": {"type": str, "always_include": True, "default": "===default value==="},
    "person_age": {"type": int, "always_include": False},
    "test_scores": {"type": list, "list_type": int, "always_include": False},
    "do_you_like_pizza": {"type": bool, "always_include": True, "default": True},
    "audio_voice": {"type": str, "always_include": False, "default": None},
}

field_map = {"some_new_field": "test_scores", "another_new_field": "person_age"}

person = {
    "name": "John",
    "age": 25,
    "scores": [1, 2, 3],
    "user_name": "TEST PASSED-USER_NAME",
    "primary_email": "TEST PASSED-PRIMARY_EMAIL",
    "firstName": "TEST PASSED-FIRST_NAME",
    "secondaryEmail": "TEST PASSED-SECONDARY_EMAIL",
    "wrongField": "TEST FAILED - WRONG FIELD",
    "some_other_field": "TEST FAILED - SOME OTHER FIELD",
    "some_new_field": [999, 888],
    "anotherNewField": 101,
    "do_you_like_pizza": "default",
    "audioVoice": "default",
}

if __name__ == '__main__':
    clear_terminal()
    result = process_object_field_definitions(field_defs, person, convert_camel_case=True, fieldname_map=field_map)
    vcprint(result, pretty=True, color="blue")

    result_camel = process_object_field_definitions(field_defs, person, convert_camel_case=True,
                                                    fieldname_map=field_map)
    vcprint(result_camel, pretty=True, color="green")

    people = [
        {
            "name": "John",
            "age": 25,
            "scores": [1, 2, 3],
            "user_name": "TEST PASSED-USER_NAME",
            "primary_email": "TEST PASSED-PRIMARY_EMAIL",
            "secondaryEmail": "TEST PASSED-SECONDARY_EMAIL",
        },
        {
            "name": "Jane",
            "age": 30,
            "scores": [4, 5, 6],
            "user_name": "TEST PASSED-USER_NAME",
            "primary_email": "TEST PASSED-PRIMARY_EMAIL",
            "secondaryEmail": "TEST PASSED-SECONDARY_EMAIL",
        },
    ]

    batch_result = process_batch_field_definitions(field_defs, people, convert_camel_case=True)
    vcprint(batch_result, pretty=True, color="green")
