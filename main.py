from graph import generate_graph, is_connected

n = 10

if __name__ == "__main__":
    while True:
        graph = generate_graph(n)
        if is_connected(graph):
            break
