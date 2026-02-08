"""
Database initialization and startup utilities for Railway deployment
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Asset, Wallet
from decimal import Decimal

def initialize_database():
    """Initialize database with tables and seed data"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    try:
        # Create database engine
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Create all tables
        print("🏗️  Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        # Seed data
        print("🌱 Seeding initial data...")
        db = SessionLocal()
        
        try:
            # Check if assets already exist
            existing_assets = db.query(Asset).count()
            if existing_assets == 0:
                # Create assets
                assets = [
                    Asset(name="Gold Coins", code="GC", description="Primary in-game currency for purchases"),
                    Asset(name="Diamonds", code="DI", description="Premium currency for exclusive items"),
                    Asset(name="Loyalty Points", code="LP", description="Reward points for user engagement")
                ]
                
                for asset in assets:
                    db.add(asset)
                db.flush()
                
                # Create system treasury wallets
                system_wallets = [
                    Wallet(user_id="system_treasury", asset_id=1, balance=Decimal("1000000.00"), is_system=True),
                    Wallet(user_id="system_treasury", asset_id=2, balance=Decimal("100000.00"), is_system=True),
                    Wallet(user_id="system_treasury", asset_id=3, balance=Decimal("500000.00"), is_system=True)
                ]
                
                for wallet in system_wallets:
                    db.add(wallet)
                db.flush()
                
                # Create user wallets
                user_wallets = [
                    # user_001 wallets
                    Wallet(user_id="user_001", asset_id=1, balance=Decimal("1000.00"), is_system=False),
                    Wallet(user_id="user_001", asset_id=2, balance=Decimal("50.00"), is_system=False),
                    Wallet(user_id="user_001", asset_id=3, balance=Decimal("500.00"), is_system=False),
                    # user_002 wallets
                    Wallet(user_id="user_002", asset_id=1, balance=Decimal("500.00"), is_system=False),
                    Wallet(user_id="user_002", asset_id=2, balance=Decimal("25.00"), is_system=False),
                    Wallet(user_id="user_002", asset_id=3, balance=Decimal("250.00"), is_system=False)
                ]
                
                for wallet in user_wallets:
                    db.add(wallet)
                
                db.commit()
                print("✅ Database initialized and seeded successfully!")
            else:
                print("✅ Database already contains data, skipping seeding")
                
        except Exception as e:
            db.rollback()
            print(f"❌ Error seeding database: {e}")
            return False
        finally:
            db.close()
            
        return True
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

if __name__ == "__main__":
    initialize_database()
