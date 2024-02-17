import heapq
import random
from graph import generate_connected_graph
import numpy as np
import hashlib


class Event:
    def __init__(self, object, function, params, time):
        self.object = object
        self.function = function
        self.params = params
        self.time = time

    def __lt__(self, other):
        return self.time < other.time

    def __eq__(self, other):
        return self.time == other.time

    def __gt__(self, other):
        return self.time > other.time

    def __le__(self, other):
        return self.time <= other.time

    def __ge__(self, other):
        return self.time >= other.times

    def __str__(self) -> str:
        return f"Object: {self.object}, Function: {self.function}, Params: {self.params}, Time: {self.time}"


class EventPriorityQueue:
    def __init__(self):
        self._queue = []

    def push(self, event):
        heapq.heappush(self._queue, event)

    def pop(self):
        return heapq.heappop(self._queue)

    def is_empty(self):
        return len(self._queue) == 0


class Simulator:
    def __init__(
        self,
        n,
        z0,
        z1,
        min_transactions_per_mining=3,
        transaction_mean_gap=15,
        max_events=100,
    ):

        self.peers = []
        self.nodes = []
        self.min_transactions_per_mining = min_transactions_per_mining
        self.transaction_mean_gap = transaction_mean_gap
        self.graph = generate_connected_graph(n)
        speeds = self.generate_array_random(n, z0)
        CPU_speeds = self.generate_array_random(n, z1)
        print(speeds, CPU_speeds)
        self.h = 1 / (n + 9 * sum(CPU_speeds))

        for i in range(n):
            node = Node(
                i, speeds[i], CPU_speeds[i], self.min_transactions_per_mining, self
            )
            self.nodes.append(node)
            self.peers.append(Peer(node, n, self))

        self.connect_peers()

        self.latencies = [[0 for _ in range(n)] for _ in range(n)]
        self.longest_chains = [
            node.blockchain.get_longest_chain() for node in self.nodes
        ]

        for i in range(n):
            for j in range(n):
                if i != j:
                    ij = np.random.uniform(10, 500)
                    cij = 100 if (self.nodes[i].speed and self.nodes[j].speed) else 5
                    dij = np.random.exponential(96 / cij)
                    self.latencies[i][j] = ij + dij
                else:
                    self.latencies[i][j] = 0

        self.priority_queue = EventPriorityQueue()
        self.generate_transactions_init()
        self.max_events = max_events

    def generate_array_random(self, n, z):
        num_ones = int(n * z)
        num_zeros = n - num_ones
        array = [1] * num_ones + [0] * num_zeros
        random.shuffle(array)
        return array

    def simulate(self):
        for i in range(self.max_events):
            self.event_handler()

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

    def generate_transactions_init(self):
        for peer in self.peers:
            event = Event(peer, "generate_transactions", {"time": 0}, 0)
            self.priority_queue.push(event)

    def get_latency(self, i, j, messg_size=1):
        cij = 100 if (self.nodes[i].speed and self.nodes[j].speed) else 5
        return self.latencies[i][j] + messg_size / cij

    def event_handler(self):
        if not self.priority_queue.is_empty():
            event = self.priority_queue.pop()
            print(event)
            if event.function == "receive_block":
                index = self.peers.index(event.object)
                longest_chain_before = event.object.node.blockchain.get_longest_chain()
                if hasattr(event.object, event.function):
                    method = getattr(event.object, event.function)
                    if event.params is not None:
                        method(**event.params)
                    else:
                        method()
                longest_chain_after = event.object.node.blockchain.get_longest_chain()
                self.longest_chains[index] = longest_chain_after
                Tk = np.random.exponential(
                    self.nodes[index].avg_time / 10 * self.h
                    if self.nodes[index].CPU_speed == 1
                    else self.h
                )
                if longest_chain_before != longest_chain_after[:-1]:
                    self.priority_queue.push(
                        Event(
                            self.nodes[index],
                            "conditional_mine_block",
                            {
                                "prev_longest_chain": longest_chain_after,
                                "time": event.time + Tk,
                            },
                            event.time + Tk,
                        )
                    )
                    pass
            else:
                if hasattr(event.object, event.function):
                    method = getattr(event.object, event.function)
                    if event.params is not None:
                        method(**event.params)
                    else:
                        method()
        else:
            print("Events are empty")

    def is_proper_prefix(self, list1, list2):
        if len(list1) < len(list2):
            return all(list1[i] == list2[i] for i in range(len(list1)))
        else:
            return False

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


