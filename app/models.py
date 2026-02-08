from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Boolean, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(10), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    wallets = relationship("Wallet", back_populates="asset")
    ledger_entries = relationship("LedgerEntry", back_populates="asset")

class Wallet(Base):
    __tablename__ = "wallets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    balance = Column(Numeric(20, 8), default=0, nullable=False)
    is_system = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    asset = relationship("Asset", back_populates="wallets")
    debit_entries = relationship("LedgerEntry", foreign_keys="LedgerEntry.debit_wallet_id", back_populates="debit_wallet")
    credit_entries = relationship("LedgerEntry", foreign_keys="LedgerEntry.credit_wallet_id", back_populates="credit_wallet")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_wallet_user_asset', 'user_id', 'asset_id'),
        Index('idx_wallet_system', 'is_system'),
    )

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(100), unique=True, nullable=False, index=True)
    transaction_type = Column(String(50), nullable=False)  # 'topup', 'bonus', 'purchase'
    amount = Column(Numeric(20, 8), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    debit_wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    credit_wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    description = Column(Text)
    status = Column(String(20), default='completed', nullable=False)  # 'pending', 'completed', 'failed'
    idempotency_key = Column(String(255), unique=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    asset = relationship("Asset")
    debit_wallet = relationship("Wallet", foreign_keys=[debit_wallet_id])
    credit_wallet = relationship("Wallet", foreign_keys=[credit_wallet_id])
    ledger_entries = relationship("LedgerEntry", back_populates="transaction")
    
    # Indexes for performance and concurrency
    __table_args__ = (
        Index('idx_transaction_type_status', 'transaction_type', 'status'),
        Index('idx_transaction_created', 'created_at'),
        Index('idx_transaction_idempotency', 'idempotency_key'),
    )

class LedgerEntry(Base):
    __tablename__ = "ledger_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    debit_wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    credit_wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    amount = Column(Numeric(20, 8), nullable=False)
    debit_balance_before = Column(Numeric(20, 8), nullable=False)
    debit_balance_after = Column(Numeric(20, 8), nullable=False)
    credit_balance_before = Column(Numeric(20, 8), nullable=False)
    credit_balance_after = Column(Numeric(20, 8), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    transaction = relationship("Transaction", back_populates="ledger_entries")
    asset = relationship("Asset", back_populates="ledger_entries")
    debit_wallet = relationship("Wallet", foreign_keys=[debit_wallet_id], back_populates="debit_entries")
    credit_wallet = relationship("Wallet", foreign_keys=[credit_wallet_id], back_populates="credit_entries")
    
    # Indexes for audit trail and performance
    __table_args__ = (
        Index('idx_ledger_transaction', 'transaction_id'),
        Index('idx_ledger_wallets', 'debit_wallet_id', 'credit_wallet_id'),
        Index('idx_ledger_created', 'created_at'),
    )
