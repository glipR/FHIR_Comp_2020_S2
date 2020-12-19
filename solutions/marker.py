class Marker:

    def __init__(self, correct_output_file, sample_lines):
        with open(correct_output_file, "r") as f:
            self.test_lines = f.read().strip().split("\n")
        self.sample_lines = sample_lines

    def mark_case(self, correct, answer):
        """All test answers follow the same format."""
        return " ".join(correct).strip().lower() == " ".join(answer).strip().lower()

    def mark(self, output_file):
        with open(output_file, "r") as f:
            lines = f.read().strip().split("\n")
        case_answers = {}
        duplicates = set()
        for line in lines:
            parts = line.split()
            # Validity checks
            if len(parts) < 3: continue
            if parts[0].lower() != "test": continue
            try:
                assert parts[1].endswith(":")
                testno = int(parts[1][:-1])
                assert 1 <= testno <= len(self.test_lines)
            except:
                continue
            if testno in case_answers:
                duplicates.add(testno)
            case_answers[testno] = parts[2:]
        correct = 0
        for key in case_answers:
            if key in duplicates: continue
            if key in self.sample_lines: continue
            correct_answer = self.test_lines[key-1].split()[2:]
            if self.mark_case(correct_answer, case_answers[key]):
                correct += 1
        return len(self.test_lines) - len(self.sample_lines), correct

    def score(self, pct, total_marks):
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
        
        def sit_middle(t, inflection=25.0):
            return (rush_to(t, inflection) + rush_from(t, inflection)) / 2
        return total_marks * sit_middle(pct)

import os
import pandas as pd

def writeResults():
    # Open the results spreadsheet to add sheets.
    writer = pd.ExcelWriter("results.xlsx", mode="w")
    res = []
    students = None
    for qName, marks, qPath in [
        ("A", 40, "solutions/Q1/correct_output.txt"),
        ("B", 60, "solutions/Q2/correct_output.txt"),
        ("C1", 40, "solutions/Q3/P1/correct_output.txt"),
        ("C2", 60, "solutions/Q3/P2/correct_output.txt"),
        ("D1", 40, "solutions/Q4/P1/correct_output.txt"),
        ("D2", 60, "solutions/Q4/P2/correct_output.txt"),
    ]:
        d, students = writeResultsForQ(writer, qName, qPath, marks)
        res.append(d)
    accum = [
        [sum(res[i][x][1] for i in range(len(res)))]
        for x in range(len(res[0]))
    ]
    df = pd.DataFrame(data=accum, columns=["Total Marks"], index=students)
    df.to_excel(writer, "Results")
    writer.save()

def writeResultsForQ(writer, qName, qPath, marks):
    # TODO: Update sample lines.
    marker = Marker(qPath, [])

    indexes = []
    data = []
    for student_id in os.listdir("submissions"):
        indexes.append(student_id)
        # Start with nothing.
        data.append([0, 0])
        sol_path = os.path.join("submissions", student_id, qName)
        if not os.path.isdir(sol_path):
            data[-1][0] = "N/A"
            continue
        text_files = []
        for solution_file in os.listdir(sol_path):
            if solution_file.endswith(".txt"):
                text_files.append(os.path.join(sol_path, solution_file))
        for text_file in text_files:
            total_possible, scored = marker.mark(text_file)
            awarded = marker.score(scored / total_possible, marks)
            if data[-1][1] < awarded:
                data[-1][0] = "{:.2f}%".format(scored / total_possible * 100)
                data[-1][1] = awarded
        if len(text_files) == 0:
            data[-1][0] = "N/A"
    columns = ["Cases Correct", "Marks Awarded"]
    df = pd.DataFrame(data=data, columns=columns, index=indexes)
    df.to_excel(writer, qName)
    return data, indexes


writeResults()
