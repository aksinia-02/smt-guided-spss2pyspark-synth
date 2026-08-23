from dataclasses import dataclass
from typing import List, Any, Callable, Optional
from enum import Enum
from enums.smt_types import DateType, DateUnit, PrimitiveType
from enums.categories import Category
from .Semantics import PrimitiveSemantics, FuncSemantics


def make_pyspark_formatter(template: str) -> Callable[[List[str]], str]:
    """
    Factory function that binds to a static string template immediately.
    Completely prevents late-binding loop variable bugs.
    """
    def formatter(args: List[str]) -> str:
        if args and "{0}" in template:
            return template.format(*args)
        return template
    return formatter


@dataclass
class Primitive:
    name: str
    return_type: DateType
    arg_types: List[DateType]
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

        pyspark_str = f"F.lit(D.as_intYM.current_month)"

        semantics = PrimitiveSemantics(
            name=f"F.lit(D.as_intYM.current_month)",
            target_type=DateType.TYPE_INT_YM,
            direction=None,
            unit=None,
            amount=None,
            jump=None
        )
        self.add_primitive(name, return_type, arg_types, category, semantics, make_pyspark_formatter(pyspark_str), python_eval=None)

        for type in [DateType.TYPE_YEAR, DateType.TYPE_MONTH, DateType.TYPE_DAY]:

            name = f"D.as_date.BD.{type.value}"
            return_type = type
            arg_types = []
            category = Category.DATE_NAMESPACE
    
            pyspark_str = f"F.lit(D.as_date.BD.{type.value})"
    
            semantics = PrimitiveSemantics(
                name=f"D.as_date.BD.{type.value}",
                target_type=type,
                direction=None,
                unit=None,
                amount=None,
                jump=None
            )
            self.add_primitive(name, return_type, arg_types, category, semantics, make_pyspark_formatter(pyspark_str), python_eval=None)


        for direction in ["plus", "minus"]:

            plus_minus = "+" if direction == "plus" else "-"
    
            name = f"D.as_date.BD.{type.value} {plus_minus}"
            return_type = DateType.TYPE_YEAR
            arg_types = [DateType.TYPE_INT]
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
            self.add_primitive(name, return_type, arg_types, category, semantics, make_pyspark_formatter(pyspark_str), python_eval=None)



        for type in [DateType.TYPE_DATE, DateType.TYPE_STRING, DateType.TYPE_INT]:
            name = f"D.as_{type.value}.BD"
            return_type = type
            arg_types = []
            category = Category.DATE_NAMESPACE

            pyspark_str = f"F.lit(D.as_{type.value}.BD)"

            semantics = PrimitiveSemantics(
                name=f"F.lit(D.as_{type.value}.BD)",
                target_type=type,
                direction=None,
                unit=None,
                amount=None,
                jump=None
            )
            self.add_primitive(name, return_type, arg_types, category, semantics, make_pyspark_formatter(pyspark_str), python_eval=None)

            for amount in [30, 60, 90]:
                for direction in ["plus", "minus"]:
                    name = f"D.as_{type.value}.{direction}_{amount}days"
                    return_type = type
                    arg_types = []
                    category = Category.DATE_NAMESPACE

                    pyspark_str = f"F.lit(D.as_{type.value}.{direction}_{amount}days)"

                    semantics = PrimitiveSemantics(
                        name=f"F.lit(D.as_{type.value}.{direction}_{amount}days)",
                        target_type=type,
                        direction=direction,
                        unit=DateUnit.DAY,
                        amount=amount,
                        jump=None
                    )
                    self.add_primitive(name, return_type, arg_types, category, semantics, make_pyspark_formatter(pyspark_str), python_eval=None)
                
        for unit in [DateUnit.MONTH, DateUnit.YEAR]:
            for jump in ["start", "end"]:
                for type in [DateType.TYPE_DATE, DateType.TYPE_STRING, DateType.TYPE_INT]:
                    name = f"D.as_{type.value}.{unit.value}_{jump}"
                    return_type = type
                    arg_types = []
                    category = Category.DATE_NAMESPACE

                    pyspark_str = f"F.lit(D.as_{type.value}.{unit.value}_{jump})"

                    semantics = PrimitiveSemantics(
                        name=f"F.lit(D.as_{type.value}.{unit.value}_{jump})",
                        target_type=type,
                        direction=None,
                        unit=None,
                        amount=None,
                        jump=f"{jump} {unit.value}"
                    )

                    self.add_primitive(name, return_type, arg_types, category, semantics, make_pyspark_formatter(pyspark_str), python_eval=None)

        for direction in ["plus", "minus"]:
            for unit in [DateUnit.DAY, DateUnit.WEEK, DateUnit.MONTH, DateUnit.YEAR]:
                for type in [DateType.TYPE_DATE, DateType.TYPE_STRING, DateType.TYPE_INT]:
                    name = f"D.as_{type.value}.{direction}_{unit.value}"
                    return_type = type
                    arg_types = [DateType.TYPE_INT]
                    category = Category.DATE_NAMESPACE

                    pyspark_str = f"F.lit(D.as_{type.value}.{direction}_{unit.value}({{0}}))"

                    semantics = PrimitiveSemantics(
                        name=f"F.lit(D.as_{type.value}.{direction}_{unit.value}({{0}}))",
                        target_type=type,
                        direction=direction,
                        unit=unit,
                        amount=None,
                        jump=None
                    )
                    self.add_primitive(name, return_type, arg_types, category, semantics, make_pyspark_formatter(pyspark_str), python_eval=None)
        
        for unit in [DateUnit.MONTH, DateUnit.YEAR]:
            for direction in ["plus", "minus"]:
                for jump in ["start", "end"]:
                    for type in [DateType.TYPE_DATE, DateType.TYPE_STRING, DateType.TYPE_INT]:
                        name = f"D.as_{type.value}.{direction}_{unit}_{jump}"
                        return_type = type
                        arg_types = [DateType.TYPE_INT] if unit == DateUnit.MONTH else []
                        category = Category.DATE_NAMESPACE
                        semantics = PrimitiveSemantics(
                            name=f"F.lit(D.as_{type.value}.{direction}_{unit.value}_{jump}(_))",
                            target_type=type,
                            direction=direction,
                            unit=unit,
                            amount=None,
                            jump=f"{jump} {unit}"
                        )
                        if unit == DateUnit.MONTH:
                            pyspark_str = f"F.lit(D.as_{type.value}.{direction}_{unit.value}_{jump}({{0}}))"
                        else:
                            pyspark_str = f"F.lit(D.as_{type.value}.{direction}_{unit.value}_{jump})"
                        self.add_primitive(name, return_type, arg_types, category, semantics, make_pyspark_formatter(pyspark_str), python_eval=None)
        for direction in ["plus", "minus"]:
            name = f"D.as_strYM.{direction}_month"
            return_type = DateType.TYPE_INT_YM
            arg_types = [DateType.TYPE_INT]
            category = Category.DATE_NAMESPACE

            pyspark_str = f"F.lit(D.as_strYM.{direction}_month({{0}}))"

            semantics = PrimitiveSemantics(
                name=f"F.lit(D.as_strYM.{direction}_month(_))",
                target_type=DateType.TYPE_INT_YM,
                direction=direction,
                unit=DateUnit.MONTH,
                amount=None,
                jump=None
            )
            self.add_primitive(name, return_type, arg_types, category, semantics, make_pyspark_formatter(pyspark_str), python_eval=None)

    def add_primitive(
            self, name: str, 
            return_type: DateType, 
            arg_types: List[DateType], 
            category: Category, 
            semantics: PrimitiveSemantics, 
            to_pyspark: Callable[[List[str]], str], 
            python_eval: Optional[Callable[[List[Any], Any], Any]] = None,
            func: bool = False
        ) -> None:
        primitive = Primitive(
            name=name,
            return_type=return_type,
            arg_types=arg_types,
            category=category,
            semantics=semantics,
            to_pyspark=to_pyspark,
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
            arg_types = []
            category = Category.CAST_TYPE
    
            pyspark_str = f"F.{type.value}({{0}})"
    
            semantics = FuncSemantics(
                name=f"F.{type.value}({{0}})",
                target_type=type,
                import_type=DateType.TYPE_DATE,
                weight=1000
            )
            self.add_primitive(name, return_type, arg_types, category, semantics, make_pyspark_formatter(pyspark_str), python_eval=None, func=True)



    def print_primitives(self) -> None:
        for primitive in self.primitives:
            print(str(primitive) + "\n")

        print(len(self.primitives), "primitives initialized.")



    # "name": "D.as_date.offset",
    #     "return_type": DateType.TYPE_DATE,
    #     "arg_types": [DateType.TYPE_INT, DateType.TYPE_STRING, DateType.TYPE_STRING], 
    #     "format": lambda args: f"F.lit(D.as_date.{args[1]}_{args[2]}({args[0]}))"