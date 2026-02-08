# Architecture Deep Dive

## System Overview

The Dino Ventures Internal Wallet Service is built on a **double-entry ledger architecture** that ensures complete auditability and data integrity for all transactions.

## Core Principles

### 1. Double-Entry Bookkeeping

Every transaction creates **exactly two ledger entries**:
- **DEBIT entry**: Increases the receiving account's balance
- **CREDIT entry**: Decreases the sending account's balance

This ensures:
- **Zero-sum accounting**: Sum of all ledger entries = 0
- **Complete audit trail**: Every credit has a corresponding debit
- **Historical accuracy**: Balances are always recalculable from entries

#### Example: User Purchases 100 Gold Coins

```
Transaction ID: txn_abc123
Type: TOPUP
Amount: 100 GOLD_COINS

Ledger Entries:
1. DEBIT  - user_001_GOLD_COINS       +100
2. CREDIT - SYSTEM_TREASURY_GOLD_COINS -100
                                       ----
                                        = 0
```

### 2. Balance Calculation

Balances are **never stored directly**. Instead, they are calculated from ledger entries:

```sql
Balance = SUM(Debits) - SUM(Credits)
```

This approach:
- Prevents balance corruption
- Enables point-in-time balance queries
- Provides complete transaction history

### 3. ACID Transactions

All operations are wrapped in PostgreSQL transactions with:
- **Atomicity**: All-or-nothing operations
- **Consistency**: Invariants are maintained
- **Isolation**: Concurrent operations don't interfere
- **Durability**: Committed data is permanent

## Concurrency Control

### Challenge: Race Conditions

Without proper locking, concurrent transactions can cause:
- Lost updates
- Dirty reads
- Phantom reads
- Inconsistent balances

### Solution: Row-Level Locking

```python
# Lock accounts before modification
SELECT * FROM accounts 
WHERE id = 'user_001_GOLD_COINS' 
FOR UPDATE;
```

**Benefits:**
- Prevents concurrent modifications
- Maintains consistency
- Allows parallel processing of different accounts

### Deadlock Prevention

**Problem**: Two transactions trying to lock the same accounts in different order:

```
Transaction A: Lock user_001, then SYSTEM
Transaction B: Lock SYSTEM, then user_001
→ Deadlock!
```

**Solution**: **Consistent Lock Ordering**

Always lock accounts in **alphabetical order** by account ID:

```python
account_ids = sorted([user_account.id, system_account.id])
for account_id in account_ids:
    # Lock in sorted order
    SELECT ... FOR UPDATE
```

This guarantees:
- No circular wait conditions
- No deadlocks
- Predictable lock acquisition

## Idempotency

### Challenge: Duplicate Requests

Network issues can cause duplicate requests:
- User clicks "Buy" twice
- Payment gateway retries
- Network timeouts with retransmission

### Solution: Idempotency Keys

Every transaction requires a unique `idempotency_key`:

```python
@unique
idempotency_key: str
```

**Behavior:**
1. First request: Process transaction, store key
2. Duplicate request: Return original transaction (same ID)
3. Different key: Process as new transaction

**Example:**
```bash
# Request 1
POST /topup
{ "idempotency_key": "key123", "amount": 100 }
→ Creates txn_abc

# Request 2 (duplicate)
POST /topup
{ "idempotency_key": "key123", "amount": 100 }
→ Returns txn_abc (no new transaction)
```

## Transaction Flow

### 1. Wallet Top-up (Purchase)

```
User Account                System Treasury
    (+100) ←------------------- (-100)
          DEBIT         CREDIT
```

**Steps:**
1. Validate input
2. Check idempotency
3. Lock accounts (sorted order)
4. Create transaction record
5. Create ledger entries (debit user, credit system)
6. Mark transaction COMPLETED
7. Commit

### 2. Bonus/Incentive

```
User Account                System Treasury
    (+50) ←-------------------- (-50)
         DEBIT          CREDIT
```

