from dataclasses import dataclass
from typing import List, Any, Callable, Optional, Tuple
from enum import Enum
from enums.smt_types import DateType, DateUnit, PrimitiveType
from enums.categories import Category
from .Semantics import PrimitiveSemantics, FuncSemantics


# Tuple format: (expected_data_type, is_column_expression_required)
# e.g., (DateType.TYPE_INT, False) -> Raw value like 1
# e.g., (DateType.TYPE_INT, True)  -> Column expression like F.lit(1) or F.col("amount")
ArgSpec = Tuple[DateType, bool]


def make_pyspark_formatter(template: str, arg_specs: List[ArgSpec] = []) -> Callable[[List[str]], str]:
    """
    Factory function that binds to a static string template immediately.
    Completely prevents late-binding loop variable bugs.
    """
    def formatter(args: List[str]) -> str:
        if not args:
            return template

        formatted_args = []
        for raw_arg, (date_type, is_column) in zip(args, arg_specs):
            # If the template already wrapped it or it's a raw column reference, handle here:
            if is_column and not raw_arg.startswith("F.lit(") and not raw_arg.startswith("F.col("):
                formatted_args.append(f"F.lit({raw_arg})")
            else:
                formatted_args.append(str(raw_arg))

        if "{0}" in template:
            return template.format(*formatted_args)
        return template

    return formatter


@dataclass
class Primitive:
    name: str
    return_type: DateType
    arg_types: List[ArgSpec]
    category: Category
    semantics: PrimitiveSemantics
    to_pyspark: Callable[[List[str]], str]
    python_eval: Optional[Callable[[List[Any], Any], Any]] = None

# @dataclass
# class FunctionCall:
#     name: str
#     return_type: 


