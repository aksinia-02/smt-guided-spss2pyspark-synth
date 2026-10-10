from dataclasses import dataclass, field
from typing import List, Tuple

from enums.smt_types import DateType, PrimitiveType

from primitives.Primitive import Primitive


@dataclass(frozen=True)
class ENode:
    op: Primitive # The operator, parameter or function represented by this node
    children: Tuple[int, ...] = () # The children of this node, represented by their EClass IDs

    def __repr__(self):
        return f"ENode(op={self.op.name}, children={self.children})"

    def get_semantic(self, params: List[Tupel[PrimitiveType, str]]):

        return self.op.get_semantic(params)