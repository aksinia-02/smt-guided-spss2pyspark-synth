from dataclasses import dataclass
from typing import List
from enums.smt_types import DateType, PrimitiveType
from enums.categories import Category

from .Semantics import DateSemantics, FuncSemantics, BaseSemantics, LiteralSemantics
from .Primitive import Primitive
from .date_primitives import DatePrimitiveRegistry
from .cast_functions import CastFunctionRegistry
from .string_functions import StringFunctionRegistry

@dataclass
class MasterPrimitiveRegistry:
    def __init__(self):

        self.registries = [
            DatePrimitiveRegistry(),
            CastFunctionRegistry(),
            StringFunctionRegistry(),
            # Add new function domain children here
        ]

        self.date_primitives = self.registries[0].primitives
        self.cast_functions = self.registries[1].primitives
        self.string_functions = self.registries[2].primitives

    def get_function_by_name(self, name: str) -> Primitive:
        """
        Returns the function with the specified name from the registered functions.
        """
        for func in self.string_functions:
            if func.name == name:
                return func
        for func in self.cast_functions:
            if func.name == name:
                return func
        print(f"Function '{name}' not found in the registered functions.")
        return None


    def get_functions_with_specified_import_type(self, import_type: DateType, functions: List[Primitive]) -> List[Primitive]:
        """
        Returns a list of functions that match the required import_type.
        """
        # print('__________-')
        # print(target_type)
        # print('__________-')
        # for func in self.cast_functions:
        #     print(func.semantics.target_type)
        # print('__________-')
        return [
            func for func in functions
            if isinstance(func.semantics, FuncSemantics) and
                import_type.eq_exact(func.semantics.import_type)
        ]

    def get_functions_with_specified_target_type(self, target_type: DateType) -> List[Primitive]:
        """
        Returns a list of functions that have the specified target_type.
        """
        # print('__________-')
        # print(target_type)
        # print('__________-')
        # for func in self.cast_functions:
        #     print(func.semantics.target_type)
        # print('__________-')
        return [
            func for func in self.cast_functions
            if isinstance(func.semantics, FuncSemantics) and
                target_type == func.semantics.target_type
        ]

    def print_premitives(self, primitives: List[Primitive]) -> None:
        """
        Prints the details of each primitive in the provided list.
        """
        for primitive in primitives:
            print(str(primitive) + "\n")

    def get_plus_function(self, type: PrimitiveType) -> Primitive:
        """
        Returns the plus function for the specified type.
        """
        if type == PrimitiveType.TYPE_STRING:
            return self.get_function_by_name("concat_ws")
        return None

    # type is not None if column is given
    def return_primitive_for_literal(self, literal: str, type: PrimitiveType = None) -> Primitive:

        column_flag=False #TODO: Determine if this should be True or False based on the context

        if not column_flag:
            determined_type = PrimitiveType.TYPE_STRING
            try:
                int(literal)
                determined_type = PrimitiveType.TYPE_INT
            except ValueError:
                pass

        final_type = type if column_flag else determined_type

        name = f"{literal}"
        return_type = final_type
        arg_types = []
        category = Category.LITERAL

        pyspark_str = f"{literal}"

        semantics = LiteralSemantics(
            name=f"{literal}",
            target_type=PrimitiveType.TYPE_STRING,
            column_flag=column_flag
        )

        return Primitive(name, return_type, arg_types, category, semantics, pyspark_str, python_eval=None)
