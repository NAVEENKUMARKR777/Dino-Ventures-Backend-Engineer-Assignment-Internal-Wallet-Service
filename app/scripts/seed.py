"""
Database seeding script.

Seeds the database with:
1. Asset Types (GOLD_COINS, DIAMONDS, LOYALTY_POINTS)
2. System Treasury Account
3. Demo Users with initial balances
"""
import asyncio
import sys
from decimal import Decimal

from sqlalchemy import select

sys.path.append('.')

from app.database import AsyncSessionLocal, init_db
from app.models.asset_type import AssetType
from app.models.account import Account, AccountType
from app.services.transaction_service import TransactionService


async def seed_asset_types(session):
    """Seed asset types."""
    print("Seeding asset types...")
    
    asset_types = [
        {
            "code": "GOLD_COINS",
            "name": "Gold Coins",
            "description": "Primary in-game currency for purchasing items and upgrades",
            "is_active": True
        },
        {
            "code": "DIAMONDS",
            "name": "Diamonds",
            "description": "Premium currency obtained through purchases or rare achievements",
            "is_active": True
        },
        {
            "code": "LOYALTY_POINTS",
            "name": "Loyalty Points",
            "description": "Rewards points earned through daily logins and activities",
            "is_active": True
        }
    ]
    
    for asset_data in asset_types:
        # Check if already exists
        result = await session.execute(
            select(AssetType).where(AssetType.code == asset_data["code"])
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            asset_type = AssetType(**asset_data)
            session.add(asset_type)
            print(f"  ✓ Created asset type: {asset_data['name']}")
        else:
            print(f"  - Asset type already exists: {asset_data['name']}")
    
    await session.commit()


async def seed_system_account(session):
    """Seed system treasury account."""
    print("\nSeeding system accounts...")
    
    treasury_user_id = "SYSTEM_TREASURY"
    
    for asset_code in ["GOLD_COINS", "DIAMONDS", "LOYALTY_POINTS"]:
        account_id = f"{treasury_user_id}_{asset_code}"
        
        # Check if already exists
        result = await session.execute(
            select(Account).where(Account.id == account_id)
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            account = Account(
                id=account_id,
                user_id=treasury_user_id,
                account_type=AccountType.SYSTEM,
                asset_type_code=asset_code
            )
            session.add(account)
            print(f"  ✓ Created system account: {asset_code}")
        else:
            print(f"  - System account already exists: {asset_code}")
    
    await session.commit()


async def seed_demo_users(session):
    """Seed demo users with initial balances."""
    print("\nSeeding demo users...")
    
    users = [
        {
            "user_id": "user_001",
            "name": "Alice",
            "balances": {
                "GOLD_COINS": Decimal("1000.00"),
                "DIAMONDS": Decimal("100.00")
            }
        },
        {
            "user_id": "user_002",
            "name": "Bob",
            "balances": {
                "GOLD_COINS": Decimal("500.00"),
                "LOYALTY_POINTS": Decimal("50.00")
            }
        }
    ]
    
    transaction_service = TransactionService(session)
    
    for user_data in users:
        user_id = user_data["user_id"]
        name = user_data["name"]
        
        print(f"\n  User: {name} ({user_id})")
        
        for asset_type, amount in user_data["balances"].items():
            idempotency_key = f"seed_{user_id}_{asset_type}_initial"
            
            # Check if transaction already exists
            existing = await transaction_service.check_idempotency(idempotency_key)
            
            if not existing:
                # Create initial balance using bonus transaction
                await transaction_service.execute_bonus(
                    user_id=user_id,
                    asset_type_code=asset_type,
                    amount=amount,
                    idempotency_key=idempotency_key,
                    metadata={
                        "reason": "initial_balance",
                        "user_name": name
                    }
                )
                print(f"    ✓ Credited {amount} {asset_type}")
            else:
                print(f"    - Initial balance already exists for {asset_type}")
        
        await session.commit()


async def main():
    """Main seeding function."""
    print("=" * 60)
    print("DATABASE SEEDING SCRIPT")
    print("Dino Ventures Wallet Service")
    print("=" * 60)
    
    try:
        # Initialize database
        print("\nInitializing database...")
        await init_db()
        print("✓ Database initialized")
        
        # Create session
        async with AsyncSessionLocal() as session:
            # Seed data
            await seed_asset_types(session)
            await seed_system_account(session)
            await seed_demo_users(session)
        
        print("\n" + "=" * 60)
        print("✓ SEEDING COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print("\nSeeded Data Summary:")
        print("  - 3 Asset Types (GOLD_COINS, DIAMONDS, LOYALTY_POINTS)")
        print("  - 1 System Account (SYSTEM_TREASURY)")
        print("  - 2 Demo Users:")
        print("    • user_001 (Alice): 1000 GOLD_COINS, 100 DIAMONDS")
        print("    • user_002 (Bob): 500 GOLD_COINS, 50 LOYALTY_POINTS")
        print("\nYou can now start the API server:")
        print("  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        print("\nAPI Documentation: http://localhost:8000/docs")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
