from EGraph import EGraph
from EGraph.ENode import ENode

from primitives.Semantics import LiteralSemantics, DateSemantics
from primitives.composite_registry import MasterPrimitiveRegistry

from enums.categories import Category

class RewriteRule:
    def __init__(self, primitives: MasterPrimitiveRegistry):
        self.primitives = primitives

    def apply(self, egraph: EGraph, primitives) -> bool:
        changed = False

        for eclass_id, enodes in list(egraph.M.items()):
            semantic = egraph.S[eclass_id]
            print(next(iter(enodes)))

            for enode in enodes:
                if enode.op.category == Category.STRING_FUNCTION:

                    children_sem, children_ids = egraph.get_date_semantic_children_values(eclass_id)
                    print(f'Children: {children_sem}')
                    print(children_ids)
                    eq_prims, param_flag = self.primitives.find_semantic_over_date_primitives(semantic, children_sem)

                    n = len(eq_prims)

                    if n > 0:
                        if param_flag:
                            child_id = egraph.add(ENode(op=eq_prims[0], children=(children_ids[0],)))
                        else:
                            child_id = egraph.add(ENode(op=eq_prims[0], children=()))

                        if n == 1:
                            egraph.merge(eclass_id, child_id)
                        else:
                            cast_id = egraph.add(ENode(op=eq_prims[1], children=(child_id,)))
                            egraph.merge(eclass_id, cast_id)

        print(egraph)


        
        return changed

    def find_equivalent(self, semantic, children):
        print('---------------')

        #TODO check that all children are date primitives and literals
        #print(children)

        eq_prims = self.primitives.find_semantic_over_date_primitives(semantic, children)
        #print(f'found for {semantic} {eq_prims}')

        return eq_prims






























    

    def _apply_month_extraction(self, egraph: EGraph, primitives) -> bool:
        changed = False
        # Iterate over e-classes looking for outer `endstring`
        for eclass_id, enodes in list(egraph.M.items()):
            for enode in enodes:
                if enode.op.name == "endstring" and len(enode.children) == 2:
                    len_class, inner_class = enode.children
                    
                    # Check if len is 2
                    len_nodes = egraph.M[egraph.U.find(len_class)]
                    if any(n.op == 2 for n in len_nodes):
                        # Inspect inner node for startstring(6, X)
                        for inner_node in egraph.M[egraph.U.find(inner_class)]:
                            if inner_node.op.name == "startstring" and len(inner_node.children) == 2:
                                inner_len_class, x_class = inner_node.children
                                if any(n.op == 6 for n in egraph.M[egraph.U.find(inner_len_class)]):
                                    
                                    # We matched: endstring(2, startstring(6, X))
                                    # Construct new MonthComponent ENode
                                    month_prim = primitives.get_function_by_name("month_component")
                                    new_node = ENode(op=month_prim, children=(x_class,))
                                    new_id = egraph.add(new_node)
                                    
                                    # Union new representation with original eclass
                                    if egraph.U.find(eclass_id) != egraph.U.find(new_id):
                                        egraph.U.union(eclass_id, new_id)
                                        changed = True
        return changed

    def _apply_iso_fusion(self, egraph: EGraph, primitives) -> bool:
        changed = False
        # Search for full 3-part concat matching Year(X) + Month(X) + Day(X)
        # When found where X = e-class 1 (D.as_int.plus_day):
        # Merge root concat e-class (14) with e-class 3 (D.as_str.plus_day)
        
        # Example union trigger once pattern is matched:
        # egraph.U.union(14, 3)
        return changed