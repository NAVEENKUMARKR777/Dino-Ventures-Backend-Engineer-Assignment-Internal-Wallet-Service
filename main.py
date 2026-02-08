"""
Dino Ventures Internal Wallet Service - Production Ready
A complete wallet service with database integration for Railway deployment
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import logging
import sqlite3
from decimal import Decimal
import uuid
from datetime import datetime

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

# Database setup (SQLite for simplicity on Railway)
def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect('wallet_service.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL,
            description TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wallets (
            id INTEGER PRIMARY KEY,
            user_id TEXT NOT NULL,
            asset_id INTEGER NOT NULL,
            balance TEXT DEFAULT '0.00',
            is_system BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (asset_id) REFERENCES assets (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY,
            transaction_id TEXT UNIQUE NOT NULL,
            transaction_type TEXT NOT NULL,
            amount TEXT NOT NULL,
            asset_id INTEGER NOT NULL,
            debit_wallet_id INTEGER NOT NULL,
            credit_wallet_id INTEGER NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'completed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (asset_id) REFERENCES assets (id),
            FOREIGN KEY (debit_wallet_id, credit_wallet_id) REFERENCES wallets (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ledger_entries (
            id INTEGER PRIMARY KEY,
            transaction_id INTEGER NOT NULL,
            asset_id INTEGER NOT NULL,
            debit_wallet_id INTEGER NOT NULL,
            credit_wallet_id INTEGER NOT NULL,
            amount TEXT NOT NULL,
            debit_balance_before TEXT NOT NULL,
            debit_balance_after TEXT NOT NULL,
            credit_balance_before TEXT NOT NULL,
            credit_balance_after TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (transaction_id) REFERENCES transactions (id),
            FOREIGN KEY (asset_id) REFERENCES assets (id),
            FOREIGN KEY (debit_wallet_id, credit_wallet_id) REFERENCES wallets (id)
        )
    ''')
    
    # Seed data
    cursor.execute("SELECT COUNT(*) FROM assets")
    if cursor.fetchone()[0] == 0:
        # Insert assets
        assets = [
            (1, "Gold Coins", "GC", "Primary in-game currency for purchases"),
            (2, "Diamonds", "DI", "Premium currency for exclusive items"),
            (3, "Loyalty Points", "LP", "Reward points for user engagement")
        ]
        cursor.executemany("INSERT INTO assets (id, name, code, description) VALUES (?, ?, ?, ?)", assets)
        
        # Insert system treasury wallets
        system_wallets = [
            (1, "system_treasury", 1, "1000000.00", True),
            (2, "system_treasury", 2, "100000.00", True),
            (3, "system_treasury", 3, "500000.00", True)
        ]
        cursor.executemany("INSERT INTO wallets (id, user_id, asset_id, balance, is_system) VALUES (?, ?, ?, ?, ?)", system_wallets)
        
        # Insert user wallets
        user_wallets = [
            (4, "user_001", 1, "1000.00", False),
            (5, "user_001", 2, "50.00", False),
            (6, "user_001", 3, "500.00", False),
            (7, "user_002", 1, "500.00", False),
            (8, "user_002", 2, "25.00", False),
            (9, "user_002", 3, "250.00", False)
        ]
        cursor.executemany("INSERT INTO wallets (id, user_id, asset_id, balance, is_system) VALUES (?, ?, ?, ?, ?)", user_wallets)
        
        logger.info("Database seeded with initial data")
    
    conn.commit()
    conn.close()
    return sqlite3.connect('wallet_service.db')

# Pydantic models
class Asset(BaseModel):
    id: int
    name: str
    code: str
    description: str

class Balance(BaseModel):
    wallet_id: int
    user_id: str
    asset_name: str
    asset_code: str
    balance: str
    is_system: bool

class TransactionRequest(BaseModel):
    transaction_type: str = Field(..., pattern="^(topup|bonus|purchase)$")
    user_id: str
    asset_code: str
    amount: float = Field(..., gt=0)
    description: Optional[str] = None
    idempotency_key: Optional[str] = None

class TransactionResponse(BaseModel):
    transaction_id: str
    transaction_type: str
    amount: float
    asset_code: str
    status: str
    description: Optional[str] = None
    created_at: datetime
    processed_at: Optional[datetime] = None

# Initialize database
db = init_db()

def get_db():
    """Get database connection"""
    return db

# Health check endpoints
@app.get("/")
async def root():
    """Root health check"""
    return {"status": "healthy", "service": "Dino Ventures Wallet Service"}

@app.get("/health")
async def health():
    """Detailed health check"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        return {
            "status": "healthy",
            "database": "connected",
            "service": "Dino Ventures Wallet Service",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Database connection failed")

