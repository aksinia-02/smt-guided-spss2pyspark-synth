import argparse

from tests.test_dataparams import test_dataparam
from tests.test_prim import test_prim
from tests.test_re_expressions import test_re_expressions
from tests.test_z3 import test_z3
#from functions_elements.invariants import Primitives
from SemanticMatcher import SemanticMatcher

def main(args):
    # test_z3()
    # return
    test_re_expressions(args.file, args.input)
    return
    # decoded_qeustions = test_prim(args.file)

    # primitives = Primitives()
    # matcher = SemanticMatcher()

    # for question in decoded_qeustions:
    #     candidates = SemanticMatcher.filter_candidates(question, primitives.primitives)
    #     print(question)
    #     print("Ranked Semantic Candidates:")
    #     for prim, score in candidates:
    #         # Fill dynamic argument if required
    #         args = [str(question.amount)] if prim.arg_types else []
    #         pyspark_code = prim.to_pyspark(args)
    #         print(f" -> Candidate: {pyspark_code} | Score: {score}")

    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parser from SPSS to pyspark code")
    parser.add_argument("-f", "--file", type=str, required=False, nargs="+", help="File with Expressions to parse")
    parser.add_argument("-i", "--input", type=str, required=False, help="File with Expressions to parse")
    args = parser.parse_args()
    #test_dataparam()

    main(args)