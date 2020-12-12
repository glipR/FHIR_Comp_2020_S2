class Marker:

    def __init__(self, correct_output_file, sample_lines):
        with open(correct_output_file, "r") as f:
            self.test_lines = f.read().strip().split()
        self.sample_lines = sample_lines

    def mark_case(self, correct, answer):
        """All test answers follow the same format."""
        return " ".join(correct).strip().lower() == " ".join(answer).strip().lower()

    def mark(self, output_file):
        with open(output_file, "r") as f:
            lines = f.read().strip().split()
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

    def score(self, output_file, total_marks):
        total_possible, scored = self.mark(output_file)
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
        return total_marks * sit_middle(scored / total_possible)
