from typing import List, Tuple

from EGraph.EGraph import EGraph
from EGraph.EGraph import ENode
from EGraph.RewriteRule import RewriteRule
from EGraph.EGraphExtractor import EGraphExtractor

from ContextAwareSynthesizer import SPSSASTVisitor

from enums.smt_types import DateType, PrimitiveType
from enums.categories import Category

from primitives.composite_registry import MasterPrimitiveRegistry
from SPSSExpressionParser import ParamNode, FunctionCallNode, BinaryOpNode, LiteralNode


class EGraphSynthesizer:
    def __init__(self, decoder, semantic_matcher):
        self.decoder = decoder
        self.matcher = semantic_matcher
        self.primitives = MasterPrimitiveRegistry()

    def synthesize(self, spss_ast, expected_type: DateType, max_iterations: int = 3) -> str:

        # visitor = SPSSASTVisitor()
        # visitor.visit(spss_ast)

        # extracted_params = visitor.params 

        egraph = EGraph()

        root_id = self.ingest_spss_ast(egraph, spss_ast, expected_type)
        egraph.root_id = root_id

        print(egraph)

        #egraph.fill_init_semantic()

        rewriter = RewriteRule(self.primitives)
        for _ in range(max_iterations):
            print('new egraph')
            print(egraph)
            if not rewriter.apply(egraph, self.primitives):
                break

        extractor = EGraphExtractor(egraph, self.primitives)
        result = extractor.extract_best()
        root_id = egraph.U.find(root_id)

        return result.get(root_id)

    def ingest_spss_ast(self, egraph: EGraph, node, expected_type) -> int:
        """Recursively populates the e-graph from an SPSS AST node."""

        if isinstance(node, ParamNode):
            decoded_spec = self.decoder.decode(node.name)
            print(decoded_spec)

            child_id = None
            if decoded_spec.amount is not None:
                child_id = egraph.add(ENode(op=self.primitives.return_primitive_for_literal(decoded_spec.amount), children=()))

            candidates = self.matcher.filter_candidates(decoded_spec, self.primitives.date_primitives)
            best_prim = candidates[0][0]

            cand_enode = ENode(op=best_prim, children=(child_id,) if child_id is not None else ())
            cand_id = egraph.add(cand_enode)

            print('------------')
            print(best_prim.return_type)
            print(expected_type)
            print('------------')

            if best_prim.return_type != expected_type:

                # expected_type = DateType.get_type_by_value_format(expected_type, best_prim.return_type.format)
                # print('Expected type')
                # print(expected_type)

                cast_func = self.primitives.match_type(best_prim.return_type, expected_type)
                print(cast_func)
                cand_id = egraph.add(ENode(op=cast_func[0], children=(cand_id,)))

            #egraph.add(ENode(op=cast_func[0], children=(cand_id,)))
            return cand_id
            #return egraph.U.find(cand_id)

        elif isinstance(node, LiteralNode):
            literal_primitive = self.primitives.return_primitive_for_literal(node.value)
            return egraph.add(ENode(op=literal_primitive))

        elif isinstance(node, BinaryOpNode):

            left_id = self.ingest_spss_ast(egraph, node.left, expected_type)
            left_type = next(iter(egraph.M[left_id])).op.return_type
            right_id = self.ingest_spss_ast(egraph, node.right, expected_type)


            plus_func = self.primitives.get_binary_function(left_type, node.op)
            return egraph.add(ENode(op=plus_func, children=(left_id, right_id)))

        elif isinstance(node, FunctionCallNode):
            fn_name = node.name.lower()
            func = self.primitives.get_function_by_name(fn_name)

            print(func)

            rewrite_cast = False

            arg_types = func.arg_types

            child_ids: Tuple[int, ...] = ()
            for i, arg in enumerate(node.args):

                print('tttttttttttttt')
                print(arg_types[i][0])
                exp_child_type = PrimitiveType.get_type_by_value(arg_types[i][0])
                print(exp_child_type)
                print('tttttttttttttt')
                child_id = self.ingest_spss_ast(egraph, arg, exp_child_type)
                child_ids += (child_id,)

                if isinstance(arg, ParamNode):
                    rewrite_cast = True

            # print(f'Reqrite cast {rewrite_cast}') 

            # if rewrite_cast and func.category == Category.CAST_TYPE:
            #     # TODO
            #     func = self.primitives.match_type(DateType.TYPE_DATE, expected_type)
            #     print(func)

            # child_ids = tuple(
            #     self.ingest_spss_ast(egraph, arg, expected_type) # TODO replace with expected_type inference based on function signature
            #     for arg in node.args
            # )

            return egraph.add(ENode(op=func, children=child_ids))

        raise TypeError(f"Unknown node type: {type(node)}")