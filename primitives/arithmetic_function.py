from typing import List
from datetime import datetime

from .base_registry import BasePrimitiveRegistry
from enums.smt_types import DateType, PrimitiveType
from enums.categories import Category
from .Semantics import FuncSemantics

class ArithmeticFunctionRegistry(BasePrimitiveRegistry):
    """Handles type conversion functions between Date, String, and Int."""
    
    def register_all(self) -> None:
        self.init_functions()

    def init_functions(self) -> None:

        name = f"+"
        return_type = PrimitiveType.TYPE_INT
        arg_types = [(PrimitiveType.TYPE_INT, False), (PrimitiveType.TYPE_INT, False)]
        category = Category.ARITHMETIC

        pyspark_str = f"{{0}} + {{1}}"
        python_eval = lambda args, _: int(args[0]) + int(args[1])

        semantics = FuncSemantics(
            name=f"+",
            target_type=PrimitiveType.TYPE_INT,
            import_type=PrimitiveType.TYPE_INT,
            weight=50
        )
        self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str, python_eval=python_eval, func=True)


        name = f"-"
        return_type = PrimitiveType.TYPE_INT
        arg_types = [(PrimitiveType.TYPE_INT, False), (PrimitiveType.TYPE_INT, False)]
        category = Category.ARITHMETIC

        pyspark_str = f"{{0}} - {{1}}"
        python_eval = lambda args, _: int(args[0]) - int(args[1])
        
        semantics = FuncSemantics(
            name=f"-",
            target_type=PrimitiveType.TYPE_INT,
            import_type=PrimitiveType.TYPE_INT,
            weight=50
        )
        self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str, python_eval=python_eval, func=True)