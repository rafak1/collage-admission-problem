import numpy as np
import networkx as nx


def calculate_max_flow_with_specific_sinks(n_orig: int, t_orig: int, M_orig: list[list[int]]):
    """
    Calculates the maximum flow in a graph constructed with a specific sink structure.

    The graph includes:
    - A 'start' node.
    - 2*n_orig 'people' nodes.
    - 2*t_orig 'topic' nodes.
    - Two intermediate sinks, 'sink_1' and 'sink_2'.
    - A 'final_sink' node.

    Edges are set up as follows:
    - From 'start' to all 'people' nodes (capacity 1).
    - From 'people' nodes to 'topic' nodes based on a doubled version of M_orig (capacity 1).
    - The first t_orig 'topic' nodes (from the 2*t_orig set) connect to 'sink_1' (capacity 1).
    - The next t_orig 'topic' nodes connect to 'sink_2' (capacity 1).
    - From 'sink_1' to 'final_sink' (capacity t_orig).
    - From 'sink_2' to 'final_sink' (capacity n_orig - t_orig).

    Args:
        n_orig: The original number of people.
        t_orig: The original number of topics.
        M_orig: The n_orig x t_orig preference matrix as a list of lists.

    Returns:
        A tuple containing:
            - flow_value (float): The maximum flow from 'start' to 'final_sink'.
            - flow_dict (dict): A dictionary of dictionaries representing the flow.
    """
    M_np = np.array(M_orig, dtype=int)
    doubled_n = 2 * n_orig
    doubled_t = 2 * t_orig

    G = nx.DiGraph()

    # Define node labels/indices to ensure clarity
    # People nodes: 0 to doubled_n - 1
    # Topic nodes: doubled_n to doubled_n + doubled_t - 1
    start_node = doubled_n + doubled_t
    sink_1_node = start_node + 1
    sink_2_node = start_node + 2
    final_sink_node = start_node + 3

    # 1. Add edges from start_node to all people_nodes
    # Each of the 2*n_orig people nodes gets an edge from the start_node.
    for i in range(doubled_n):
        G.add_edge(start_node, i, capacity=1)

    # 2. Add edges from people_nodes to topic_nodes (based on doubled matrix logic)
    # The original M_np (n_orig x t_orig) dictates connections.
    for r_orig in range(n_orig):  # Iterate through rows of the original M_np
        for c_orig in range(t_orig):  # Iterate through columns of the original M_np
            if M_np[r_orig, c_orig] == 1:
                # Connections for the "top-left" quadrant of the conceptual doubled matrix:
                # Person node index: r_orig
                # Topic node index: doubled_n + c_orig
                G.add_edge(r_orig, doubled_n + c_orig, capacity=1)

                # Connections for the "bottom-right" quadrant:
                # Person node index: r_orig + n_orig
                # Topic node index: doubled_n + c_orig + t_orig
                G.add_edge(r_orig + n_orig, doubled_n + c_orig + t_orig, capacity=1)

    # 3. Add edges from topic_nodes to the two intermediate sinks
    # The first t_orig topic nodes (indices from doubled_n to doubled_n + t_orig - 1) connect to sink_1_node.
    for j in range(t_orig):
        topic_node_global_idx = doubled_n + j
        G.add_edge(topic_node_global_idx, sink_1_node, capacity=1)

    # The next t_orig topic nodes (indices from doubled_n + t_orig to doubled_n + doubled_t - 1) connect to sink_2_node.
    # doubled_t is 2*t_orig, so j ranges from t_orig to 2*t_orig - 1.
    for j in range(t_orig, doubled_t):
        topic_node_global_idx = doubled_n + j
        G.add_edge(topic_node_global_idx, sink_2_node, capacity=1)

    # 4. Add edges from intermediate sinks to the final_sink_node
    # Edge from sink_1_node to final_sink_node with capacity t_orig.
    G.add_edge(sink_1_node, final_sink_node, capacity=t_orig)

    # Edge from sink_2_node to final_sink_node with capacity n_orig - t_orig.
    # As per user request "its weight is equal to n-t".
    # NetworkX requires non-negative capacities. If n_orig < t_orig, this will result in an error.
    capacity_sink2_to_final = n_orig - t_orig
    G.add_edge(sink_2_node, final_sink_node, capacity=capacity_sink2_to_final)

    # 5. Calculate the maximum flow from start_node to final_sink_node
    flow_value, flow_dict = nx.maximum_flow(G, start_node, final_sink_node)

    return flow_value, flow_dict


if __name__ == '__main__':
    n = 4  # number of people (n_orig)
    t = 3  # number of topics (t_orig)
    M = [  # matrix of preferences n x t (M_orig)
        [1, 1, 1],
        [0, 0, 1],
        [0, 1, 1],
        [1, 1, 0]
    ]

    try:
        max_flow_val, flow_det = calculate_max_flow_with_specific_sinks(n, t, M)
        print(f"Maximum flow value: {max_flow_val}")
        # For the example n=4, t=3:
        # Capacity (sink_1 -> final_sink) = t = 3
        # Capacity (sink_2 -> final_sink) = n - t = 4 - 3 = 1
        # Expected max flow for this example is 4.0
    except nx.NetworkXUnfeasible as e:
        print(f"Error: {e}. This might be due to a negative capacity if n_orig < t_orig.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

