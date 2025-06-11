import pulp


def solve(n_students, n_topics, preferences):
    students = range(n_students)
    topics = range(n_topics)

    model = pulp.LpProblem("Assigment", pulp.LpMinimize)

    x = pulp.LpVariable.dicts("x", (students, topics), cat='Binary')

    z = pulp.LpVariable("z", lowBound=0, cat="Continuous")

    model += z

    # each student assigned to exactly one topic
    for i in students:
        model += pulp.lpSum(x[i][j] for j in topics) == 1

    # each topic assigned to at least one student and at most two students
    for j in topics:
        model += pulp.lpSum(x[i][j] for i in students) >= 1
        model += pulp.lpSum(x[i][j] for i in students) <= 2

    # minimize the maximum dissatisfaction
    for i in students:
        model += pulp.lpSum(preferences[i, j] * x[i][j] for j in topics) <= z

    model.solve()

    result = [-1] * n_students
    min_max_dissatisfaction = 0
    for i in students:
        for j in topics:
            if pulp.value(x[i][j]) == 1:
                result[i] = j
                min_max_dissatisfaction = max(min_max_dissatisfaction, preferences[i, j])

    return result, min_max_dissatisfaction


if __name__ == "__main__":
    n_students = 5
    n_topics = 3
    preferences = {
        (0, 0): 1, (0, 1): 2, (0, 2): 3,
        (1, 0): 3, (1, 1): 1, (1, 2): 2,
        (2, 0): 2, (2, 1): 1, (2, 2): 3,
        (3, 0): 1, (3, 1): 3, (3, 2): 2,
        (4, 0): 2, (4, 1): 3, (4, 2): 1,
    }
    
    result, dissatisfaction = solve(n_students, n_topics, preferences)
    print("Assignments:", result)
    print("Min Max dissatisfaction:", dissatisfaction)