class Block:
    def __init__(self, block_id, previous_block_id, transactions):
        self.block_id = block_id
        self.previous_block_id = previous_block_id
        self.transactions = transactions

    def __eq__(self, other):
        return (
            self.block_id == other.block_id
            and self.previous_block_id == other.previous_block_id
            and self.transactions[:-1] == other.transactions[:-1]
        )


class Blockchain:
    def __init__(self):
        self.blocks = []

    def add_block(self, block):
        self.blocks.append(block)

    def create_block(self, transactions, node_id):
        # Create a new block with transactions
        transactions_string = "".join(
            [
                str(txn.sender) + str(txn.receiver) + str(txn.amount)
                for txn in transactions[:-1]
            ]
        )
        block_id = hashlib.sha256(transactions_string.encode()).hexdigest()

        if not self.blocks:
            previous_block_id = None
        else:
            longest_chain = self.get_longest_chain()
            previous_block_id = longest_chain[-1].block_id if longest_chain else None

        new_block = Block(block_id, previous_block_id, transactions)
        self.blocks.append(new_block)
        return new_block

    def get_longest_chain(self):
        longest_chain = []
        for block in self.blocks:
            current_chain = [block]
            while current_chain[-1].previous_block_id is not None:
                prev_block = self.find_block_by_id(current_chain[-1].previous_block_id)
                if prev_block:
                    current_chain.append(prev_block)
                else:
                    break
            if len(current_chain) > len(longest_chain):
                longest_chain = current_chain
        return longest_chain

    def find_block_by_id(self, block_id):
        for block in self.blocks:
            if block.block_id == block_id:
                return block
        return None


class Node:
    def __init__(
        self, id, speed, CPU_speed, min_transactions_per_mining, simulator=None
    ):
        self.id = id
        self.speed = speed
        self.CPU_speed = CPU_speed
        self.blockchain = Blockchain()
        self.transaction_pool = []
        self.peers = []
        self.min_transactions_per_mining = min_transactions_per_mining
        self.simulator = simulator
        self.blocks_received = 0
        self.time_for_avg = 0
        self.avg_time = 0

    def __eq__(self, other):
        return self.id == other.id

    def add_peer(self, peer):
        # Add a peer to the list of connected peers
        self.peers.append(peer)

    def check_if_exists_in_blockchain(self, block):
        for b in self.blockchain.blocks:
            if b == block:
                return True
        return False

    def receive_block(self, block, time):
        # Add the received block to the blockchain
        self.time_for_avg += time
        self.blocks_received += 1
        self.avg_time = self.time_for_avg / self.blocks_received
        if self.validate_block(block) and not self.check_if_exists_in_blockchain(block):
            for transaction in block.transactions:
                (
                    self.transaction_pool.remove(transaction)
                    if transaction in self.transaction_pool
                    else None
                )
            self.blockchain.add_block(block)
            self.simulator.priority_queue.push(
                Event(self, "propagate_block", {"block": block, "time": time}, time)
            )

    def receive_transaction(self, transaction, time):
        # Add the received transaction to the transaction pool
        found = False
        for block in self.blockchain.blocks:
            if transaction in block.transactions:
                found = True
                break
        if not found:
            self.transaction_pool.append(transaction)

        # Automatically mine a block when the transaction pool reaches a size of 2
        time += 1
        if len(self.transaction_pool) >= self.min_transactions_per_mining:
            self.mine_block(time)

    def mine_block(self, time):
        # Mine a new block with transactions from the pool
        self.transaction_pool.append(
            Transaction(-1, self.id, 50, timestamp=time)
        )  # Add a reward transaction
        new_block = self.blockchain.create_block(self.transaction_pool, self.id)
        self.simulator.longest_chains[self.simulator.nodes.index(self)] = (
            self.blockchain.get_longest_chain()
        )
        self.propagate_block(new_block, time)
        self.transaction_pool = []  # Clear the transaction pool
        return new_block

    def conditional_mine_block(self, prev_longest_chain, time):

        if self.simulator.is_proper_prefix(
            prev_longest_chain, self.blockchain.get_longest_chain()
        ):
            self.mine_block(time)

    def propagate_block(self, block, time):
        # Propagate the mined block to other nodes in the network
        for peer in self.peers:
            self.simulator.priority_queue.push(
                Event(
                    peer,
                    "receive_block",
                    {
                        "block": block,
                        "time": time
                        + self.simulator.get_latency(
                            self.id, peer.node.id, messg_size=len(block.transactions)
                        ),
                    },
                    time
                    + self.simulator.get_latency(
                        self.id, peer.node.id, messg_size=len(block.transactions)
                    ),
                )
            )
            # peer.receive_block(block, time)

    def validate_block(self, block):
        # Validate the received block before adding it to the blockchain
        # Check if sender has sufficient balance
        for transaction in block.transactions:
            if transaction.sender != -1:
                sender_balance = self.get_balance(transaction.sender)
                if sender_balance < transaction.amount:
                    return False
        # For simplicity, assume all blocks are valid in this implementation
        return True

    def get_balance(self, account_id):
        # Get the balance of an account from the blockchain
        balance = 1200000
        for b in self.blockchain.blocks:
            for txn in b.transactions:
                if txn.sender == account_id:
                    balance -= txn.amount
                if txn.receiver == account_id:
                    balance += txn.amount
        return balance


