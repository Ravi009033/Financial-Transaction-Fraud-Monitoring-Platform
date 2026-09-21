from fastapi import APIRouter, HTTPException

from app.schemas.ml import (
    RealFraudPredictionRequest,
    RealFraudPredictionResponse,
    RealFraudModelInfoResponse,
    RealFraudModelMetricsResponse
)

from ml.src.real_predict import predict_real_fraud
from ml.src.real_predict import metadata


router = APIRouter(
    prefix="/ml",
    tags=["Machine Learning"],
)


@router.post(
    "/predict",
    response_model=RealFraudPredictionResponse,
)
def predict_fraud(
    request: RealFraudPredictionRequest,
):

    try:
        features = request.model_dump()

        result = predict_real_fraud(
            features
        )

        return result

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )

@router.get(
    "/model-info",
    response_model=RealFraudModelInfoResponse,
)
def get_real_fraud_model_info():
    return {
        "model_name": metadata["model_name"],
        "model_type": metadata["model_type"],
        "model_version": metadata["model_version"],
        "threshold": metadata["threshold_selection"]["selected_threshold"],
        "features": metadata["dataset"]["features"],
        "training": metadata["training"],
        "validation_metrics": metadata["validation_metrics"],
        "test_metrics": metadata["test_metrics"],
        "threshold_selection": metadata["threshold_selection"],
    }

@router.get(
    "/metrics",
    response_model=RealFraudModelMetricsResponse,
)
def get_real_fraud_model_metrics():
    return {
        "validation_metrics": metadata["validation_metrics"],
        "test_metrics": metadata["test_metrics"],
    }