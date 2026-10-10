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

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if not isinstance(other, Primitive):
            return False
        return self.name == other.name

    def __repr__(self):
        return f"Primitive(name={self.name}, \nreturn_type={self.return_type}, \narg_types={self.arg_types}, \ncategory={self.category}, \nsemantics={self.semantics})"

    def get_semantic(self, params: List[Tuple[PrimitiveType, str]]):

        if isinstance(self.semantics, DateSemantics):

            today = date.today()
            today_int = today.year * 10000 + today.month * 100 + today.day
            
            D = DatesNamespace(today_int)

            if len(params) > 0:
                expr = f"{self.to_pyspark([str(params[0][1])])}"
            else:
                expr = f"{self.to_pyspark([])}"

            print(f"Expression: {expr}")

        
            return (self.return_type.primitive_type, f"{eval(expr, {"D": D})}")

        elif isinstance(self.semantics, FuncSemantics):
            eval_children = [child[1] for child in params]
            print(f'Evaluated children: {eval_children}')
            if self.python_eval is not None:
                try:
                    result = self.python_eval(eval_children, {})
                except (TypeError, ValueError, IndexError):
                    eval_children.reverse()
                    result = self.python_eval(eval_children, {})

                print(result)

                return (self.semantics.target_type, result)

        elif isinstance(self.semantics, BaseSemantics):
            print(self.semantics.target_type)
            return (self.return_type, int(self.semantics.name)) if self.semantics.target_type == PrimitiveType.TYPE_INT else (self.semantics.target_type, self.semantics.name)

        return None