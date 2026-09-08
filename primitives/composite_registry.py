from dataclasses import dataclass
from typing import List
from enums.smt_types import DateType

from .Semantics import DateSemantics, FuncSemantics
from .Primitive import Primitive
from .date_primitives import DatePrimitiveRegistry
from .cast_functions import CastFunctionRegistry

@dataclass
class MasterPrimitiveRegistry:
    def __init__(self):

        self.registries = [
            DatePrimitiveRegistry(),
            CastFunctionRegistry(),
            # Add new function domain children here
        ]

        self.date_primitives = self.registries[0].primitives
        self.cast_functions = self.registries[1].primitives


    def get_functions_with_specified_import_type(self, import_type: DateType, functions: List[Primitive]) -> List[Primitive]:
        """
        Returns a list of functions that match the required import_type.
        """
        return [
            func for func in functions
            if isinstance(func.semantics, FuncSemantics) and
               func.semantics.import_type == import_type
        ]

    def get_functions_with_specified_target_type(self, target_type: DateType) -> List[Primitive]:
        """
        Returns a list of functions that have the specified target_type.
        """
        return [
            func for func in self.cast_functions
            if isinstance(func.semantics, FuncSemantics) and
               func.semantics.target_type == target_type
        ]