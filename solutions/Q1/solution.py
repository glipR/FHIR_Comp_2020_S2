import os
from ..read_data import read_dataset

data = read_dataset("dataset/build")


def solve(lines):
    n = int(lines[0])
    answers = []
    for testno in range(1, n + 1):
        patient_id = lines[testno].strip()
        patient = data['patients'][patient_id]
        ppn = None
        for identifier in patient.identifier:
            try:
                if identifier['type']['coding'][0]['code'] == 'PPN':
                    ppn = identifier['value']
            except Exception:
                pass
        if ppn is None:
            answers.append('Not Recorded')
        else:
            answers.append(ppn)
    return "\n".join(
        f"Test {i + 1}: {answers[i]}"
        for i in range(n)
    )


input_file_path = os.path.join(os.path.dirname(__file__), "input.txt")
output_file_path = os.path.join(os.path.dirname(__file__), "correct_output.txt")

with open(input_file_path, "r") as f:
    inp = f.readlines()
result = solve(inp)
with open(output_file_path, "w") as f:
    f.write(result)
