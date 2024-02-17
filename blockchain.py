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

    def visualize(self):
        # Create a directed graph
        G = nx.DiGraph()

        # Add nodes and edges for each block
        for block in self.blocks:
            G.add_node(block.block_id)
            if block.previous_block_id:
                G.add_edge(block.previous_block_id, block.block_id)

        # Create a mapping of block IDs to block information for quick access
        block_info = {block.block_id: block for block in self.blocks}

        # Plot the graph
        plt.figure(figsize=(20, 10))  # Full screen mode
        pos = nx.spring_layout(G)  # Position nodes using the spring layout algorithm

        # Draw nodes for each block
        for node in G.nodes():
            block = block_info[node]
            transactions_text = self.get_transactions_text(block.transactions)
            node_size = max(
                1000, 100 + 50 * len(transactions_text.split("\n"))
            )  # Adjust node size based on text length
            nx.draw_networkx_nodes(
                G,
                pos,
                nodelist=[node],
                node_size=node_size,
                node_shape="s",
                node_color="lightblue",
                # edgecolors="black",
                # linewidths=2,
            )

            # Add label with block ID and transactions text
            label = f"{block.block_id}"
            nx.draw_networkx_labels(
                G, pos, labels={node: label}, font_size=10, font_weight="bold"
            )

        # Draw directed edges with increased arrow size
        nx.draw_networkx_edges(G, pos, arrows=True, arrowsize=50)

        plt.title("Blockchain Visualization")
        plt.axis("off")  # Turn off axis
        plt.show()

    def get_transactions_text(self, transactions):
        if len(transactions) <= 3:
            return "\n".join(str(txn) for txn in transactions)
        else:
            first_three = "\n".join(str(txn) for txn in transactions[:3])
            remaining_count = len(transactions) - 3
            return f"{first_three}\n\n{remaining_count} more..."
