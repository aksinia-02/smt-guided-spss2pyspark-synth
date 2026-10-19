from typing import Dict, Set, Tuple

from EGraph.ENode import ENode
from EGraph.UnionFind import UnionFind

from enums.smt_types import PrimitiveType

from primitives.Semantics import LiteralSemantics, DateSemantics

# Example of execution:
# For expression (x + 0) * y
# UnionFind: {0: 0, 1: 1, 2: 2}
# Add (x + 0) -> EClass ID 3 with children (0, 1)
# Merge (3, 0) -> canon_children: {0: 0, 1: 1, 2: 2, 3: 0}
# Add node (x + 0) * y -> EClass ID 4 with children (3, 2) -> canonicalize to (0, 2)
# Add node x * y -> EClass ID 5 with children (0, 2) -> canonicalize to (0, 2) already exists, so return EClass ID 4

# Merge of 0:x and 3:x + 0 -> root1 = 0, root2 = 3, new_root = 3, old_root = 0
# self.M[new_root] = {ENode(op=Primitive.ADD, children=(0, 1)), ENode(op=Primitive.VAR, children=())}

SemanticSpec = Tuple[PrimitiveType, str]

class EGraph:
    def __init__(self):
        self.U = UnionFind()
        self.H: Dict[ENode, int] = {} # check if an ENode already exists in the graph and get its EClass ID
        self.M: Dict[int, Set[ENode]] = {} # mapps EClass IDs to their corresponding ENode sets
        self.class_data: Dict[int, dict] = {} # metadata for each EClass

        self.S: Dict[int, SemanticSpec] = {}# mapps EClass IDs to extracted semantic
        self.R: Dict[int, str] = {}

        self.root_id: int

        self.len_nodes = 0

    # after merging two EClasses, we need to update the ENode children to their canonical representatives
    # replaces every child id with its leader id in the ENode children
    def canonicalize(self, node: ENode) -> ENode:
        """Definition 2.2: canonicalize(f(a1, a2, ...)) = f(find(a1), find(a2), ...)."""
        canon_children = tuple(self.U.find(c) for c in node.children)
        return ENode(node.op, canon_children)

    # Example of add execution:
    # For expression (x + 0) * y
    def add(self, node: ENode) -> int:
        node = self.canonicalize(node)
        if node in self.H:
            return self.U.find(self.H[node])

        eclass_id = self.U.make_set()
        self.H[node] = eclass_id
        self.M[eclass_id] = {node}
        self.class_data[eclass_id] = {"type": None, "score": float("inf")}
        self.len_nodes += 1

        self.fill_semanctic(eclass_id, node)
        #self.fill_pyspark_repr(node)

        return eclass_id

    def merge(self, id1: int, id2: int) -> int:
        root1 = self.U.find(id1)
        root2 = self.U.find(id2)
        if root1 == root2:
            return root1

        new_root = self.U.union(root1, root2)
        old_root = root1 if new_root == root2 else root2

        # Combine nodes in equivalence M
        self.M[new_root].update(self.M[old_root])
        del self.M[old_root]
        return new_root

    def fill_semanctic(self, eclass_id: int, enode: ENode):

        sem = self.S.get(eclass_id)

        if sem is None:
            children = []
            for child_id in enode.children:
                child_sem = self.S[child_id]
                children.append(child_sem)
            self.S[eclass_id] = enode.get_semantic(children)

    # def fill_pyspark_repr(self, enode: ENode):

    #     children = []
    #     for child_id in enode.children:
    #         child_repr = self.R[child_id]
    #         children.append(child_repr)
    #     self.R[]



    def fill_init_semantic(self):
        #TODO make assertion
        for eclass_id, enodes in list(self.M.items()):
            for enode in enodes:
                children = []
                print(enode)
                for child_id in enode.children:
                    child_sem = self.S[child_id]
                    children.append(child_sem)
                evaluation = enode.get_semantic(children)
                print(evaluation)
                self.S[eclass_id] = evaluation

    
    def get_date_semantic_children_values(
        self,
        eclass_id: int,
        parent_date: bool = False,
        visiting: set[tuple[int, bool]] | None = None,
    ):
        if visiting is None:
            visiting = set()

        canon_class_id = self.U.find(eclass_id)
        state = (canon_class_id, parent_date)

        # Detect a cycle along the current recursion path
        if state in visiting:
            return [], []

        enodes = self.M.get(canon_class_id, set())

        if not enodes:
            return [], []

        visiting.add(state)

        try:
            children_values = []
            children_ids = []

            for enode in enodes:
                if len(enode.children) == 0 and parent_date:
                    val = self.S.get(canon_class_id)

                    if val is not None and val[1] not in children_values:
                        children_values.append(val[1])
                        children_ids.append(canon_class_id)

                else:
                    child_date = isinstance(
                        enode.op.semantics, DateSemantics
                    )

                    for child_eclass_id in enode.children:
                        canon_child_id = self.U.find(child_eclass_id)

                        res_sem, res_id = (
                            self.get_date_semantic_children_values(
                                canon_child_id,
                                child_date,
                                visiting,
                            )
                        )

                        if isinstance(res_sem, (list, tuple)):
                            for sem_item in res_sem:
                                if sem_item not in children_values:
                                    children_values.append(sem_item)

                            for id_item in res_id:
                                if id_item not in children_ids:
                                    children_ids.append(id_item)

                        elif res_sem is not None:
                            if res_sem not in children_values:
                                children_values.append(res_sem)

                            if (
                                res_id is not None
                                and res_id not in children_ids
                            ):
                                children_ids.append(res_id)

            return children_values, children_ids

        finally:
            visiting.remove(state)


    def __repr__(self):
        return f"EGraph(\n\nUnionFind={self.U}, \n\nH={self.H}, \n\nM={self.M}, \n\nS={self.S})"