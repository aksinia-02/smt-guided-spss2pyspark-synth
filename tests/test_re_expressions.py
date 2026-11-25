from SPSSDateParamDecoder import SPSSDateParamDecoder
from SPSSExpressionParser import SPSSExpressionParser
from ContextAwareSynthesizer import ContextAwareSynthesizer
from EGraphSynthesizer import EGraphSynthesizer
from SemanticMatcher import SemanticMatcher
from enums.smt_types import PrimitiveType
from handlers.GECISVerifierHandler import UserConsoleHandler, GecisVerifierHandler

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_re_expressions(file_paths, file_arg=None):
    decoded_questions = []

    raw_path = Path(file_arg or "examples.json")
    
    json_path = raw_path if raw_path.is_absolute() else PROJECT_ROOT / raw_path

    with json_path.open("r", encoding="utf-8") as f:
        items = json.load(f)

    for index, item in enumerate(items):
        expression, available_columns = item[0], item[1]
        print(expression)
        print(available_columns)

        parser = SPSSExpressionParser(expression)
        ast = parser.parse()
        parser.print_ast(ast)

        synthesizer = EGraphSynthesizer(SPSSDateParamDecoder(), SemanticMatcher())
        result = synthesizer.synthesize(ast, PrimitiveType.get_type_by_value(expression), available_columns, max_iterations=1)
    return

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

                synthesizer = EGraphSynthesizer(SPSSDateParamDecoder(), SemanticMatcher())
                result = synthesizer.synthesize(ast, PrimitiveType.get_type_by_value(exp_type), max_iterations=1)

                print(result[1])

                return
                


                synthesizer = ContextAwareSynthesizer(SPSSDateParamDecoder(), SemanticMatcher())

                exp_type = PrimitiveType.get_type_by_value(exp_type)
                candidates = synthesizer.synthesize(ast, exp_type)

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