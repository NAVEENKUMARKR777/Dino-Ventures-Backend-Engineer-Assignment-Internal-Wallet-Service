# Dino Ventures - Internal Wallet Service

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](TEST_RESULTS.md)
[![API](https://img.shields.io/badge/API-FastAPI-009688)](http://localhost:8001/docs)
[![Python](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791)](https://www.postgresql.org/)

A production-ready wallet service implementing a **double-entry ledger system** for managing application credits (Gold Coins, Diamonds, Loyalty Points) with complete transactional integrity.

> **✅ Status:** All endpoints tested and verified. See [TEST_RESULTS.md](TEST_RESULTS.md) for detailed test report.

## 🎯 Features

### Core Requirements
- ✅ **Double-Entry Ledger Architecture**: Full audit trail of all transactions
- ✅ **ACID Transactions**: PostgreSQL with row-level locking
- ✅ **Idempotency**: Prevent duplicate transactions using idempotency keys
- ✅ **Concurrency Control**: Row-level locks and optimistic locking
- ✅ **Deadlock Avoidance**: Consistent lock ordering (alphabetically by account ID)
- ✅ **RESTful API**: FastAPI with automatic OpenAPI documentation
- ✅ **Docker Support**: Full containerization with docker-compose
- ✅ **Railway Deployment**: Ready for cloud deployment

### Transaction Types
1. **Wallet Top-up**: User purchases credits (assumes working payment system)
2. **Bonus/Incentive**: System issues free credits (referrals, promotions)
3. **Purchase/Spend**: User spends credits for in-app services

## 🏗️ Technology Stack

### Backend
- **Language**: Python 3.11
- **Framework**: FastAPI (high-performance async framework)
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0 (async)
- **Validation**: Pydantic v2

### Why This Stack?
- **Python**: Excellent ecosystem, readable, maintainable
- **FastAPI**: Auto-generated OpenAPI docs, async support, type hints
- **PostgreSQL**: ACID compliance, row-level locking, excellent concurrency
- **SQLAlchemy**: Mature ORM with advanced transaction management
- **Docker**: Reproducible environments, easy deployment

## 🚀 Quick Start

> **📌 Note:** The API runs on **port 8001** (mapped from container port 8000) to avoid conflicts with other services.

### Prerequisites
- Docker and Docker Compose installed
- Or: Python 3.11+ and PostgreSQL 15+

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd "Dino Ventures Backend Engineer Assignment Internal Wallet Service"

# Start all services (database + API)
docker-compose up -d

# Check logs
docker-compose logs -f api

# API will be available at http://localhost:8001
# API Documentation at http://localhost:8001/docs
```

The database will be automatically seeded with:
- 3 Asset types (Gold Coins, Diamonds, Loyalty Points)
- 1 System account (Treasury)
- 2 User accounts with initial balances

### Option 2: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://wallet_user:wallet_pass@localhost:5432/wallet_db"

# Start PostgreSQL (if not running)
# Run migrations and seed data
python -m app.scripts.seed

# Start the API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Verify Setup

```bash
# Check API health
curl http://localhost:8001/health

# Get all users
curl http://localhost:8001/api/v1/users

# Check a user's balance
curl http://localhost:8001/api/v1/wallets/user_001/balance
```

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **Test Results**: [TEST_RESULTS.md](TEST_RESULTS.md)

### Key Endpoints

#### Transaction Operations
```bash
# 1. Wallet Top-up (Purchase)
POST /api/v1/transactions/topup
{
  "user_id": "user_001",
  "asset_type": "GOLD_COINS",
  "amount": "100.00",
  "idempotency_key": "unique-key-123",
  "metadata": {
    "payment_id": "pay_xyz",
    "payment_method": "credit_card"
  }
}

# 2. Bonus/Incentive
POST /api/v1/transactions/bonus
{
  "user_id": "user_001",
  "asset_type": "LOYALTY_POINTS",
  "amount": "50.00",
  "idempotency_key": "bonus-key-456",
  "metadata": {
    "reason": "referral_bonus",
    "referral_code": "REF123"
  }
}

# 3. Purchase/Spend
POST /api/v1/transactions/spend
{
  "user_id": "user_001",
  "asset_type": "GOLD_COINS",
  "amount": "25.00",
  "idempotency_key": "spend-key-789",
  "metadata": {
    "item_id": "skin_premium_001",
    "item_name": "Dragon Skin"
  }
}
```

#### Balance & Transaction History
```bash
# Get wallet balance
GET /api/v1/wallets/{user_id}/balance

# Get transaction history
GET /api/v1/wallets/{user_id}/transactions?limit=50&offset=0

# Get specific transaction
GET /api/v1/transactions/{transaction_id}
```

## 🏛️ Architecture

### Double-Entry Ledger System

Every transaction creates **two ledger entries** (debit and credit) ensuring:
- Complete audit trail
- Balance integrity (sum of all entries = 0)
- Historical accuracy

```
Example: User purchases 100 Gold Coins for $10

Ledger Entries:
1. DEBIT  - User Account    +100 GOLD_COINS
2. CREDIT - System Account  -100 GOLD_COINS

Transaction Record:
- Type: TOPUP
- Amount: 100
- Status: COMPLETED
- Metadata: {payment_id: "pay_xyz"}
```

### Database Schema

```sql
-- Core Tables
accounts: Wallet accounts (users, system)
asset_types: Currency definitions (Gold Coins, etc.)
transactions: Transaction records
ledger_entries: Double-entry bookkeeping
idempotency_keys: Prevent duplicate operations

-- Key Indexes
- user_id, asset_type for fast balance queries
- idempotency_key for duplicate detection
- transaction_id for audit trails
```

### Concurrency Strategy

1. **Row-Level Locking**: `SELECT ... FOR UPDATE` on accounts
2. **Lock Ordering**: Always lock accounts in alphabetical order to prevent deadlocks
3. **Optimistic Locking**: Version numbers on critical records
4. **Idempotency**: Unique keys prevent duplicate transactions
5. **Transaction Isolation**: `SERIALIZABLE` level for critical operations

### Deadlock Prevention

```python
# Always acquire locks in consistent order (alphabetical)
account_ids = sorted([source_account_id, dest_account_id])
locked_accounts = []
for account_id in account_ids:
    account = await session.execute(
        select(Account)
        .where(Account.id == account_id)
        .with_for_update()  # Row-level lock
    )
    locked_accounts.append(account)
```

## 🧪 Testing

### Automated Testing

```bash
# Run unit tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

### Manual API Testing

All endpoints have been thoroughly tested. See **[TEST_RESULTS.md](TEST_RESULTS.md)** for complete test report.

**Quick Test Commands:**

```powershell
# Health check
curl http://localhost:8001/health

# Get user balance
Invoke-RestMethod -Uri "http://localhost:8001/api/v1/wallets/user_001/balance"

# Create a top-up transaction
$body = @{
    user_id = "user_001"
    asset_type = "GOLD_COINS"
    amount = "100.00"
    idempotency_key = "test_$(Get-Date -Format 'yyyyMMddHHmmss')"
    metadata = @{payment_id = "pay_123"}
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/api/v1/transactions/topup" `
    -Method POST -Body $body -ContentType "application/json"
```

### Test Results Summary

✅ **All 10 endpoint categories tested and verified:**
- Health & System endpoints
- User management
- Balance queries
- Transaction operations (Topup, Bonus, Spend)
- Transaction history
- Idempotency verification
- Error handling

**Success Rate: 100%** - See [TEST_RESULTS.md](TEST_RESULTS.md) for details.

### Load Testing
```bash
# Load testing
locust -f tests/load_test.py --host=http://localhost:8001
```

## 🐳 Docker Details

### Services
- **db**: PostgreSQL 15 with persistent volume
- **api**: FastAPI application

### Volumes
- `postgres_data`: Persistent database storage

### Networks
- `wallet-network`: Internal communication

### Environment Variables
```env
DATABASE_URL=postgresql+asyncpg://wallet_user:wallet_pass@db:5432/wallet_db
ENVIRONMENT=production
LOG_LEVEL=info
```

## 🚢 Deployment (Railway)

### Steps
1. Install Railway CLI: `npm i -g @railway/cli`
2. Login: `railway login`
3. Initialize: `railway init`
4. Add PostgreSQL: `railway add`
5. Deploy: `railway up`

### Environment Setup
```bash
# Railway will auto-detect Dockerfile
# Set environment variable:
DATABASE_URL=<railway-postgres-url>
```

## 📊 Monitoring & Logging

- Structured JSON logging
- Request/response logging
- Transaction audit trail
- Error tracking with stack traces

## 🔒 Security Considerations

- Input validation with Pydantic
- SQL injection prevention (ORM)
- Transaction amount limits
- Rate limiting (configurable)
- CORS configuration

## 🎯 Performance

- Async I/O for high concurrency
- Connection pooling
- Indexed queries
- Batch operations support

## 📝 Data Seeding

The system comes pre-seeded with:

**Asset Types:**
- Gold Coins (in-game currency)
- Diamonds (premium currency)
- Loyalty Points (rewards)

**System Account:**
- Treasury (source/sink for all funds)

**User Accounts:**
- user_001: Alice (1000 Gold Coins, 100 Diamonds)
- user_002: Bob (500 Gold Coins, 50 Loyalty Points)

## 🛠️ Development

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Format code
black app/
isort app/

# Lint
flake8 app/
mypy app/

# Database migrations (Alembic)
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## 📖 Project Structure

```
.
├── app/
│   ├── main.py              # FastAPI application entry
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection
│   ├── models/              # SQLAlchemy models
│   │   ├── account.py
│   │   ├── asset_type.py
│   │   ├── transaction.py
│   │   └── ledger.py
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   │   ├── wallet_service.py
│   │   └── transaction_service.py
│   ├── routers/             # API routes
│   └── scripts/
│       └── seed.py          # Database seeding
├── tests/                   # Test suite
├── alembic/                 # Database migrations
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 🤝 Contributing

This is an assignment project, but feedback is welcome!

## 📄 License

MIT License

## 👤 Author

Dino Ventures Backend Engineer Assignment

## 🙏 Acknowledgments

Built with modern best practices for production-grade wallet systems.

---

## 📚 Complete Documentation

This project includes comprehensive documentation:

| Document | Description |
|----------|-------------|
| [README.md](README.md) | Main project overview and setup guide (this file) |
| [QUICKSTART.md](QUICKSTART.md) | Get started in 5 minutes |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Deep dive into system architecture |
| [ARCHITECTURE_DIAGRAM.txt](ARCHITECTURE_DIAGRAM.txt) | ASCII architecture diagrams |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Railway deployment guide |
| [API_EXAMPLES.md](API_EXAMPLES.md) | Comprehensive API usage examples |
| [TEST_RESULTS.md](TEST_RESULTS.md) | Complete API testing results |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | Executive summary and features |
| [ASSIGNMENT_CHECKLIST.md](ASSIGNMENT_CHECKLIST.md) | Requirements verification |

## 🔗 Quick Links

- **📖 API Documentation:** [http://localhost:8001/docs](http://localhost:8001/docs)
- **📊 Test Results:** [TEST_RESULTS.md](TEST_RESULTS.md)
- **🏗️ Architecture:** [ARCHITECTURE.md](ARCHITECTURE.md)
- **🚀 Quick Start:** [QUICKSTART.md](QUICKSTART.md)
- **☁️ Deploy:** [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 🎯 Project Status

✅ **Production Ready**
- All core requirements implemented
- All bonus features completed
- 100% endpoint test coverage
- Comprehensive documentation
- Docker containerized
- Railway deployment ready

**Build Date:** 2026-02-08  
**Version:** 1.0.0  
**Status:** ✅ Complete & Tested
