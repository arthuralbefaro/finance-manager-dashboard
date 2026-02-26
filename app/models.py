from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True)
    password = Column(String(255))

    transactions = relationship("Transaction", back_populates="owner")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String(200))
    category = Column(String(100))
    amount = Column(Float)
    type = Column(String(50))
    date = Column(Date)

    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="transactions")