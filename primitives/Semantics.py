from abc import ABC
from dataclasses import dataclass
from typing import Optional
from enums.smt_types import DateType, DateUnit, PrimitiveType

@dataclass
class BaseSemantics(ABC):
    """Abstract parent class for all semantics objects."""
    name: Optional[str]
    target_type: Optional[DateType]  # e.g. TYPE_DATE, TYPE_INT_YM, TYPE_INT

    def __repr__(self) -> str:
        """Custom repr that prints only fields with non-None values."""
        non_none_kwargs = [
            f"{k}={v!r}" for k, v in self.__dict__.items() if v is not None
        ]
        return f"{self.__class__.__name__}({', '.join(non_none_kwargs)})"

@dataclass
class DateSemantics(BaseSemantics):
    """Semantics specific to core date operations and offsets."""
    direction: Optional[str] = None     # "plus", "minus", or None
    unit: Optional[DateUnit] = None     # DateUnit.DAY, MONTH, YEAR
    amount: Optional[int] = None       # Fixed amount or None if dynamic
    jump: Optional[str] = None         # "last month", "last year", "month_start", etc.


@dataclass
class FuncSemantics(BaseSemantics):
    """Semantics specific to functions and type transformations."""
    import_type: Optional[DateType] = None
    weight: int = 1000