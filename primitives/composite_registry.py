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

import functools
import inspect
import logging
from logger.logger import logger, log_primitive, log_list

def log_step(func):
    """A decorator that logs the class name, function name, arguments, and the return result."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        arguments = bound_args.arguments
        
        # Extract self, cls, and other values cleanly if they exist
        self_val = arguments.get('self', None)
        cls_val = arguments.get('cls', None)
        other_val = arguments.get('other', None)
        func_name = func.__name__
        
        # Dynamically determine the class name
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

            if isinstance(result, list):
                log_list(f"Exiting {display_name} -> Result", result, level=logging.DEBUG)
            else:
                logger.debug(f"Exiting {display_name} -> Result: {result!r}")
            return result
        except Exception as e:
            logger.error(f"Exception in {display_name}: {e}")
            raise

    return wrapper

@dataclass
class MasterPrimitiveRegistry:
    def __init__(self):

        self.registries = [
            DatePrimitiveRegistry(20261026),
            CastFunctionRegistry(),
            StringFunctionRegistry(),
            ArithmeticFunctionRegistry(),
            #DatePrimitiveRegistry(20250225)
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


    @log_step
    def get_functions_with_specified_import_type(self, import_type: DateType, functions: List[Primitive]) -> List[Primitive]:
        """
        Returns a list of functions that match the required import_type.
        """
        # for func in functions:
        #     print(import_type.eq_exact(func.semantics.import_type))
        # print(f'mport type {import_type}')
        # print(import_type != PrimitiveType.TYPE_DATE)
        # for func in functions:
        #     print(func)
        #     print(func.semantics.import_type.value != 'any')
        return [
            func for func in functions
            if isinstance(func.semantics, FuncSemantics) and
                import_type.eq_exact(func.semantics.import_type) and
                (import_type != PrimitiveType.TYPE_DATE or func.semantics.import_type.value != 'any')
                #func.semantics.import_type.eq_exact(import_type)
        ]

    @log_step
    def get_functions_with_specified_target_type(self, target_type: DateType) -> List[Primitive]:
        """
        Returns a list of functions that have the specified target_type.
        """
        return [
            func for func in self.cast_functions
            if isinstance(func.semantics, FuncSemantics) and
                target_type == func.semantics.target_type
        ]

    @log_step
    def get_functions_with_specified_types(self, import_type: DateType, target_type: PrimitiveType):

        funcs = self.get_functions_with_specified_target_type(target_type)
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


    @log_step
    def match_type(self, return_type: DateType, expected_type: PrimitiveType, default_string: bool = True, strich: bool = False):
        if return_type.eq_exact(expected_type):
            print(f"\nCandidate matches expected type")
            return None
        else:
            #print(f"\nCandidate does not match expected type. Looking for cast functions to convert {return_type} to {expected_type}.")
            matching_casts = self.get_functions_with_specified_types(return_type, expected_type)

            # print('Selected matches')
            # print(matching_casts)

            if default_string:
                matching_casts = [
                    func for func in matching_casts
                    if not func.semantics.overwrite_format
                    #if isinstance(func.return_type, PrimitiveType)
                ]

            if strich:
                matching_casts = [
                    func for func in matching_casts
                    #if not func.semantics.overwrite_format
                    if isinstance(func.return_type, DateType)
                ]

            return matching_casts

    @log_step
    def find_semantic_over_date_primitives(self, semantic, children):

        # print(f'length: {len(self.date_primitives)}')

        results = set()

        for i, date_prim in enumerate(self.date_primitives):

            param_flag = False
            # print(f'before result: {date_prim}')
            if len(date_prim.arg_types) == 0:
                result = date_prim.get_semantic_prim([])
            else:
                #TODO extend for multiply params
                # print('To evaluate')
                # print(date_prim)
                if len(children) > 0:
                    param_flag = True
                    result = date_prim.get_semantic_prim(children)
                    #result_eval = 
            # print(f'f result: {date_prim}')

            if result[0] == semantic[0]:
                # print('FOUND')
                # print(result)
                # print('FOR')
                # print(semantic)

                if result == semantic:
                    # print('FOUND')
                    # print(result)
                    # print('FOR')
                    # print(semantic)
                    results.add(((date_prim,), param_flag))
                    #return [date_prim], param_flag

            else:
                # print('start to find cast')
                # print(result)
                # print(semantic)
                strich = PrimitiveType.TYPE_STRING == result[0] or PrimitiveType.TYPE_DATE == result[0]
                cast_funcs = self.match_type(result[0], semantic[0], strich= strich)
                #print(len(cast_funcs))

                for cast_func in cast_funcs:
                    cast_result = cast_func.get_semantic_prim([result[1]])
                    #print(f'cast result: {cast_result}')

                    if cast_result == semantic:
                        # print('FOUND')
                        # print(cast_result)
                        # print('FOR')
                        # print(semantic)
                        results.add(((date_prim, cast_func), param_flag))
                        #return [date_prim, cast_func], param_flag
                    # print('11111111111111')
                    # print(result)
                    # if semantic == result:
                    #     print('FOund')
        return results
