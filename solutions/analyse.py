import os
import time
from .read_data import read_dataset

s = time.time()
data = read_dataset("dataset/build")
e = time.time()

print(f"Dataset read took {e-s} seconds.")

def write_inputs():

    n_orgs = len(list(data["organizations"].keys()))
    res = f"{n_orgs}\n" + "\n".join(key for key in data["organizations"]) + "\n"
    with open("solutions/organizations.txt", "w") as f:
        f.write(res)
    
    n_pracs = len(list(data["practitioners"].keys()))
    res = f"{n_pracs}\n" + "\n".join(key for key in data["practitioners"]) + "\n"
    with open("solutions/practitioners.txt", "w") as f:
        f.write(res)

def get_num_patients():

    n_orgs = len(list(data["organizations"].keys()))
    res = f"{n_orgs}\n" + "\n".join(f"{key} {len(org.patients)}" for key, org in data["organizations"].items()) + "\n"
    with open("solutions/organizations_num_patients.txt", "w") as f:
        f.write(res)
    
    n_pracs = len(list(data["practitioners"].keys()))
    res = f"{n_pracs}\n" + "\n".join(f"{key} {len(prac.patients)}" for key, prac in data["practitioners"].items()) + "\n"
    with open("solutions/practitioners_num_patients.txt", "w") as f:
        f.write(res)

def get_serum_values():
    from .Q3.misc import total_serum_required
    
    n_pracs = len(list(data["practitioners"].keys()))
    serum = {}
    for prac in data["practitioners"]:
        serum[prac] = total_serum_required(data, prac)
    res = f"{n_pracs}\n" + "\n".join(f"{key} {serum[key]}" for key in data["practitioners"]) + "\n"
    with open("solutions/practitioners_total_serum.txt", "w") as f:
        f.write(res)

def generate_random_serum_amounts():
    import numpy as np
    def sigmoid(x):
        return 1.0 / (1 + np.exp(-x))

    def smooth(t, inflection=10.0):
        error = sigmoid(-inflection / 2)
        return np.clip(
            (sigmoid(inflection * (t - 0.5)) - error) / (1 - 2 * error),
            0,
            1,
        )

    def rush_to(t, inflection=10.0):
        return 2 * smooth(t / 2.0, inflection)
    
    def rush_from(t, inflection=10.0):
        return 2 * smooth(t / 2.0 + 0.5, inflection) - 1
    
    def sit_middle(t, inflection=15.0):
        return (rush_to(t, inflection) + rush_from(t, inflection)) / 2

    with open("solutions/practitioners_total_serum.txt", "r") as f:
        lines = f.readlines()[1:]
    actual_serum = [-1] * (len(lines))
    for i, line in enumerate(lines):
        prac, serum = line.split()
        serum = float(serum)
        # Choose anywhere from 0 to 1.01 * serum (small chance of having enough for everyone)
        # It seems like cases with about half the serum give the most interesting cases to break (Too little or too much and the answer is vert similar between p1/p2.)
        actual_serum[i] = sit_middle(np.random.random()) * 1.01 * serum

    res = f"{len(lines)}\n" + "\n".join(f"{lines[i].split()[0]} {actual_serum[i]}" for i in range(len(lines))) + "\n"
    with open("solutions/practitioners_serum_random.txt", "w") as f:
        f.write(res)

def q3_test_p1_p2_discrepancy(input_file):
    from .Q3.P1.solution import indiv_solve as p1_solve
    from .Q3.P2.solution import indiv_solve as p2_solve
    with open(input_file, "r") as f:
        lines = f.readlines()[1:]
    diff = 0
    for i, line in enumerate(lines):
        prac, serum = line.split()
        serum = float(serum)
        p1 = p1_solve(data, prac, serum)
        p2 = p2_solve(data, prac, serum)
        if p1 > p2[1]:
            diff += 1
    print(f"{100 * diff / len(lines)}% of practitioners have different answers when considering civilization.")

# Function calls

s = time.time()

# write_inputs()
# get_num_patients()
# get_serum_values()
generate_random_serum_amounts()
q3_test_p1_p2_discrepancy("solutions/practitioners_serum_random.txt")

e = time.time()

print(f"Analysis took {e-s} seconds.")
