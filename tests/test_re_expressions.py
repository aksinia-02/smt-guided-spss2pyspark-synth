from SPSSDateParamDecoder import SPSSDateParamDecoder
from SPSSExpressionParser import SPSSExpressionParser
from ContextAwareSynthesizer import ContextAwareSynthesizer
from SemanticMatcher import SemanticMatcher
from enums.smt_types import PrimitiveType
from handlers.GECISVerifierHandler import UserConsoleHandler, GecisVerifierHandler


def test_re_expressions(file_paths):
    decoded_questions = []
    for file_path in file_paths:
        with open(file_path, 'r') as f:
            for question_answer in f:
                if question_answer == "\n":
                    continue
                question_answer = question_answer.split("#")
                print(question_answer)
                expr = question_answer[0].strip()
                exp_type = question_answer[2].strip()

                parser = SPSSExpressionParser(expr)
                ast = parser.parse()
                parser.print_ast(ast)


                synthezer = ContextAwareSynthesizer(SPSSDateParamDecoder(), SemanticMatcher())

                exp_type = PrimitiveType.get_type_by_value(exp_type)
                candidates = synthezer.synthesize(ast, exp_type)

                user_handler = UserConsoleHandler()
                user_handler.select_candidate(candidates)
                return
                correct_answer = question_answer[1].strip()
                correct_answer = ""
                print(expr)
                try:
                    decoded = SPSSDateParamDecoder.decode(expr)
                    #print(f"Decoded '{expr}': {decoded}; Expected: {correct_answer}")
                    decoded_questions.append(decoded)
                except ValueError as e:
                    print(f"Error decoding '{expr}': {e}")
    return decoded_questions