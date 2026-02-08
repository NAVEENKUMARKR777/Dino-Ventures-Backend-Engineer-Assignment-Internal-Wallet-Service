-- Dino Ventures Internal Wallet Service - Database Seed Script
-- This script initializes the database with required data
-- Note: Tables should be created first using create_tables.sql

-- Insert Asset Types
INSERT INTO assets (name, code, description) VALUES 
('Gold Coins', 'GC', 'Primary in-game currency for purchases'),
('Diamonds', 'DI', 'Premium currency for exclusive items'),
('Loyalty Points', 'LP', 'Reward points for user engagement')
ON CONFLICT (id) DO NOTHING;

-- Create System Wallets (Treasury accounts)
INSERT INTO wallets (user_id, asset_id, balance, is_system) VALUES 
('system_treasury', 1, 1000000.00, true),  -- Gold Coins Treasury
('system_treasury', 2, 100000.00, true),   -- Diamonds Treasury  
('system_treasury', 3, 500000.00, true)    -- Loyalty Points Treasury
ON CONFLICT (id) DO NOTHING;

-- Create User Accounts with initial balances
INSERT INTO wallets (user_id, asset_id, balance, is_system) VALUES 
('user_001', 1, 1000.00, false),  -- User 1: 1000 Gold Coins
('user_001', 2, 50.00, false),    -- User 1: 50 Diamonds
('user_001', 3, 500.00, false),   -- User 1: 500 Loyalty Points
('user_002', 1, 500.00, false),   -- User 2: 500 Gold Coins
('user_002', 2, 25.00, false),    -- User 2: 25 Diamonds
('user_002', 3, 250.00, false)    -- User 2: 250 Loyalty Points
ON CONFLICT (id) DO NOTHING;

-- Create some sample transactions for testing
INSERT INTO transactions (transaction_id, transaction_type, amount, asset_id, debit_wallet_id, credit_wallet_id, description, status) VALUES 
('txn_topup_001', 'topup', 100.00, 1, 7, 1, 'User 001 purchased 100 Gold Coins', 'completed'),
('txn_bonus_001', 'bonus', 50.00, 3, 9, 3, 'User 001 referral bonus', 'completed'),
('txn_purchase_001', 'purchase', 25.00, 1, 4, 7, 'User 001 bought in-game item', 'completed')
ON CONFLICT (transaction_id) DO NOTHING;

-- Create corresponding ledger entries for the transactions
INSERT INTO ledger_entries (transaction_id, asset_id, debit_wallet_id, credit_wallet_id, amount, debit_balance_before, debit_balance_after, credit_balance_before, credit_balance_after) VALUES 
(1, 1, 7, 1, 100.00, 1000000.00, 999900.00, 900.00, 1000.00),  -- Top-up: Treasury -> User 001
(2, 3, 9, 3, 50.00, 500000.00, 499950.00, 450.00, 500.00),      -- Bonus: Treasury -> User 001  
(3, 1, 4, 7, 25.00, 1000.00, 975.00, 999900.00, 999925.00)     -- Purchase: User 001 -> Treasury
ON CONFLICT (id) DO NOTHING;

-- Display seeded data
SELECT '=== Assets ===' as info;
SELECT id, name, code, description FROM assets ORDER BY id;

SELECT '=== System Wallets ===' as info;
SELECT w.id, w.user_id, a.name as asset_name, w.balance, w.is_system 
FROM wallets w 
JOIN assets a ON w.asset_id = a.id 
WHERE w.is_system = true 
ORDER BY w.asset_id;

SELECT '=== User Wallets ===' as info;
SELECT w.id, w.user_id, a.name as asset_name, w.balance, w.is_system 
FROM wallets w 
JOIN assets a ON w.asset_id = a.id 
WHERE w.is_system = false 
ORDER BY w.user_id, w.asset_id;

SELECT '=== Sample Transactions ===' as info;
SELECT t.transaction_id, t.transaction_type, t.amount, a.code as asset_code, 
       dw.user_id as debit_user, cw.user_id as credit_user, t.status
FROM transactions t
JOIN assets a ON t.asset_id = a.id
JOIN wallets dw ON t.debit_wallet_id = dw.id
JOIN wallets cw ON t.credit_wallet_id = cw.id
ORDER BY t.id;

SELECT '=== Ledger Entries ===' as info;
SELECT le.id, t.transaction_id, a.code as asset_code, le.amount,
       dw.user_id as debit_user, cw.user_id as credit_user
FROM ledger_entries le
JOIN transactions t ON le.transaction_id = t.id
JOIN assets a ON le.asset_id = a.id
JOIN wallets dw ON le.debit_wallet_id = dw.id
JOIN wallets cw ON le.credit_wallet_id = cw.id
ORDER BY le.id;
