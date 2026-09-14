from app.db.database import Base, engine

# Import ALL models so SQLAlchemy registers their tables
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction


Base.metadata.create_all(bind=engine)