-- Dino Ventures Internal Wallet Service - Database Schema Creation
-- This script creates the database tables before seeding data

-- Create Assets table
CREATE TABLE IF NOT EXISTS assets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    code VARCHAR(10) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create Wallets table
CREATE TABLE IF NOT EXISTS wallets (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    asset_id INTEGER NOT NULL REFERENCES assets(id),
    balance NUMERIC(20,8) DEFAULT 0 NOT NULL,
    is_system BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create Transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(100) UNIQUE NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    amount NUMERIC(20,8) NOT NULL,
    asset_id INTEGER NOT NULL REFERENCES assets(id),
    debit_wallet_id INTEGER NOT NULL REFERENCES wallets(id),
    credit_wallet_id INTEGER NOT NULL REFERENCES wallets(id),
    description TEXT,
    status VARCHAR(20) DEFAULT 'completed' NOT NULL,
    idempotency_key VARCHAR(255) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP WITH TIME ZONE
);

-- Create Ledger Entries table
CREATE TABLE IF NOT EXISTS ledger_entries (
    id SERIAL PRIMARY KEY,
    transaction_id INTEGER NOT NULL REFERENCES transactions(id),
    asset_id INTEGER NOT NULL REFERENCES assets(id),
    debit_wallet_id INTEGER NOT NULL REFERENCES wallets(id),
    credit_wallet_id INTEGER NOT NULL REFERENCES wallets(id),
    amount NUMERIC(20,8) NOT NULL,
    debit_balance_before NUMERIC(20,8) NOT NULL,
    debit_balance_after NUMERIC(20,8) NOT NULL,
    credit_balance_before NUMERIC(20,8) NOT NULL,
    credit_balance_after NUMERIC(20,8) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_wallet_user_asset ON wallets(user_id, asset_id);
CREATE INDEX IF NOT EXISTS idx_wallet_system ON wallets(is_system);
CREATE INDEX IF NOT EXISTS idx_transaction_type_status ON transactions(transaction_type, status);
CREATE INDEX IF NOT EXISTS idx_transaction_created ON transactions(created_at);
CREATE INDEX IF NOT EXISTS idx_transaction_idempotency ON transactions(idempotency_key);
CREATE INDEX IF NOT EXISTS idx_ledger_transaction ON ledger_entries(transaction_id);
CREATE INDEX IF NOT EXISTS idx_ledger_wallets ON ledger_entries(debit_wallet_id, credit_wallet_id);
CREATE INDEX IF NOT EXISTS idx_ledger_created ON ledger_entries(created_at);
