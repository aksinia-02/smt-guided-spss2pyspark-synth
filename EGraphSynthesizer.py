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

import functools
import inspect

import logging
from logger.logger import logger, log_primitive, log_list

def log_step(func):
    """A robust decorator to log entry, arguments (like node), and exit of class methods."""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        sig = inspect.signature(func)
        bound_args = sig.bind(self, *args, **kwargs)
        bound_args.apply_defaults()
        
        node_val = bound_args.arguments.get('node', 'N/A')
        
        logger.debug(f"Entering {func.__name__} | Node: {node_val}")
        
        try:
            result = func(self, *args, **kwargs)
            #print(result)
            result_name = type(result).__name__ if result is not None else "None"
            logger.debug(f"Exiting {func.__name__} -> Produced id: {result}")
            return result
        except Exception as e:
            logger.error(f"Exception in {func.__name__}: {e}")
            raise
            
    return wrapper


class EGraphSynthesizer:
    def __init__(self, decoder, semantic_matcher):
        logger.info(f"Initializing synthesir")
        self.decoder = decoder
        self.matcher = semantic_matcher
        self.primitives = MasterPrimitiveRegistry()

        # for p in self.primitives.date_primitives:
        #     if "D.as_str" in p.name and len(p.arg_types) == 0:
        #         print(
        #             "name:", p.name,
        #             "semantics:", p.semantics.name,
        #             "eval:", p.python_eval([], None)
        #         )
        #     else:
        #         print(
        #             "name:", p.name,
        #             "semantics:", p.semantics.name,
        #             "eval:", p.python_eval([1], None)
        #         )

    def synthesize(self, spss_ast, expected_type: DateType, max_iterations: int = 3) -> str:

        # visitor = SPSSASTVisitor()
        # visitor.visit(spss_ast)

        # extracted_params = visitor.params 

        egraph = EGraph()

        logger.debug("##########       Construction EGraph       ##########")
        root_id = self.ingest_spss_ast(egraph, spss_ast, expected_type)
        egraph.root_id = root_id

        logger.debug(egraph)

        #egraph.fill_init_semantic()

        logger.debug("##########       Rewrite EGraph       ##########")
        rewriter = RewriteRule(self.primitives)
        for _ in range(max_iterations):
            logger.debug(f' new Graph {egraph}')
            if not rewriter.apply(egraph, self.primitives):
                break

        extractor = EGraphExtractor(egraph, self.primitives)
        result = extractor.extract_best()
        root_id = egraph.U.find(root_id)

        expressions = extractor.extract_all()
        print(expressions)

        for item in expressions:
            print(item)

        return result.get(root_id)

    @log_step
    def ingest_spss_ast(self, egraph: EGraph, node, expected_type) -> int:
        """Recursively populates the e-graph from an SPSS AST node."""

        #logger.debug(f"Entering {func.__name__} | Node: {node}, Expected Type: {expected_type}")

        if isinstance(node, ParamNode):
            decoded_spec = self.decoder.decode(node.name)

            child_id = None
            if decoded_spec.amount is not None:
                child_id = egraph.add(ENode(op=self.primitives.return_primitive_for_literal(decoded_spec.amount), children=()))

            candidates = self.matcher.filter_candidates(decoded_spec, self.primitives.date_primitives)
            best_prim = candidates[0][0]

            cand_enode = ENode(op=best_prim, children=(child_id,) if child_id is not None else ())
            cand_id = egraph.add(cand_enode)

            log_primitive("Best primitive found", best_prim, level=logging.INFO)

            if best_prim.return_type != expected_type:

                # expected_type = DateType.get_type_by_value_format(expected_type, best_prim.return_type.format)
                # print('Expected type')
                # print(expected_type)

                cast_func = self.primitives.match_type(best_prim.return_type, expected_type)
                log_list("Cast functions found", cast_func, level=logging.INFO)
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

            log_primitive("Function found", func, level=logging.INFO)

            rewrite_cast = False

            arg_types = func.arg_types

            child_ids: Tuple[int, ...] = ()
            for i, arg in enumerate(node.args):

                exp_child_type = PrimitiveType.get_type_by_value(arg_types[i][0])
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