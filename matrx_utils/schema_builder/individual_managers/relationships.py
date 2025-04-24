from matrx_utils import vcprint

from matrx_utils.schema_builder.individual_managers.common import (
    schema_builder_verbose,
    schema_builder_debug,
    schema_builder_info,
    schema_builder_utils,
)


class Relationship:
    def __init__(
        self,
        constraint_name,
        column,
        foreign_column,
        target_table=None,
        source_table=None,
    ):
        self.utils = schema_builder_utils
        self.constraint_name = constraint_name
        self.column = column
        self.foreign_column = foreign_column
        self.target_table = target_table  # Foreign key-related table
        self.source_table = source_table  # Inverse foreign key source table
        self.frontend_column = self.utils.to_camel_case(self.column)
        self.frontend_foreign_column = self.utils.to_camel_case(self.foreign_column)
        self.frontend_target_table = self.utils.to_camel_case(target_table.name) if target_table is not None else None
        self.frontend_source_table = self.utils.to_camel_case(source_table.name) if source_table is not None else None

        self.verbose = schema_builder_verbose
        self.debug = schema_builder_debug
        self.info = schema_builder_info

        vcprint(
            self.to_dict(),
            title="Relationship initialized",
            pretty=True,
            verbose=self.verbose,
            color="yellow",
        )

    def __repr__(self):
        return f"<Relationship {self.constraint_name}: {self.column} -> {self.foreign_column}>"

    def to_dict(self):
        return {
            "constraint_name": self.constraint_name,
            "column": self.column,
            "foreign_column": self.foreign_column,
            "target_table": self.target_table,
            "source_table": self.source_table,
            "frontend_column": self.frontend_column,
            "frontend_foreign_column": self.frontend_foreign_column,
            "frontend_target_table": self.frontend_target_table,
            "frontend_source_table": self.frontend_source_table,
        }
