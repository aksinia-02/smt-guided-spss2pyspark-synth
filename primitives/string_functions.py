from typing import List

from .base_registry import BasePrimitiveRegistry
from enums.smt_types import DateType
from enums.categories import Category
from .Semantics import FuncSemantics

class StringFunctionRegistry(BasePrimitiveRegistry):
    """Handles string manipulation functions."""
    
    def register_all(self) -> None:
        self.init_cast_functions()

    def init_cast_functions(self) -> None:
        # Date component extractors (Year, Month, Day)
        for type in [DateType.TYPE_YEAR, DateType.TYPE_MONTH, DateType.TYPE_DAY]:
        
            name = f"F.{type.value}()"
            return_type = type
            arg_types = List[DateType]
            category = Category.CAST_TYPE
    
            pyspark_str = f"F.{type.value}({{0}})"
    
            semantics = FuncSemantics(
                name=f"F.{type.value}({{0}})",
                target_type=type,
                import_type=DateType.TYPE_DATE,
                weight=1000
            )
            self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str, python_eval=None, func=True)

        ### Cast Functions for different types (Date, String, Int)

        ## Int to Date
        name = f"cast_from_int_to_date"
        return_type = DateType.TYPE_DATE
        arg_types = [(DateType.TYPE_INT, True)]
        category = Category.CAST_TYPE

        pyspark_str = f"F.to_date({{0}}.cast(t.StringType()), 'yyyyMMdd')"

        semantics = FuncSemantics(
            name=f"cast_from_int_to_date",
            target_type=DateType.TYPE_DATE,
            import_type=DateType.TYPE_INT,
            weight=1000
        )
        self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str, python_eval=None, func=True)

        ## Int to String
        name = f"cast_from_int_to_string"
        return_type = DateType.TYPE_STRING
        arg_types = [(DateType.TYPE_INT, True)]
        category = Category.CAST_TYPE

        pyspark_str = f"F.date_format(F.to_date({{0}}.cast(t.StringType()), 'yyyyMMdd'), 'yyyy-MM-dd')"

        semantics = FuncSemantics(
            name=f"cast_from_int_to_string",
            target_type=DateType.TYPE_STRING,
            import_type=DateType.TYPE_INT,
            weight=1000
        )
        self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str, python_eval=None, func=True)

        ## String to Date
        name = f"cast_from_string_to_date"
        return_type = DateType.TYPE_DATE
        arg_types = [(DateType.TYPE_STRING, True)]
        category = Category.CAST_TYPE

        pyspark_str = f"F.to_date({{0}}, 'yyyy-MM-dd')"

        semantics = FuncSemantics(
            name=f"cast_from_string_to_date",
            target_type=DateType.TYPE_DATE,
            import_type=DateType.TYPE_STRING,
            weight=1000
        )
        self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str, python_eval=None, func=True)

        ## String to Int
        name = f"cast_from_string_to_int"
        return_type = DateType.TYPE_INT
        arg_types = [(DateType.TYPE_STRING, True)]
        category = Category.CAST_TYPE

        pyspark_str = f"F.date_format(F.to_date({{0}}, 'yyyy-MM-dd'), 'yyyyMMdd').cast(t.IntegerType())"

        semantics = FuncSemantics(
            name=f"cast_from_string_to_int",
            target_type=DateType.TYPE_INT,
            import_type=DateType.TYPE_STRING,
            weight=1000
        )
        self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str, python_eval=None, func=True)

        ## Date to String
        name = f"cast_from_date_to_string"
        return_type = DateType.TYPE_STRING
        arg_types = [(DateType.TYPE_DATE, True)]
        category = Category.CAST_TYPE
        pyspark_str = f"F.date_format({{0}}, 'yyyy-MM-dd')"

        semantics = FuncSemantics(
            name=f"cast_from_date_to_string",
            target_type=DateType.TYPE_STRING,
            import_type=DateType.TYPE_DATE,
            weight=1000
        )
        self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str, python_eval=None, func=True)

        ### Date to Int
        name = f"cast_from_date_to_int"
        return_type = DateType.TYPE_INT
        arg_types = [(DateType.TYPE_DATE, True)]
        category = Category.CAST_TYPE
        pyspark_str = f"F.date_format({{0}}, 'yyyyMMdd').cast(t.IntegerType())"
        semantics = FuncSemantics(
            name=f"cast_from_date_to_int",
            target_type=DateType.TYPE_INT,
            import_type=DateType.TYPE_DATE,
            weight=1000
        )
        self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str, python_eval=None, func=True)