class TransactionService:
    def __init__(self, amount, merchant, location, transaction_type):
        self.amount = amount
        self.merchant = merchant
        self.location = location
        self.transaction_type = transaction_type

    def create_transaction(self):
        return {
            "amount": self.amount,
            "merchant": self.merchant,
            "location": self.location,
            "transaction_type": self.transaction_type
        }