"""
Emergency fix for Railway deployment issues
This script creates a minimal FastAPI app that bypasses database initialization
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create minimal FastAPI app
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

@app.get("/")
async def root():
    """Simple health check endpoint"""
    return {
        "status": "healthy", 
        "service": "Dino Ventures Wallet Service",
        "message": "Emergency deployment - database initialization bypassed"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "service": "Dino Ventures Wallet Service",
        "database": "bypassed for deployment"
    }

@app.get("/assets")
async def get_assets():
    """Mock assets endpoint"""
    return [
        {"id": 1, "name": "Gold Coins", "code": "GC", "description": "Primary in-game currency"},
        {"id": 2, "name": "Diamonds", "code": "DI", "description": "Premium currency"},
        {"id": 3, "name": "Loyalty Points", "code": "LP", "description": "Reward points"}
    ]

@app.get("/balance/{user_id}")
async def get_balance(user_id: str):
    """Mock balance endpoint"""
    return [
        {"wallet_id": 1, "user_id": user_id, "asset_name": "Gold Coins", "asset_code": "GC", "balance": "1000.00", "is_system": False},
        {"wallet_id": 2, "user_id": user_id, "asset_name": "Diamonds", "asset_code": "DI", "balance": "50.00", "is_system": False},
        {"wallet_id": 3, "user_id": user_id, "asset_name": "Loyalty Points", "asset_code": "LP", "balance": "500.00", "is_system": False}
    ]

@app.post("/transaction")
async def create_transaction(transaction_data: dict):
    """Mock transaction endpoint"""
    return {
        "transaction_id": "mock-txn-id",
        "transaction_type": transaction_data.get("transaction_type"),
        "amount": transaction_data.get("amount"),
        "asset_code": transaction_data.get("asset_code"),
        "status": "completed",
        "description": transaction_data.get("description"),
        "message": "Emergency deployment - transaction not processed"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
