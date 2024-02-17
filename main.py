from simulator import Simulator

if __name__ == "__main__":

    simulator = Simulator(
        3,
        0.2,
        0.5,
        min_transactions_per_mining=9,
        transaction_mean_gap=150,
        max_events=int(1e3),
    )

    simulator.simulate()
    simulator.print_blockchain()
    simulator.visualize()
