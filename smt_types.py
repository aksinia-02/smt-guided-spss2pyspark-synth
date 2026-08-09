from enum import Enum


class DateType(Enum):
    TYPE_DATE = "Date"
    TYPE_STRING = "String"
    TYPE_INT = "Int"
    TYPE_INT_YM = "IntYM"  # YYYYMM
    TYPE_YEAR = "INTY"
    TYPE_MONTH = "INTM"
    TYPE_DAY = "INTD"

    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"'{self.value}'"

class DateUnit(Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"

    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"'{self.value}'"