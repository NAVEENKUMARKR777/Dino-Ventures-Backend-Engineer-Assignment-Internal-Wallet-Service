from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from typing import Optional

class AssetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=10)
    description: Optional[str] = None

class AssetCreate(AssetBase):
    pass

class Asset(AssetBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class WalletBase(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100)
    asset_id: int
    is_system: bool = False

class WalletCreate(WalletBase):
    initial_balance: Decimal = Field(default=0, ge=0)

class Wallet(WalletBase):
    id: int
    balance: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class WalletWithAsset(Wallet):
    asset: Asset

class TransactionBase(BaseModel):
    transaction_type: str = Field(..., pattern="^(topup|bonus|purchase)$")
    amount: Decimal = Field(..., gt=0)
    asset_id: int
    debit_wallet_id: int
    credit_wallet_id: int
    description: Optional[str] = None

class TransactionCreate(TransactionBase):
    idempotency_key: Optional[str] = None

class Transaction(TransactionBase):
    id: int
    transaction_id: str
    status: str
    idempotency_key: Optional[str] = None
    created_at: datetime
    processed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class LedgerEntryBase(BaseModel):
    amount: Decimal
    debit_balance_before: Decimal
    debit_balance_after: Decimal
    credit_balance_before: Decimal
    credit_balance_after: Decimal

class LedgerEntry(LedgerEntryBase):
    id: int
    transaction_id: int
    asset_id: int
    debit_wallet_id: int
    credit_wallet_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class BalanceResponse(BaseModel):
    wallet_id: int
    user_id: str
    asset_name: str
    asset_code: str
    balance: Decimal
    is_system: bool

class TransactionRequest(BaseModel):
    transaction_type: str = Field(..., pattern="^(topup|bonus|purchase)$")
    user_id: str = Field(..., min_length=1, max_length=100)
    asset_code: str = Field(..., min_length=1, max_length=10)
    amount: Decimal = Field(..., gt=0)
    description: Optional[str] = None
    idempotency_key: Optional[str] = None

class TransactionResponse(BaseModel):
    transaction_id: str
    transaction_type: str
    amount: Decimal
    asset_code: str
    status: str
    description: Optional[str] = None
    created_at: datetime
    processed_at: Optional[datetime] = None

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
