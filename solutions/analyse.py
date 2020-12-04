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

# Function calls

s = time.time()

# write_inputs()
# get_num_patients()
# get_serum_values()

e = time.time()

print(f"Analysis took {e-s} seconds.")
