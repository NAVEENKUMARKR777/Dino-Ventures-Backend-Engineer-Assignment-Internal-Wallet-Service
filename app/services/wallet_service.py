"""
Wallet Service - Handles wallet operations and balance queries.
"""
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account, AccountType
from app.models.asset_type import AssetType
from app.models.ledger import LedgerEntry, EntryType
from app.schemas import BalanceDetail, WalletBalanceResponse


class WalletService:
    """Service for wallet operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_or_create_account(
        self, 
        user_id: str, 
        asset_type_code: str,
        account_type: AccountType = AccountType.USER
    ) -> Account:
        """
        Get or create an account for a user and asset type.
        
        Args:
            user_id: User identifier
            asset_type_code: Asset type code
            account_type: Type of account (USER or SYSTEM)
            
        Returns:
            Account instance
        """
        # Try to find existing account
        result = await self.db.execute(
            select(Account).where(
                Account.user_id == user_id,
                Account.asset_type_code == asset_type_code
            )
        )
        account = result.scalar_one_or_none()
        
        if account:
            return account
        
        # Create new account
        account_id = f"{user_id}_{asset_type_code}"
        account = Account(
            id=account_id,
            user_id=user_id,
            asset_type_code=asset_type_code,
            account_type=account_type,
        )
        self.db.add(account)
        await self.db.flush()
        
        return account
    
    async def get_balance(self, user_id: str, asset_type_code: str) -> Decimal:
        """
        Calculate balance for a user's account using ledger entries.
        
        Balance = Sum(Debits) - Sum(Credits)
        
        Args:
            user_id: User identifier
            asset_type_code: Asset type code
            
        Returns:
            Current balance
        """
        # Get account
        result = await self.db.execute(
            select(Account).where(
                Account.user_id == user_id,
                Account.asset_type_code == asset_type_code
            )
        )
        account = result.scalar_one_or_none()
        
        if not account:
            return Decimal("0.00")
        
        # Calculate balance from ledger entries
        # Debit entries increase balance
        debit_result = await self.db.execute(
            select(func.coalesce(func.sum(LedgerEntry.amount), 0))
            .where(
                LedgerEntry.debit_account_id == account.id,
                LedgerEntry.entry_type == EntryType.DEBIT
            )
        )
        total_debits = Decimal(str(debit_result.scalar() or 0))
        
        # Credit entries decrease balance
        credit_result = await self.db.execute(
            select(func.coalesce(func.sum(LedgerEntry.amount), 0))
            .where(
                LedgerEntry.credit_account_id == account.id,
                LedgerEntry.entry_type == EntryType.CREDIT
            )
        )
        total_credits = Decimal(str(credit_result.scalar() or 0))
        
        balance = total_debits - total_credits
        return balance
    
    async def get_all_balances(self, user_id: str) -> WalletBalanceResponse:
        """
        Get all balances for a user across all asset types.
        
        Args:
            user_id: User identifier
            
        Returns:
            Wallet balance response with all balances
        """
        # Get all accounts for user
        result = await self.db.execute(
            select(Account).where(Account.user_id == user_id)
        )
        accounts = result.scalars().all()
        
        balances = []
        for account in accounts:
            balance = await self.get_balance(user_id, account.asset_type_code)
            balances.append(
                BalanceDetail(
                    asset_type=account.asset_type_code,
                    balance=balance,
                    account_id=account.id
                )
            )
        
        return WalletBalanceResponse(
            user_id=user_id,
            balances=balances
        )
    
    async def lock_accounts(self, account_ids: List[str]) -> List[Account]:
        """
        Lock accounts in a consistent order to prevent deadlocks.
        
        Always locks accounts in alphabetical order by ID to ensure
        consistent lock acquisition order across all transactions.
        
        Args:
            account_ids: List of account IDs to lock
            
        Returns:
            List of locked accounts
        """
        # Sort account IDs to ensure consistent lock order
        sorted_ids = sorted(account_ids)
        
        locked_accounts = []
        for account_id in sorted_ids:
            result = await self.db.execute(
                select(Account)
                .where(Account.id == account_id)
                .with_for_update()  # Row-level lock
            )
            account = result.scalar_one_or_none()
            if account:
                locked_accounts.append(account)
        
        return locked_accounts
