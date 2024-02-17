from simulator import Simulator
import sys

if __name__ == "__main__":
    simulator = Simulator(
        int(sys.argv[2]),
        float(sys.argv[4]),
        float(sys.argv[6]),
        min_transactions_per_mining=999,
        transaction_mean_gap=int(sys.argv[8]),
        max_events=10000,
    )

    simulator.simulate()

    if "--print-blockchain" in sys.argv:
        simulator.print_blockchain()

    if "--visualize-blockchain" in sys.argv:
        index = input("Enter the index of the node you want to visualize: ")
        if index.isdigit():
            index = int(index)
            if index < len(simulator.nodes):
                simulator.nodes[index].blockchain.visualize(index)
            else:
                print(
                    f"Invalid index. Index should be an integer from 0 to {int(sys.argv[2]) - 1}"
                )
        else:
            print(
                f"Invalid index. Index should be an integer from 0 to {int(sys.argv[2]) - 1}"
            )
