from ast import expr
from typing import List, Optional, Callable, Any, Tuple
from dataclasses import dataclass
from enums.smt_types import DateType

from enums.categories import Category
from enums.smt_types import PrimitiveType
from .Semantics import BaseSemantics, LiteralSemantics, FuncSemantics, StringSemantics, DateSemantics

from primitives.dataparams.dataparams import DatesNamespace

from datetime import date

ArgSpec = Tuple[DateType, bool] # True if the argument is a column, False if it's a constant value

@dataclass
class Primitive:
    name: str
    return_type: DateType
    arg_types: List[ArgSpec]
    category: Category
    semantics: BaseSemantics
    to_pyspark: Callable[[List[str]], str]
    python_eval: Optional[Callable[[List[Any], Any], Any]] = None

    evaluated_value: Optional[Any] = None  # Store the evaluated value of the primitive

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if not isinstance(other, Primitive):
            return False
        return self.name == other.name

    def __repr__(self):
        return f"Primitive(name={self.name}, \nreturn_type={self.return_type}, \narg_types={self.arg_types}, \ncategory={self.category}, \nsemantics={self.semantics})"

    def get_semantic(self, params: List[Primitive]):

        if self.evaluated_value is not None:
            self.evaluated_value = self.evaluated_value

        if isinstance(self.semantics, DateSemantics):

            today = date.today()
            today_int = today.year * 10000 + today.month * 100 + today.day
            
            D = DatesNamespace(today_int)

            if len(params) > 0:
                val = next(iter(params[0]))
                print(f"Parameter: {val}")
                expr = f"{self.to_pyspark([str(val.get_semantic([]))])}"
            else:
                expr = f"{self.to_pyspark([])}"

            print(f"Expression: {expr}")

        
            self.evaluated_value = eval(expr, {"D": D})

        elif isinstance(self.semantics, FuncSemantics):
            eval_children = [next(iter(child)).get_semantic([]) for child in params]
            print(f"Evaluated children: {eval_children}")
            if self.python_eval is not None:
                self.evaluated_value = eval(self.python_eval)

        elif isinstance(self.semantics, BaseSemantics):
            return int(self.semantics.name) if self.semantics.target_type == PrimitiveType.TYPE_INT else self.semantics.name

        return self.evaluated_value