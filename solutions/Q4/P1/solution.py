import os
from ...read_data import read_dataset
from dateutil import parser
from collections import defaultdict

NUM_COUPONS = 3

def indiv_solve(d, org):
    pracs = d["organizations"][org].practitioners
    patient_info = {
        # Number of encounters, and earliest encounter.
        prac: defaultdict(lambda: (0, None))
        for prac in pracs
    }
    for pat_id in d["organizations"][org].patients:
        for encounter_id in d["patients"][pat_id].encounters:
            encounter = d["encounters"][encounter_id]
            for prac in encounter.practitioners:
                patient_info[prac][pat_id] = (patient_info[prac][pat_id][0] + 1, patient_info[prac][pat_id][1])
                if patient_info[prac][pat_id][1] is None or patient_info[prac][pat_id][1] > parser.parse(encounter.period_start):
                    patient_info[prac][pat_id] = (patient_info[prac][pat_id][0], parser.parse(encounter.period_start))
    all_patients = set()
    for prac in pracs:
        # Sort by encounters descending, then datetime ascending.
        my_pats = sorted(list(patient_info[prac].items()), key=lambda kv: (-kv[1][0], kv[1][1], kv[0]))
        for pat_id, value in my_pats[:NUM_COUPONS]:
            all_patients.add(pat_id)

    return len(all_patients) == NUM_COUPONS * len(pracs)

def solve(d, lines):
    n = int(lines[0])
    answers = []
    for testno in range(1, n + 1):
        org_id = lines[testno].strip()
        if indiv_solve(d, org_id):
            answers.append("POSSIBLE")
        else:
            answers.append("IMPOSSIBLE")

    return "\n".join(
        f"Test {i + 1}: {answers[i]}"
        for i in range(n)
    )


if __name__ == "__main__":
    data = read_dataset("dataset/build")
    input_file_path = os.path.join(os.path.dirname(__file__), "input.txt")
    output_file_path = os.path.join(os.path.dirname(__file__), "correct_output.txt")

    with open(input_file_path, "r") as f:
        inp = f.readlines()
    result = solve(data, inp)
    with open(output_file_path, "w") as f:
        f.write(result)
