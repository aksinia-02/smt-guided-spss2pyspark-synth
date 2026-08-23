from enum import Enum

class PrimitiveType(Enum):

    TYPE_INT = "int"
    TYPE_STRING = "str"
    TYPE_DATE = "date"

    def __str__(self) -> str:
        return self.value
        
    def __repr__(self) -> str:
        return f"'{self.value}'"


class DateType(Enum):
    TYPE_DATE = ("date", PrimitiveType.TYPE_DATE, "YYYY-MM-DD", 30)
    TYPE_STRING = ("str", PrimitiveType.TYPE_STRING, "YYYY-MM-DD", 30)
    TYPE_INT = ("int", PrimitiveType.TYPE_INT, "YYYYMMDD", 30)
    TYPE_INT_YM = ("strYM", PrimitiveType.TYPE_INT, "YYYYMM", 15)
    TYPE_YEAR = ("year", PrimitiveType.TYPE_INT, "YYYY", 5)
    TYPE_MONTH = ("month", PrimitiveType.TYPE_INT, "MM", 3)
    TYPE_DAY = ("day", PrimitiveType.TYPE_INT, "DD", 2)

    def __init__(
        self,
        value: str,
        primitive: PrimitiveType,
        fmt: str | None,
        inf_level: int | None,
    ):
        self._value_ = value
        self.primitive_type = primitive
        self.format = fmt
        self.inf_level = inf_level

    @classmethod
    def get_type_by_value(cls, value: str) -> "DateType | None":
        for member in cls:
            if member.value == value:
                return member
        return None 

    def __eq__(self, other):
        if isinstance(other, DateType):
            return self.primitive_type == other.primitive_type
        return super().__eq__(other)

    def eq_score(self, other) -> int:
        ## returns the score, that represents how easy other is derivable from self
        if isinstance(other, DateType):
            if self.primitive_type == other.primitive_type:
                if self.inf_level == other.inf_level:
                    return 1
                elif self.inf_level % other.inf_level == 0:
                    return 0.8
                else:
                    return 0
            else:
                if self.inf_level == other.inf_level:
                    return 0.5
                elif self.inf_level % other.inf_level == 0:
                    return 0.3
                else:
                    return 0
        return 0


    def __hash__(self):
        return super().__hash__()

    def __str__(self) -> str:
        return f"'{self.value}, {self.primitive_type}, {self.format}, {self.inf_level}'"

    def __repr__(self) -> str:
        return f"'{self.value}, {self.primitive_type}, {self.format}, {self.inf_level}'"

class DateUnit(Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"

    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"'{self.value}'"
