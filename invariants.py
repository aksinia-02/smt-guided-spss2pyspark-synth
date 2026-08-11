from dataclasses import dataclass
from typing import List, Any, Callable, Optional
from enum import Enum
from enums.smt_types import DateType, DateUnit
from enums.categories import Category


@dataclass
class PrimitiveSemantics:
    target_type: DateType | None  # e.g. TYPE_DATE, TYPE_INT_YM, TYPE_INT
    direction: str | None       # "plus", "minus", or None
    unit: DateUnit | None         # DateUnit.DAY, MONTH, YEAR
    amount: int | None           # Fixed amount (e.g. 30 for minus_30days) or None if dynamic
    jump: str | None             # "last month", "last year", "month_start", etc.

    def __repr__(self) -> str:
        non_none_kwargs = [
            f"{k}={v!r}" for k, v in self.__dict__.items() if v is not None
        ]
        return f"{self.__class__.__name__}({', '.join(non_none_kwargs)})"


@dataclass
class Primitive:
    name: str
    return_type: DateType
    arg_types: List[DateType]
    category: Category
    semantics: PrimitiveSemantics
    to_pyspark: Callable[[List[str]], str]
    python_eval: Optional[Callable[[List[Any], Any], Any]] = None


@dataclass
class Primitives:

    def __init__(self):
        self.primitives: List[Primitive] = []
        self.init_privitives()

    def init_privitives(self) -> None:

        for type in [DateType.TYPE_DATE, DateType.TYPE_STRING, DateType.TYPE_INT]:
            name = f"D.as_{type.value}.BD"
            return_type = type
            arg_types = []
            category = Category.DATE_NAMESPACE
            semantics = PrimitiveSemantics(
                target_type=type,
                direction=None,
                unit=None,
                amount=None,
                jump=None
            )
            to_pyspark = lambda args: f"F.lit(D.as_{type.name.lower()}.BD)"
            self.add_primitive(name, return_type, arg_types, category, semantics, to_pyspark, python_eval=None)

            for amount in [30, 60, 90]:
                for direction in ["plus", "minus"]:
                    name = f"D.as_{type.value}.{direction}_{amount}days"
                    return_type = type
                    arg_types = []
                    category = Category.DATE_NAMESPACE
                    semantics = PrimitiveSemantics(
                        target_type=type,
                        direction=direction,
                        unit=DateUnit.DAY,
                        amount=amount,
                        jump=None
                    )
                    to_pyspark = lambda args: f"F.lit(D.as_{type.name.lower()}.{direction}_{amount}days)"
                    self.add_primitive(name, return_type, arg_types, category, semantics, to_pyspark, python_eval=None)
                
        for unit in [DateUnit.MONTH, DateUnit.YEAR]:
            for jump in ["start", "end"]:
                for type in [DateType.TYPE_DATE, DateType.TYPE_STRING, DateType.TYPE_INT]:
                    name = f"D.as_{type.value}.{unit.value}_{jump}"
                    return_type = type
                    arg_types = []
                    category = Category.DATE_NAMESPACE
                    semantics = PrimitiveSemantics(
                        target_type=type,
                        direction=None,
                        unit=None,
                        amount=None,
                        jump=f"{jump} {unit.value}"
                    )

                    ##lambda args: 
                    to_pyspark = lambda args: f"F.lit(D.as_{type.name.lower()}.{unit.value}_{jump})"
                    self.add_primitive(name, return_type, arg_types, category, semantics, to_pyspark, python_eval=None)

        for direction in ["plus", "minus"]:
            for unit in [DateUnit.DAY, DateUnit.WEEK, DateUnit.MONTH, DateUnit.YEAR]:
                for type in [DateType.TYPE_DATE, DateType.TYPE_STRING, DateType.TYPE_INT]:
                    name = f"D.as_{type.value}.{direction}_{unit.value}"
                    return_type = type
                    arg_types = [DateType.TYPE_INT]
                    category = Category.DATE_NAMESPACE
                    semantics = PrimitiveSemantics(
                        target_type=type,
                        direction=direction,
                        unit=unit,
                        amount=None,
                        jump=None
                    )
                    #lambda args: 
                    to_pyspark = lambda args: f"F.lit(D.as_{type.name.lower()}.{direction}_{unit.value}({args[0]}))"
                    self.add_primitive(name, return_type, arg_types, category, semantics, to_pyspark, python_eval=None)
        
        for unit in [DateUnit.MONTH, DateUnit.YEAR]:
            for direction in ["plus", "minus"]:
                for jump in ["start", "end"]:
                    for type in [DateType.TYPE_DATE, DateType.TYPE_STRING, DateType.TYPE_INT]:
                        name = f"D.as_{type.value}.{direction}_{unit}_{jump}"
                        return_type = type
                        arg_types = [DateType.TYPE_INT] if unit == DateUnit.MONTH else []
                        category = Category.DATE_NAMESPACE
                        semantics = PrimitiveSemantics(
                            target_type=type,
                            direction=direction,
                            unit=unit,
                            amount=None,
                            jump=f"{jump} {unit}"
                        )
                        if unit == DateUnit.MONTH:
                            to_pyspark = lambda args: f"F.lit(D.as_{type.name.lower()}.{direction}_{unit.value}_{jump}({args[0]}))"
                        else:
                            to_pyspark = lambda args: f"F.lit(D.as_{type.name.lower()}.{direction}_{unit.value}_{jump}"
                        self.add_primitive(name, return_type, arg_types, category, semantics, to_pyspark, python_eval=None)
        for direction in ["plus", "minus"]:
            name = f"D.as_strYM.{direction}_month"
            return_type = DateType.TYPE_INT_YM
            arg_types = [DateType.TYPE_INT]
            category = Category.DATE_NAMESPACE
            semantics = PrimitiveSemantics(
                target_type=DateType.TYPE_INT_YM,
                direction=direction,
                unit=DateUnit.MONTH,
                amount=None,
                jump=None
            )
            to_pyspark = lambda args: f"F.lit(D.as_strYM.{direction}_month({args[0]}))"
            self.add_primitive(name, return_type, arg_types, category, semantics, to_pyspark, python_eval=None)

    def add_primitive(
            self, name: str, 
            return_type: DateType, 
            arg_types: List[DateType], 
            category: Category, 
            semantics: PrimitiveSemantics, 
            to_pyspark: Callable[[List[str]], str], 
            python_eval: Optional[Callable[[List[Any], Any], Any]] = None
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
        self.primitives.append(primitive)

    def print_primitives(self) -> None:
        for primitive in self.primitives:
            print(str(primitive) + "\n")

        print(len(self.primitives), "primitives initialized.")



    # "name": "D.as_date.offset",
    #     "return_type": DateType.TYPE_DATE,
    #     "arg_types": [DateType.TYPE_INT, DateType.TYPE_STRING, DateType.TYPE_STRING], 
    #     "format": lambda args: f"F.lit(D.as_date.{args[1]}_{args[2]}({args[0]}))"