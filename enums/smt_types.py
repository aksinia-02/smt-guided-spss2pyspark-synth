from enum import Enum


class DateType(Enum):
    TYPE_DATE = "date"
    TYPE_STRING = "str"
    TYPE_INT = "int"
    TYPE_INT_YM = "strYM"  # YYYYMM
    TYPE_YEAR = "intY"
    TYPE_MONTH = "intM"
    TYPE_DAY = "intD"

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