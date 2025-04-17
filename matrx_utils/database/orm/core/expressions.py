class F:
    """
    This mimics Django's F-expressions for arithmetic or other
    operations directly on DB fields.
    """

    def __init__(self, field_name: str):
        self.field_name = field_name

    def __add__(self, other):
        return Expression(self.field_name, "+", other)

    def __sub__(self, other):
        return Expression(self.field_name, "-", other)


class Expression:
    """
    Basic wrapper for an expression, e.g. (field + 5).
    The ORM can interpret this to produce SQL like `field = field + 5`.
    """

    def __init__(self, field_name: str, operator: str, value):
        self.field_name = field_name
        self.operator = operator
        self.value = value
