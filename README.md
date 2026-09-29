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
