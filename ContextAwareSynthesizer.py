from enums.smt_types import DateType
from dataclasses import dataclass
from typing import List, Union
from SPSSExpressionParser import ASTNode, ParamNode, FunctionCallNode, BinaryOpNode


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
    def __init__(self, decoder, semantic_matcher, primitives):
        self.decoder = decoder
        self.matcher = semantic_matcher
        self.primitives = primitives

    def synthesize(self, spss_ast: ASTNode, expected_type: DateType) -> str:

        visitor = SPSSASTVisitor()
        visitor.visit(spss_ast)
        
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

        # TODO: only for date parameters, we need to handle other types of parameters as well
        if len(extracted_params) == 1 and len(pyspark_functions) == 0:
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

                if candidate.return_type == expected_type:
                    final_expr = f'F.lit({core_expr})'
                else:
                    matching_casts = self.primitives.get_functions_with_specified_import_type(
                        import_type=candidate.return_type, 
                        functions=target_cast_functions
                    )

                    if matching_casts:
                        cast_func = matching_casts[0]
                        final_expr = cast_func.to_pyspark([core_expr])
                    else:
                        print("No matching cast function found for candidate:", candidate)
                        final_expr = f'F.lit({core_expr})'

                synthesized_expressions.append((final_expr, top_score))

            return synthesized_expressions

        # TODO implement synthesis for more complex ASTs with multiple parameters and functions and make it before trying to find better solution
        return self._synthesize_full_ast(spss_ast, pyspark_functions)