class Peer:
    def __init__(self, node, n, simulator=None):
        self.node = node
        self.connections = []
        self.rel_transaction_timestamp = 0
        self.n = n
        self.simulator = simulator

    def __eq__(self, other) -> bool:
        return self.node.id == other.node.id

    def connect_to_peer(self, peer):
        # Establish a connection to another peer
        self.connections.append(peer)

    def generate_transactions(self, time):
        print(time)
        # Generate a new transaction
        sender = self.node.id
        nodes = [i for i in range(self.n) if i != sender]
        receiver = random.choice(nodes)
        amount = random.randint(1, 50)
        transaction = Transaction(
            sender, receiver, amount, self.rel_transaction_timestamp
        )
        self.rel_transaction_timestamp += np.random.exponential(
            self.simulator.transaction_mean_gap
        )
        self.simulator.priority_queue.push(
            Event(
                self,
                "generate_transactions",
                {"time": self.rel_transaction_timestamp},
                self.rel_transaction_timestamp,
            )
        )
        self.simulator.priority_queue.push(
            Event(
                self,
                "broadcast_transaction",
                {"transaction": transaction, "time": self.rel_transaction_timestamp},
                self.rel_transaction_timestamp,
            )
        )
        # self.broadcast_transaction(transaction)

    def receive_block(self, block, time):
        # Forward the received block to the node
        self.node.receive_block(block, time)

    def receive_transaction(self, transaction, time):
        # Forward the received transaction to the node
        self.node.receive_transaction(transaction, time)

    def mine_block(self):
        # Mine a new block using the node's mining function
        return self.node.mine_block()

    def propagate_block(self, block, time):
        # Propagate the mined block to other peers
        for peer in self.connections:
            self.simulator.priority_queue.push(
                Event(peer, "receive_block", {"block": block, "time": time}, time)
            )

    def broadcast_transaction(self, transaction, time):
        # Broadcast a transaction to other peers
        self.simulator.priority_queue.push(
            Event(
                self.node,
                "receive_transaction",
                {"transaction": transaction, "time": time},
                time,
            )
        )


class Transaction:
    def __init__(self, sender, receiver, amount, timestamp=0):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.timestamp = timestamp

    def __str__(self) -> str:
        return f"Sender: {self.sender}, Receiver: {self.receiver}, Amount: {self.amount} TimeStamp {self.timestamp}"


simulator = Simulator(
    4,
    0.2,
    0.5,
    min_transactions_per_mining=2,
    transaction_mean_gap=15000,
    max_events=100,
)

simulator.simulate()
simulator.print_blockchain()
