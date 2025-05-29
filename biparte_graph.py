import numpy as np
from scipy.optimize import linear_sum_assignment

def solve(n_students, n_topics, preferences):

    true_cost_matrix = np.zeros((n_students, 2 * n_topics), dtype=int)
    cost_matrix = np.zeros((n_students, 2 * n_topics), dtype=int)

    for i in range(n_students):
        for j in range(n_topics):
            cost_matrix[i][j] = preferences[(i,j)]
            cost_matrix[i][n_topics + j] = n_topics + preferences[(i,j)]
            true_cost_matrix[i][j] = preferences[(i,j)]
            true_cost_matrix[i][n_topics + j] = preferences[(i,j)]

    row_ind, col_ind = linear_sum_assignment(cost_matrix)

    assignment = np.zeros(n_students, dtype=int)
    dissatisfaction = sum(true_cost_matrix[row_ind, col_ind])
    for i in range(n_students):
        if col_ind[i] < n_topics:
            assignment[i] = col_ind[i]
        else:
            assignment[i] = col_ind[i] - n_topics

    return list(assignment), dissatisfaction


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
    print("Total dissatisfaction:", dissatisfaction)