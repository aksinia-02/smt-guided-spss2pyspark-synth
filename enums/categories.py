from enum import Enum


class Category(Enum):
    DATE_NAMESPACE = "date_namespace"
    CAST_TYPE = "cast_type"
    STRING_FUNCTION = "string_function"

    def __repr__(self) -> str:
        return f"'{self.value}'"