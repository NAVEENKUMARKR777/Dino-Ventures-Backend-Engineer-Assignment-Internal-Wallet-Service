"""
Simple test to verify imports work correctly.
"""
def test_imports():
    """Test that all main modules can be imported."""
    from app import config
    from app import database
    from app import main
    from app import schemas
    from app.models import account
    from app.models import asset_type
    from app.models import transaction
    from app.models import ledger
    from app.services import wallet_service
    from app.services import transaction_service
    from app.routers import transactions
    from app.routers import wallets
    from app.routers import users
    
    assert config is not None
    assert database is not None
    assert main is not None
    print("✓ All imports successful!")


if __name__ == "__main__":
    test_imports()
