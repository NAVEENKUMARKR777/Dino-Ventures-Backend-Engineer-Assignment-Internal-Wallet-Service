"""
Transaction Service - Handles all transaction operations with double-entry ledger.
"""
from decimal import Decimal
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.models.ledger import LedgerEntry, EntryType
from app.models.account import AccountType
from app.services.wallet_service import WalletService


class TransactionService:
    """Service for handling transactions with double-entry bookkeeping."""
    
    # System treasury account ID
    SYSTEM_TREASURY_USER_ID = "SYSTEM_TREASURY"
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.wallet_service = WalletService(db)
    
    async def check_idempotency(self, idempotency_key: str) -> Optional[Transaction]:
        """
        Check if a transaction with this idempotency key already exists.
        
        Args:
            idempotency_key: Unique idempotency key
            
        Returns:
            Existing transaction or None
        """
        result = await self.db.execute(
            select(Transaction).where(
                Transaction.idempotency_key == idempotency_key
            )
        )
        return result.scalar_one_or_none()
    
    async def create_double_entry(
        self,
        transaction: Transaction,
        debit_account_id: str,
        credit_account_id: str,
        amount: Decimal,
        asset_type_code: str
    ):
        """
        Create double-entry ledger entries.
        
        Debit Entry: Increases the debit account balance
        Credit Entry: Decreases the credit account balance
        
        Args:
            transaction: Transaction record
            debit_account_id: Account receiving funds (balance increases)
            credit_account_id: Account sending funds (balance decreases)
            amount: Transaction amount
            asset_type_code: Asset type code
        """
        # Create DEBIT entry (increases balance)
        debit_entry = LedgerEntry(
            transaction_id=transaction.id,
            entry_type=EntryType.DEBIT,
            debit_account_id=debit_account_id,
            credit_account_id=credit_account_id,
            asset_type_code=asset_type_code,
            amount=amount
        )
        
        # Create CREDIT entry (decreases balance)
        credit_entry = LedgerEntry(
            transaction_id=transaction.id,
            entry_type=EntryType.CREDIT,
            debit_account_id=debit_account_id,
            credit_account_id=credit_account_id,
            asset_type_code=asset_type_code,
            amount=amount
        )
        
        self.db.add(debit_entry)
        self.db.add(credit_entry)
    
    async def execute_topup(
        self,
        user_id: str,
        asset_type_code: str,
        amount: Decimal,
        idempotency_key: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Transaction:
        """
        Execute a wallet top-up transaction.
        
        User purchases credits with real money.
        Funds flow: System Treasury -> User Account
        
        Args:
            user_id: User identifier
            asset_type_code: Asset type code
            amount: Amount to top up
            idempotency_key: Unique key for idempotency
            metadata: Additional metadata
            
        Returns:
            Completed transaction
        """
        # Check idempotency
        existing = await self.check_idempotency(idempotency_key)
        if existing:
            return existing
        
        # Get or create accounts
        user_account = await self.wallet_service.get_or_create_account(
            user_id, asset_type_code, AccountType.USER
        )
        system_account = await self.wallet_service.get_or_create_account(
            self.SYSTEM_TREASURY_USER_ID, asset_type_code, AccountType.SYSTEM
        )
        
        # Lock accounts in consistent order
        await self.wallet_service.lock_accounts([user_account.id, system_account.id])
        
        # Create transaction record
        transaction = Transaction(
            transaction_type=TransactionType.TOPUP,
            status=TransactionStatus.PENDING,
            user_id=user_id,
            asset_type_code=asset_type_code,
            amount=amount,
            description=f"Wallet top-up for {user_id}",
            extra_data=metadata,
            idempotency_key=idempotency_key
        )
        self.db.add(transaction)
        await self.db.flush()
        
        # Create double-entry ledger entries
        # Debit: User account (increases balance)
        # Credit: System account (decreases system balance)
        await self.create_double_entry(
            transaction=transaction,
            debit_account_id=user_account.id,
            credit_account_id=system_account.id,
            amount=amount,
            asset_type_code=asset_type_code
        )
        
        # Mark transaction as completed
        transaction.status = TransactionStatus.COMPLETED
        await self.db.flush()
        
        return transaction
    
    async def execute_bonus(
        self,
        user_id: str,
        asset_type_code: str,
        amount: Decimal,
        idempotency_key: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Transaction:
        """
        Execute a bonus/incentive transaction.
        
        System issues free credits to user (referral bonus, promotion, etc.)
        Funds flow: System Treasury -> User Account
        
        Args:
            user_id: User identifier
            asset_type_code: Asset type code
            amount: Bonus amount
            idempotency_key: Unique key for idempotency
            metadata: Additional metadata (reason, referral code, etc.)
            
        Returns:
            Completed transaction
        """
        # Check idempotency
        existing = await self.check_idempotency(idempotency_key)
        if existing:
            return existing
        
        # Get or create accounts
        user_account = await self.wallet_service.get_or_create_account(
            user_id, asset_type_code, AccountType.USER
        )
        system_account = await self.wallet_service.get_or_create_account(
            self.SYSTEM_TREASURY_USER_ID, asset_type_code, AccountType.SYSTEM
        )
        
        # Lock accounts in consistent order
        await self.wallet_service.lock_accounts([user_account.id, system_account.id])
        
        # Create transaction record
        transaction = Transaction(
            transaction_type=TransactionType.BONUS,
            status=TransactionStatus.PENDING,
            user_id=user_id,
            asset_type_code=asset_type_code,
            amount=amount,
            description=f"Bonus credit for {user_id}",
            extra_data=metadata,
            idempotency_key=idempotency_key
        )
        self.db.add(transaction)
        await self.db.flush()
        
        # Create double-entry ledger entries
        await self.create_double_entry(
            transaction=transaction,
            debit_account_id=user_account.id,
            credit_account_id=system_account.id,
            amount=amount,
            asset_type_code=asset_type_code
        )
        
        # Mark transaction as completed
        transaction.status = TransactionStatus.COMPLETED
        await self.db.flush()
        
        return transaction
    
    async def execute_spend(
        self,
        user_id: str,
        asset_type_code: str,
        amount: Decimal,
        idempotency_key: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Transaction:
        """
        Execute a spend transaction.
        
        User spends credits to purchase in-app items/services.
        Funds flow: User Account -> System Treasury
        
        Args:
            user_id: User identifier
            asset_type_code: Asset type code
            amount: Amount to spend
            idempotency_key: Unique key for idempotency
            metadata: Additional metadata (item_id, item_name, etc.)
            
        Returns:
            Completed transaction
            
        Raises:
            ValueError: If insufficient balance
        """
        # Check idempotency
        existing = await self.check_idempotency(idempotency_key)
        if existing:
            return existing
        
        # Get or create accounts
        user_account = await self.wallet_service.get_or_create_account(
            user_id, asset_type_code, AccountType.USER
        )
        system_account = await self.wallet_service.get_or_create_account(
            self.SYSTEM_TREASURY_USER_ID, asset_type_code, AccountType.SYSTEM
        )
        
        # Lock accounts in consistent order
        await self.wallet_service.lock_accounts([user_account.id, system_account.id])
        
        # Check balance
        current_balance = await self.wallet_service.get_balance(user_id, asset_type_code)
        if current_balance < amount:
            raise ValueError(
                f"Insufficient balance. Current: {current_balance}, Required: {amount}"
            )
        
        # Create transaction record
        transaction = Transaction(
            transaction_type=TransactionType.SPEND,
            status=TransactionStatus.PENDING,
            user_id=user_id,
            asset_type_code=asset_type_code,
            amount=amount,
            description=f"Purchase by {user_id}",
            extra_data=metadata,
            idempotency_key=idempotency_key
        )
        self.db.add(transaction)
        await self.db.flush()
        
        # Create double-entry ledger entries
        # Debit: System account (increases system balance)
        # Credit: User account (decreases user balance)
        await self.create_double_entry(
            transaction=transaction,
            debit_account_id=system_account.id,
            credit_account_id=user_account.id,
            amount=amount,
            asset_type_code=asset_type_code
        )
        
        # Mark transaction as completed
        transaction.status = TransactionStatus.COMPLETED
        await self.db.flush()
        
        return transaction
    
    async def get_transaction_history(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Transaction]:
        """
        Get transaction history for a user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of transactions to return
            offset: Number of transactions to skip
            
        Returns:
            List of transactions
        """
        result = await self.db.execute(
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .order_by(Transaction.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
    
    async def get_transaction_by_id(self, transaction_id: str) -> Optional[Transaction]:
        """Get a specific transaction by ID."""
        result = await self.db.execute(
            select(Transaction).where(Transaction.id == transaction_id)
        )
        return result.scalar_one_or_none()
