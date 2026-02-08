"""
Test wallet service.
"""
import pytest
from decimal import Decimal

from app.services.wallet_service import WalletService
from app.services.transaction_service import TransactionService


@pytest.mark.asyncio
async def test_get_balance(db_session):
    """Test balance calculation."""
    wallet_service = WalletService(db_session)
    transaction_service = TransactionService(db_session)
    
    # Add balance
    await transaction_service.execute_topup(
        user_id="test_user_balance",
        asset_type_code="GOLD_COINS",
        amount=Decimal("500.00"),
        idempotency_key="balance_test_001"
    )
    
    # Check balance
    balance = await wallet_service.get_balance("test_user_balance", "GOLD_COINS")
    assert balance == Decimal("500.00")


@pytest.mark.asyncio
async def test_balance_after_multiple_transactions(db_session):
    """Test balance after multiple transactions."""
    wallet_service = WalletService(db_session)
    transaction_service = TransactionService(db_session)
    
    user_id = "test_user_multi"
    
    # Add 1000
    await transaction_service.execute_topup(
        user_id=user_id,
        asset_type_code="GOLD_COINS",
        amount=Decimal("1000.00"),
        idempotency_key="multi_001"
    )
    
    # Add 500 more
    await transaction_service.execute_bonus(
        user_id=user_id,
        asset_type_code="GOLD_COINS",
        amount=Decimal("500.00"),
        idempotency_key="multi_002"
    )
    
    # Spend 300
    await transaction_service.execute_spend(
        user_id=user_id,
        asset_type_code="GOLD_COINS",
        amount=Decimal("300.00"),
        idempotency_key="multi_003"
    )
    
    # Balance should be 1000 + 500 - 300 = 1200
    balance = await wallet_service.get_balance(user_id, "GOLD_COINS")
    assert balance == Decimal("1200.00")


@pytest.mark.asyncio
async def test_get_all_balances(db_session):
    """Test getting all balances for a user."""
    wallet_service = WalletService(db_session)
    transaction_service = TransactionService(db_session)
    
    user_id = "test_user_all_balances"
    
    # Add GOLD_COINS
    await transaction_service.execute_topup(
        user_id=user_id,
        asset_type_code="GOLD_COINS",
        amount=Decimal("100.00"),
        idempotency_key="all_balances_001"
    )
    
    # Get all balances
    response = await wallet_service.get_all_balances(user_id)
    
    assert response.user_id == user_id
    assert len(response.balances) > 0
