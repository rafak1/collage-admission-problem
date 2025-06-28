from sum import linear_programming
import random
import copy
from sum import biparte_graph
from utils import generate_random_preferences

tries = 100

for i in range(tries):
    n_topics = random.randint(1, 5)
    n_students = random.randint(n_topics, 2 * n_topics)

    preferences = generate_random_preferences(n_students, n_topics)
    
    result1, dissatisfaction1 = linear_programming.solve(n_students, n_topics, copy.deepcopy(preferences))
    result2, dissatisfaction2 = biparte_graph.solve(n_students, n_topics, copy.deepcopy(preferences))
    #brut.solve(n_students, n_topics, copy.deepcopy(preferences))

    if dissatisfaction1 != dissatisfaction2:
        print(f"Discrepancy found!")
        print(f"Students: {n_students}, Topics: {n_topics}")
        print(f"Preferences: {preferences}")
        print(f"Linear Programming Result: {result1}, Dissatisfaction: {dissatisfaction1}")
        print(f"Other Result: {result2}, Dissatisfaction: {dissatisfaction2}")
        break

    print("noice")
    