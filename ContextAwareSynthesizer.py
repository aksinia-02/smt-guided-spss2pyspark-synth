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


        if len(extracted_params) == 1:
            raw_param = extracted_params[0]
            decoded_spec = self.decoder.decode(raw_param)
            
            decoded_spec.target_type = expected_type
            
            candidates = self.matcher.filter_candidates(decoded_spec, self.primitives.primitives)
            candidates = candidates[0:4]
            for i in range(0, len(candidates)):
                best_primitive, top_score = candidates[i]
                if decoded_spec.amount is not None and best_primitive.arg_types:
                    print(best_primitive.to_pyspark([str(decoded_spec.amount)]))
                else:
                    print(best_primitive.to_pyspark([]))
            
            if candidates:
                best_primitive, top_score = candidates[0]
                
                if decoded_spec.amount is not None and best_primitive.arg_types:
                    return best_primitive.to_pyspark([str(decoded_spec.amount)])
                else:
                    return best_primitive.to_pyspark([])

        return self._synthesize_full_ast(spss_ast, pyspark_functions)