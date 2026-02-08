"""
Wallet API endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import WalletBalanceResponse, TransactionResponse
from app.services.wallet_service import WalletService
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/wallets", tags=["Wallets"])


@router.get("/{user_id}/balance", response_model=WalletBalanceResponse)
async def get_wallet_balance(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all wallet balances for a user.
    
    Returns balances for all asset types the user has accounts for.
    Balances are calculated from ledger entries in real-time.
    
    - **user_id**: User identifier
    
    Returns:
    - user_id
    - balances: List of balances for each asset type
    - timestamp: Current timestamp
    """
    service = WalletService(db)
    balances = await service.get_all_balances(user_id)
    return balances


@router.get("/{user_id}/transactions", response_model=List[TransactionResponse])
async def get_transaction_history(
    user_id: str,
    limit: int = Query(50, ge=1, le=100, description="Maximum number of transactions to return"),
    offset: int = Query(0, ge=0, description="Number of transactions to skip"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get transaction history for a user.
    
    Returns a paginated list of transactions sorted by creation time (newest first).
    
    - **user_id**: User identifier
    - **limit**: Maximum number of results (1-100, default: 50)
    - **offset**: Number of results to skip (for pagination)
    
    Returns list of transactions.
    """
    service = TransactionService(db)
    transactions = await service.get_transaction_history(user_id, limit, offset)
    return transactions
