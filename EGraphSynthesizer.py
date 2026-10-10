from EGraph.EGraph import EGraph
from EGraph.EGraph import ENode
from EGraph.RewriteRule import RewriteRule
#from EGraph.EGraphExtractor import EGraphExtractor

from ContextAwareSynthesizer import SPSSASTVisitor

from enums.smt_types import DateType

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

        root_id = self.ingest_spss_ast(egraph, spss_ast, self.decoder, self.matcher, self.primitives, expected_type)
        print(egraph)

        egraph.fill_init_semantic()
        return

        rewriter = RewriteRule()
        rewriter.apply(egraph, self.primitives)
        return
        for _ in range(max_iterations):
            if not rewriter.apply(egraph, self.primitives):
                break

        extractor = EGraphExtractor(egraph, self.primitives)
        result = extractor.extract(root_id, expected_type)

        return result.code

    def ingest_spss_ast(self, egraph: EGraph, node, decoder, matcher, primitives, expected_type) -> int:
        """Recursively populates the e-graph from an SPSS AST node."""

        if isinstance(node, ParamNode):
            decoded_spec = self.decoder.decode(node.name)
            print(decoded_spec)

            child_id = None
            if decoded_spec.amount is not None:
                child_id = egraph.add(ENode(op=self.primitives.return_primitive_for_literal(decoded_spec.amount)))

            candidates = matcher.filter_candidates(decoded_spec, primitives.date_primitives)

            param_eclass = None
            for candidate, _ in candidates:
                cand_enode = ENode(op=candidate, children=(child_id,) if child_id is not None else ())
                cand_id = egraph.add(cand_enode)
                if param_eclass is None:
                    param_eclass = cand_id
                # if decoded_spec.amount is not None and candidate.arg_types:
                #     core_expr = candidate.to_pyspark([str(decoded_spec.amount)])
                # else:
                #     core_expr = candidate.to_pyspark([])
                # print(core_expr)
            
            return egraph.U.find(param_eclass)

        elif isinstance(node, LiteralNode):
            literal_primitive = self.primitives.return_primitive_for_literal(node.value)
            return egraph.add(ENode(op=literal_primitive))

        elif isinstance(node, BinaryOpNode):

            left_id = self.ingest_spss_ast(egraph, node.left, decoder, matcher, primitives, expected_type)
            left_type = next(iter(egraph.M[left_id])).op.return_type
            right_id = self.ingest_spss_ast(egraph, node.right, decoder, matcher, primitives, expected_type)

            plus_func = self.primitives.get_plus_function(left_type)
            return egraph.add(ENode(op=plus_func, children=(left_id, right_id)))

        elif isinstance(node, FunctionCallNode):
            fn_name = node.name.lower()
            func = self.primitives.get_function_by_name(fn_name)

            child_ids = tuple(
                self.ingest_spss_ast(egraph, arg, decoder, matcher, primitives, expected_type) # TODO replace with expected_type inference based on function signature
                for arg in node.args
            )

            return egraph.add(ENode(op=func, children=child_ids))

        raise TypeError(f"Unknown node type: {type(node)}")