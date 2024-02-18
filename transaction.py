class Transaction:
    def __init__(self, sender, receiver, amount, timestamp=0):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.timestamp = timestamp

    def __str__(self) -> str:
        return f"TxnID: ID{self.sender} pays ID{self.receiver} {self.amount} coins"
