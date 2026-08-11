from SPSSDateParamDecoder import SPSSDateParamDecoder


def test_prim(file_paths):
    decoded_questions = []
    for file_path in file_paths:
        with open(file_path, 'r') as f:
            for question_answer in f:
                if question_answer == "\n":
                    continue
                question_answer = question_answer.split("#")
                print(question_answer)
                expr = question_answer[0].strip()
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