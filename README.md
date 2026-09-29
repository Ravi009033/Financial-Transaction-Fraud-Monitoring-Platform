# Financial Fraud Monitoring Platform

An end-to-end financial transaction monitoring and fraud detection platform built with **Python, FastAPI, PostgreSQL, SQLAlchemy, XGBoost, Scikit-learn, Streamlit, Pytest, Docker, and Alembic**.

The project combines backend engineering, database design, machine learning, API development, automated testing, and dashboarding into a production-oriented application.

---

## 🚀 Project Overview

The platform allows authenticated users to manage accounts and transactions while evaluating transactions for potential fraud.

When a transaction is created, the system:

1. Validates the request.
2. Authenticates the user.
3. Verifies account ownership.
4. Checks account balance.
5. Retrieves historical transaction data.
6. Generates behavioral features.
7. Runs the fraud detection model.
8. Generates a fraud score.
9. Applies business thresholds.
10. Classifies the transaction as `APPROVED`, `REVIEW`, or `BLOCKED`.
11. Updates the account balance when appropriate.
12. Stores the transaction and fraud/model metadata in PostgreSQL.

---

# 🏗️ Architecture

```text
                         ┌──────────────────────┐
                         │     Streamlit UI     │
                         │        :8501         │
                         └──────────┬───────────┘
                                    │
                                    │ HTTP/REST
                                    ▼
                         ┌──────────────────────┐
                         │       FastAPI        │
                         │        :8000         │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    API Routers       │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Pydantic Schemas   │
                         │ Validation/Serialize │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    Service Layer     │
                         │    Business Logic    │
                         └───────┬────────┬─────┘
                                 │        │
                    ┌────────────┘        └──────────────┐
                    ▼                                    ▼
          ┌────────────────────┐              ┌────────────────────┐
          │ Repository Layer   │              │ Fraud Detection    │
          │ Database Operations│              │ Service            │
          └──────────┬─────────┘              └─────────┬──────────┘
                     │                                  │
                     ▼                                  ▼
          ┌────────────────────┐              ┌────────────────────┐
          │   SQLAlchemy ORM   │              │ Feature Engineering│
          └──────────┬─────────┘              └─────────┬──────────┘
                     │                                  │
                     ▼                                  ▼
          ┌────────────────────┐              ┌────────────────────┐
          │    PostgreSQL      │              │    XGBoost Model   │
          │ Users              │              └─────────┬──────────┘
          │ Accounts           │                        │
          │ Transactions       │                        ▼
          └────────────────────┘                  Fraud Score


                                                        │
                                      ┌─────────────────┼─────────────────┐
                                      ▼                 ▼                 ▼
                                  APPROVED            REVIEW            BLOCKED

```


# ✨ Key Features
---
## Backend
- RESTful APIs using FastAPI
- Layered architecture
- User management
- Account management
- Transaction CRUD operations
- JWT authentication
- Password hashing
- Resource ownership authorization
- Pydantic request/response validation
- Pagination
- Transaction status filtering
- Custom exception handling
- Global exception handling
- Database transaction management
## Database
- PostgreSQL
- SQLAlchemy ORM
- UUID primary keys
- Foreign key relationships
- Unique constraints
- PostgreSQL ENUM types
- NUMERIC for financial amounts
- Alembic database migrations
## Fraud Detection
- XGBoost
- Scikit-learn
- Behavioral feature engineering
- Historical transaction analysis
- Fraud probability scoring
- Threshold-based decisions
- Class imbalance handling
- Precision/Recall/F1 evaluation
- ROC-AUC
- PR-AUC
- SHAP explainability
- Model version metadata
- Model threshold metadata
## Dashboard
- Streamlit frontend
- Dashboard KPIs
- Transaction trends
- Fraud/suspicious transaction distribution
- Transaction filtering
- Transaction pagination
- Transaction details
## Testing
- Pytest
- Unit tests
- API tests
- Service tests
- ML prediction tests
- Database integration tests
- Authentication/authorization tests
- Isolated PostgreSQL test database
## Deployment
- Docker
- Docker Compose
- PostgreSQL container
- FastAPI container
- Streamlit container
- PostgreSQL health check
- Automatic Alembic migrations on API startup
- Environment-based configuration
---

# 🔐 Authentication and Authorization
The application uses JWT-based authentication.

```text
Login
  ↓
Email + Password
  ↓
Password Hash Verification
  ↓
JWT Access Token
  ↓
Authorization: Bearer <token>
  ↓
Protected API
  ↓
Authenticated User
  ↓
Resource Ownership Check
```
Users can access only their own accounts and transactions.

# 💳 Transaction Processing
The transaction workflow is:
```text
POST /transactions
        │
        ▼
Request Validation
        │
        ▼
JWT Authentication
        │
        ▼
Account Ownership Check
        │
        ▼
Balance Validation
        │
        ▼
Historical Transaction Retrieval
        │
        ▼
Behavioral Feature Engineering
        │
        ▼
XGBoost Fraud Prediction
        │
        ▼
Fraud Score
        │
        ▼
Business Decision
        │
        ├── score < 0.33
        │       └── APPROVED
        │
        ├── 0.33 ≤ score < 0.70
        │       └── REVIEW
        │
        └── score ≥ 0.70
                └── BLOCKED
        │
        ▼
Persist Transaction
        │
        ▼
Update Account Balance
(if approved)
```
# 📊 Model Explainability
SHAP is used to understand model behavior.
The system can analyze which features contributed toward a model prediction.
```text
Transaction Features
        ↓
XGBoost Prediction
        ↓
SHAP
        ↓
Feature Contributions
```
SHAP explanations describe model contribution and should not be interpreted as causal explanations.
# 📈 Dashboard
The Streamlit dashboard provides transaction monitoring and analytics.
Current dashboard functionality includes:
Summary
- Total transactions
- Total transaction amount
- Approved transactions
- Review transactions
- Blocked transactions
- Pending transactions
- Suspicious transactions
- Suspicious transaction rate

# 🧪 Testing Strategy
The project uses Pytest with an isolated PostgreSQL test database.
Examples of tested scenarios:
- User creation
- Authentication
- Invalid credentials
- Account creation
- Duplicate account
- Account authorization
- Transaction creation
- Transaction retrieval
- Transaction update
- Insufficient balance
- Unauthorized transaction
- Processed transaction modification
- Fraud prediction
- ML model metadata
- Missing ML features
- Dashboard APIs
- Pagination
- Transaction status filtering
