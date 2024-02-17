import hashlib


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
