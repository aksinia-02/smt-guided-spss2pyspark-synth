from typing import List

from .base_registry import BasePrimitiveRegistry
from enums.smt_types import DateType, PrimitiveType
from enums.categories import Category
from .Semantics import FuncSemantics

class StringFunctionRegistry(BasePrimitiveRegistry):
    """Handles string manipulation functions."""
    
    def register_all(self) -> None:
        self.init_string_functions()

    def init_string_functions(self) -> None:

        name = f"startstring"
        return_type = PrimitiveType.TYPE_STRING
        arg_types = [(PrimitiveType.TYPE_STRING, True), (PrimitiveType.TYPE_INT, False)]
        category = Category.STRING_FUNCTION

        pyspark_str = f"F.substring({{0}}, 1, {{1}})"
        semantics = FuncSemantics(
            name=f"startstring",
            target_type=PrimitiveType.TYPE_STRING,
            import_type=PrimitiveType.TYPE_STRING,
            weight=1000
        )
        self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str, python_eval=None, func=True)

        name = f"endstring"
        return_type = PrimitiveType.TYPE_STRING
        arg_types = [(PrimitiveType.TYPE_STRING, True), (PrimitiveType.TYPE_INT, False)]
        category = Category.STRING_FUNCTION

        pyspark_str = f"F.substring({{0}}, -{{1}}, {{1}})"
        semantics = FuncSemantics(
            name=f"endstring",
            target_type=PrimitiveType.TYPE_STRING,
            import_type=PrimitiveType.TYPE_STRING,
            weight=1000
        )
        self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str, python_eval=None, func=True)

        name = f"substring"
        return_type = PrimitiveType.TYPE_STRING
        arg_types = [(PrimitiveType.TYPE_STRING, True), (PrimitiveType.TYPE_INT, False), (PrimitiveType.TYPE_INT, False)]
        category = Category.STRING_FUNCTION

        pyspark_str = f"F.substring({{0}}, {{1}}, {{2}})"
        semantics = FuncSemantics(
            name=f"substring",
            target_type=PrimitiveType.TYPE_STRING,
            import_type=PrimitiveType.TYPE_STRING,
            weight=1000
        )
        self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str, python_eval=None, func=True)

        # name = f"concat_ws"
        # return_type = PrimitiveType.TYPE_STRING
        # arg_types = [(PrimitiveType.TYPE_STRING, True), (PrimitiveType.TYPE_INT, False), (PrimitiveType.TYPE_INT, False)]
        # category = Category.STRING_FUNCTION

        # pyspark_str = f"F.concat_ws({{0}}, {{1}}, {{2}})"
        # F.concat_ws("", F.col("a"), F.col("b"), F.col("c"))
        # semantics = FuncSemantics(
        #     name=f"concat_ws",
        #     target_type=PrimitiveType.TYPE_STRING,
        #     import_type=PrimitiveType.TYPE_STRING,
        #     weight=1000
        # )
        # self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str, python_eval=None, func=True)

        #fallback return f"F.{fn_name}({', '.join(arg_exprs)})"