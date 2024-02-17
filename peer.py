from blockchain import Blockchain
import numpy as np, random
from transaction import Transaction
from event import Event


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