# Asset endpoints
@app.get("/assets", response_model=List[Asset])
async def get_assets():
    """Get all available assets"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, code, description FROM assets")
    assets = [{"id": row[0], "name": row[1], "code": row[2], "description": row[3]} for row in cursor.fetchall()]
    conn.close()
    return assets

# Balance endpoints
@app.get("/balance/{user_id}", response_model=List[Balance])
async def get_user_balances(user_id: str):
    """Get all balances for a user"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT w.id, w.user_id, a.name, a.code, w.balance, w.is_system 
        FROM wallets w 
        JOIN assets a ON w.asset_id = a.id 
        WHERE w.user_id = ? AND w.is_system = FALSE
    ''', (user_id,))
    
    balances = [
        {
            "wallet_id": row[0],
            "user_id": row[1],
            "asset_name": row[2],
            "asset_code": row[3],
            "balance": row[4],
            "is_system": bool(row[5])
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    
    if not balances:
        raise HTTPException(status_code=404, detail=f"No balances found for user {user_id}")
    
    return balances

# Transaction endpoints
@app.post("/transaction", response_model=TransactionResponse)
async def create_transaction(transaction: TransactionRequest):
    """Process a wallet transaction"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Get asset
        cursor.execute("SELECT id FROM assets WHERE code = ?", (transaction.asset_code,))
        asset = cursor.fetchone()
        if not asset:
            raise HTTPException(status_code=400, detail=f"Asset {transaction.asset_code} not found")
        
        asset_id = asset[0]
        
        # Get wallets
        if transaction.transaction_type in ['topup', 'bonus']:
            # System -> User
            cursor.execute("SELECT id, balance FROM wallets WHERE user_id = 'system_treasury' AND asset_id = ?", (asset_id,))
            debit_wallet = cursor.fetchone()
            cursor.execute("SELECT id, balance FROM wallets WHERE user_id = ? AND asset_id = ?", (transaction.user_id, asset_id))
            credit_wallet = cursor.fetchone()
        else:  # purchase
            # User -> System
            cursor.execute("SELECT id, balance FROM wallets WHERE user_id = ? AND asset_id = ?", (transaction.user_id, asset_id))
            debit_wallet = cursor.fetchone()
            cursor.execute("SELECT id, balance FROM wallets WHERE user_id = 'system_treasury' AND asset_id = ?", (asset_id,))
            credit_wallet = cursor.fetchone()
        
        if not debit_wallet or not credit_wallet:
            raise HTTPException(status_code=400, detail="Wallet not found")
        
        # Check balance for purchase
        if transaction.transaction_type == 'purchase':
            if Decimal(debit_wallet[1]) < Decimal(str(transaction.amount)):
                raise HTTPException(status_code=400, detail="Insufficient balance")
        
        # Process transaction
        transaction_id = str(uuid.uuid4())
        created_at = datetime.now()
        
        # Insert transaction
        cursor.execute('''
            INSERT INTO transactions (transaction_id, transaction_type, amount, asset_id, debit_wallet_id, credit_wallet_id, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (transaction_id, transaction.transaction_type, str(transaction.amount), asset_id, debit_wallet[0], credit_wallet[0], transaction.description, created_at))
        
        # Update balances
        new_debit_balance = Decimal(debit_wallet[1]) - Decimal(str(transaction.amount))
        new_credit_balance = Decimal(credit_wallet[1]) + Decimal(str(transaction.amount))
        
        cursor.execute("UPDATE wallets SET balance = ? WHERE id = ?", (str(new_debit_balance), debit_wallet[0]))
        cursor.execute("UPDATE wallets SET balance = ? WHERE id = ?", (str(new_credit_balance), credit_wallet[0]))
        
        # Insert ledger entry
        cursor.execute('''
            INSERT INTO ledger_entries (transaction_id, asset_id, debit_wallet_id, credit_wallet_id, amount, debit_balance_before, debit_balance_after, credit_balance_before, credit_balance_after, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (cursor.lastrowid, asset_id, debit_wallet[0], credit_wallet[0], str(transaction.amount), debit_wallet[1], str(new_debit_balance), credit_wallet[1], str(new_credit_balance), created_at))
        
        conn.commit()
        logger.info(f"Processed {transaction.transaction_type} transaction: {transaction_id}")
        
        return TransactionResponse(
            transaction_id=transaction_id,
            transaction_type=transaction.transaction_type,
            amount=transaction.amount,
            asset_code=transaction.asset_code,
            status="completed",
            description=transaction.description,
            created_at=created_at,
            processed_at=created_at
        )
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Transaction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/transaction/{user_id}/history")
async def get_transaction_history(user_id: str, limit: int = 50):
    """Get transaction history for a user"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT t.transaction_id, t.transaction_type, t.amount, a.code, t.debit_wallet_id, t.credit_wallet_id, t.description, t.created_at
        FROM transactions t
        JOIN assets a ON t.asset_id = a.id
        JOIN wallets w ON (t.debit_wallet_id = w.id OR t.credit_wallet_id = w.id)
        WHERE w.user_id = ?
        ORDER BY t.created_at DESC
        LIMIT ?
    ''', (user_id, limit))
    
    transactions = [
        {
            "transaction_id": row[0],
            "transaction_type": row[1],
            "amount": float(row[2]),
            "debit_wallet_id": row[3],
            "credit_wallet_id": row[4],
            "description": row[5],
            "created_at": row[6]
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    
    return {
        "user_id": user_id,
        "transactions": transactions,
        "count": len(transactions)
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting Dino Ventures Wallet Service on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