**Same flow as top-up**, different transaction type and metadata.

### 3. Purchase/Spend

```
System Treasury             User Account
    (+25) ←-------------------- (-25)
         DEBIT          CREDIT
```

**Additional step**: Check sufficient balance before transaction.

## Database Schema

### Tables

#### asset_types
- Defines currency types (GOLD_COINS, etc.)
- Master data table

#### accounts
- One account per user per asset type
- Includes system accounts (SYSTEM_TREASURY)
- `version` field for optimistic locking

#### transactions
- High-level transaction records
- Includes status, type, metadata
- `idempotency_key` for duplicate prevention

#### ledger_entries
- Double-entry bookkeeping
- References both debit and credit accounts
- Immutable once created

### Indexes

**Performance-critical indexes:**

```sql
-- Fast balance queries
CREATE INDEX ix_ledger_debit_asset 
ON ledger_entries(debit_account_id, asset_type_code);

-- Fast transaction history
CREATE INDEX ix_transactions_user_created 
ON transactions(user_id, created_at);

-- Idempotency checks
CREATE UNIQUE INDEX ix_transactions_idempotency_key 
ON transactions(idempotency_key);
```

## Error Handling

### Insufficient Balance

```python
if balance < amount:
    raise ValueError("Insufficient balance")
```

Returns HTTP 400 with error message.

### Duplicate Idempotency Key

Returns the **original transaction** (HTTP 201) instead of creating a duplicate.

### Database Constraint Violations

- Caught and returned as HTTP 400
- Logged for debugging

### Unexpected Errors

- Logged with stack trace
- Transaction rolled back automatically
- HTTP 500 returned

## Security Considerations

### Input Validation

All inputs validated with Pydantic:
- Amount must be positive
- Asset type must exist
- User IDs validated

### SQL Injection Prevention

Using SQLAlchemy ORM:
- Parameterized queries
- No raw SQL with user input

### Transaction Limits

Configurable limits:
```python
MAX_TRANSACTION_AMOUNT = 1_000_000
MIN_TRANSACTION_AMOUNT = 0.01
```

## Performance Optimization

### 1. Connection Pooling

```python
pool_size=20
max_overflow=0
```

Reuses connections, reduces overhead.

### 2. Async I/O

FastAPI with async/await:
- Non-blocking database calls
- High concurrency support

### 3. Indexed Queries

All frequent queries use indexes:
- Balance calculations
- Transaction history
- Idempotency checks

### 4. Query Optimization

```python
# Efficient balance calculation
SELECT COALESCE(SUM(amount), 0)
FROM ledger_entries
WHERE debit_account_id = :account_id
  AND entry_type = 'DEBIT'
```

## Scalability

### Horizontal Scaling

**Application layer:**
- Stateless API servers
- Can run multiple instances
- Load balancer distributes requests

**Database layer:**
- PostgreSQL read replicas for queries
- Write operations to primary
- Connection pooling per instance

### Vertical Scaling

- Increase database resources
- Optimize indexes
- Partition large tables (future)

## Monitoring & Observability

### Logging

Structured JSON logs:
```python
logger.info(f"Transaction {txn.id} completed", extra={
    "transaction_id": txn.id,
    "user_id": txn.user_id,
    "amount": txn.amount
})
```

### Metrics

Track:
- Transaction throughput
- Average response time
- Error rates
- Database connection pool usage

### Audit Trail

Complete transaction history:
- All transactions logged
- Ledger entries immutable
- Timestamps on all records

## Future Enhancements

1. **Transaction Reversal/Refund**: Implement refund flow
2. **Multi-currency Swaps**: Exchange between asset types
3. **Scheduled Transactions**: Recurring bonuses
4. **Rate Limiting**: Per-user transaction limits
5. **Webhooks**: Notify external systems of transactions
6. **Analytics Dashboard**: Real-time metrics
7. **Database Partitioning**: For massive scale
8. **Caching Layer**: Redis for balance caching
