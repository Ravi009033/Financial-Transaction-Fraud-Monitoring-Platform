
class DuplicateAccountError(Exception):
    pass

class InsufficientBalanceError(Exception):
    pass

class TransactionAlreadyProcessedError(Exception):
    pass

class AccountAccessDeniedError(Exception):
    pass

class TransactionAccessDeniedError(Exception):
    pass