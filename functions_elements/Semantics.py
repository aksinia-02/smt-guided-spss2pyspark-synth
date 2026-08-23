from dataclasses import dataclass

from enums.smt_types import DateType, DateUnit, PrimitiveType

@dataclass
class PrimitiveSemantics:
    name: str | None
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
class FuncSemantics:
    name: str | None
    target_type: DateType | None  # e.g. TYPE_DATE, TYPE_INT_YM, TYPE_INT
    import_type: DateType | None
    weight: int

    def __repr__(self) -> str:
        non_none_kwargs = [
            f"{k}={v!r}" for k, v in self.__dict__.items() if v is not None
        ]
        return f"{self.__class__.__name__}({', '.join(non_none_kwargs)})"