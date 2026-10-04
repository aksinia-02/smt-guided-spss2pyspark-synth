from typing import List

from .base_registry import BasePrimitiveRegistry
from enums.smt_types import DateType, PrimitiveType
from enums.categories import Category
from .Semantics import FuncSemantics

class ConditionsRegistry(BasePrimitiveRegistry):
    """Handles conditions like is null, is not null, is empty, etc."""
    
    def register_all(self) -> None:
        self.init_conditions()

    def init_conditions(self) -> None:

        name = f"is_null"
        return_type = PrimitiveType.TYPE_BOOLEAN
        arg_types = [(PrimitiveType.TYPE_ANY, True)]
        category = Category.CONDITION

        pyspark_str = f"F.col({{0}}).isNull()"
        semantics = FuncSemantics(
            name=f"is_null",
            target_type=PrimitiveType.TYPE_BOOLEAN,
            import_type=PrimitiveType.TYPE_ANY,
            weight=1000
        )
        self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str, python_eval=None, func=True)

        name = f"is_not_null"
        return_type = PrimitiveType.TYPE_BOOLEAN
        arg_types = [(PrimitiveType.TYPE_ANY, True)]
        category = Category.CONDITION

        pyspark_str = f"F.col({{0}}).isNotNull()"
        semantics = FuncSemantics(
            name=f"is_not_null",
            target_type=PrimitiveType.TYPE_BOOLEAN,
            import_type=PrimitiveType.TYPE_ANY,
            weight=1000
        )
        self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str, python_eval=None, func=True)