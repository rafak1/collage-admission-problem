from abc import ABC, abstractmethod
from dataclasses import dataclass
from itertools import permutations

from linear_programming import solve as lp_solve


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

        with open("changes.txt", mode="a") as f:
            if bpreference is not None:
                print(f"Student {student_id} changed declaration", file=f)
                current_assignment = assign_students(
                    gs.declared_preferences.preferences)
                dissatisfaction = gs.preferences.total_dissatisfaction(
                    current_assignment)
                sds = [gs.preferences.student_dissatisfaction(
                    current_assignment, sid) for sid in range(gs.n_students)]
                print(
                    f"Dissatisfaction before: total = {dissatisfaction}, students: {sds}", file=f)
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
                print(
                    f"Dissatisfaction after change: total = {dissatisfaction}, student: {sds}", file=f)
                print("New declarations:", file=f)
                save_preferences_table(gs.declared_preferences.preferences, f)

                print("------", file=f)


class LPSolver(AssignmentSolver):
    def solve(self, n_students: int, n_topics: int, preferences: dict[tuple[int, int], int]):
        assignment, _ = lp_solve(n_students, n_topics, preferences)
        return assignment


def simulate_game(preferences: dict[tuple[int, int], int], n_rounds: int = 10):
    n_students = 5
    n_topics = 3

    gs = GameState(
        solver=LPSolver(),
        preferences=Preferences(preferences, n_students),
        declared_preferences=Preferences(preferences, n_students),
        n_topics=n_topics,
        n_students=n_students,
    )

    manipulator = Manipulator()
    for r in range(n_rounds):
        with open("changes.txt", mode="a") as f:
            print(f"Round: {r}", file=f)
            print("------", file=f)

        for s_id in range(n_students):
            manipulator.manipulate(gs, s_id)


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


def main():
    # preferences = {
    #     (0, 0): 1, (0, 1): 2, (0, 2): 3,
    #     (1, 0): 3, (1, 1): 1, (1, 2): 2,
    #     (2, 0): 2, (2, 1): 1, (2, 2): 3,
    #     (3, 0): 1, (3, 1): 3, (3, 2): 2,
    #     (4, 0): 2, (4, 1): 3, (4, 2): 1,
    # }
    # simulate_game(preferences, n_rounds=2)

    preferences = {
        (0, 0): 1, (0, 1): 2, (0, 2): 3,
        (1, 0): 3, (1, 1): 1, (1, 2): 2,
        (2, 0): 2, (2, 1): 1, (2, 2): 3,
        (3, 0): 1, (3, 1): 3, (3, 2): 2,
        (4, 0): 1, (4, 1): 2, (4, 2): 3,
    }
    with open("changes.txt", mode="w") as f:
        print("Real preferences:", file=f)
        save_preferences_table(preferences, f)
    simulate_game(preferences, n_rounds=10)


if __name__ == "__main__":
    main()
