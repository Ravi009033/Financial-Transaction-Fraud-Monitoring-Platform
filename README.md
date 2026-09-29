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

# 🛡️ Exception Handling
The application uses custom exceptions for business-level errors.
Examples:
```text
DuplicateAccountError
InsufficientBalanceError
TransactionAlreadyProcessedError
AccountAccessDeniedError
TransactionAccessDeniedError
```
The application also contains global exception handling to prevent unexpected internal errors from exposing implementation details.
Typical HTTP mappings include:
```text
400 → Bad Request
401 → Unauthenticated
403 → Forbidden
404 → Resource Not Found
409 → Conflict
422 → Validation Error
500 → Internal Server Error
```
# 🗄️ Database Design
The main relationship is:
```text
User
 │
 │ 1:N
 ▼
Account
 │
 │ 1:N
 ▼
Transaction
```
## User
```text
id
name
email
phone
address
password_hash
```
## Account
```text
id
account_number
user_id
balance
created_at
```
## Transaction
```text
id
account_id
amount
merchant
location
transaction_type
timestamp
status
fraud_score
fraud_decision
model_version
model_threshold
created_at
```
Financial amounts use PostgreSQL NUMERIC/Python Decimal rather than binary floating-point representation.

# 🔄 Database Migrations
Alembic is used for database schema management.
Migration workflow:
```text
Model Change
     ↓
Alembic Revision
     ↓
Migration File
     ↓
alembic upgrade head
     ↓
PostgreSQL Schema
```
The Docker API startup also runs:
```text
alembic upgrade head
```
# 🐳 Docker Architecture
Docker Compose runs the main application components:
```text
Docker Compose
│
├── PostgreSQL
│      └── fraud_db
│
├── FastAPI
│      └── API :8000
│
└── Streamlit
       └── UI :8501
```
The Streamlit container communicates with FastAPI using the Docker Compose service name:
```text
http://api:8000
```
# ⚙️ Installation
## Prerequisites
Install:
- Python 3.11
- PostgreSQL
- Docker Desktop
- Git

## Clone Repository
```
git clone https://github.com/Ravi009033/Financial-Transaction-Fraud-Monitoring-Platform

cd fraud-detection-platform
```
## 🔧 Environment Variables
Create a .env file:
```
DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/fraud_db

TEST_DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/fraud_test_db

SECRET_KEY=your-secure-secret

ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30

FRAUD_REVIEW_THRESHOLD=0.33

FRAUD_BLOCK_THRESHOLD=0.70
```
## ▶️ Run Locally
Create a virtual environment:
```
python -m venv venv
```
Activate it on Windows:
```
venv\Scripts\activate
```
Install dependencies:
```
pip install -r requirements.txt
```
Run migrations:
```
alembic upgrade head
```
Start FastAPI:
```
uvicorn app.main:app --reload
```
API documentation:
```
http://localhost:8000/docs
```
Run Streamlit
```
streamlit run frontend/app.py
```
Open:
```
http://localhost:8501
```
## 🐳 Run With Docker
Build the application:
```
docker compose build
```
Start the services:
```
docker compose up
```
Services:
```
FastAPI:
http://localhost:8000

Swagger:
http://localhost:8000/docs

Streamlit:
http://localhost:8501
```
Stop services:
```
docker compose down
```
## 🧪 Run Tests
Run the complete test suite:
```
pytest -q
```
Run with coverage:
```
pytest --cov=app
```
# 🔌 Important API Endpoints
## Authentication
```
POST /auth/login
```
## Users
```
GET    /users
POST   /users
GET    /users/{user_id}
PUT    /users/{user_id}
DELETE /users/{user_id}
```
## Accounts
```
GET    /accounts
POST   /accounts
GET    /accounts/{account_id}
PUT    /accounts/{account_id}
DELETE /accounts/{account_id}
```
## Transactions
```
GET    /transactions/
POST   /transactions/
GET    /transactions/{transaction_id}
PUT    /transactions/{transaction_id}
DELETE /transactions/{transaction_id}
```
## Dashboard
```
GET /dashboard/summary

GET /dashboard/transaction-trends

GET /dashboard/fraud-distribution
```
## Machine Learning
```
POST /ml/predict

GET /ml/model-info

GET /ml/metrics
```

# ⚠️ Current Limitations
This project is production-oriented but is still a portfolio/learning implementation.
Current limitations include:
- Production ML model uses synthetic demonstration training data.
- No claim is made that the model represents real banking fraud performance.
- Distributed message processing has not been implemented.
- Kafka/message queues have not been implemented.
- Redis caching has not been implemented.
- Production model monitoring/drift detection has not been implemented.
- Large-scale distributed deployment has not been implemented.
- CI/CD pipeline is not part of the current implementation.
These are potential future extensions rather than existing functionality.

# 🔮 Future Improvements
Potential next steps include:
- Redis caching
- Kafka/event-driven transaction processing
- Dedicated ML inference service
- Model registry/version management
- Model drift monitoring
- Prometheus/Grafana monitoring
- Centralized structured logging
- Distributed tracing
- CI/CD with GitHub Actions
- Load balancing
- Database read replicas
- Database partitioning
- Cloud deployment
- Role-based access control
- Production-grade secrets management

# 📚 Technologies
## Backend
```
Python
FastAPI
Pydantic
SQLAlchemy
PostgreSQL
Alembic
JWT
bcrypt
```
## Machine Learning
```
Scikit-learn
XGBoost
Pandas
NumPy
SHAP
Joblib
```
## Frontend
```
Streamlit
Requests
```
## Testing
```
Pytest
Pytest-Cov
```
## DevOps
```
Docker
Docker Compose
```
# 🎯 Project Highlights
- End-to-end backend architecture using API → Service → Repository → ORM → Database
- JWT authentication and resource-level authorization
- PostgreSQL relational data model
- Real-time fraud scoring integrated into transaction processing
- XGBoost-based fraud detection
- Behavioral feature engineering
- Imbalanced classification evaluation
- SHAP model explainability
- Model version and threshold audit metadata
- Streamlit monitoring dashboard
- Automated API/service/ML/database tests
- 160 passing tests
- Dockerized multi-service application
- Alembic database migrations
## 👨‍💻 Author
Name - Ravi Kumar
Email - ravi009033@gmail.com
