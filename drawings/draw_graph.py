import random

import matplotlib.pyplot as plt
import networkx as nx

# Parameters
n = 5  # number of v vertices
m = 3  # number of t vertices

# Create bipartite graph
G = nx.Graph()

# Add vertices
v_vertices = [f'v_{i}' for i in range(1, n + 1)]
v_prime_vertices = [f"v'_{i}" for i in range(1, n + 1)]
t_vertices = [f't_{i}' for i in range(1, m + 1)]
t_prime_vertices = [f"t'_{i}" for i in range(1, m + 1)]

G.add_nodes_from(v_vertices, bipartite=0)
G.add_nodes_from(v_prime_vertices, bipartite=0)
G.add_nodes_from(t_vertices, bipartite=1)
G.add_nodes_from(t_prime_vertices, bipartite=1)

# Add edges: each v and v' vertex connects to 2-4 random t and t' vertices
for v_node in v_prime_vertices:  # + v_prime_vertices: # Renamed 'v' to 'v_node' to avoid conflict
    num_edges = random.choice([2, 3, 4])
    # Ensure that the number of targets requested is not more than available targets
    # Total t and t' vertices = m + m = 2*m
    # If num_edges > 2*m, then sample size will be larger than population
    actual_num_edges = min(num_edges, m)
    targets = random.sample(t_prime_vertices,  # + t_prime_vertices,
                            actual_num_edges)
    for t_node in targets:  # Renamed 't' to 't_node'
        G.add_edge(v_node, t_node)
        G.add_edge(v_node.replace("'", ""), t_node.replace("'", ""))  # Connect v' to t and v to t

# Position nodes
pos = {}

# Left side: v vertices vertically spaced at x=0
for i, v_node in enumerate(v_vertices):  # Renamed 'v' to 'v_node'
    pos[v_node] = (0, -i)

# Below v vertices: v' vertices vertically spaced at x=0, below v vertices
for i, v_prime_node in enumerate(v_prime_vertices):  # Renamed 'v_prime' to 'v_prime_node'
    pos[v_prime_node] = (0, -n - i - 1)

# Right side: t vertices vertically spaced at x=1
for i, t_node in enumerate(t_vertices):  # Renamed 't' to 't_node'
    pos[t_node] = (1, -i-1)

# Below t vertices: t' vertices vertically spaced at x=1, below t vertices
for i, t_prime_node in enumerate(t_prime_vertices):  # Renamed 't_prime' to 't_prime_node'
    pos[t_prime_node] = (1, -m - i - 4)

# Draw graph
plt.figure(figsize=(8, 10))  # Adjusted figure size for better layout

# Draw nodes with colors
nx.draw_networkx_nodes(G, pos, nodelist=v_vertices, node_color='lightblue', label='v vertices')
nx.draw_networkx_nodes(G, pos, nodelist=v_prime_vertices, node_color='lightblue', label="v' vertices")
nx.draw_networkx_nodes(G, pos, nodelist=t_vertices, node_color='lightgreen', label='t vertices')
nx.draw_networkx_nodes(G, pos, nodelist=t_prime_vertices, node_color='lightgreen', label="t' vertices")

# Draw edges
nx.draw_networkx_edges(G, pos)

# Draw labels
nx.draw_networkx_labels(G, pos)

plt.title("Bipartite Graph with v, v', t, t' vertices and edges")
plt.axis('off')
# plt.legend(scatterpoints=1, loc='lower center', ncol=2) # Adjusted legend position
plt.show()
