import time
import threading
from contextlib import contextmanager
from typing import Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import Wallet

class DeadlockAvoidanceManager:
    """
    Deadlock avoidance using ordered locking strategy.
    Always acquire locks in a consistent order to prevent deadlocks.
    """
    
    def __init__(self):
        self._lock = threading.Lock()
        self._wallet_locks: Dict[int, threading.Lock] = {}
    
    def get_wallet_lock(self, wallet_id: int) -> threading.Lock:
        """Get or create a lock for a specific wallet"""
        with self._lock:
            if wallet_id not in self._wallet_locks:
                self._wallet_locks[wallet_id] = threading.Lock()
            return self._wallet_locks[wallet_id]
    
    @contextmanager
    def acquire_wallets_locks(self, wallet_ids: list[int]):
        """
        Acquire locks for multiple wallets in a consistent order (ascending)
        to prevent deadlocks.
        """
        # Sort wallet IDs to ensure consistent locking order
        sorted_wallet_ids = sorted(wallet_ids)
        locks = []
        
        try:
            # Acquire locks in order
            for wallet_id in sorted_wallet_ids:
                lock = self.get_wallet_lock(wallet_id)
                lock.acquire()
                locks.append(lock)
            
            yield
            
        finally:
            # Release locks in reverse order
            for lock in reversed(locks):
                lock.release()

# Global deadlock avoidance manager instance
deadlock_manager = DeadlockAvoidanceManager()

class IdempotencyManager:
    """
    Manages idempotency for transactions to prevent duplicate processing.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_and_mark_idempotency(self, idempotency_key: str) -> bool:
        """
        Check if an idempotency key has been used.
        Returns True if the key is new (can proceed), False if already used.
        """
        from app.models import Transaction
        
        # Check if transaction with this idempotency key exists
        existing = self.db.execute(
            select(Transaction).where(Transaction.idempotency_key == idempotency_key)
        ).scalar_one_or_none()
        
        return existing is None
    
    def get_existing_transaction(self, idempotency_key: str):
        """Get existing transaction by idempotency key"""
        from app.models import Transaction
        
        return self.db.execute(
            select(Transaction).where(Transaction.idempotency_key == idempotency_key)
        ).scalar_one_or_none()

class ConcurrencyControl:
    """
    Advanced concurrency control with retry mechanisms for high-load scenarios.
    """
    
    def __init__(self, max_retries: int = 3, backoff_factor: float = 0.1):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
    
    def execute_with_retry(self, operation, *args, **kwargs):
        """
        Execute an operation with automatic retry for deadlock scenarios.
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                # Check if it's a deadlock or serialization failure
                if self._is_retryable_error(e) and attempt < self.max_retries:
                    # Exponential backoff
                    sleep_time = self.backoff_factor * (2 ** attempt)
                    time.sleep(sleep_time)
                    continue
                else:
                    # Not retryable or max retries reached
                    raise
        
        # If we get here, all retries failed
        raise last_exception
    
    def _is_retryable_error(self, exception: Exception) -> bool:
        """
        Determine if an exception is retryable (deadlock, serialization failure, etc.).
        """
        error_message = str(exception).lower()
        retryable_keywords = [
            'deadlock', 'serialization failure', 'could not serialize access',
            'lock wait timeout', 'duplicate key'
        ]
        
        return any(keyword in error_message for keyword in retryable_keywords)

@contextmanager
def database_transaction_with_retry(db: Session, max_retries: int = 3):
    """
    Context manager for database transactions with automatic retry.
    """
    concurrency_control = ConcurrencyControl(max_retries=max_retries)
    
    def execute_operation():
        # The actual database operations will be performed here
        yield db
        db.commit()
    
    try:
        concurrency_control.execute_with_retry(execute_operation)
    except Exception as e:
        db.rollback()
        raise e
