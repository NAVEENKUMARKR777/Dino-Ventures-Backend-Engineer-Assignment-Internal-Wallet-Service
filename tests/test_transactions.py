"""
Test transaction service.
"""
import pytest
from decimal import Decimal

from app.services.transaction_service import TransactionService
from app.models.transaction import TransactionStatus


@pytest.mark.asyncio
async def test_topup_transaction(db_session):
    """Test wallet top-up transaction."""
    service = TransactionService(db_session)
    
    transaction = await service.execute_topup(
        user_id="test_user_001",
        asset_type_code="GOLD_COINS",
        amount=Decimal("100.00"),
        idempotency_key="test_topup_001",
        metadata={"payment_id": "pay_123"}
    )
    
    assert transaction.status == TransactionStatus.COMPLETED
    assert transaction.amount == Decimal("100.00")
    assert transaction.user_id == "test_user_001"


@pytest.mark.asyncio
async def test_bonus_transaction(db_session):
    """Test bonus transaction."""
    service = TransactionService(db_session)
    
    transaction = await service.execute_bonus(
        user_id="test_user_002",
        asset_type_code="GOLD_COINS",
        amount=Decimal("50.00"),
        idempotency_key="test_bonus_001",
        metadata={"reason": "referral"}
    )
    
    assert transaction.status == TransactionStatus.COMPLETED
    assert transaction.amount == Decimal("50.00")


@pytest.mark.asyncio
async def test_spend_transaction(db_session):
    """Test spend transaction."""
    service = TransactionService(db_session)
    
    # First add balance
    await service.execute_topup(
        user_id="test_user_003",
        asset_type_code="GOLD_COINS",
        amount=Decimal("200.00"),
        idempotency_key="test_topup_before_spend"
    )
    
    # Then spend
    transaction = await service.execute_spend(
        user_id="test_user_003",
        asset_type_code="GOLD_COINS",
        amount=Decimal("75.00"),
        idempotency_key="test_spend_001",
        metadata={"item_id": "item_123"}
    )
    
    assert transaction.status == TransactionStatus.COMPLETED
    assert transaction.amount == Decimal("75.00")


@pytest.mark.asyncio
async def test_insufficient_balance(db_session):
    """Test spending with insufficient balance."""
    service = TransactionService(db_session)
    
    with pytest.raises(ValueError, match="Insufficient balance"):
        await service.execute_spend(
            user_id="test_user_004",
            asset_type_code="GOLD_COINS",
            amount=Decimal("1000.00"),
            idempotency_key="test_spend_fail"
        )


@pytest.mark.asyncio
async def test_idempotency(db_session):
    """Test idempotency - duplicate requests return same transaction."""
    service = TransactionService(db_session)
    
    # First request
    transaction1 = await service.execute_topup(
        user_id="test_user_005",
        asset_type_code="GOLD_COINS",
        amount=Decimal("100.00"),
        idempotency_key="test_idempotency_001"
    )
    
    # Duplicate request with same idempotency key
    transaction2 = await service.execute_topup(
        user_id="test_user_005",
        asset_type_code="GOLD_COINS",
        amount=Decimal("100.00"),
        idempotency_key="test_idempotency_001"
    )
    
    # Should return the same transaction
    assert transaction1.id == transaction2.id
