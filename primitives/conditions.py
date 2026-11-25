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
        z3_rep = f"null"
        semantics = FuncSemantics(
            name=f"is_null",
            target_type=PrimitiveType.TYPE_BOOLEAN,
            import_type=PrimitiveType.TYPE_ANY,
            weight=0
        )
        self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str, python_eval=None, func=True)

        name = f"is_not_null"
        return_type = PrimitiveType.TYPE_BOOLEAN
        arg_types = [(PrimitiveType.TYPE_ANY, True)]
        category = Category.CONDITION

        pyspark_str = f"F.col({{0}}).isNotNull()"
        z3_rep = f"not_null"
        semantics = FuncSemantics(
            name=f"is_not_null",
            target_type=PrimitiveType.TYPE_BOOLEAN,
            import_type=PrimitiveType.TYPE_ANY,
            weight=0
        )
        self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str, python_eval=None, func=True)

        name = f"="
        return_type = PrimitiveType.TYPE_BOOLEAN
        arg_types = [(PrimitiveType.TYPE_INT, True), (PrimitiveType.TYPE_INT, True)]
        category = Category.ARITHMETIC

        pyspark_str = f"{{0}}.eqNullSafe({{1}})"
        
        semantics = FuncSemantics(
            name=f"=",
            target_type=PrimitiveType.TYPE_INT,
            import_type=PrimitiveType.TYPE_INT,
            weight=50
        )
        self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str, func=True)

        for op in [">", "<", ">=", "<="]:
            return_type = PrimitiveType.TYPE_BOOLEAN
            arg_types = [(PrimitiveType.TYPE_INT, False), (PrimitiveType.TYPE_INT, False)]
            category = Category.ARITHMETIC

            pyspark_str = f"{{0}} {op} {{1}}"
            
            semantics = FuncSemantics(
                name=f"{op}",
                target_type=PrimitiveType.TYPE_BOOLEAN,
                import_type=PrimitiveType.TYPE_INT,
                weight=50
            )
            self.add_primitive(op, return_type, arg_types, category, semantics, pyspark_str, func=True)

        bool_map = {
            "and": "&",
            "or": "|",
        }

        for bool_cond in ['and', 'or', 'not']:
            name = f"{bool_cond}"
            return_type = PrimitiveType.TYPE_BOOLEAN
            if bool_cond == 'not':
                arg_types = [(PrimitiveType.TYPE_BOOLEAN, True)]
            else:
                arg_types = [(PrimitiveType.TYPE_BOOLEAN, True), (PrimitiveType.TYPE_BOOLEAN, True)]
            category = Category.CONDITION

            pyspark_str = f"({{0}} {bool_map[bool_cond]} {{1}})" if bool_cond != 'not' else f"~{{0}}"
            z3_rep = f"{bool_cond}"
            semantics = FuncSemantics(
                name=f"{bool_cond}",
                target_type=PrimitiveType.TYPE_BOOLEAN,
                import_type=PrimitiveType.TYPE_BOOLEAN,
                weight=0
            )
            self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str, python_eval=None, func=True)