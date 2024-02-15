from network import Network


if __name__ == "__main__":
    net = Network(4, 0.1, 0.4, max_transactions=3, min_transactions_per_mining=3)
    net.connect_peers()
    net.generate_transactions()
    net.print_blockchain()
