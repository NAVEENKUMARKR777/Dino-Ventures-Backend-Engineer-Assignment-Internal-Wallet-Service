import uuid
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select, update, and_
from sqlalchemy.exc import IntegrityError
from typing import Optional, Tuple

from app.models import Asset, Wallet, Transaction, LedgerEntry
from app.schemas import TransactionRequest, TransactionResponse, BalanceResponse
from app.database import get_db
from app.concurrency import deadlock_manager, IdempotencyManager, ConcurrencyControl

class WalletService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_balance(self, user_id: str, asset_code: str) -> Optional[BalanceResponse]:
        """Get user balance for a specific asset"""
        query = (
            select(Wallet, Asset)
            .join(Asset)
            .where(and_(Wallet.user_id == user_id, Asset.code == asset_code))
        )
        result = self.db.execute(query).first()
        
        if not result:
            return None
            
        wallet, asset = result
        return BalanceResponse(
            wallet_id=wallet.id,
            user_id=wallet.user_id,
            asset_name=asset.name,
            asset_code=asset.code,
            balance=wallet.balance,
            is_system=wallet.is_system
        )

    def get_all_user_balances(self, user_id: str) -> list[BalanceResponse]:
        """Get all balances for a user"""
        query = (
            select(Wallet, Asset)
            .join(Asset)
            .where(Wallet.user_id == user_id)
        )
        results = self.db.execute(query).all()
        
        balances = []
        for wallet, asset in results:
            balances.append(BalanceResponse(
                wallet_id=wallet.id,
                user_id=wallet.user_id,
                asset_name=asset.name,
                asset_code=asset.code,
                balance=wallet.balance,
                is_system=wallet.is_system
            ))
        return balances

    def _get_or_create_wallet(self, user_id: str, asset_id: int, is_system: bool = False) -> Wallet:
        """Get existing wallet or create new one"""
        wallet = self.db.execute(
            select(Wallet).where(
                and_(Wallet.user_id == user_id, Wallet.asset_id == asset_id)
            )
        ).scalar_one_or_none()
        
        if not wallet:
            wallet = Wallet(
                user_id=user_id,
                asset_id=asset_id,
                balance=Decimal('0'),
                is_system=is_system
            )
            self.db.add(wallet)
            self.db.flush()  # Get the ID without committing
        return wallet

    def _lock_wallets(self, debit_wallet_id: int, credit_wallet_id: int):
        """Lock wallets for concurrent access (pessimistic locking)"""
        self.db.execute(
            select(Wallet)
            .where(Wallet.id.in_([debit_wallet_id, credit_wallet_id]))
            .with_for_update()
        )

    def _create_ledger_entry(self, transaction: Transaction, debit_wallet: Wallet, credit_wallet: Wallet):
        """Create ledger entry with balance snapshots"""
        ledger_entry = LedgerEntry(
            transaction_id=transaction.id,
            asset_id=transaction.asset_id,
            debit_wallet_id=debit_wallet.id,
            credit_wallet_id=credit_wallet.id,
            amount=transaction.amount,
            debit_balance_before=debit_wallet.balance + transaction.amount,  # Before debit
            debit_balance_after=debit_wallet.balance,                        # After debit
            credit_balance_before=credit_wallet.balance - transaction.amount, # Before credit
            credit_balance_after=credit_wallet.balance                       # After credit
        )
        self.db.add(ledger_entry)

    def process_transaction(self, request: TransactionRequest) -> Tuple[Optional[TransactionResponse], Optional[str]]:
        """Process a transaction with full ACID compliance, idempotency, and deadlock avoidance"""
        concurrency_control = ConcurrencyControl(max_retries=3)
        idempotency_manager = IdempotencyManager(self.db)
        
        def execute_transaction():
            try:
                # Get asset
                asset = self.db.execute(
                    select(Asset).where(Asset.code == request.asset_code)
                ).scalar_one_or_none()
                
                if not asset:
                    return None, f"Asset with code '{request.asset_code}' not found"

                # Check for idempotency
                if request.idempotency_key:
                    if not idempotency_manager.check_and_mark_idempotency(request.idempotency_key):
                        # Return existing transaction
                        existing_transaction = idempotency_manager.get_existing_transaction(request.idempotency_key)
                        if existing_transaction:
                            return TransactionResponse(
                                transaction_id=existing_transaction.transaction_id,
                                transaction_type=existing_transaction.transaction_type,
                                amount=existing_transaction.amount,
                                asset_code=request.asset_code,
                                status=existing_transaction.status,
                                description=existing_transaction.description,
                                created_at=existing_transaction.created_at,
                                processed_at=existing_transaction.processed_at
                            ), None
                        else:
                            return None, "Idempotency key conflict"

                # Determine wallets based on transaction type
                if request.transaction_type == 'topup':
                    # System treasury -> User wallet
                    debit_wallet = self._get_or_create_wallet('system_treasury', asset.id, is_system=True)
                    credit_wallet = self._get_or_create_wallet(request.user_id, asset.id, is_system=False)
                elif request.transaction_type == 'bonus':
                    # System treasury -> User wallet
                    debit_wallet = self._get_or_create_wallet('system_treasury', asset.id, is_system=True)
                    credit_wallet = self._get_or_create_wallet(request.user_id, asset.id, is_system=False)
                elif request.transaction_type == 'purchase':
                    # User wallet -> System treasury
                    debit_wallet = self._get_or_create_wallet(request.user_id, asset.id, is_system=False)
                    credit_wallet = self._get_or_create_wallet('system_treasury', asset.id, is_system=True)
                    
                    # Check if user has sufficient balance for purchases
                    if debit_wallet.balance < request.amount:
                        return None, "Insufficient balance for purchase"
                else:
                    return None, f"Invalid transaction type: {request.transaction_type}"

                # Use deadlock avoidance manager to lock wallets in consistent order
                with deadlock_manager.acquire_wallets_locks([debit_wallet.id, credit_wallet.id]):
                    # Re-fetch wallets within the lock to ensure we have the latest data
                    debit_wallet = self.db.execute(
                        select(Wallet).where(Wallet.id == debit_wallet.id)
                    ).scalar_one()
                    
                    credit_wallet = self.db.execute(
                        select(Wallet).where(Wallet.id == credit_wallet.id)
                    ).scalar_one()

                    # Double-check balance for purchase transactions
                    if request.transaction_type == 'purchase' and debit_wallet.balance < request.amount:
                        return None, "Insufficient balance for purchase"

                    # Create transaction record
                    transaction = Transaction(
                        transaction_id=str(uuid.uuid4()),
                        transaction_type=request.transaction_type,
                        amount=request.amount,
                        asset_id=asset.id,
                        debit_wallet_id=debit_wallet.id,
                        credit_wallet_id=credit_wallet.id,
                        description=request.description,
                        idempotency_key=request.idempotency_key,
                        status='completed'
                    )
                    self.db.add(transaction)
                    self.db.flush()  # Get the transaction ID

                    # Update wallet balances
                    debit_wallet.balance -= request.amount
                    credit_wallet.balance += request.amount

                    # Create ledger entry
                    self._create_ledger_entry(transaction, debit_wallet, credit_wallet)

                    return TransactionResponse(
                        transaction_id=transaction.transaction_id,
                        transaction_type=transaction.transaction_type,
                        amount=transaction.amount,
                        asset_code=request.asset_code,
                        status=transaction.status,
                        description=transaction.description,
                        created_at=transaction.created_at,
                        processed_at=transaction.processed_at
                    ), None

            except IntegrityError as e:
                self.db.rollback()
                raise Exception(f"Database integrity error: {str(e)}")
            except Exception as e:
                raise Exception(f"Transaction processing error: {str(e)}")

        try:
            # Execute with automatic retry for deadlock scenarios
            return concurrency_control.execute_with_retry(execute_transaction)
        except Exception as e:
            return None, str(e)

    def get_transaction_history(self, user_id: str, limit: int = 50) -> list[Transaction]:
        """Get transaction history for a user"""
        query = (
            select(Transaction)
            .join(Wallet, Transaction.debit_wallet_id == Wallet.id)
            .where(Wallet.user_id == user_id)
            .order_by(Transaction.created_at.desc())
            .limit(limit)
        )
        return self.db.execute(query).scalars().all()

    def get_wallet_by_id(self, wallet_id: int) -> Optional[Wallet]:
        """Get wallet by ID"""
        return self.db.execute(
            select(Wallet).where(Wallet.id == wallet_id)
        ).scalar_one_or_none()
