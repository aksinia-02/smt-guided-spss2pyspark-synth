from abc import ABC, abstractmethod
from typing import List, Optional, Callable, Any, Tuple
from dataclasses import dataclass
from enums.smt_types import DateType
from enums.categories import Category

from .Semantics import BaseSemantics
from .Primitive import Primitive

ArgSpec = Tuple[DateType, bool]

@dataclass
class BasePrimitiveRegistry(ABC):
    def __init__(self):
        self.primitives: List[Primitive] = []
        self.register_all()

    @abstractmethod
    def register_all(self) -> None:
        """Subclasses override this to register their domain-specific functions/primitives."""
        pass

    def make_pyspark_formatter(self, template: str, arg_specs: List[ArgSpec] = []) -> Callable[[List[str]], str]:
        """
        Factory function that binds to a static string template immediately.
        Completely prevents late-binding loop variable bugs.
        """
        def formatter(args: List[str]) -> str:
            if not args:
                return template

            formatted_args = []
            for raw_arg, (date_type, is_column) in zip(args, arg_specs):
                # If the template already wrapped it or it's a raw column reference, handle here:
                if is_column and not raw_arg.startswith("F.lit(") and not raw_arg.startswith("F.col("):
                    formatted_args.append(f"F.lit({raw_arg})")
                else:
                    formatted_args.append(str(raw_arg))

            if "{0}" in template:
                return template.format(*formatted_args)
            return template

        return formatter

    def add_primitive(
        self, name: str, 
        return_type: DateType, 
        arg_types: List[DateType], 
        category: Category, 
        semantics: BaseSemantics,
        pyspark_str: str,
        python_eval: Optional[Callable[[List[Any], Any], Any]] = None,
        func: bool = False
    ) -> None:
        primitive = Primitive(
            name=name,
            return_type=return_type,
            arg_types=arg_types,
            category=category,
            semantics=semantics,
            to_pyspark=self.make_pyspark_formatter(pyspark_str, arg_types),
            python_eval=python_eval
        )
        self.primitives.append(primitive)

    def print_primitives(self) -> None:
        for primitive in self.primitives:
            print(str(primitive) + "\n")

        print(len(self.primitives), "primitives initialized.")