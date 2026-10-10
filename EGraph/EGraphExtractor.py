from EGraph.EGraph import EGraph
from enums.smt_types import DateType

from dataclasses import dataclass, field 

@dataclass
class ExtractedExpr:
    cost: float
    code: str


class EGraphExtractor:
    def __init__(self, egraph: EGraph, primitives):
        self.egraph = egraph
        self.primitives = primitives

    def extract(self, eclass_id: int, expected_type: DateType) -> ExtractedExpr:
        eclass_id = self.egraph.uf.find(eclass_id)
        best_expr = ExtractedExpr(cost=float("inf"), code="")

        for node in self.egraph.classes[eclass_id]:
            # Terminals
            if node.op == "LITERAL":
                val = f"'{node.payload}'" if isinstance(node.payload, str) else str(node.payload)
                expr = ExtractedExpr(cost=1.0, code=f"F.lit({val})")

            elif node.op == "PARAM":
                expr = ExtractedExpr(cost=10.0, code=f"F.col('{node.payload}')")

            elif node.op == "PRIMITIVE":
                prim = node.payload
                code = prim.to_pyspark([])
                cost = 5.0
                if hasattr(prim, 'semantics') and hasattr(prim.semantics, 'weight'):
                    cost = float(prim.semantics.weight)
                expr = ExtractedExpr(cost=cost, code=code)

            # Operators / Function Applications
            elif node.op == "F.concat":
                children_ext = [self.extract(c, expected_type) for c in node.children]
                total_cost = sum(c.cost for c in children_ext) + 2.0
                args_code = ", ".join(c.code for c in children_ext)
                expr = ExtractedExpr(cost=total_cost, code=f"F.concat({args_code})")

            elif node.op == "CAST":
                cast_func = node.payload
                child_ext = self.extract(node.children[0], cast_func.semantics.import_type)
                total_cost = child_ext.cost + cast_func.semantics.weight
                code = cast_func.to_pyspark([child_ext.code])
                expr = ExtractedExpr(cost=total_cost, code=code)

            else:
                # Generic fallback for binary/function nodes
                children_ext = [self.extract(c, expected_type) for c in node.children]
                total_cost = sum(c.cost for c in children_ext) + 1.0
                args_code = ", ".join(c.code for c in children_ext)
                expr = ExtractedExpr(cost=total_cost, code=f"{node.op}({args_code})")

            if expr.cost < best_expr.cost:
                best_expr = expr

        return best_expr