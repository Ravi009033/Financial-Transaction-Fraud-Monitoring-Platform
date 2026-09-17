from decimal import Decimal

class FraudDetectionService:
    def calculate_fraud_score(self, amount: Decimal, transaction_type: str) -> Decimal:
        score = Decimal("0.0")
         # Rule 1: High transaction amount
        if amount >= Decimal("100000"):
            score += Decimal("0.6")

        elif amount >= Decimal("50000"):
            score += Decimal("0.4")

        # Rule 2: Online transactions carry additional risk
        if transaction_type == "online":
            score += Decimal("0.1")

        # Keep score between 0 and 1
        score = min(score, Decimal("1.0"))

        return score

    def make_decision(self, score: Decimal) -> str:

        if score >= Decimal("0.7"):
            return "blocked"

        elif score >= Decimal("0.4"):
            return "review"

        return "approved"

    def evaluate_transaction(self, amount: Decimal, transaction_type: str):
        score = self.calculate_fraud_score(
            amount,
            transaction_type
        )

        decision = self.make_decision(score)

        return {
            "fraud_score": score,
            "fraud_decision": decision
        }