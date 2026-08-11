from enum import Enum


class Category(Enum):
    DATE_NAMESPACE = "date_namespace"

    def __repr__(self) -> str:
        return f"'{self.value}'"