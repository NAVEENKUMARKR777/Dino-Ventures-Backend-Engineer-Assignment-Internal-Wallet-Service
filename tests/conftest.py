"""
Test configuration and fixtures.
"""
import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.database import Base
from app.models.asset_type import AssetType
from app.models.account import Account, AccountType


# Test database URL (use in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=True,
)

# Create test session factory
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with TestSessionLocal() as session:
        # Seed basic data
        asset_types = [
            AssetType(code="GOLD_COINS", name="Gold Coins", description="Test gold", is_active=True),
            AssetType(code="DIAMONDS", name="Diamonds", description="Test diamonds", is_active=True),
        ]
        for asset in asset_types:
            session.add(asset)
        
        # Add system account
        system_account = Account(
            id="SYSTEM_TREASURY_GOLD_COINS",
            user_id="SYSTEM_TREASURY",
            account_type=AccountType.SYSTEM,
            asset_type_code="GOLD_COINS"
        )
        session.add(system_account)
        await session.commit()
        
        yield session
    
    # Drop tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
