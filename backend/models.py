from datetime import date  # Import the date type

from database import Base
from pydantic import BaseModel
from sqlalchemy import Column, Date, Float, Integer, String


# SQLAlchemy Model for the database table
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    description = Column(String, index=True)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=True)

# Pydantic Model for API responses

class TransactionResponse(BaseModel):
    id: int
    date: date
    description: str
    amount: float
    category: str | None = None

    class Config:
        from_attributes = True


# Add Pydantic models for categorization and advice endpoints if not present
class CategorizationRequest(BaseModel):
    description: str

class CategorizationResult(BaseModel):
    description: str
    category: str
    confidence: float

class AdviceRequest(BaseModel):
    prompt: str

class AdviceResult(BaseModel):
    advice: str

class TransactionCreate(BaseModel):
    date: date
    description: str
    amount: float
    category: str | None = None
