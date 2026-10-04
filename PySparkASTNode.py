from dataclasses import dataclass
from typing import List, Optional

class PySparkASTNode:
    """Base class for PySpark AST representations."""
    def render(self) -> str:
        raise NotImplementedError

@dataclass
class PySparkCol(PySparkASTNode):
    name: str
    def render(self) -> str:
        return f"F.col('{self.name}')"

@dataclass
class PySparkLit(PySparkASTNode):
    value: object
    def render(self) -> str:
        if isinstance(self.value, str):
            return f"F.lit('{self.value}')"
        return f"F.lit({self.value})"

@dataclass
class PySparkBinOp(PySparkASTNode):
    op: str
    left: PySparkASTNode
    right: PySparkASTNode
    def render(self) -> str:
        return f"({self.left.render()} {self.op} {self.right.render()})"

@dataclass
class PySparkPrimitiveNode(PySparkASTNode):
    primitive: object  # Reference to primitive object in registry
    args: List[PySparkASTNode]
    
    def render(self) -> str:
        rendered_args = [a.render() for a in self.args]
        return self.primitive.to_pyspark(rendered_args)

@dataclass
class PySparkCast(PySparkASTNode):
    child: PySparkASTNode
    target_type: str  # e.g. "t.IntegerType()"
    
    def render(self) -> str:
        return f"{self.child.render()}.cast({self.target_type})"