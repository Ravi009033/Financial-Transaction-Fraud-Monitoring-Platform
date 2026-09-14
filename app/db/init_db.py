from app.models.transaction import Transaction
from app.models.user import User
from app.models.account import Account
from app.db.database import Base, engine

Base.metadata.create_all(engine)