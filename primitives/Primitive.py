from typing import List, Optional, Callable, Any, Tuple
from dataclasses import dataclass
from enums.smt_types import DateType

from enums.categories import Category
from .Semantics import BaseSemantics

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

    def __repr__(self):
        return f"Primitive(name={self.name}, \nreturn_type={self.return_type}, \narg_types={self.arg_types}, \ncategory={self.category}, \nsemantics={self.semantics})"