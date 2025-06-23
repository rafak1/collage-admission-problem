import random


def generate_random_preferences(n_students, n_topics):
    preferences = {}
    for i in range(n_students):
        perm = list(range(1, n_topics + 1))
        random.shuffle(perm)
        for j in range(n_topics):
            preferences[(i, j)] = perm[j]

    return preferences