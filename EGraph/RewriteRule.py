from EGraph import EGraph, ENode

class RewriteRule:

    def fill_init_semanctic(self, egraph: EGraph):

        for eclass_id, enodes in list(egraph.M.items()):
            for enode in enodes:
                children = []
                for child_id in enode.children:
                    child = egraph.M[child_id]
                    children.append(child)
                evaluation = enode.get_semantic(children)
                print(evaluation)

    def apply(self, egraph: EGraph, primitives) -> bool:
        changed = False

        for eclass_id, enodes in list(egraph.M.items()):
            for enode in enodes:
                children = []
                for child_id in enode.children:
                    child = egraph.M[child_id]
                    children.append(child)
                evaluation = enode.get_semantic(children)
                print(evaluation)
        
        # # Rule 1: Match endstring(2, startstring(6, X)) -> MonthComponent(X)
        # changed |= self._apply_month_extraction(egraph, primitives)
        
        # # Rule 2: Match ISO Concat -> AsStr representation
        # changed |= self._apply_iso_fusion(egraph, primitives)
        
        return changed

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