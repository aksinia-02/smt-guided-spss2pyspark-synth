from EGraph import EGraph
from EGraph.ENode import ENode

from primitives.Semantics import LiteralSemantics, DateSemantics
from primitives.composite_registry import MasterPrimitiveRegistry

from enums.categories import Category

import logging
from logger.logger import logger, log_primitive, log_list

class RewriteRule:
    def __init__(self, primitives: MasterPrimitiveRegistry):
        self.primitives = primitives

    def apply(self, egraph: EGraph, primitives) -> bool:
        changed = False

        for eclass_id, enodes in list(egraph.M.items()):
            semantic = egraph.S[eclass_id]

            #for enode in enodes:
            enode = next(iter(enodes))
            if enode.op.category == Category.STRING_FUNCTION:
                logger.debug(f"Entering first rule | Node: {enode}")

                eclass_id = egraph.U.find(eclass_id)
                print(f'canonical eclass_id: {eclass_id}')

                children_sem, children_ids = egraph.get_date_semantic_children_values(eclass_id)
                logger.debug(f"Children: {children_sem}, ids: {children_ids}")
                results = self.primitives.find_semantic_over_date_primitives(semantic, children_sem, next(iter(egraph.M[eclass_id])).op.semantics.date_rep)
                print(f'Enode: {enode} | Children: {children_sem}, ids: {children_ids} | Results: {results}')

                for eq_prims, param_flag in results:

                    n = len(eq_prims)

                    if n > 0:
                        if param_flag:
                            child_id = egraph.add(ENode(op=eq_prims[0], children=(children_ids[0],)))
                        else:
                            child_id = egraph.add(ENode(op=eq_prims[0], children=()))

                        if n == 1:
                            changed = egraph.merge(eclass_id, child_id)
                        else:
                            cast_id = egraph.add(ENode(op=eq_prims[1], children=(child_id,)))
                            changed = egraph.merge(eclass_id, cast_id)

            if enode.op.category == Category.CAST_TYPE:
                logger.debug(f"Entering second rule | Node: {enode}")

                child_id = enode.children[0]
                canon_id = egraph.U.find(child_id)
                child = next(iter(egraph.M.get(canon_id)))
                child_type = child.op.return_type[0]

                if child_type == enode.op.return_type[0]:
                    changed = egraph.merge(eclass_id, child_id)

            if enode.op.category == Category.CAST_TYPE:
                logger.debug(f"Entering third rule | Node: {enode}")

                eclass_id = egraph.U.find(eclass_id)
                print(f'canonical eclass_id: {eclass_id}')
            
                children_sem, children_ids = egraph.get_date_semantic_children_values(eclass_id)
                logger.debug(f"Children: {children_sem}, ids: {children_ids}")

                print('hello')
                print(eclass_id)
                print(egraph)
                
                results = self.primitives.find_semantic_over_date_primitives(semantic, children_sem, next(iter(egraph.M[eclass_id])).op.semantics.date_rep)
                print(f'Enode: {enode} |  Children: {children_sem}, ids: {children_ids} | Results: {results}')

                for eq_prims, param_flag in results:

                    n = len(eq_prims)
                    if n > 0:
                        if param_flag:
                            child_id = egraph.add(ENode(op=eq_prims[0], children=(children_ids[0],)))
                        else:
                            child_id = egraph.add(ENode(op=eq_prims[0], children=()))
                        if n == 1:
                            changed = egraph.merge(eclass_id, child_id)
                        else:
                            cast_id = egraph.add(ENode(op=eq_prims[1], children=(child_id,)))
                            changed = egraph.merge(eclass_id, cast_id)

            if enode.op.category == Category.ARITHMETIC:
                logger.debug(f"Entering flip rule | Node: {enode}")


                if enode.op.name == "<=" or enode.op.name == '<':
                    new_op = self.primitives.get_function_by_name(enode.op.name.replace('<', '>'))
                    new_id = egraph.add(ENode(op=new_op, children=(enode.children[1], enode.children[0])))
                    changed = egraph.merge(eclass_id, new_id)

            if enode.op.semantics.symmetric:
                print('Found symmetric')

                child1_id, child2_id = enode.children
                new_id = egraph.add(ENode(op=enode.op, children=(child2_id, child1_id)))
                print(f'class id: {eclass_id}, new id: {new_id}')
                changed = egraph.merge(eclass_id, new_id)
                print(f'Changed {changed}')

            if enode.op.category == Category.CONDITION:

                if enode.op.name == "and":

                    child1_id, child2_id = enode.children

                    child1 = egraph.find_node_in_class(child1_id, ">=")
                    child2 = egraph.find_node_in_class(child2_id, ">=")

                    if child1 is not None and child2 is not None:

                        child_1_1_id, child_1_2_id = child1.children
                        child_2_1_id, child_2_2_id = child2.children

                        new_op = self.primitives.get_function_by_name('between')
                        if child_1_1_id == child_2_2_id:
                            new_id = egraph.add(ENode(op=new_op, children=(child_1_1_id, child_1_2_id, child_2_1_id)))
                            changed = egraph.merge(eclass_id, new_id)
                        elif child_1_2_id == child_2_1_id:
                            new_id = egraph.add(ENode(op=new_op, children=(child_1_2_id, child_2_2_id, child_1_1_id)))
                            changed = egraph.merge(eclass_id, new_id)
                        print('Done')

        
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