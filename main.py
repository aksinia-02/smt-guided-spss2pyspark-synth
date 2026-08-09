import argparse

from SPSSDateParamDecoder import SPSSDateParamDecoder
from tests.test_dataparams import test_dataparam

def main(args):
    for file_path in args.file:
        with open(file_path, 'r') as f:
            for question_answer in f:
                if question_answer == "\n":
                    continue
                question_answer = question_answer.split("#")
                print(question_answer)
                expr = question_answer[0].strip()
                correct_answer = question_answer[1].strip()
                print(expr)
                try:
                    decoded = SPSSDateParamDecoder.decode(expr)
                    print(f"Decoded '{expr}': {decoded}; Expected: {correct_answer}")
                except ValueError as e:
                    print(f"Error decoding '{expr}': {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parser from SPSS to pyspark code")
    parser.add_argument("-f", "--file", type=str, required=True, nargs="+", help="File with Expressions to parse, e.g., '$P-plus1tag', '$P-minus2monat'")
    args = parser.parse_args()
    #test_dataparam()

    main(args)