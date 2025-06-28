import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from itertools import permutations

from sum.linear_programming import solve as lp_solve
from utils import generate_random_preferences


@dataclass
class Preferences:
    preferences: dict[tuple[int, int], int]
    n_students: int

    def student_dissatisfaction(self, assignment: list[int], student_id: int):
        sd = self.preferences[student_id, assignment[student_id]]
        return sd

    def total_dissatisfaction(self, assignment: list[int]):
        return sum(self.student_dissatisfaction(assignment, i) for i in range(self.n_students))

    def updated_preferences(self, preference_change: dict[int, int], student_id: int):
        update = {(student_id, topic_id): v
                  for topic_id, v in preference_change.items()}
        return self.preferences | update


class AssignmentSolver(ABC):
    @abstractmethod
    def solve(self, n_students: int, n_topics: int, preferences: dict[tuple[int, int], int]) -> list[int]:
        pass


def get_possible_student_preferences(n_topics: int) -> list[dict[int, int]]:
    topics = list(range(n_topics))
    rankings = permutations(range(1, n_topics + 1))
    return [dict(zip(topics, ranking)) for ranking in rankings]


@dataclass
class GameState:
    solver: AssignmentSolver
    preferences: Preferences
    declared_preferences: Preferences
    n_topics: int
    n_students: int


class Manipulator(ABC):
    def __init__(self, log_file=None):
        super().__init__()
        self.log_file = log_file
    
    def print(self, msg):
        if self.log_file is not None:
            print(msg, file=self.log_file)
    
    def manipulate(self, gs: GameState, student_id):
        possible_preferences = get_possible_student_preferences(gs.n_topics)

        def assign_students(preferences):
            assignment = gs.solver.solve(
                gs.n_students,
                gs.n_topics,
                preferences
            )
            return assignment

        def compute_dissatisfaction(preference: dict[int, int]):
            manipulated_preferences = gs.declared_preferences.updated_preferences(
                preference,
                student_id,
            )
            assignment = assign_students(manipulated_preferences)
            sd = gs.preferences.student_dissatisfaction(assignment, student_id)
            return sd

        current_assignment = assign_students(
            gs.declared_preferences.preferences)
        bsd = gs.preferences.student_dissatisfaction(
            current_assignment, student_id)

        bpreference = None

        for preference in possible_preferences:
            sd = compute_dissatisfaction(preference)
            if sd < bsd:
                bsd = sd
                bpreference = preference

        if bpreference is not None:
            self.print(f"Student {student_id} changed declaration")
            current_assignment = assign_students(
                gs.declared_preferences.preferences)
            dissatisfaction = gs.preferences.total_dissatisfaction(
                current_assignment)
            sds = [gs.preferences.student_dissatisfaction(
                current_assignment, sid) for sid in range(gs.n_students)]
            self.print(
                f"Dissatisfaction before: total = {dissatisfaction}, students: {sds}")
            gs.declared_preferences.preferences = gs.declared_preferences.updated_preferences(
                bpreference,
                student_id,
            )
            current_assignment = assign_students(
                gs.declared_preferences.preferences)
            dissatisfaction = gs.preferences.total_dissatisfaction(
                current_assignment)
            sds = [gs.preferences.student_dissatisfaction(
                current_assignment, sid) for sid in range(gs.n_students)]
            self.print(
                f"Dissatisfaction after change: total = {dissatisfaction}, student: {sds}")
            self.print("New declarations:")
            
            if self.log_file is not None:
                save_preferences_table(gs.declared_preferences.preferences, f=self.log_file)

            self.print("------")


class LPSolver(AssignmentSolver):
    def solve(self, n_students: int, n_topics: int, preferences: dict[tuple[int, int], int]):
        assignment, _ = lp_solve(n_students, n_topics, preferences)
        return assignment


def initialize_game(preferences, n_students, n_topics) -> GameState:
    gs = GameState(
        solver=LPSolver(),
        preferences=Preferences(preferences, n_students),
        declared_preferences=Preferences(preferences, n_students),
        n_topics=n_topics,
        n_students=n_students,
    )

    return gs


def simulate_game(gs: GameState, log_file, n_rounds: int = 10):
    manipulator = Manipulator(log_file=log_file)
    for r in range(n_rounds):
        print(f"Round: {r}", file=log_file)
        print("------", file=log_file)

        for s_id in range(gs.n_students):
            manipulator.manipulate(gs, s_id)


def is_stable_to_swaps(gs: GameState, log_file):
    assignment = gs.solver.solve(
        gs.n_students,
        gs.n_topics,
        gs.declared_preferences.preferences
    )

    students_dissatistactions = [gs.preferences.student_dissatisfaction(
        assignment, i) for i in range(gs.n_students)]

    for s1 in range(gs.n_students):
        for s2 in range(s1 + 1, gs.n_students):
            new_assignment = assignment.copy()
            new_assignment[s1], new_assignment[s2] = assignment[s2], assignment[s1]

            new_diss1 = gs.preferences.student_dissatisfaction(
                new_assignment, s1)
            new_diss2 = gs.preferences.student_dissatisfaction(
                new_assignment, s2)
            prev_diss1, prev_diss2 = students_dissatistactions[s1], students_dissatistactions[s2]

            if (new_diss1 < prev_diss1 and new_diss2 <= prev_diss2) or (new_diss1 == prev_diss1 and new_diss2 < prev_diss2):
                print(f"Before {students_dissatistactions}, students swapped: {s1}, {s2}", file=log_file)
                print(f"Prev assignment: {assignment}, new one: {new_assignment}", file=log_file)
                return False

    return True