@dataclass
class Primitives:

    def __init__(self):
        self.primitives: List[Primitive] = []
        self.functions: List[Primitive] = []
        self.init_privitives()
        self.init_functions()

    def init_privitives(self) -> None:

        name = f"D.as_intYM.current_month"
        return_type = DateType.TYPE_INT_YM
        arg_types = []
        category = Category.DATE_NAMESPACE

        pyspark_str = f"D.as_intYM.current_month)"

        semantics = PrimitiveSemantics(
            name=f"D.as_intYM.current_month)",
            target_type=DateType.TYPE_INT_YM,
            direction=None,
            unit=None,
            amount=None,
            jump=None
        )
        self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str)

        for type in [DateType.TYPE_YEAR, DateType.TYPE_MONTH, DateType.TYPE_DAY]:

            name = f"D.as_date.BD.{type.value}"
            return_type = type
            arg_types = []
            category = Category.DATE_NAMESPACE
    
            pyspark_str = f"D.as_date.BD.{type.value}"
    
            semantics = PrimitiveSemantics(
                name=f"D.as_date.BD.{type.value}",
                target_type=type,
                direction=None,
                unit=None,
                amount=None,
                jump=None
            )
            self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str)


        for direction in ["plus", "minus"]:

            plus_minus = "+" if direction == "plus" else "-"
    
            name = f"D.as_date.BD.{type.value} {plus_minus}"
            return_type = DateType.TYPE_YEAR
            arg_types = [(DateType.TYPE_INT, False)]
            category = Category.DATE_NAMESPACE
    
            pyspark_str = f"D.as_date.BD.{DateType.TYPE_YEAR.value} {plus_minus} {{0}}"
    
            semantics = PrimitiveSemantics(
                name=f"D.as_date.BD.{DateType.TYPE_YEAR.value} {plus_minus} {{0}}",
                target_type=DateType.TYPE_YEAR,
                direction=direction,
                unit=None,
                amount=None,
                jump=None
            )
            self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str)



        for type in [DateType.TYPE_DATE, DateType.TYPE_STRING, DateType.TYPE_INT]:
            name = f"D.as_{type.value}.BD"
            return_type = type
            arg_types = []
            category = Category.DATE_NAMESPACE

            pyspark_str = f"D.as_{type.value}.BD)"

            semantics = PrimitiveSemantics(
                name=f"D.as_{type.value}.BD)",
                target_type=type,
                direction=None,
                unit=None,
                amount=None,
                jump=None
            )
            self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str)

            for amount in [30, 60, 90]:
                for direction in ["plus", "minus"]:
                    name = f"D.as_{type.value}.{direction}_{amount}days"
                    return_type = type
                    arg_types = []
                    category = Category.DATE_NAMESPACE

                    pyspark_str = f"D.as_{type.value}.{direction}_{amount}days"

                    semantics = PrimitiveSemantics(
                        name=f"D.as_{type.value}.{direction}_{amount}days",
                        target_type=type,
                        direction=direction,
                        unit=DateUnit.DAY,
                        amount=amount,
                        jump=None
                    )
                    self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str)
                
        for unit in [DateUnit.MONTH, DateUnit.YEAR]:
            for jump in ["start", "end"]:
                for type in [DateType.TYPE_DATE, DateType.TYPE_STRING, DateType.TYPE_INT]:
                    name = f"D.as_{type.value}.{unit.value}_{jump}"
                    return_type = type
                    arg_types = []
                    category = Category.DATE_NAMESPACE

                    pyspark_str = f"D.as_{type.value}.{unit.value}_{jump}"

                    semantics = PrimitiveSemantics(
                        name=f"D.as_{type.value}.{unit.value}_{jump}",
                        target_type=type,
                        direction=None,
                        unit=None,
                        amount=None,
                        jump=f"{jump} {unit.value}"
                    )

                    self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str)

        for direction in ["plus", "minus"]:
            for unit in [DateUnit.DAY, DateUnit.WEEK, DateUnit.MONTH, DateUnit.YEAR]:
                for type in [DateType.TYPE_DATE, DateType.TYPE_STRING, DateType.TYPE_INT]:
                    name = f"D.as_{type.value}.{direction}_{unit.value}"
                    return_type = type
                    arg_types = [(DateType.TYPE_INT, False)]
                    category = Category.DATE_NAMESPACE

                    pyspark_str = f"D.as_{type.value}.{direction}_{unit.value}({{0}})"

                    semantics = PrimitiveSemantics(
                        name=f"D.as_{type.value}.{direction}_{unit.value}({{0}})",
                        target_type=type,
                        direction=direction,
                        unit=unit,
                        amount=None,
                        jump=None
                    )
                    self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str)
        
        for unit in [DateUnit.MONTH, DateUnit.YEAR]:
            for direction in ["plus", "minus"]:
                for jump in ["start", "end"]:
                    for type in [DateType.TYPE_DATE, DateType.TYPE_STRING, DateType.TYPE_INT]:
                        name = f"D.as_{type.value}.{direction}_{unit}_{jump}"
                        return_type = type
                        arg_types = [(DateType.TYPE_INT, False)] if unit == DateUnit.MONTH else []
                        category = Category.DATE_NAMESPACE
                        semantics = PrimitiveSemantics(
                            name=f"D.as_{type.value}.{direction}_{unit.value}_{jump}(_)",
                            target_type=type,
                            direction=direction,
                            unit=unit,
                            amount=None,
                            jump=f"{jump} {unit}"
                        )
                        if unit == DateUnit.MONTH:
                            pyspark_str = f"D.as_{type.value}.{direction}_{unit.value}_{jump}({{0}})"
                        else:
                            pyspark_str = f"D.as_{type.value}.{direction}_{unit.value}_{jump}"
                        self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str)
        for direction in ["plus", "minus"]:
            name = f"D.as_strYM.{direction}_month"
            return_type = DateType.TYPE_INT_YM
            arg_types = [(DateType.TYPE_INT, False)]
            category = Category.DATE_NAMESPACE

            pyspark_str = f"D.as_strYM.{direction}_month({{0}})"

            semantics = PrimitiveSemantics(
                name=f"D.as_strYM.{direction}_month(_)",
                target_type=DateType.TYPE_INT_YM,
                direction=direction,
                unit=DateUnit.MONTH,
                amount=None,
                jump=None
            )
            self.add_primitive(name, return_type, arg_types, category, semantics, pyspark_str)

    def add_primitive(
            self, name: str, 
            return_type: DateType, 
            arg_types: List[DateType], 
            category: Category, 
            semantics: PrimitiveSemantics,
            pyspark_str: str,
            python_eval: Optional[Callable[[List[Any], Any], Any]] = None,
            func: bool = False
        ) -> None:
        primitive = Primitive(
            name=name,
            return_type=return_type,
            arg_types=arg_types,
            category=category,
            semantics=semantics,
            to_pyspark=make_pyspark_formatter(pyspark_str, arg_types),
            python_eval=python_eval
        )
        if func:
            self.functions.append(primitive)
        else:
            self.primitives.append(primitive)

    def init_functions(self) -> None:

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



    def print_primitives(self) -> None:
        for primitive in self.primitives:
            print(str(primitive) + "\n")

        print(len(self.primitives), "primitives initialized.")

    def print_functions(self) -> None:
        for function in self.functions:
            print(str(function) + "\n")

        print(len(self.functions), "functions initialized.")

    def get_functions_with_specified_import_type(self, import_type: DateType, functions: List[Primitive]) -> List[Primitive]:
        """
        Returns a list of functions that match the required import_type.
        """
        return [
            func for func in functions
            if isinstance(func.semantics, FuncSemantics) and
               func.semantics.import_type == import_type
        ]

    def get_functions_with_specified_target_type(self, target_type: DateType) -> List[Primitive]:
        """
        Returns a list of functions that have the specified target_type.
        """
        return [
            func for func in self.functions
            if isinstance(func.semantics, FuncSemantics) and
               func.semantics.target_type == target_type
        ]



    # "name": "D.as_date.offset",
    #     "return_type": DateType.TYPE_DATE,
    #     "arg_types": [DateType.TYPE_INT, DateType.TYPE_STRING, DateType.TYPE_STRING], 
    #     "format": lambda args: f"F.lit(D.as_date.{args[1]}_{args[2]}({args[0]}))"