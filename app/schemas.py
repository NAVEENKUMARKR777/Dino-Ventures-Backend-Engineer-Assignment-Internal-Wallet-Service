"""
Pydantic schemas for API validation and serialization.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator
from enum import Enum


# Enums
class TransactionTypeEnum(str, Enum):
    TOPUP = "TOPUP"
    BONUS = "BONUS"
    SPEND = "SPEND"
    REFUND = "REFUND"
    ADJUSTMENT = "ADJUSTMENT"


class TransactionStatusEnum(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REVERSED = "REVERSED"


class AccountTypeEnum(str, Enum):
    USER = "USER"
    SYSTEM = "SYSTEM"


# Asset Type Schemas
class AssetTypeBase(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    is_active: bool = True


class AssetTypeCreate(AssetTypeBase):
    pass


class AssetTypeResponse(AssetTypeBase):
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Account Schemas
class AccountBase(BaseModel):
    user_id: str = Field(..., max_length=100)
    asset_type_code: str = Field(..., max_length=50)
    account_type: AccountTypeEnum = AccountTypeEnum.USER


class AccountCreate(AccountBase):
    pass


class AccountResponse(AccountBase):
    id: str
    version: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Transaction Request Schemas
class TransactionBase(BaseModel):
    user_id: str = Field(..., description="User ID")
    asset_type: str = Field(..., description="Asset type code (e.g., GOLD_COINS)")
    amount: Decimal = Field(..., gt=0, description="Transaction amount (must be positive)")
    idempotency_key: str = Field(..., description="Unique key to prevent duplicate transactions")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        # Ensure 2 decimal places
        return round(v, 2)


class TopupRequest(TransactionBase):
    """Request schema for wallet top-up (purchase)."""
    pass


class BonusRequest(TransactionBase):
    """Request schema for bonus/incentive."""
    pass


class SpendRequest(TransactionBase):
    """Request schema for spending credits."""
    pass

# Transaction Response Schemas
class TransactionResponse(BaseModel):
    id: str
    transaction_type: TransactionTypeEnum
    status: TransactionStatusEnum
    user_id: str
    asset_type_code: str
    amount: Decimal
    description: Optional[str]
    metadata: Optional[Dict[str, Any]] = Field(None, alias="extra_data")
    idempotency_key: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        populate_by_name = True  # Allow both metadata and extra_data


# Balance Schemas
class BalanceDetail(BaseModel):
    asset_type: str
    balance: Decimal
    account_id: str


class WalletBalanceResponse(BaseModel):
    user_id: str
    balances: List[BalanceDetail]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Ledger Entry Schemas
class LedgerEntryResponse(BaseModel):
    id: str
    transaction_id: str
    entry_type: str
    debit_account_id: Optional[str]
    credit_account_id: Optional[str]
    asset_type_code: str
    amount: Decimal
    created_at: datetime
    
    class Config:
        from_attributes = True


# Health Check
class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str = "1.0.0"


# Error Response
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
