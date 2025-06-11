import itertools

def solve(n_students, n_topics, preferences):
    students = range(n_students)
    topics = range(n_topics)

    best_assignment = None
    min_dissatisfaction = float('inf')

    for assignment in itertools.product(topics, repeat=n_students):
        topic_counts = [0] * n_topics
        for topic in assignment:
            topic_counts[topic] += 1
        
        if any(count < 1 or count > 2 for count in topic_counts):
            continue

        dissatisfaction = sum(preferences[i, assignment[i]] for i in students)

        if dissatisfaction < min_dissatisfaction:
            min_dissatisfaction = dissatisfaction
            best_assignment = assignment

    return list(best_assignment), min_dissatisfaction


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