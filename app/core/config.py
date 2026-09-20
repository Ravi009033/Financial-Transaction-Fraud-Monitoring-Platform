from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    TEST_DATABASE_URL: str | None = None

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    FRAUD_REVIEW_THRESHOLD: float = 0.33
    FRAUD_BLOCK_THRESHOLD: float = 0.70

    class Config:
        env_file = ".env"


settings = Settings()