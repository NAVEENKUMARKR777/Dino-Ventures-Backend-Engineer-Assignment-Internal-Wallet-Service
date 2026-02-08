# Example API Requests

This document provides comprehensive examples of all API endpoints with request/response samples.

## Base URL

- **Local**: `http://localhost:8000`
- **Production**: `https://your-service.up.railway.app`

All API endpoints are prefixed with `/api/v1`.

---

## 1. Health Check

### Request
```bash
GET /health
```

```bash
curl http://localhost:8000/health
```

### Response (200 OK)
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.123456",
  "version": "1.0.0"
}
```

---

## 2. List Users

### Request
```bash
GET /api/v1/users
```

```bash
curl http://localhost:8000/api/v1/users
```

### Response (200 OK)
```json
[
  {
    "user_id": "user_001",
    "account_count": 2
  },
  {
    "user_id": "user_002",
    "account_count": 2
  }
]
```

---

## 3. Get User Accounts

### Request
```bash
GET /api/v1/users/{user_id}/accounts
```

```bash
curl http://localhost:8000/api/v1/users/user_001/accounts
```

### Response (200 OK)
```json
[
  {
    "user_id": "user_001",
    "asset_type_code": "GOLD_COINS",
    "account_type": "USER",
    "id": "user_001_GOLD_COINS",
    "version": 0,
    "created_at": "2024-01-15T10:00:00",
    "updated_at": "2024-01-15T10:00:00"
  },
  {
    "user_id": "user_001",
    "asset_type_code": "DIAMONDS",
    "account_type": "USER",
    "id": "user_001_DIAMONDS",
    "version": 0,
    "created_at": "2024-01-15T10:00:00",
    "updated_at": "2024-01-15T10:00:00"
  }
]
```

---

## 4. Get Wallet Balance

### Request
```bash
GET /api/v1/wallets/{user_id}/balance
```

```bash
curl http://localhost:8000/api/v1/wallets/user_001/balance
```

### Response (200 OK)
```json
{
  "user_id": "user_001",
  "balances": [
    {
      "asset_type": "GOLD_COINS",
      "balance": "1000.00",
      "account_id": "user_001_GOLD_COINS"
    },
    {
      "asset_type": "DIAMONDS",
      "balance": "100.00",
      "account_id": "user_001_DIAMONDS"
    }
  ],
  "timestamp": "2024-01-15T10:30:00"
}
```

---

## 5. Wallet Top-up (Purchase)

### Request
```bash
POST /api/v1/transactions/topup
Content-Type: application/json

{
  "user_id": "user_001",
  "asset_type": "GOLD_COINS",
  "amount": "100.00",
  "idempotency_key": "topup_20240115_001",
  "metadata": {
    "payment_id": "pay_xyz123",
    "payment_method": "credit_card",
    "payment_provider": "stripe"
  }
}
```

```bash
curl -X POST http://localhost:8000/api/v1/transactions/topup \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "asset_type": "GOLD_COINS",
    "amount": "100.00",
    "idempotency_key": "topup_20240115_001",
    "metadata": {
      "payment_id": "pay_xyz123",
      "payment_method": "credit_card"
    }
  }'
