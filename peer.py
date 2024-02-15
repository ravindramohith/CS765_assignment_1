from blockchain import Blockchain
import numpy as np, random
from transaction import Transaction


class Node:
    def __init__(self, id, speed, CPU_speed, min_transactions_per_mining):
        self.id = id
        self.speed = speed
        self.CPU_speed = CPU_speed
        self.blockchain = Blockchain()
        self.transaction_pool = []
        self.peers = []
        self.min_transactions_per_mining = min_transactions_per_mining

    def add_peer(self, peer):
        # Add a peer to the list of connected peers
        self.peers.append(peer)

    def check_if_exists_in_blockchain(self, block):
        for b in self.blockchain.blocks:
            if b == block:
                return True
        return False

    def receive_block(self, block):
        # Add the received block to the blockchain
        # print("Received block:", block.block_id, self.id)
        if self.validate_block(block) and not self.check_if_exists_in_blockchain(block):
            for transaction in block.transactions:
                (
                    self.transaction_pool.remove(transaction)
                    if transaction in self.transaction_pool
                    else None
                )
            self.blockchain.add_block(block)
            self.propagate_block(block)

    def receive_transaction(self, transaction):
        # Add the rfeceived transaction to the transaction pool
        # self.transaction_pool.append(transaction) if transaction not in self.transaction_pool else None
        found = False
        for block in self.blockchain.blocks:
            if transaction in block.transactions:
                found = True
                break
        if not found:
            self.transaction_pool.append(transaction)

        # for i in self.transaction_pool:
        #     print(self.id, " : ", i)
        # print("pool_printed")
        # Automatically mine a block when
        #  the transaction pool reaches a size of 2
        if len(self.transaction_pool) >= self.min_transactions_per_mining:
            # print("mining")
            self.mine_block()

    def mine_block(self):
        # Mine a new block with transactions from the pool
        self.transaction_pool.append(
            Transaction(-1, self.id, 50)
        )  # Add a reward transaction
        new_block = self.blockchain.create_block(self.transaction_pool, self.id)
        # print("mined", new_block.block_id, self.id)
        self.propagate_block(new_block)
        self.transaction_pool = []  # Clear the transaction pool
        # print("cleared")
        return new_block

    def propagate_block(self, block):
        # Propagate the mined block to other nodes in the network
        # print("propagating", block.block_id, self.id)
        for peer in self.peers:
            # print("propagating to peer i", block.block_id, self.id, peer.node.id)
            peer.receive_block(block)

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
    def __init__(self, node, n):
        self.node = node
        self.connections = []
        self.rel_transaction_timestamp = 0
        self.n = n

    def connect_to_peer(self, peer):
        # Establish a connection to another peer
        self.connections.append(peer)

    def generate_transaction(self, nodes):
        # Generate a new transaction
        sender = self.node.id
        nodes.remove(self.node.id)
        receiver = random.choice(nodes)
        amount = random.randint(1, 50)
        transaction = Transaction(
            sender, receiver, amount, self.rel_transaction_timestamp
        )
        self.rel_transaction_timestamp += np.random.exponential(15)
        self.B(transaction)

    def receive_block(self, block):
        # Forward the received block to the node
        self.node.receive_block(block)
        # self.propagate_block(block)

    def receive_transaction(self, transaction, visted):
        # Forward the received transaction to the node
        self.broadcast_transaction(transaction, visted)
        # Also add the transaction to the local transaction pool
        # for peer in self.connections:
        #     peer.receive_transaction(transaction)

    def mine_block(self):
        # Mine a new block using the node's mining function
        new_block = self.node.mine_block()
        return new_block

    def propagate_block(self, block):
        # Propagate the mined block to other peers
        for peer in self.connections:
            peer.receive_block(block)

    def broadcast_transaction(self, transaction, visited):
        # Broadcast a transaction to other peers'
        # self.receive_transaction(transaction, visited)
        if transaction not in self.node.transaction_pool:
            self.node.receive_transaction(transaction)
        # self.node.transaction_pool.append(transaction)
        visited[self.node.id - 1] = True
        for peer in self.connections:
            if not visited[peer.node.id - 1]:
                visited[peer.node.id - 1] = True
                peer.receive_transaction(transaction, visited)

    def B(self, transaction):
        visited = [False] * self.n
        self.broadcast_transaction(transaction, visited)
