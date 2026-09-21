from typing import Dict, Any

from pydantic import BaseModel, Field


class RealFraudPredictionRequest(BaseModel):
    Time: float = Field(ge=0)

    V1: float
    V2: float
    V3: float
    V4: float
    V5: float
    V6: float
    V7: float
    V8: float
    V9: float
    V10: float
    V11: float
    V12: float
    V13: float
    V14: float
    V15: float
    V16: float
    V17: float
    V18: float
    V19: float
    V20: float
    V21: float
    V22: float
    V23: float
    V24: float
    V25: float
    V26: float
    V27: float
    V28: float

    Amount: float = Field(ge=0)


class RealFraudPredictionResponse(BaseModel):
    fraud_score: float
    fraud_decision: str
    threshold: float
    model_name: str
    model_version: str

class RealFraudModelInfoResponse(BaseModel):
    model_name: str
    model_type: str
    model_version: str
    threshold: float
    features: list[str]
    training: dict[str, Any]
    validation_metrics: dict[str, Any]
    test_metrics: dict[str, Any]
    threshold_selection: dict[str, Any]

class RealFraudModelMetricsResponse(BaseModel):
    validation_metrics: dict[str, Any]
    test_metrics: dict[str, Any]