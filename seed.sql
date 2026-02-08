-- Database Seed Script for Dino Ventures Wallet Service
-- This file provides the SQL schema and initial data

-- ============================================================================
-- SCHEMA CREATION
-- ============================================================================

-- Asset Types Table
CREATE TABLE IF NOT EXISTS asset_types (
    code VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Accounts Table (Wallet Accounts)
CREATE TABLE IF NOT EXISTS accounts (
    id VARCHAR(100) PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    account_type VARCHAR(20) NOT NULL CHECK (account_type IN ('USER', 'SYSTEM')),
    asset_type_code VARCHAR(50) NOT NULL REFERENCES asset_types(code),
    version INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, asset_type_code)
);

-- Transactions Table
CREATE TABLE IF NOT EXISTS transactions (
    id VARCHAR(100) PRIMARY KEY,
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('TOPUP', 'BONUS', 'SPEND', 'REFUND', 'ADJUSTMENT')),
    status VARCHAR(20) NOT NULL CHECK (status IN ('PENDING', 'COMPLETED', 'FAILED', 'REVERSED')),
    user_id VARCHAR(100) NOT NULL,
    asset_type_code VARCHAR(50) NOT NULL REFERENCES asset_types(code),
    amount NUMERIC(20, 2) NOT NULL,
    description TEXT,
    metadata JSONB,
    idempotency_key VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Ledger Entries Table (Double-Entry Bookkeeping)
CREATE TABLE IF NOT EXISTS ledger_entries (
    id VARCHAR(100) PRIMARY KEY,
    transaction_id VARCHAR(100) NOT NULL REFERENCES transactions(id),
    entry_type VARCHAR(10) NOT NULL CHECK (entry_type IN ('DEBIT', 'CREDIT')),
    debit_account_id VARCHAR(100) REFERENCES accounts(id),
    credit_account_id VARCHAR(100) REFERENCES accounts(id),
    asset_type_code VARCHAR(50) NOT NULL REFERENCES asset_types(code),
    amount NUMERIC(20, 2) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Account indexes
CREATE INDEX IF NOT EXISTS ix_accounts_user_id ON accounts(user_id);
CREATE INDEX IF NOT EXISTS ix_accounts_asset_type_code ON accounts(asset_type_code);

-- Transaction indexes
CREATE INDEX IF NOT EXISTS ix_transactions_id ON transactions(id);
CREATE INDEX IF NOT EXISTS ix_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS ix_transactions_idempotency_key ON transactions(idempotency_key);
CREATE INDEX IF NOT EXISTS ix_transactions_user_created ON transactions(user_id, created_at);
CREATE INDEX IF NOT EXISTS ix_transactions_type_status ON transactions(transaction_type, status);
CREATE INDEX IF NOT EXISTS ix_transactions_created_at ON transactions(created_at);

-- Ledger indexes
CREATE INDEX IF NOT EXISTS ix_ledger_entries_id ON ledger_entries(id);
CREATE INDEX IF NOT EXISTS ix_ledger_entries_transaction_id ON ledger_entries(transaction_id);
CREATE INDEX IF NOT EXISTS ix_ledger_entries_debit_account_id ON ledger_entries(debit_account_id);
CREATE INDEX IF NOT EXISTS ix_ledger_entries_credit_account_id ON ledger_entries(credit_account_id);
CREATE INDEX IF NOT EXISTS ix_ledger_entries_created_at ON ledger_entries(created_at);
CREATE INDEX IF NOT EXISTS ix_ledger_debit_asset ON ledger_entries(debit_account_id, asset_type_code);
CREATE INDEX IF NOT EXISTS ix_ledger_credit_asset ON ledger_entries(credit_account_id, asset_type_code);

-- ============================================================================
-- SEED DATA
-- ============================================================================

-- Insert Asset Types
INSERT INTO asset_types (code, name, description, is_active) 
VALUES 
    ('GOLD_COINS', 'Gold Coins', 'Primary in-game currency for purchasing items and upgrades', TRUE),
    ('DIAMONDS', 'Diamonds', 'Premium currency obtained through purchases or rare achievements', TRUE),
    ('LOYALTY_POINTS', 'Loyalty Points', 'Rewards points earned through daily logins and activities', TRUE)
ON CONFLICT (code) DO NOTHING;

-- Insert System Treasury Accounts
INSERT INTO accounts (id, user_id, account_type, asset_type_code, version)
VALUES 
    ('SYSTEM_TREASURY_GOLD_COINS', 'SYSTEM_TREASURY', 'SYSTEM', 'GOLD_COINS', 0),
    ('SYSTEM_TREASURY_DIAMONDS', 'SYSTEM_TREASURY', 'SYSTEM', 'DIAMONDS', 0),
    ('SYSTEM_TREASURY_LOYALTY_POINTS', 'SYSTEM_TREASURY', 'SYSTEM', 'LOYALTY_POINTS', 0)
ON CONFLICT (user_id, asset_type_code) DO NOTHING;

-- Insert Demo User Accounts
INSERT INTO accounts (id, user_id, account_type, asset_type_code, version)
VALUES 
    ('user_001_GOLD_COINS', 'user_001', 'USER', 'GOLD_COINS', 0),
    ('user_001_DIAMONDS', 'user_001', 'USER', 'DIAMONDS', 0),
    ('user_002_GOLD_COINS', 'user_002', 'USER', 'GOLD_COINS', 0),
    ('user_002_LOYALTY_POINTS', 'user_002', 'USER', 'LOYALTY_POINTS', 0)
ON CONFLICT (user_id, asset_type_code) DO NOTHING;

-- Note: Demo user balances are created through bonus transactions
-- This is handled by the seed script to maintain ledger integrity

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify asset types
-- SELECT * FROM asset_types;

-- Verify accounts
-- SELECT * FROM accounts ORDER BY user_id, asset_type_code;

-- Verify transactions
-- SELECT * FROM transactions ORDER BY created_at DESC;

-- Verify ledger entries
-- SELECT * FROM ledger_entries ORDER BY created_at DESC;

-- Calculate user balance
-- SELECT 
--     a.user_id,
--     a.asset_type_code,
--     COALESCE(SUM(CASE WHEN le.entry_type = 'DEBIT' THEN le.amount ELSE 0 END), 0) -
--     COALESCE(SUM(CASE WHEN le.entry_type = 'CREDIT' THEN le.amount ELSE 0 END), 0) as balance
-- FROM accounts a
-- LEFT JOIN ledger_entries le ON (le.debit_account_id = a.id OR le.credit_account_id = a.id)
-- WHERE a.account_type = 'USER'
-- GROUP BY a.user_id, a.asset_type_code
-- ORDER BY a.user_id, a.asset_type_code;
