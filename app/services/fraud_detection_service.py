from ml.src.predict import predict_fraud


class FraudDetectionService:

    @staticmethod
    def predict(features: dict) -> dict:
        """
        Generate a fraud prediction using the trained ML model.
        """

        return predict_fraud(features)