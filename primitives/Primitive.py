from typing import List, Optional, Callable, Any, Tuple
from dataclasses import dataclass
from enums.smt_types import DateType

ArgSpec = Tuple[DateType, bool]

@dataclass
class Primitive:
    name: str
    return_type: DateType
    arg_types: List[ArgSpec]
    category: Category
    semantics: DateSemantics
    to_pyspark: Callable[[List[str]], str]
    python_eval: Optional[Callable[[List[Any], Any], Any]] = None