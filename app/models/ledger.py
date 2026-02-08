"""
Ledger Entry model - implements double-entry bookkeeping.
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Index, Enum
from sqlalchemy.orm import relationship
import enum
import uuid

from app.database import Base


class EntryType(str, enum.Enum):
    """Entry type enumeration."""
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


class LedgerEntry(Base):
    """
    Ledger Entry model implementing double-entry bookkeeping.
    Every transaction creates exactly TWO entries: one debit and one credit.
    
    Debit = Increases user balance (money coming in)
    Credit = Decreases source balance (money going out)
    
    The sum of all entries in the system should always be zero.
    """
    __tablename__ = "ledger_entries"
    
    id = Column(String(100), primary_key=True, default=lambda: f"led_{uuid.uuid4().hex[:16]}", index=True)
    transaction_id = Column(String(100), ForeignKey("transactions.id"), nullable=False, index=True)
    entry_type = Column(Enum(EntryType), nullable=False)
    
    # Double-entry: each entry references a debit and credit account
    debit_account_id = Column(String(100), ForeignKey("accounts.id"), nullable=True, index=True)
    credit_account_id = Column(String(100), ForeignKey("accounts.id"), nullable=True, index=True)
    
    asset_type_code = Column(String(50), ForeignKey("asset_types.code"), nullable=False)
    amount = Column(Numeric(20, 2), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    transaction = relationship("Transaction", back_populates="ledger_entries")
    debit_account = relationship("Account", foreign_keys=[debit_account_id], back_populates="debit_entries")
    credit_account = relationship("Account", foreign_keys=[credit_account_id], back_populates="credit_entries")
    asset_type = relationship("AssetType", back_populates="ledger_entries")
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_ledger_debit_asset', 'debit_account_id', 'asset_type_code'),
        Index('ix_ledger_credit_asset', 'credit_account_id', 'asset_type_code'),
    )
    
    def __repr__(self):
        return f"<LedgerEntry {self.id}: {self.entry_type} - {self.amount}>"
