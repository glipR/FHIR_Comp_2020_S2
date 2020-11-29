import collections
import os
from ...read_data import read_dataset
from dateutil import parser
from collections import defaultdict

data = read_dataset("dataset/build")


def solve(lines):
    n = int(lines[0])
    answers = []
    for testno in range(1, n + 1):
        org_id = lines[testno].strip()
        pracs = data["organizations"][org_id].practitioners
        patient_info = {
            # Number of encounters, and earliest encounter.
            prac: defaultdict(lambda: (0, None))
            for prac in pracs
        }
        for encounter in data["encounters"].values():
            if data["patients"][encounter.patient].organization != org_id: continue
            for prac in encounter.practitioners:
                patient_info[prac][encounter.patient] = (patient_info[prac][encounter.patient][0] + 1, patient_info[prac][encounter.patient][1])
                if patient_info[prac][encounter.patient][1] is None or patient_info[prac][encounter.patient][1] > parser.parse(encounter.period_start):
                    patient_info[prac][encounter.patient] = (patient_info[prac][encounter.patient][0], parser.parse(encounter.period_start))
        all_patients = set()
        for prac in pracs:
            # Sort by encounters descending, then datetime ascending.
            my_pats = sorted(list(patient_info[prac].items()), key=lambda kv: (-kv[1][0], kv[1][1], kv[0]))
            for pat_id, value in my_pats[:3]:
                all_patients.add(pat_id)

        if len(all_patients) == 3 * len(pracs):
            answers.append("POSSIBLE")
        else:
            answers.append("IMPOSSIBLE")

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
