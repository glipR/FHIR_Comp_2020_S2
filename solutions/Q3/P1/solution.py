import os
import itertools
from dateutil import parser
from ...read_data import read_dataset

data = read_dataset("dataset/build")

def indiv_solve(d, prac_id, serum):
    patients = {
        id: d["patients"][id]
        for id in d["practitioners"][prac_id].patients
    }
    for pat in patients.values():
        pat.platelets = None
        for obs_id in pat.observations:
            obs = d["observations"][obs_id]
            if obs.code != "32623-1":
                continue
            if pat.platelets is None or pat.platelets[1] < parser.parse(obs.effective):
                pat.platelets = (
                    (obs.value["value"], obs.value["unit"]),
                    parser.parse(obs.effective),
                )
    saveable_patients = sorted(
        [pat for pat in patients.values() if pat.platelets is not None],
        key=lambda pat: pat.platelets[0][0],
    )

    # Assert units are the same.
    assert (
        len(
            list(
                itertools.groupby(
                    saveable_patients, lambda pat: pat.platelets[0][1]
                )
            )
        )
        <= 1
    ), "More than one unit of measurement detected."

    # saveable_patients are now sorted with platelet volume increasing. Save patients from the beginning of the list.
    cur_index = 0
    while cur_index < len(saveable_patients):
        required = 20 * saveable_patients[cur_index].platelets[0][0] + 10
        if serum >= required:
            serum -= required
            cur_index += 1
        else:
            break
    return cur_index

def solve(lines):
    # First, get the number of practitioners.
    n_pracs = int(lines[0])
    prac_ids = [""] * n_pracs
    solutions = [0] * n_pracs
    for testno in range(n_pracs):
        prac_ids[testno], serum = lines[testno + 1].split()
        serum = int(serum)
        solutions[testno] = indiv_solve(data, prac_ids[testno], serum)
    return "\n".join(
        f"Test {i}: {sol}"
        for i, (prac_id, sol) in enumerate(zip(prac_ids, solutions), start=1)
    )


input_file_path = os.path.join(os.path.dirname(__file__), "input.txt")
output_file_path = os.path.join(os.path.dirname(__file__), "correct_output.txt")

with open(input_file_path, "r") as f:
    inp = f.readlines()
result = solve(inp)
with open(output_file_path, "w") as f:
    f.write(result)
