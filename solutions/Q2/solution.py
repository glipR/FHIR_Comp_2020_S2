import os
from ..read_data import read_dataset
from dateutil import parser

data = read_dataset("dataset/build")


def solve(lines):
    n = int(lines[0])
    answers = []
    for testno in range(1, n + 1):
        org_id = lines[testno].strip()
        patients = data['organizations'][org_id].patients
        count = 0

        for patient_id in patients:
            obs = data['patients'][patient_id].observations
            latest_never = None
            for observation_id in obs:
                observation = data['observations'][observation_id]
                if observation.code != '72166-2' or observation.valueCode != '266919005':
                    continue
                if latest_never is None or parser.parse(observation.effective) > latest_never:
                    latest_never = parser.parse(observation.effective)

            for observation_id in obs:
                observation = data['observations'][observation_id]
                if observation.code != '72166-2' or observation.valueCode in ['266919005', '266927001']:
                    continue
                if latest_never is not None and latest_never > parser.parse(observation.effective):
                    count += 1
                    break

        answers.append(count)

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
