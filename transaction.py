import numpy as np


def hash(x):
    return x


class Peer:
    def __init__(self, id, balance, transactions, CPU_speed=0, speed=0):
        self.id = id
        self.balance = balance
        self.transactions = transactions
        self.CPU_speed = CPU_speed
        self.speed = speed

    def __str__(self):
        return f"Peer {self.id} has balance {self.balance} and \n transactions {self.transactions}"

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def add_transaction(self, transaction):
        self.transactions.append(transaction)

    def update_balance(self, amount):
        self.balance += amount

    def get_balance(self):
        return self.balance

    def get_transactions(self):
        return self.transactions

    def get_id(self):
        return self.id


class Transaction:
    def __init__(self, sender, receiver, amount, latency, size_in_kb=1):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.latency = latency
        self.size_in_kb = size_in_kb
        self.ρij = np.random.uniform(10, 500)
        self.cij = 100 if (sender.speed and receiver.speed) else 5
        self.dij = np.random.exponential(96 / self.cij)
        

    def __str__(self):
        return f"TxnID: {self.sender} pays {self.receiver} {self.amount} coins"

    def __eq__(self, other):
        return (
            self.sender == other.sender
            and self.receiver == other.receiver
            and self.amount == other.amount
        )

    def __hash__(self):
        return hash(self.sender) + hash(self.receiver) + hash(self.amount)

    def get_sender(self):
        return self.sender

    def get_receiver(self):
        return self.receiver

    def get_amount(self):
        return self.amount


class Block:
    def __init__(self, transactions, previous_hash):
        self.transactions = transactions
        self.previous_hash = previous_hash

    def __str__(self):
        return f"Block with transactions {self.transactions} and previous hash {self.previous_hash}"

    def __eq__(self, other):
        return (
            self.transactions == other.transactions
            and self.previous_hash == other.previous_hash
        )

    def __hash__(self):
        return hash(self.transactions) + hash(self.previous_hash)

    def get_transactions(self):
        return self.transactions

    def get_previous_hash(self):
        return self.previous_hash

    def get_hash(self):
        return hash(self.transactions) + hash(self.previous_hash)

    def get_block(self):
        return self

    def get_block_hash(self):
        return hash(self)


class Blockchain:
    def __init__(self, blocks):
        self.blocks = blocks

    def __str__(self):
        return f"Blockchain with blocks {self.blocks}"

    def __eq__(self, other):
        return self.blocks == other.blocks

    def __hash__(self):
        return hash(self.blocks)

    def add_block(self, block):
        self.blocks.append(block)

    def get_blocks(self):
        return self.blocks

    def get_block(self, index):
        return self.blocks[index]

    def get_blockchain(self):
        return self

    def get_blockchain_hash(self):
        return hash(self)

    def get_block_hash(self, index):
        return hash(self.blocks[index])


class Network:
    def __init__(self, peers, blockchain):
        self.peers = peers
        self.blockchain = blockchain

    def __str__(self):
        return f"Network with peers {self.peers} and blockchain {self.blockchain}"

    def __eq__(self, other):
        return self.peers == other.peers and self.blockchain == other.blockchain

    def __hash__(self):
        return hash(self.peers) + hash(self.blockchain)

    def add_peer(self, peer):
        self.peers.append(peer)

    def add_block(self, block):
        self.blockchain.add_block(block)

    def get_peers(self):
        return self.peers

    def get_peer(self, index):
        return self.peers[index]

    def get_blockchain(self):
        return self.blockchain

    def get_network(self):
        return self

    def get_network_hash(self):
        return hash(self)

    def get_peer_hash(self, index):
        return hash(self.peers[index])

    def get_blockchain_hash(self):
        return hash(self.blockchain)


def main():
    peers = [Peer(0, 100, []), Peer(1, 100, []), Peer(2, 100, [])]
    transactions = [
        Transaction(0, 1, 10),
        Transaction(1, 2, 20),
        Transaction(2, 0, 30),
    ]
    block = Block(transactions, 0)
    blockchain = Blockchain([block])
    network = Network(peers, blockchain)
    print(network.get_network_hash())
    print(network.get_peer_hash(0))
    print(network.get_blockchain_hash())
    print(network.get_peer(0))
    print(network.get_blockchain())
    print(network.get_network())
    print(network.get_blockchain().get_blocks())
    print(network.get_blockchain().get_block(0))
    print(network.get_blockchain().get_block(0).get_transactions())
    print(network.get_blockchain().get_block(0).get_previous_hash())
    print(network.get_blockchain().get_block(0).get_block_hash())
    print(network.get_blockchain().get_block(0).get_block())


if __name__ == "__main__":
    main()
