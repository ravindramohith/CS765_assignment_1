import hashlib
import matplotlib.pyplot as plt
import networkx as nx


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
        self.genesis_block = Block("0", None, [])
        self.blocks = [self.genesis_block]

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
        block_id = hashlib.sha1(transactions_string.encode()).hexdigest()

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
        return longest_chain[::-1]

    def find_block_by_id(self, block_id):
        for block in self.blocks:
            if block.block_id == block_id:
                return block
        return None

    def visualize(self, node_id):
        G = nx.DiGraph()

        for block in self.blocks:
            G.add_node(block.block_id)
            if block.previous_block_id:
                G.add_edge(block.previous_block_id, block.block_id)

        block_info = {block.block_id: block for block in self.blocks}

        plt.figure(figsize=(20, 10))  # Full screen mode
        pos = nx.spring_layout(G) 

        # Draw nodes for each block
        for i, node in enumerate(G.nodes()):
            block = block_info[node]
            nx.draw_networkx_nodes(
                G,
                pos,
                nodelist=[node],
                node_size=1000,
                node_shape="s",
                node_color="lightblue",
                edgecolors="black",
                # linewidths=2,
            )

            label = f"{block.block_id}"
            nx.draw_networkx_labels(
                G, pos, labels={node: label}, font_size=1, font_weight="bold"
            )

        nx.draw_networkx_edges(G, pos, arrows=True, arrowsize=30)
        plt.title(f"Peer {node_id}'s Blockchain Visualization")

        plt.axis("off")
        plt.show()
