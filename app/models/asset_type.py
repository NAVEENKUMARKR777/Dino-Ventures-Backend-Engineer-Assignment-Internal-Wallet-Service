"""
Asset Type model - defines the types of currencies in the system.
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship

from app.database import Base


class AssetType(Base):
    """
    Asset Type model representing different currencies.
    E.g., GOLD_COINS, DIAMONDS, LOYALTY_POINTS
    """
    __tablename__ = "asset_types"
    
    code = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    accounts = relationship("Account", back_populates="asset_type")
    transactions = relationship("Transaction", back_populates="asset_type")
    ledger_entries = relationship("LedgerEntry", back_populates="asset_type")
    
    def __repr__(self):
        return f"<AssetType {self.code}: {self.name}>"
