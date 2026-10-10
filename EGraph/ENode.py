from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Union, Optional
from enums.smt_types import DateType

from primitives.Primitive import Primitive


@dataclass(frozen=True)
class ENode:
    op: Primitive # The operator, parameter or function represented by this node
    children: Tuple[int, ...] = () # The children of this node, represented by their EClass IDs

    def __repr__(self):
        return f"ENode(op={self.op.name}, children={self.children})"

    def get_semantic(self, params: List[Primitive]):

        return self.op.get_semantic(params)