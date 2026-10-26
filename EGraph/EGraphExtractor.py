from EGraph.EGraph import EGraph
from enums.smt_types import DateType

from dataclasses import dataclass, field 

from math import inf
import itertools

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

    def extract_all(self):
        """
        Extracts all valid expressions for every canonical e-class,
        safely breaking cycles using a path-tracking visiting set.
        """
        # Map each canonical root to its set of (cost, expression) tuples
        cache: dict[int, set[tuple[float, str]]] = {}

        # Get all canonical e-class roots
        classes = {}
        for class_id, nodes in self.egraph.M.items():
            root = self.egraph.U.find(class_id)
            classes.setdefault(root, set()).update(nodes)

        def dfs(root_id: int, visiting: set[int]) -> set[tuple[float, str]]:
            # 1. Return cached results if already computed
            if root_id in cache:
                return cache[root_id]

            # 2. Cycle Detection: If this root is already in the current recursion path, break the cycle
            if root_id in visiting:
                return set()

            visiting.add(root_id)
            local_exprs = set()

            try:
                nodes = classes.get(root_id, set())
                for node in nodes:
                    child_ids = tuple(self.egraph.U.find(c) for c in node.children)

                    # Recursively get expressions for all children
                    child_expr_lists = []
                    all_children_valid = True
                    
                    for c_id in child_ids:
                        c_exprs = dfs(c_id, visiting)
                        if not c_exprs:
                            all_children_valid = False
                            break
                        child_expr_lists.append(c_exprs)

                    if not all_children_valid:
                        continue

                    # Combine child expressions using Cartesian product
                    for child_comb in itertools.product(*child_expr_lists):
                        op_weight = getattr(node.op.semantics, 'weight', 1.0)
                        candidate_cost = op_weight + sum(c[0] for c in child_comb)
                        
                        child_strings = [c[1] for c in child_comb]
                        candidate_expr = node._render(child_strings)
                        
                        local_exprs.add((candidate_cost, candidate_expr))

            finally:
                visiting.remove(root_id)

            cache[root_id] = local_exprs
            return local_exprs

        # Run DFS for all roots
        results = {}
        for root in classes:
            expr_set = dfs(root, set())
            if expr_set:
                results[root] = sorted(expr_set, key=lambda x: x[0])

        return results

    # def extract_all(self):
    #     """
    #     Return all valid expressions for every reachable e-class, 
    #     ordered by cost (ascending).

    #     Returns:
    #         dict[int, list[tuple[float, str]]]
    #         Maps canonical e-class IDs to a list of (cost, expression) tuples, 
    #         sorted from lowest to highest cost.
    #     """
    #     classes = {}
    #     for class_id, nodes in self.egraph.M.items():
    #         root = self.egraph.U.find(class_id)
    #         classes.setdefault(root, set()).update(nodes)

    #     # Map each root to a set of unique (cost, expression) tuples
    #     expressions: dict[int, set[tuple[float, str]]] = {root: set() for root in classes}

    #     print(classes)

    #     # Iteratively discover and propagate expressions until fixpoint
    #     changed = True
    #     while changed:
    #         print(f'Expressions: {expressions}')
    #         changed = False
    #         return

    #         for root, nodes in classes.items():
    #             for node in nodes:
    #                 child_ids = tuple(self.egraph.U.find(c) for c in node.children)

    #                 # An operator can be evaluated only when all children have at least one known expression
    #                 if any(c not in expressions or not expressions[c] for c in child_ids):
    #                     continue

    #                 # Get all expression lists for each child
    #                 child_expr_lists = [expressions[c] for c in child_ids]

    #                 # Take the Cartesian product to combine all possible child expressions
    #                 for child_comb in itertools.product(*child_expr_lists):
    #                     # child_comb is a tuple of (child_cost, child_code) for each child
    #                     candidate_cost = node.op.semantics.weight + sum(c[0] for c in child_comb)
    #                     child_strings = [c[1] for c in child_comb]
                        
    #                     candidate_expr = node._render(child_strings)
    #                     candidate = (candidate_cost, candidate_expr)

    #                     # If this is a new unique expression for this root, add it and mark changed
    #                     if candidate not in expressions[root]:
    #                         expressions[root].add(candidate)
    #                         changed = True

    #     # Sort each e-class's expressions by cost (ascending) and return
    #     result = {}
    #     for root, expr_set in expressions.items():
    #         if expr_set:
    #             sorted_exprs = sorted(expr_set, key=lambda x: x[0])
    #             result[root] = sorted_exprs

    #     return result