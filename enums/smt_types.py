from enum import Enum

import functools
import inspect
from logger.logger import logger

def log_step(func):
    """A decorator that logs 'self', 'other' (if present), and the return result."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        arguments = bound_args.arguments
        
        # Extract self/cls and other values cleanly if they exist
        self_val = arguments.get('self', arguments.get('cls', None))
        other_val = arguments.get('other', None)
        cls_val = arguments.get('cls', None)
        func_name = func.__name__

        target_obj = self_val if self_val is not None else cls_val
        if target_obj is not None:
            class_name = target_obj.__name__ if isinstance(target_obj, type) else target_obj.__class__.__name__
            display_name = f"{class_name}.{func_name}"
        else:
            display_name = func_name
        
        # Format the log line based on whether 'other' exists in the signature
        if other_val is not None:
            logger.debug(f"Entering {display_name} | self: {self_val!r}, other: {other_val!r}")
        else:
            arg_summary = ", ".join(f"{k}={v!r}" for k, v in arguments.items() if k not in ('self', 'cls'))
            logger.debug(f"Entering {display_name} | Args: ({arg_summary})")

        try:
            result = func(*args, **kwargs)
            logger.debug(f"Exiting {display_name} -> Result: {result!r}")
            return result
        except Exception as e:
            logger.error(f"Exception in {display_name}: {e}")
            raise

    return wrapper

class PrimitiveType(Enum):

    TYPE_INT = "int"
    TYPE_STRING = "str"
    TYPE_DATE = "date"
    TYPE_BOOLEAN = "bool"
    TYPE_ANY = "any"

    def __str__(self) -> str:
        return self.value
        
    def __repr__(self) -> str:
        return f"'{self.value}'"

    @classmethod
    @log_step
    def get_type_by_value(cls, value: str) -> "PrimitiveType | None":
        if isinstance(value, cls):
            return value
        for member in cls:
            if member.value == value:
                return member
        return None



    @log_step
    def __eq__(self, other):
        if self.value == self.TYPE_ANY.value:
            return True
        if other.value == self.TYPE_ANY.value:
            if self.value == 'date':
                return False
            return True
        if isinstance(other, PrimitiveType):
            return self.value == other.value
        if isinstance(other, DateType):
            return self.value == other.primitive_type.value
        return super().__eq__(other)

    @log_step
    def eq_exact(self, other) -> bool:
        if self.value == self.TYPE_ANY.value:
            return True
        if other.value == self.TYPE_ANY.value:
            return True
        return self.value == other.value


class DateType(Enum):
    TYPE_DATE = ("date", PrimitiveType.TYPE_DATE, "yyyy-MM-dd", 30)
    TYPE_STRING = ("str", PrimitiveType.TYPE_STRING, "yyyy-MM-dd", 30)
    TYPE_INT = ("int", PrimitiveType.TYPE_INT, "yyyyMMdd", 30)
    TYPE_INT_YM = ("intYM", PrimitiveType.TYPE_INT, "yyyyMM", 15)
    TYPE_YEAR = ("year", PrimitiveType.TYPE_INT, "yyyy", 5)
    TYPE_MONTH = ("month", PrimitiveType.TYPE_INT, "MM", 3)
    TYPE_DAY = ("day", PrimitiveType.TYPE_INT, "dd", 2)

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
    @log_step
    def get_type_by_value(cls, value: str) -> "DateType | None":
        for member in cls:
            if member.value == value:
                return member
        return None 

    @classmethod
    @log_step
    def get_type_by_value_format(cls, value: str, format: str) -> "DateType | None":
        for member in cls:
            #print(f'{value}, {format}')
            if member.value == value and member.format == format:
                return member
        return None 

    @log_step
    def __eq__(self, other):
        if isinstance(other, DateType):
            return self.primitive_type == other.primitive_type
        elif isinstance(other, PrimitiveType):
            return self.primitive_type == other
        return False

    @log_step
    def eq_exact(self, other) -> bool:
        if isinstance(other, DateType):
            return (
                self.primitive_type == other.primitive_type and
                self.format == other.format
            )
        elif isinstance(other, PrimitiveType):
            return self.primitive_type == other
        return False

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
