"""
Transaction API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import (
    TopupRequest, BonusRequest, SpendRequest,
    TransactionResponse, ErrorResponse
)
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/topup", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def topup_wallet(
    request: TopupRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    **Wallet Top-up (Purchase)**
    
    User purchases credits with real money. Assumes a fully working payment system.
    
    - **user_id**: User identifier
    - **asset_type**: Currency type (GOLD_COINS, DIAMONDS, LOYALTY_POINTS)
    - **amount**: Amount to add (must be positive)
    - **idempotency_key**: Unique key to prevent duplicate transactions
    - **metadata**: Optional payment information (payment_id, payment_method, etc.)
    
    Returns the completed transaction with ledger entries.
    """
    try:
        service = TransactionService(db)
        transaction = await service.execute_topup(
            user_id=request.user_id,
            asset_type_code=request.asset_type,
            amount=request.amount,
            idempotency_key=request.idempotency_key,
            metadata=request.metadata
        )
        return transaction
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/bonus", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def issue_bonus(
    request: BonusRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    **Bonus/Incentive**
    
    System issues free credits to user (referral bonus, promotion, achievement reward, etc.)
    
    - **user_id**: User identifier
    - **asset_type**: Currency type (GOLD_COINS, DIAMONDS, LOYALTY_POINTS)
    - **amount**: Bonus amount (must be positive)
    - **idempotency_key**: Unique key to prevent duplicate bonuses
    - **metadata**: Optional bonus information (reason, referral_code, achievement_id, etc.)
    
    Returns the completed transaction with ledger entries.
    """
    try:
        service = TransactionService(db)
        transaction = await service.execute_bonus(
            user_id=request.user_id,
            asset_type_code=request.asset_type,
            amount=request.amount,
            idempotency_key=request.idempotency_key,
            metadata=request.metadata
        )
        return transaction
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/spend", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def spend_credits(
    request: SpendRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    **Purchase/Spend**
    
    User spends credits to purchase in-app items or services.
    
    - **user_id**: User identifier
    - **asset_type**: Currency type (GOLD_COINS, DIAMONDS, LOYALTY_POINTS)
    - **amount**: Amount to spend (must be positive and <= current balance)
    - **idempotency_key**: Unique key to prevent duplicate purchases
    - **metadata**: Optional purchase information (item_id, item_name, quantity, etc.)
    
    Returns the completed transaction with ledger entries.
    Raises 400 error if insufficient balance.
    """
    try:
        service = TransactionService(db)
        transaction = await service.execute_spend(
            user_id=request.user_id,
            asset_type_code=request.asset_type,
            amount=request.amount,
            idempotency_key=request.idempotency_key,
            metadata=request.metadata
        )
        return transaction
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get details of a specific transaction by ID.
    
    - **transaction_id**: Transaction ID
    
    Returns the transaction details.
    """
    service = TransactionService(db)
    transaction = await service.get_transaction_by_id(transaction_id)
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction {transaction_id} not found"
        )
    
    return transaction
