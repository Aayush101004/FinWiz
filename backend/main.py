import time
from typing import List

# Change imports from ".models" and ".services"
import models
import services
from database import Base, SessionLocal, engine
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

# This is a crucial addition for robust startup
# It ensures the application waits for the database to be ready
retries = 5
while retries > 0:
    try:
        # Create all tables in the database.
        Base.metadata.create_all(bind=engine)
        print("Database tables created/verified.")
        # Try to connect
        db = SessionLocal()
        db.execute(text('SELECT 1'))
        db.close()
        print("Database connection successful.")
        break # Exit the loop if connection is successful
    except OperationalError:
        print("Database connection failed. Retrying...")
        retries -= 1
        time.sleep(5) # Wait for 5 seconds before the next retry
if retries == 0:
    print("Could not connect to database after several attempts. Application might not work correctly.")


app = FastAPI(
    title="FinWiz API",
    description="API for managing personal finance transactions and getting AI-powered insights.",
    version="1.0.0"
)

# CORS (Cross-Origin Resource Sharing) middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins for simplicity, restrict in production
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)

# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/transactions", response_model=List[models.TransactionResponse])
def get_transactions(db: Session = Depends(get_db)):
    """
    Retrieve all financial transactions from the database.
    """
    # Query all transactions and return as list of TransactionResponse
    transactions = db.query(models.Transaction).all()
    return [models.TransactionResponse.from_orm(t) for t in transactions]


# Use the correct service function and model for categorization
@app.post("/categorize", response_model=models.CategorizationResult)
async def categorize_transaction(request: models.CategorizationRequest):
    """
    Uses the Gemini AI to categorize a transaction based on its description.
    """
    try:
        # Assuming the service returns a dict with keys: category, confidence
        result = await services.get_ai_categorization(request.description)
        return models.CategorizationResult(
            description=request.description,
            category=result['category'],
            confidence=result['confidence']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Use the correct service function and model for advice
@app.post("/transactions", response_model=models.TransactionResponse)
def create_transaction(transaction: models.TransactionCreate, db: Session = Depends(get_db)):
    """
    Create a new transaction in the database.
    """
    db_transaction = models.Transaction(
        date=transaction.date,
        description=transaction.description,
        amount=transaction.amount,
        category=transaction.category
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@app.post("/advice", response_model=models.AdviceResult)
async def get_financial_advice(request: models.AdviceRequest, db: Session = Depends(get_db)):
    """
    Provides AI-powered financial advice based on the user's recent transactions.
    """
    try:
        transactions = db.query(models.Transaction).all()
        # Convert to TransactionResponse for the service if needed
        txns = [models.TransactionResponse.from_orm(t) for t in transactions]
        # --- MODIFIED LINE ---
        advice = await services.get_financial_advice_from_ai(txns, request.prompt) # <-- Call the correct, powerful function
        return models.AdviceResult(advice=advice)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

