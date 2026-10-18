from EGraph.EGraph import EGraph
from enums.smt_types import DateType

from dataclasses import dataclass, field 

from math import inf

@dataclass
class ExtractedExpr:
    cost: float
    code: str


class EGraphExtractor:
    def __init__(self, egraph: EGraph, primitives):
        self.egraph = egraph
        self.primitives = primitives

    def extract_best(self):
        """
        Return the minimum-cost expression for every reachable e-class.

        Returns:
            dict[int, tuple[float, str]]
            Maps canonical e-class IDs to (cost, expression).

        Assumes operator weights are numeric and non-negative.
        """

        classes = {}
        for class_id, nodes in self.egraph.M.items():
            root = self.egraph.U.find(class_id)
            classes.setdefault(root, set()).update(nodes)


        # cost[root] and expr[root] hold the best known solution.
        cost = {root: inf for root in classes}
        expr = {root: None for root in classes}


        # Repeatedly improve the best expression for each class.
        changed = True
        while changed:
            changed = False

            for root, nodes in classes.items():
                for node in nodes:
                    child_ids = tuple(self.egraph.U.find(c) for c in node.children)

                    # An operator can be evaluated only when all children
                    # have a known finite-cost expression.
                    if any(c not in cost or cost[c] == inf for c in child_ids):
                        continue

                    candidate_cost = node.op.semantics.weight + sum(
                        cost[c] for c in child_ids
                    )
                    child_strings = [expr[c] for c in child_ids]

                    #print(node)
                    candidate_expr = node._render(child_strings)

                    #print(candidate_expr)

                    # Strict improvement prevents endless updates on
                    # zero-cost cycles.
                    if candidate_cost < cost[root]:
                        cost[root] = candidate_cost
                        expr[root] = candidate_expr
                        changed = True

        return {
            root: (cost[root], expr[root])
            for root in classes
            if expr[root] is not None
        }

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