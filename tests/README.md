# API Testing Examples

This directory contains test scripts and examples for testing the Wallet Service API.

## Running Tests

### Unit Tests
```bash
pytest tests/ -v
```

### With Coverage
```bash
pytest tests/ --cov=app --cov-report=html
```

## Manual API Testing

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. List Users
```bash
curl http://localhost:8000/api/v1/users
```

### 3. Get User Balance
```bash
curl http://localhost:8000/api/v1/wallets/user_001/balance
```

### 4. Top-up Transaction
```bash
curl -X POST http://localhost:8000/api/v1/transactions/topup \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "asset_type": "GOLD_COINS",
    "amount": "100.00",
    "idempotency_key": "topup_'$(date +%s)'",
    "metadata": {
      "payment_id": "pay_xyz123",
      "payment_method": "credit_card"
    }
  }'
```

### 5. Bonus Transaction
```bash
curl -X POST http://localhost:8000/api/v1/transactions/bonus \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "asset_type": "LOYALTY_POINTS",
    "amount": "50.00",
    "idempotency_key": "bonus_'$(date +%s)'",
    "metadata": {
      "reason": "referral_bonus",
      "referral_code": "REF123"
    }
  }'
```

### 6. Spend Transaction
```bash
curl -X POST http://localhost:8000/api/v1/transactions/spend \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "asset_type": "GOLD_COINS",
    "amount": "25.00",
    "idempotency_key": "spend_'$(date +%s)'",
    "metadata": {
      "item_id": "skin_dragon_001",
      "item_name": "Dragon Skin Premium"
    }
  }'
```

### 7. Get Transaction History
```bash
curl "http://localhost:8000/api/v1/wallets/user_001/transactions?limit=10&offset=0"
```

### 8. Get Specific Transaction
```bash
curl http://localhost:8000/api/v1/transactions/txn_abc123
```

## Testing Concurrency

To test concurrent transactions, you can use tools like:

### Apache Bench
```bash
# 100 requests, 10 concurrent
ab -n 100 -c 10 -p topup.json -T application/json http://localhost:8000/api/v1/transactions/topup
```

### Locust (Python load testing)
```bash
locust -f tests/load_test.py --host=http://localhost:8000
```

## Testing Idempotency

### First Request
```bash
curl -X POST http://localhost:8000/api/v1/transactions/topup \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "asset_type": "GOLD_COINS",
    "amount": "100.00",
    "idempotency_key": "idempotency_test_123",
    "metadata": {}
  }'
```

### Duplicate Request (should return same transaction)
```bash
curl -X POST http://localhost:8000/api/v1/transactions/topup \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "asset_type": "GOLD_COINS",
    "amount": "100.00",
    "idempotency_key": "idempotency_test_123",
    "metadata": {}
  }'
```

Both requests should return the same transaction ID.
