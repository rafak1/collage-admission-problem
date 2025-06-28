import networkx as nx

def solve_with_flow(n_students, n_topics, preferences):
    # Build cost matrix for 2 slots per topic
    cost_matrix = [[0] * (2 * n_topics) for _ in range(n_students)]
    for i in range(n_students):
        for j in range(n_topics):
            base_cost = preferences[i, j]
            cost_matrix[i][j] = base_cost  # slot 0
            cost_matrix[i][n_topics + j] = base_cost + n_topics  # slot 1, slightly worse to break ties

    def is_feasible(threshold):
        G = nx.DiGraph()
        source, sink = "S", "T"
        students = [f"s_{i}" for i in range(n_students)]
        slots = [f"slot_{j}" for j in range(2 * n_topics)]
        topics = [f"topic_{j}" for j in range(n_topics)]

        # Source to students
        for s in students:
            G.add_edge(source, s, capacity=1)

        # Students to slots (only if under threshold)
        for i, s in enumerate(students):
            for j, slot in enumerate(slots):
                if cost_matrix[i][j] <= threshold:
                    G.add_edge(s, slot, capacity=1)

        # Slots to topics
        for j, slot in enumerate(slots):
            topic_index = j % n_topics
            G.add_edge(slot, topics[topic_index], capacity=1)

        # Topics to sink with lower bounds (min 1 student per topic)
        demand = {}
        for t in topics:
            G.add_edge(t, sink, capacity=2)
            demand[t] = 1  # min 1 flow required
        for s in slots:
            demand[s] = 0
        for s in students:
            demand[s] = -1
        demand[source] = n_students
        demand[sink] = -n_topics

        super_source, super_sink = "SS", "TT"
        G.add_node(super_source)
        G.add_node(super_sink)
        total_demand = 0

        for node, d in demand.items():
            if d > 0:
                G.add_edge(super_source, node, capacity=d)
                total_demand += d
            elif d < 0:
                G.add_edge(node, super_sink, capacity=-d)

        G.add_edge(sink, source, capacity=n_students)  # circulation
        flow_val, flow_dict = nx.maximum_flow(G, super_source, super_sink)

        # extract the assignments
        #print(flow_dict)
        result = [-1] * n_students
        for i, s in enumerate(students):
            if s in flow_dict:
                for slot_name, flow in flow_dict[s].items():
                    if flow == 1 and slot_name.startswith("slot_"):
                        slot_index = int(slot_name.split("_")[1])
                        topic_index = slot_index % n_topics
                        result[i] = topic_index
                        break

        print(f"Flow value: {flow_val}, Total demand: {total_demand}")
        return flow_val == total_demand, result

    # Binary search over dissatisfaction threshold
    low, high = 0, max(preferences.values()) + n_topics
    answer = -1
    print(f"start {low} high {high}")
    while low <= high:
        mid = (low + high) // 2
        print(f"Checking feasibility for threshold: {mid}")
        feasible, assigments = is_feasible(mid)
        if feasible:
            print(f"Feasible for threshold: {mid}")
            answer = mid
            high = mid - 1
        else:
            print(f"Not feasible for threshold: {mid}")
            low = mid + 1

    _, assigments = is_feasible(answer)

    return answer, assigments

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

    n_students = 2
    n_topics = 2
    preferences = {
        (0, 0): 1, (0, 1): 2,
        (1, 0): 2, (1, 1): 1,
    }

    dissatisfaction, assigments = solve_with_flow(n_students, n_topics, preferences)
    print(f"Minimum dissatisfaction: {dissatisfaction}")
    print(f"Assignments: {assigments}") 
