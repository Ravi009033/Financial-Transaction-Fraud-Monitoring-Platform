class DashboardService:

    def __init__(self, transaction_repository):
        self.transaction_repository = transaction_repository

    def get_summary(self, user_id):
        return self.transaction_repository.get_dashboard_summary(
            user_id
        )

    def get_transaction_trends(self, user_id):
        return self.transaction_repository.get_transaction_trends(
            user_id
        )

    def get_fraud_distribution(self, user_id):
        return self.transaction_repository.get_fraud_distribution(
            user_id
        )