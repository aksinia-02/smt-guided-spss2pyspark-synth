import argparse

from tests.test_dataparams import test_dataparam
from tests.test_prim import test_prim
from invariants import Primitives
from SemanticMatcher import SemanticMatcher

def main(args):
    decoded_qeustions = test_prim(args.file)

    primitives = Primitives()
    matcher = SemanticMatcher()

    for question in decoded_qeustions:
        candidates = SemanticMatcher.filter_candidates(question, primitives.primitives)
        print(question)
        print("Ranked Semantic Candidates:")
        for prim, score in candidates:
            # Fill dynamic argument if required
            args = [str(question['amount'])] if prim.arg_types else []
            pyspark_code = prim.to_pyspark(args)
            print(f" -> Candidate: {pyspark_code} | Score: {score}")

    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parser from SPSS to pyspark code")
    parser.add_argument("-f", "--file", type=str, required=True, nargs="+", help="File with Expressions to parse, e.g., '$P-plus1tag', '$P-minus2monat'")
    args = parser.parse_args()
    #test_dataparam()

    main(args)