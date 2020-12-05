import os
from ...read_data import read_dataset
import queue

NUM_COUPONS = 10

def indiv_solve(d, org_id):
    pracs = d["organizations"][org_id].practitioners
    id_mapping = {
        prac: i
        for i, prac in enumerate(pracs)
    }
    patients = d["organizations"][org_id].patients
    pat_edges = {
        pat: set()
        for pat in patients
    }
    for pat_id in patients:
        for encounter_id in d["patients"][pat_id].encounters:
            encounter = d["encounters"][encounter_id]
            for prac in encounter.practitioners:
                pat_edges[pat_id].add(prac)

    INF = int(1e9)
    # U:= patients
    # V:= pracs, with NUM_COUPONS nodes per prac.
    PU = [None]*len(patients)
    PV = [None]*(NUM_COUPONS*len(pracs))
    dist = [0]*(len(patients)+1)
    Q = queue.Queue()
    NIL = len(patients)

    def bfs():
        for i in range(len(patients)):
            if PU[i] == NIL:
                dist[i] = 0
                Q.put(i)
            else:
                dist[i] = INF
        dist[NIL] = INF
        while not Q.empty():
            i = Q.get()
            if dist[i] < dist[NIL]:
                for prac in pat_edges[patients[i]]:
                    j = id_mapping[prac]
                    for k in range(NUM_COUPONS):
                        index = k*len(pracs) + j
                        if dist[PV[index]] == INF:
                            dist[PV[index]] = dist[i] + 1
                            Q.put(PV[index])
        return dist[NIL] != INF
    
    def dfs(u):
        if u != NIL:
            for prac in pat_edges[patients[u]]:
                j = id_mapping[prac]
                for k in range(NUM_COUPONS):
                    index = k*len(pracs) + j
                    if dist[PV[index]] == dist[u] + 1:
                        if dfs(PV[index]):
                            PV[index] = u
                            PU[u] = index
                            return True
            dist[u] = INF
            return False
        return True
    
    def hopcroft_karp():
        for i in range(len(patients)):
            PU[i] = NIL
        for i in range(NUM_COUPONS*len(pracs)):
            PV[i] = NIL
        matching = 0
        while bfs():
            for i in range(len(patients)):
                if PU[i] == NIL:
                    if dfs(i):
                        matching += 1
        return matching

    n_matches = hopcroft_karp()
    return n_matches == NUM_COUPONS * len(pracs)

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
