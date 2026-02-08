"""
Database initialization for Railway deployment
This script will be called by the main application to initialize the database
"""

import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Asset, Wallet
from decimal import Decimal

logger = logging.getLogger(__name__)

def init_database():
    """Initialize database with tables and seed data"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL not found in environment variables")
        return False
    
    try:
        logger.info("🏗️  Creating database engine...")
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Create all tables
        logger.info("🏗️  Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        # Seed data
        logger.info("🌱 Seeding initial data...")
        db = SessionLocal()
        
        try:
            # Check if assets already exist
            existing_assets = db.query(Asset).count()
            if existing_assets == 0:
                logger.info("Creating assets...")
                # Create assets
                assets = [
                    Asset(name="Gold Coins", code="GC", description="Primary in-game currency for purchases"),
                    Asset(name="Diamonds", code="DI", description="Premium currency for exclusive items"),
                    Asset(name="Loyalty Points", code="LP", description="Reward points for user engagement")
                ]
                
                for asset in assets:
                    db.add(asset)
                db.flush()
                
                logger.info("Creating system treasury wallets...")
                # Create system treasury wallets
                system_wallets = [
                    Wallet(user_id="system_treasury", asset_id=1, balance=Decimal("1000000.00"), is_system=True),
                    Wallet(user_id="system_treasury", asset_id=2, balance=Decimal("100000.00"), is_system=True),
                    Wallet(user_id="system_treasury", asset_id=3, balance=Decimal("500000.00"), is_system=True)
                ]
                
                for wallet in system_wallets:
                    db.add(wallet)
                db.flush()
                
                logger.info("Creating user wallets...")
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
                logger.info("✅ Database initialized and seeded successfully!")
            else:
                logger.info("✅ Database already contains data, skipping seeding")
                
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error seeding database: {e}")
            return False
        finally:
            db.close()
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        return False
