"""
User management endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.account import Account, AccountType
from app.schemas import AccountResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=List[dict])
async def list_users(
    db: AsyncSession = Depends(get_db)
):
    """
    List all users in the system.
    
    Returns a list of unique user IDs with their account count.
    System accounts are excluded from the list.
    """
    result = await db.execute(
        select(Account.user_id, func.count(Account.id).label('account_count'))
        .where(Account.account_type == AccountType.USER)
        .group_by(Account.user_id)
    )
    
    users = []
    for row in result:
        users.append({
            "user_id": row.user_id,
            "account_count": row.account_count
        })
    
    return users


@router.get("/{user_id}/accounts", response_model=List[AccountResponse])
async def get_user_accounts(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all accounts for a specific user.
    
    - **user_id**: User identifier
    
    Returns list of accounts with their details.
    """
    result = await db.execute(
        select(Account).where(Account.user_id == user_id)
    )
    accounts = result.scalars().all()
    return accounts
