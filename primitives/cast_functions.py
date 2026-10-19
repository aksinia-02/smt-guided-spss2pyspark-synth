from typing import List
from datetime import datetime

from .base_registry import BasePrimitiveRegistry
from enums.smt_types import DateType, PrimitiveType
from enums.categories import Category
from .Semantics import FuncSemantics

class CastFunctionRegistry(BasePrimitiveRegistry):
    """Handles type conversion functions between Date, String, and Int."""
    
    def register_all(self) -> None:
        self.init_cast_functions()

    def init_cast_functions(self) -> None:
        # Date component extractors (Year, Month, Day)
        for type in [DateType.TYPE_YEAR, DateType.TYPE_MONTH, DateType.TYPE_DAY]:
        
            name = f"F.{type.value}()"
            return_type = type
            arg_types = [(PrimitiveType.TYPE_DATE, True)]
            category = Category.CAST_TYPE
    
            pyspark_str = f"F.{type.value}({{0}})"

            #pyspark_str = lambda args, dt=type: f"F.{dt.value}({args[0]})"

            if type == DateType.TYPE_YEAR:
                python_eval = lambda args, _: datetime.strptime(str(args[0]), '%Y-%m-%d').year if isinstance(args[0], str) else int(str(args[0])[:4])
            elif type == DateType.TYPE_MONTH:
                python_eval = lambda args, _: datetime.strptime(str(args[0]), '%Y-%m-%d').month if isinstance(args[0], str) else int(str(args[0])[4:6])
            else:  # TYPE_DAY
                python_eval = lambda args, _: datetime.strptime(str(args[0]), '%Y-%m-%d').day if isinstance(args[0], str) else int(str(args[0])[6:])
    
            semantics = FuncSemantics(
                name=f"F.{type.value}({{0}})",
                target_type=type,
                import_type=DateType.TYPE_DATE,
                weight=20
            )
            self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str, python_eval=python_eval, func=True)

        ### Cast Functions for different types (Date, String, Int)

        ## Int to Date
        name = f"cast_from_int_to_date"
        return_type = DateType.TYPE_DATE
        arg_types = [(DateType.TYPE_INT, True)]
        category = Category.CAST_TYPE

        pyspark_str = f"F.to_date({{0}}.cast(t.StringType()), 'yyyyMMdd')"
        #pyspark_str = lambda args: f"F.to_date({args[0]}.cast(t.StringType()), 'yyyyMMdd')"
        python_eval = lambda args, _: datetime.strptime(str(args[0]), '%Y%m%d').strftime('%Y-%m-%d')

        semantics = FuncSemantics(
            name=f"cast_from_int_to_date",
            target_type=DateType.TYPE_DATE,
            import_type=DateType.TYPE_INT,
            weight=20
        )
        self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str, python_eval=python_eval, func=True)

        ## Int to String
        name = f"cast_from_int_to_string"
        return_type = DateType.TYPE_STRING
        arg_types = [(DateType.TYPE_INT, True)]
        category = Category.CAST_TYPE

        pyspark_str = f"F.date_format(F.to_date({{0}}.cast(t.StringType()), 'yyyyMMdd'), 'yyyy-MM-dd')"
        #pyspark_str = lambda args: f"F.date_format(F.to_date({args[0]}.cast(t.StringType()), 'yyyyMMdd'), 'yyyy-MM-dd')"
        python_eval = lambda args, _: f"{str(args[0])[:4]}-{str(args[0])[4:6]}-{str(args[0][6:])}"

        semantics = FuncSemantics(
            name=f"cast_from_int_to_string",
            target_type=DateType.TYPE_STRING,
            import_type=DateType.TYPE_INT,
            weight=20
        )
        self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str, python_eval=python_eval, func=True)

        ## String to Date
        name = f"cast_from_string_to_date"
        return_type = DateType.TYPE_DATE
        arg_types = [(DateType.TYPE_STRING, True)]
        category = Category.CAST_TYPE

        pyspark_str = f"F.to_date({{0}}, 'yyyy-MM-dd')"
        #pyspark_str = lambda args: f"F.to_date({args[0]}, 'yyyy-MM-dd')"
        python_eval = lambda args, _: datetime.strptime(str(args[0]), '%Y-%m-%d').date() if isinstance(args[0], str) else args[0]

        semantics = FuncSemantics(
            name=f"cast_from_string_to_date",
            target_type=DateType.TYPE_DATE,
            import_type=DateType.TYPE_STRING,
            weight=20
        )
        self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str, python_eval=python_eval, func=True)

        ## String to Int
        name = f"cast_from_string_to_int"
        return_type = DateType.TYPE_INT
        arg_types = [(DateType.TYPE_STRING, True)]
        category = Category.CAST_TYPE

        pyspark_str = f"F.date_format(F.to_date({{0}}, 'yyyy-MM-dd'), 'yyyyMMdd').cast(t.IntegerType())"
        #pyspark_str = lambda args: f"F.date_format(F.to_date({args[0]}, 'yyyy-MM-dd'), 'yyyyMMdd').cast(t.IntegerType())"
        python_eval = lambda args, _: int(str(args[0]).replace('-', ''))

        semantics = FuncSemantics(
            name=f"cast_from_string_to_int",
            target_type=DateType.TYPE_INT,
            import_type=DateType.TYPE_STRING,
            weight=20
        )
        self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str, python_eval=python_eval, func=True)

        ## Date to String
        name = f"cast_from_date_to_string"
        return_type = DateType.TYPE_STRING
        arg_types = [(DateType.TYPE_DATE, True)]
        category = Category.CAST_TYPE

        pyspark_str = f"F.date_format({{0}}, 'yyyy-MM-dd')"
        #pyspark_str = lambda args: f"F.date_format({args[0]}, 'yyyy-MM-dd')"

        python_eval = lambda args, _: str(args[0])

        semantics = FuncSemantics(
            name=f"cast_from_date_to_string",
            target_type=DateType.TYPE_STRING,
            import_type=DateType.TYPE_DATE,
            weight=20
        )
        self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str, python_eval=python_eval, func=True)

        ### Date to Int
        name = f"cast_from_date_to_int"
        return_type = DateType.TYPE_INT
        arg_types = [(DateType.TYPE_DATE, True)]
        category = Category.CAST_TYPE

        pyspark_str = f"F.date_format({{0}}, 'yyyyMMdd').cast(t.IntegerType())"
        #pyspark_str = lambda args: f"F.date_format({args[0]}, 'yyyyMMdd').cast(t.IntegerType())"

        python_eval = lambda args, _: int(str(args[0]).replace('-', ''))

        semantics = FuncSemantics(
            name=f"cast_from_date_to_int",
            target_type=DateType.TYPE_INT,
            import_type=DateType.TYPE_DATE,
            weight=20
        )
        self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str, python_eval=python_eval, func=True)

        ## Int to String any format #TODO add another casting for any format
        name = f"to_string"
        return_type = PrimitiveType.TYPE_STRING
        arg_types = [(PrimitiveType.TYPE_ANY, True)]
        category = Category.CAST_TYPE

        pyspark_str = f"{{0}}.cast(t.StringType())"
        #pyspark_str = lambda args: f"{args[0]}.cast(t.StringType())"

        python_eval = lambda args, _: str(args[0])

        semantics = FuncSemantics(
            name=f"to_string",
            target_type=PrimitiveType.TYPE_STRING,
            import_type=PrimitiveType.TYPE_ANY,
            weight=20
        )
        self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str, python_eval=python_eval, func=True)

        name = f"to_integer"
        return_type = PrimitiveType.TYPE_INT
        arg_types = [(PrimitiveType.TYPE_ANY, True)]
        category = Category.CAST_TYPE

        pyspark_str = f"{{0}}.cast(t.IntegerType())"
        #pyspark_str = lambda args: f"{args[0]}.cast(t.IntegerType())"

        python_eval = lambda args, _: int(args[0])

        semantics = FuncSemantics(
            name=f"to_integer",
            target_type=PrimitiveType.TYPE_INT,
            import_type=PrimitiveType.TYPE_ANY,
            weight=20
        )
        self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str, python_eval=python_eval, func=True)