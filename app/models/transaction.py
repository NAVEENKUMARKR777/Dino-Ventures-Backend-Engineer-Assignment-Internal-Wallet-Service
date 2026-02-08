"""
Transaction model - records all wallet transactions.
"""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, String, DateTime, Enum, Numeric, ForeignKey, Text, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
import enum
import uuid

from app.database import Base


class TransactionType(str, enum.Enum):
    """Transaction type enumeration."""
    TOPUP = "TOPUP"      # User purchases credits
    BONUS = "BONUS"       # System issues free credits
    SPEND = "SPEND"       # User spends credits
    REFUND = "REFUND"     # Refund of spent credits
    ADJUSTMENT = "ADJUSTMENT"  # Manual adjustment


class TransactionStatus(str, enum.Enum):
    """Transaction status enumeration."""
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REVERSED = "REVERSED"


class Transaction(Base):
    """
    Transaction model representing a wallet transaction.
    Each transaction creates corresponding ledger entries.
    """
    __tablename__ = "transactions"
    
    id = Column(String(100), primary_key=True, default=lambda: f"txn_{uuid.uuid4().hex[:16]}", index=True)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    status = Column(Enum(TransactionStatus), nullable=False, default=TransactionStatus.PENDING)
    user_id = Column(String(100), nullable=False, index=True)
    asset_type_code = Column(String(50), ForeignKey("asset_types.code"), nullable=False)
    amount = Column(Numeric(20, 2), nullable=False)
    description = Column(Text, nullable=True)
    extra_data = Column(JSONB, nullable=True, name='metadata')  # Store additional data as JSON
    idempotency_key = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    asset_type = relationship("AssetType", back_populates="transactions")
    ledger_entries = relationship("LedgerEntry", back_populates="transaction")
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_transactions_user_created', 'user_id', 'created_at'),
        Index('ix_transactions_type_status', 'transaction_type', 'status'),
    )
    
    def __repr__(self):
        return f"<Transaction {self.id}: {self.transaction_type} - {self.amount}>"
