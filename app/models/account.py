"""
Account model - represents wallet accounts for users and system.
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Index, Integer
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class AccountType(str, enum.Enum):
    """Account type enumeration."""
    USER = "USER"
    SYSTEM = "SYSTEM"


class Account(Base):
    """
    Account model representing a wallet account.
    Each user can have multiple accounts (one per asset type).
    System accounts are used as source/sink for transactions.
    """
    __tablename__ = "accounts"
    
    id = Column(String(100), primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    account_type = Column(Enum(AccountType), nullable=False, default=AccountType.USER)
    asset_type_code = Column(String(50), ForeignKey("asset_types.code"), nullable=False)
    version = Column(Integer, default=0, nullable=False)  # For optimistic locking
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    asset_type = relationship("AssetType", back_populates="accounts")
    debit_entries = relationship("LedgerEntry", foreign_keys="LedgerEntry.debit_account_id", back_populates="debit_account")
    credit_entries = relationship("LedgerEntry", foreign_keys="LedgerEntry.credit_account_id", back_populates="credit_account")
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_accounts_user_asset', 'user_id', 'asset_type_code', unique=True),
    )
    
    def __repr__(self):
        return f"<Account {self.id}: {self.user_id} - {self.asset_type_code}>"
