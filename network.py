import random
from graph import generate_connected_graph
from peer import Node, Peer
import numpy as np


class Network:
    def __init__(
        self, n, z0, z1, max_transactions=3, min_transactions_per_mining=3, graph=None
    ):

        def generate_array_random(n, z):
            num_ones = int(n * z0)
            num_zeros = n - num_ones
            array = [1] * num_ones + [0] * num_zeros
            random.shuffle(array)
            return array

        self.max_transactions = max_transactions
        self.min_transactions_per_mining = min_transactions_per_mining

        self.peers = []
        self.nodes = []
        self.latencies = [[0 for _ in range(n)] for _ in range(n)]

        for i in range(n):
            for j in range(n):
                if i != j:
                    ij = np.random.uniform(10, 500)
                    cij = 100 if (self.nodes[i].speed and self.nodes[j].speed) else 5
                    dij = np.random.exponential(96 / cij)
                    self.latencies[i][j] = ij + dij
                else:
                    self.latencies[i][j] = 0

        speeds = generate_array_random(n, z0)
        CPU_speeds = generate_array_random(n, z1)

        self.graph = generate_connected_graph(n)

        for i in range(n):
            node = Node(i, speeds[i], CPU_speeds[i], self.min_transactions_per_mining)
            self.nodes.append(node)
            self.peers.append(Peer(node, n))
            # self.rel_transaction_timestamp = 0

    def connect_peers(self):
        for i, row in enumerate(self.graph):
            for j, connected in enumerate(row):
                if j <= i:
                    continue
                if connected:
                    self.peers[i].connect_to_peer(self.peers[j])
                    self.nodes[i].add_peer(self.peers[j])
                    self.peers[j].connect_to_peer(self.peers[i])
                    self.nodes[j].add_peer(self.peers[i])

    def generate_transactions(self):
        for _ in range(3):
            for peer in self.peers:
                peer.generate_transaction([i for i in range(len(self.nodes))])

    def print_blockchain(self):
        for node in self.nodes:
            print(f"Node {node.id} Blockchain:")
            for block in node.blockchain.blocks:
                print("Block ID:", block.block_id)
                print("Previous Block ID:", block.previous_block_id)
                print("Transactions:")
                for txn in block.transactions:
                    print(txn)
                print()

    def get_latency(self, i, j, messg_size=1):
        cij = 100 if (self.nodes[i].speed and self.nodes[j].speed) else 5
        return self.latencies[i][j] + messg_size / cij
