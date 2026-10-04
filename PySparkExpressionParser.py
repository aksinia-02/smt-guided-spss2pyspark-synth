from enums.smt_types import DateType
from dataclasses import dataclass
from typing import List, Union
from SPSSExpressionParser import ASTNode, ParamNode, FunctionCallNode, BinaryOpNode, LiteralNode

from primitives.composite_registry import MasterPrimitiveRegistry


class SPSSASTVisitor:
    """Traverses the SPSS AST to extract parameters and used functions."""
    def __init__(self):
        self.params: List[str] = []
        self.functions: List[str] = []

    def visit(self, node: ASTNode):
        if isinstance(node, ParamNode):
            if node.name not in self.params:
                self.params.append(node.name)

        elif isinstance(node, FunctionCallNode):
            if node.name not in self.functions:
                self.functions.append(node.name)
            for arg in node.args:
                self.visit(arg)

        elif isinstance(node, BinaryOpNode):
            self.visit(node.left)
            self.visit(node.right)


SPSS_TO_PYSPARK_FUNCTION_MAP = {
    "startstring": "F.substring",
    "endstring": "F.substring",
    "concat": "F.concat",
    "+": "F.concat"
}

class ContextAwareSynthesizer:
    def __init__(self, decoder, semantic_matcher):
        self.decoder = decoder
        self.matcher = semantic_matcher
        self.primitives = MasterPrimitiveRegistry()

    def _synthesize_full_ast(self, node: ASTNode, expected_type: DateType) -> str:
        """Recursively walks the AST and emits PySpark Column expressions."""
        
        # Parameter Node (TODO: now it woks only for date primitives)
        if isinstance(node, ParamNode):
            try:
                # Try resolving the individual parameter using your SemanticMatcher
                decoded_spec = self.decoder.decode(node.name)
                candidates = self.matcher.filter_candidates(decoded_spec, self.primitives.date_primitives)
                
                if candidates:
                    best_primitive, _ = candidates[0]
                    if decoded_spec.amount is not None and best_primitive.arg_types:
                        return best_primitive.to_pyspark([str(decoded_spec.amount)])
                    return best_primitive.to_pyspark([])
            except Exception:
                print( f"Failed to decode or match parameter: {node.name}. Falling back to direct column reference.")
            
            # Fallback if no matching primitive is found
            return f"F.col('{node.name}')" #TODO F.lit vs F.col

        # Literal Nodes
        elif isinstance(node, LiteralNode):
            if isinstance(node.value, str):
                return f"F.lit('{node.value}')"
            return str(node.value)

        # Binary Operations TODO: now supports only concatination and addition ---
        elif isinstance(node, BinaryOpNode):
            left_expr = self._synthesize_full_ast(node.left, expected_type)
            right_expr = self._synthesize_full_ast(node.right, expected_type)
            
            if node.op == "+":
                # Check if we are dealing with string concatenation vs arithmetic addition
                if "F.lit('" in left_expr or "F.lit('" in right_expr or "F.substring" in left_expr or "F.substring" in right_expr:
                    return f"F.concat({left_expr}, {right_expr})"
                return f"({left_expr} + {right_expr})"
            
            return f"({left_expr} {node.op} {right_expr})"

        # Function Calls TODO: currently supports only string functions like startstring, endstring, substring
        elif isinstance(node, FunctionCallNode):
            fn_name = node.name.lower()

            func = self.primitives.get_function_by_name(fn_name)
            args_len = len(node.args)

            if args_len == 1:
                expr = self._synthesize_full_ast(node.args[0], expected_type)
                return func.to_pyspark([expr])
            else:
                length_expr = self._synthesize_full_ast(node.args[0], expected_type)
                target_expr = self._synthesize_full_ast(node.args[1], expected_type)

                return func.to_pyspark([target_expr,length_expr])

            # elif fn_name in ["concat", "string_concat"]:
            #     arg_exprs = [self._synthesize_full_ast(arg, expected_type) for arg in node.args]
            #     return f"F.concat({', '.join(arg_exprs)})"

            # else:
            #     # Generic fallback for unmapped function calls
            #     arg_exprs = [self._synthesize_full_ast(arg, expected_type) for arg in node.args]
            #     return f"F.{fn_name}({', '.join(arg_exprs)})"

        raise TypeError(f"Unsupported AST node type: {type(node)}")

    def synthesize(self, spss_ast: ASTNode, expected_type: DateType) -> str:

        visitor = SPSSASTVisitor()
        visitor.visit(spss_ast)

        first_expression = self._synthesize_full_ast(spss_ast, expected_type)
        print(f"First synthesized expression: {first_expression}")
        
        extracted_params = visitor.params 
        spss_functions = visitor.functions

        
        # TODO rewite functions mapping
        pyspark_functions = [
            SPSS_TO_PYSPARK_FUNCTION_MAP[fn] 
            for fn in spss_functions 
            if fn in SPSS_TO_PYSPARK_FUNCTION_MAP
        ]

        for param in pyspark_functions:
            print(param)
        
        for param in extracted_params:
            print(param)
        return

        # TODO: only for date parameters, we need to handle other types of parameters as well
        if len(extracted_params) == 1:
            print(extracted_params[0])
            raw_param = extracted_params[0]
            decoded_spec = self.decoder.decode(raw_param)
        #TODO: for every candidate calculate the complexity of calculation
        #TODO: another idea filter candidates must return not the score only but also what is wrong with the candidate
            
            candidates = self.matcher.filter_candidates(decoded_spec, self.primitives.date_primitives)
            target_cast_functions = self.primitives.get_functions_with_specified_target_type(expected_type)

            synthesized_expressions = []

            for candidate, top_score in candidates:

                if decoded_spec.amount is not None and candidate.arg_types:
                    core_expr = candidate.to_pyspark([str(decoded_spec.amount)])
                else:
                    core_expr = candidate.to_pyspark([])

                print(f'compare {candidate.return_type} with {expected_type}')
                if candidate.return_type.eq_exact(expected_type):
                    final_expr = f'F.lit({core_expr})'
                    print(f"\nCandidate matches expected type: {final_expr}")
                else:
                    print(f"\nCandidate does not match expected type: {core_expr}. Looking for cast functions to convert {candidate.return_type} to {expected_type}.")
                    matching_casts = self.primitives.get_functions_with_specified_import_type(
                        import_type=candidate.return_type, 
                        functions=target_cast_functions
                    )

                    # print('___________________________________')
                    # self.primitives.print_premitives(matching_casts)

                    if matching_casts:
                        for cast_func in matching_casts:
                            print(f"Found matching cast function: {cast_func.to_pyspark([core_expr])}")
                            synthesized_expressions.append((cast_func.to_pyspark([core_expr]), top_score))
                        continue
                    else:
                        print("No matching cast function found for candidate:", core_expr)
                        continue
                print(f"Adding synthesized expression: {final_expr} with score {top_score}")
                synthesized_expressions.append((final_expr, top_score))

            return synthesized_expressions

        # TODO implement synthesis for more complex ASTs with multiple parameters and functions and make it before trying to find better solution
        return self._synthesize_full_ast(spss_ast, pyspark_functions)