def save_preferences_table(preferences, f):
    student_ids = sorted({s for s, _ in preferences})
    topic_ids = sorted({t for _, t in preferences})

    header = ["Student \\ Topic"] + [f"T{t}" for t in topic_ids]
    rows = []

    for s in student_ids:
        row = [f"S{s}"]
        for t in topic_ids:
            pref = preferences.get((s, t), "-")
            row.append(str(pref))
        rows.append(row)

    col_widths = [max(len(cell) for cell in col) for col in zip(header, *rows)]

    def format_row(row):
        return " | ".join(cell.ljust(width) for cell, width in zip(row, col_widths))

    f.write(format_row(header) + "\n")
    f.write("-+-".join("-" * w for w in col_widths) + "\n")
    for row in rows:
        f.write(format_row(row) + "\n")


def test_stability():
    n_students = 7
    n_topics = 4
    
    stability_filename = f"stability_students={n_students},topics={n_topics}.txt"
    if os.path.exists(stability_filename):
        os.remove(stability_filename)

    for i in range(100):
        preferences = generate_random_preferences(n_students, n_topics)

        changes_dir = f"changes_students={n_students},topics={n_topics}"
        os.makedirs(changes_dir, exist_ok=True)
        log_filename = f"{changes_dir}/{i}.txt"
        if os.path.exists(log_filename):
            os.remove(log_filename)
        with open(log_filename, mode="w") as f:
            print("Real preferences:", file=f)
            save_preferences_table(preferences, f)

            gs = initialize_game(preferences, n_students, n_topics)
            simulate_game(gs, f, n_rounds=10)

            with open(stability_filename, "a") as stable_file:
                is_stable = is_stable_to_swaps(gs, stable_file)
                stable_file.write(f"Stable to topic swaps? {is_stable}\n")

            print("Stable to topic swaps?", is_stable)


def main():
    # preferences = {
    #     (0, 0): 1, (0, 1): 2, (0, 2): 3,
    #     (1, 0): 3, (1, 1): 1, (1, 2): 2,
    #     (2, 0): 2, (2, 1): 1, (2, 2): 3,
    #     (3, 0): 1, (3, 1): 3, (3, 2): 2,
    #     (4, 0): 2, (4, 1): 3, (4, 2): 1,
    # }
    # simulate_game(preferences, n_rounds=2)

    # preferences = {
    #     (0, 0): 1, (0, 1): 2, (0, 2): 3,
    #     (1, 0): 3, (1, 1): 1, (1, 2): 2,
    #     (2, 0): 2, (2, 1): 1, (2, 2): 3,
    #     (3, 0): 1, (3, 1): 3, (3, 2): 2,
    #     (4, 0): 1, (4, 1): 2, (4, 2): 3,
    # }

    test_stability()


def simulate_and_check_cycles(
        preferences: dict[tuple[int, int], int],
        n_students: int = 5,
        n_topics: int = 3,
        max_rounds: int = 50
) -> str:
    """
    Simulates the preference manipulation game and checks for cycles or stabilization in preferences.

    Args:
        preferences: Initial preference dictionary mapping (student_id, topic_id) to dissatisfaction value.
        n_students: Number of students in the simulation.
        n_topics: Number of topics in the simulation.
        max_rounds: Maximum number of rounds to simulate before concluding insufficient steps.

    Returns:
        A string indicating one of three outcomes:
        - "Cycle detected in preferences"
        - "Preferences stabilized"
        - "Insufficient rounds to determine outcome"
    """
    # Initialize game state
    gs = GameState(
        solver=LPSolver(),
        preferences=Preferences(preferences, n_students),
        declared_preferences=Preferences(dict(preferences), n_students),
        n_topics=n_topics,
        n_students=n_students,
    )

    manipulator = Manipulator()
    seen_configurations: dict[str, int] = {}
    last_few_configs: list[str] = []
    # Number of rounds with same config to consider stabilized
    stabilization_threshold = 3

    for round_num in range(max_rounds):
        # Convert current preferences to a string for comparison
        current_config = str(
            sorted(gs.declared_preferences.preferences.items()))

        # Check for cycles
        if current_config in seen_configurations:
            return "Cycle detected in preferences"
        seen_configurations[current_config] = round_num

        # Track last few configurations for stabilization check
        last_few_configs.append(current_config)
        if len(last_few_configs) > stabilization_threshold:
            last_few_configs.pop(0)
            if len(set(last_few_configs)) == 1:  # All recent configs are the same
                return "Preferences stabilized"

        # Simulate one round of manipulation for all students
        changes_made = False
        for student_id in range(n_students):
            if manipulator.manipulate(gs, student_id):
                changes_made = True

        # If no changes were made in this round, check if it's stable
        if not changes_made and len(set(last_few_configs)) == 1:
            return "Preferences stabilized"

    return "Insufficient rounds to determine outcome"


if __name__ == "__main__":
    main()
    # preferences = {
    #     (0, 0): 1, (0, 1): 2, (0, 2): 3,
    #     (1, 0): 3, (1, 1): 1, (1, 2): 2,
    #     (2, 0): 2, (2, 1): 1, (2, 2): 3,
    #     (3, 0): 1, (3, 1): 3, (3, 2): 2,
    #     (4, 0): 1, (4, 1): 2, (4, 2): 3,
    # }
    # result = simulate_and_check_cycles(preferences)
    # print(result)
