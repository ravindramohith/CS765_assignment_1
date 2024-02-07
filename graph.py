import random
import networkx as nx
import matplotlib.pyplot as plt


def generate_graph(n, min_edges=random.choice([3, 4, 5, 6])):
    graph = [[False] * n for _ in range(n)]
    indices = [i for i in range(n)]
    for i in range(n):
        check = 0
        for j in range(n):
            if graph[i][j]:
                check += 1
        if check >= min_edges:
            continue

        k = min_edges - check
        copy = indices.copy()
        if i in copy:
            copy.remove(i)
        while k != 0 and copy:
            choice = random.choice(copy)
            if not graph[i][choice]:
                graph[i][choice] = True
                graph[choice][i] = True
                k -= 1
            copy.remove(choice)

        for g in indices:
            c = 0
            for j in range(n):
                if graph[g][j]:
                    c += 1
            if c >= min_edges:
                if g in indices:
                    indices.remove(g)

    return graph


# def connected_components(graph):
#     def dfs(node):
#         visited[node] = True
#         component.append(node)
#         for neighbor in range(len(graph)):
#             if graph[node][neighbor] and not visited[neighbor]:
#                 dfs(neighbor)

#     visited = [False] * len(graph)
#     components = []
#     for node in range(len(graph)):
#         if not visited[node]:
#             component = []
#             dfs(node)
#             components.append(component)
#     return components


def visualize_graph(graph):
    G = nx.Graph()
    for i, row in enumerate(graph):
        for j, connected in enumerate(row):
            if connected:
                G.add_edge(i, j)
    nx.draw(G, with_labels=True)
    plt.show()


def is_connected(graph):
    def dfs(node):
        visited[node] = True
        for neighbor in range(len(graph)):
            if graph[node][neighbor] and not visited[neighbor]:
                dfs(neighbor)

    visited = [False] * len(graph)
    dfs(0)
    return all(visited)