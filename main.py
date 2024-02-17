from simulator import Simulator

if __name__ == "__main__":
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
