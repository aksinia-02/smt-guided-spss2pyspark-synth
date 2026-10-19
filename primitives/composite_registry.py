from dataclasses import dataclass
from typing import List
from enums.smt_types import DateType, PrimitiveType
from enums.categories import Category

from .Semantics import DateSemantics, FuncSemantics, BaseSemantics, LiteralSemantics
from .Primitive import Primitive
from .date_primitives import DatePrimitiveRegistry
from .cast_functions import CastFunctionRegistry
from .string_functions import StringFunctionRegistry
from .arithmetic_function import ArithmeticFunctionRegistry

from .base_registry import BasePrimitiveRegistry

@dataclass
class MasterPrimitiveRegistry:
    def __init__(self):

        self.registries = [
            DatePrimitiveRegistry(),
            CastFunctionRegistry(),
            StringFunctionRegistry(),
            ArithmeticFunctionRegistry()
            # Add new function domain children here
        ]

        self.date_primitives = self.registries[0].primitives
        self.cast_functions = self.registries[1].primitives
        self.string_functions = self.registries[2].primitives
        self.arith_functions = self.registries[3].primitives

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
        for func in self.arith_functions:
            if func.name == name:
                return func
        print(f"Function '{name}' not found in the registered functions.")
        return None


    def get_functions_with_specified_import_type(self, import_type: DateType, functions: List[Primitive]) -> List[Primitive]:
        """
        Returns a list of functions that match the required import_type.
        """
        print('Import type')
        print(import_type)
        for func in functions:
            print('func types')
            print(func.name)
            print(func.semantics.import_type)
            print(import_type.eq_exact(func.semantics.import_type))
        return [
            func for func in functions
            if isinstance(func.semantics, FuncSemantics) and
                import_type.eq_exact(func.semantics.import_type)
        ]

    def get_functions_with_specified_target_type(self, target_type: DateType) -> List[Primitive]:
        """
        Returns a list of functions that have the specified target_type.
        """
        print(f'Target type: {target_type}')
        return [
            func for func in self.cast_functions
            if isinstance(func.semantics, FuncSemantics) and
                target_type == func.semantics.target_type
        ]

    def get_functions_with_specified_types(self, import_type: DateType, target_type: PrimitiveType):

        funcs = self.get_functions_with_specified_target_type(target_type)
        print('gggg')
        print(funcs)
        print('gggg')
        return self.get_functions_with_specified_import_type(import_type, funcs)
        

    def print_premitives(self, primitives: List[Primitive]) -> None:
        """
        Prints the details of each primitive in the provided list.
        """
        for primitive in primitives:
            print(str(primitive) + "\n")

    def get_binary_function(self, type: PrimitiveType, op:str) -> Primitive:
        """
        Returns the plus function for the specified type.
        """
        if type == PrimitiveType.TYPE_STRING:
            return self.get_function_by_name("concat_ws")
        if type == PrimitiveType.TYPE_INT:
            return self.get_function_by_name("-")
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

        pyspark_str = BasePrimitiveRegistry.make_pyspark_formatter(f"{literal}", arg_types)

        semantics = LiteralSemantics(
            name=f"{literal}",
            target_type=final_type,
            column_flag=column_flag
        )

        return Primitive(name, return_type, arg_types, category, semantics, pyspark_str, python_eval=None)


    def match_type(self, return_type: DateType, expected_type: PrimitiveType, default_string: bool = True):
        if return_type.eq_exact(expected_type):
            print(f"\nCandidate matches expected type")
            return None
        else:
            #print(f"\nCandidate does not match expected type. Looking for cast functions to convert {return_type} to {expected_type}.")
            matching_casts = self.get_functions_with_specified_types(return_type, expected_type)

            if default_string:
                matching_casts = [
                    func for func in matching_casts
                    if isinstance(func.return_type, PrimitiveType)
                ]

            return matching_casts

    def find_semantic_over_date_primitives(self, semantic, children):

        for date_prim in self.date_primitives:

            param_flag = False
            if len(date_prim.arg_types) == 0:
                result = date_prim.get_semantic_prim([])
            else:
                #TODO extend for multiply params
                # print('To evaluate')
                # print(date_prim)
                if len(children) > 0:
                    param_flag = True
                    result = date_prim.get_semantic_prim(children)
            #print(f'result: {result}')

            if result[0] == semantic[0]:

                if result == semantic:
                    # print('FOUND')
                    # print(result)
                    # print('FOR')
                    # print(semantic)
                    return [date_prim], param_flag

            else:
                cast_funcs = self.match_type(result[0], semantic[0])
                #print(len(cast_funcs))

                for cast_func in cast_funcs:
                    cast_result = cast_func.get_semantic_prim([result[1]])
                    #print(f'cast result: {cast_result}')

                    if cast_result == semantic:
                        # print('FOUND')
                        # print(cast_result)
                        # print('FOR')
                        # print(semantic)

                        return [date_prim, cast_func], param_flag
                    # print('11111111111111')
                    # print(result)
                    # if semantic == result:
                    #     print('FOund')
        return [], param_flag