```

### Response (201 Created)
```json
{
  "id": "txn_a1b2c3d4e5f6g7h8",
  "transaction_type": "TOPUP",
  "status": "COMPLETED",
  "user_id": "user_001",
  "asset_type_code": "GOLD_COINS",
  "amount": "100.00",
  "description": "Wallet top-up for user_001",
  "metadata": {
    "payment_id": "pay_xyz123",
    "payment_method": "credit_card",
    "payment_provider": "stripe"
  },
  "idempotency_key": "topup_20240115_001",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

---

## 6. Bonus/Incentive

### Request
```bash
POST /api/v1/transactions/bonus
Content-Type: application/json

{
  "user_id": "user_001",
  "asset_type": "LOYALTY_POINTS",
  "amount": "50.00",
  "idempotency_key": "bonus_20240115_001",
  "metadata": {
    "reason": "referral_bonus",
    "referral_code": "REF123",
    "referred_user": "user_003"
  }
}
```

```bash
curl -X POST http://localhost:8000/api/v1/transactions/bonus \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "asset_type": "LOYALTY_POINTS",
    "amount": "50.00",
    "idempotency_key": "bonus_20240115_001",
    "metadata": {
      "reason": "referral_bonus",
      "referral_code": "REF123"
    }
  }'
```

### Response (201 Created)
```json
{
  "id": "txn_i9j0k1l2m3n4o5p6",
  "transaction_type": "BONUS",
  "status": "COMPLETED",
  "user_id": "user_001",
  "asset_type_code": "LOYALTY_POINTS",
  "amount": "50.00",
  "description": "Bonus credit for user_001",
  "metadata": {
    "reason": "referral_bonus",
    "referral_code": "REF123",
    "referred_user": "user_003"
  },
  "idempotency_key": "bonus_20240115_001",
  "created_at": "2024-01-15T10:35:00",
  "updated_at": "2024-01-15T10:35:00"
}
```

---

## 7. Purchase/Spend

### Request
```bash
POST /api/v1/transactions/spend
Content-Type: application/json

{
  "user_id": "user_001",
  "asset_type": "GOLD_COINS",
  "amount": "25.00",
  "idempotency_key": "spend_20240115_001",
  "metadata": {
    "item_id": "skin_dragon_001",
    "item_name": "Dragon Skin Premium",
    "item_category": "cosmetics",
    "quantity": 1
  }
}
```

```bash
curl -X POST http://localhost:8000/api/v1/transactions/spend \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "asset_type": "GOLD_COINS",
    "amount": "25.00",
    "idempotency_key": "spend_20240115_001",
    "metadata": {
      "item_id": "skin_dragon_001",
      "item_name": "Dragon Skin Premium"
    }
  }'
```

### Response (201 Created)
```json
{
  "id": "txn_q7r8s9t0u1v2w3x4",
  "transaction_type": "SPEND",
  "status": "COMPLETED",
  "user_id": "user_001",
  "asset_type_code": "GOLD_COINS",
  "amount": "25.00",
  "description": "Purchase by user_001",
  "metadata": {
    "item_id": "skin_dragon_001",
    "item_name": "Dragon Skin Premium",
    "item_category": "cosmetics",
    "quantity": 1
  },
  "idempotency_key": "spend_20240115_001",
  "created_at": "2024-01-15T10:40:00",
  "updated_at": "2024-01-15T10:40:00"
}
```

### Error Response - Insufficient Balance (400 Bad Request)
```json
{
  "detail": "Insufficient balance. Current: 10.00, Required: 25.00"
}
```

---

## 8. Get Transaction History

### Request
```bash
GET /api/v1/wallets/{user_id}/transactions?limit=10&offset=0
```

```bash
curl "http://localhost:8000/api/v1/wallets/user_001/transactions?limit=10&offset=0"
```

### Response (200 OK)
```json
[
  {
    "id": "txn_q7r8s9t0u1v2w3x4",
    "transaction_type": "SPEND",
    "status": "COMPLETED",
    "user_id": "user_001",
    "asset_type_code": "GOLD_COINS",
    "amount": "25.00",
    "description": "Purchase by user_001",
    "metadata": {
      "item_id": "skin_dragon_001",
      "item_name": "Dragon Skin Premium"
    },
    "idempotency_key": "spend_20240115_001",
    "created_at": "2024-01-15T10:40:00",
    "updated_at": "2024-01-15T10:40:00"
  },
  {
    "id": "txn_i9j0k1l2m3n4o5p6",
    "transaction_type": "BONUS",
    "status": "COMPLETED",
    "user_id": "user_001",
    "asset_type_code": "LOYALTY_POINTS",
    "amount": "50.00",
    "description": "Bonus credit for user_001",
    "metadata": {
      "reason": "referral_bonus",
      "referral_code": "REF123"
    },
    "idempotency_key": "bonus_20240115_001",
    "created_at": "2024-01-15T10:35:00",
    "updated_at": "2024-01-15T10:35:00"
  }
]
```

---

## 9. Get Specific Transaction

### Request
```bash
GET /api/v1/transactions/{transaction_id}
```

```bash
curl http://localhost:8000/api/v1/transactions/txn_a1b2c3d4e5f6g7h8
```

### Response (200 OK)
```json
{
  "id": "txn_a1b2c3d4e5f6g7h8",
  "transaction_type": "TOPUP",
  "status": "COMPLETED",
  "user_id": "user_001",
  "asset_type_code": "GOLD_COINS",
  "amount": "100.00",
  "description": "Wallet top-up for user_001",
  "metadata": {
    "payment_id": "pay_xyz123",
    "payment_method": "credit_card"
  },
  "idempotency_key": "topup_20240115_001",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

### Error Response - Not Found (404)
```json
{
  "detail": "Transaction txn_invalid123 not found"
}
```

---

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

Response:
```json
{
  "id": "txn_abc123",
  ...
}
```

### Duplicate Request (Same Idempotency Key)
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

Response (Same transaction ID):
```json
{
  "id": "txn_abc123",
  ...
}
```

**Note**: The transaction ID is the same, proving idempotency works!

---

## PowerShell Examples (Windows)

### Get Balance
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/wallets/user_001/balance" | Select-Object -Expand Content | ConvertFrom-Json
```

### Create Top-up Transaction
```powershell
$body = @{
    user_id = "user_001"
    asset_type = "GOLD_COINS"
    amount = "100.00"
    idempotency_key = "topup_$(Get-Date -Format 'yyyyMMddHHmmss')"
    metadata = @{
        payment_id = "pay_xyz123"
    }
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/v1/transactions/topup" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

---

## Error Responses

### 400 Bad Request - Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "amount"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal Server Error",
  "detail": "Database connection failed",
  "timestamp": "2024-01-15T10:30:00"
}
```
