from typing import Any, Type
from enum import Enum


def validate_enum(value: Any, enum_type: Type[Enum]) -> None:
    """
    Ensures the value is a valid member of an Enum.
    """
    if value not in enum_type.__members__.values():
        raise ValueError(f"Invalid value '{value}'. Must be one of {list(enum_type.__members__.values())}")
