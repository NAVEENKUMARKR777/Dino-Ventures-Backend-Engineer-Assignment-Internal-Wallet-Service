from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select, text
from typing import List
import logging
import os

from app.database import get_db, engine
from app.models import Base, Asset, Wallet
from app.schemas import (
    TransactionRequest, TransactionResponse, BalanceResponse, 
    ErrorResponse, Asset as AssetSchema
)
from app.wallet_service import WalletService
from app.startup import initialize_database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Dino Ventures Wallet Service",
    description="Internal wallet service for gaming platforms",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("🚀 Starting Dino Ventures Wallet Service...")
    
    # Initialize database tables and seed data
    if initialize_database():
        logger.info("✅ Database initialization completed")
    else:
        logger.error("❌ Database initialization failed")
        # Don't raise exception to allow service to start for debugging

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Dino Ventures Wallet Service"}

@app.get("/assets", response_model=List[AssetSchema])
async def get_assets(db: Session = Depends(get_db)):
    """Get all available assets"""
    assets = db.execute(select(Asset)).scalars().all()
    return assets

@app.get("/balance/{user_id}", response_model=List[BalanceResponse])
async def get_user_balances(user_id: str, db: Session = Depends(get_db)):
    """Get all balances for a user"""
    wallet_service = WalletService(db)
    balances = wallet_service.get_all_user_balances(user_id)
    
    if not balances:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No balances found for user {user_id}"
        )
    
    return balances

@app.get("/balance/{user_id}/{asset_code}", response_model=BalanceResponse)
async def get_user_balance(user_id: str, asset_code: str, db: Session = Depends(get_db)):
    """Get user balance for a specific asset"""
    wallet_service = WalletService(db)
    balance = wallet_service.get_user_balance(user_id, asset_code)
    
    if not balance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No balance found for user {user_id} with asset {asset_code}"
        )
    
    return balance

@app.post("/transaction", response_model=TransactionResponse)
async def create_transaction(
    request: TransactionRequest, 
    db: Session = Depends(get_db)
):
    """Process a wallet transaction (topup, bonus, or purchase)"""
    wallet_service = WalletService(db)
    
    try:
        transaction, error = wallet_service.process_transaction(request)
        
        if error:
            logger.error(f"Transaction failed: {error}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )
        
        logger.info(f"Transaction processed: {transaction.transaction_id}")
        return transaction
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.get("/transaction/{user_id}/history")
async def get_transaction_history(
    user_id: str, 
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get transaction history for a user"""
    if limit <= 0 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be between 1 and 100"
        )
    
    wallet_service = WalletService(db)
    transactions = wallet_service.get_transaction_history(user_id, limit)
    
    return {
        "user_id": user_id,
        "transactions": transactions,
        "count": len(transactions)
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Detailed health check including database connectivity"""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "service": "Dino Ventures Wallet Service"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
