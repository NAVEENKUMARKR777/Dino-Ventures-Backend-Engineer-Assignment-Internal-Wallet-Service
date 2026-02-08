# Dino Ventures Internal Wallet Service

A high-performance, transactionally secure wallet service designed for gaming platforms and loyalty rewards systems. Built with Python, FastAPI, and PostgreSQL, featuring ledger-based accounting, advanced concurrency control, and enterprise-grade reliability.

## 🎯 Problem Statement

This service manages virtual credits (Gold Coins, Diamonds, Loyalty Points) in a closed-loop system where data integrity is paramount. Every transaction must be accurately recorded, balances must never go negative or out of sync, and no transactions can be lost—even under heavy traffic or system failures.

## 🏗️ Architecture Overview

### Technology Stack
- **Backend Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 15 with ACID transactions
- **ORM**: SQLAlchemy 2.0 with async support
- **Containerization**: Docker & Docker Compose
- **API Documentation**: OpenAPI/Swagger (auto-generated)

### Key Features
- ✅ **Ledger-Based Architecture**: Double-entry bookkeeping for complete auditability
- ✅ **ACID Compliance**: All transactions are atomic, consistent, isolated, and durable
- ✅ **Concurrency Control**: Advanced deadlock avoidance and retry mechanisms
- ✅ **Idempotency**: Prevent duplicate transaction processing
- ✅ **RESTful API**: Clean, documented endpoints for all operations
- ✅ **Health Monitoring**: Built-in health checks and monitoring
- ✅ **Containerized**: Easy deployment with Docker Compose

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Setup & Run

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd "dino-ventures-backend-engineer-assignment-internal-wallet-service"
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Manual Setup (Alternative)**
   ```bash
   # Copy environment file
   cp .env.example .env
   
   # Build and start services
   docker-compose build
   docker-compose up -d
   
   # Wait for services to start
   sleep 10
   ```

3. **Verify Installation**
   ```bash
   # Check health
   curl http://localhost:8001/health
   
   # View API documentation
   open http://localhost:8001/docs
   ```

### 🎯 **Service URLs**
- **API Base URL**: `http://localhost:8001`
- **Interactive Docs**: `http://localhost:8001/docs`
- **Health Check**: `http://localhost:8001/health`
- **Database**: `localhost:5432`

## 📊 Database Schema

### Core Tables

#### Assets
Defines virtual currencies available in the system.
- `Gold Coins (GC)`: Primary in-game currency
- `Diamonds (DI)`: Premium currency for exclusive items  
- `Loyalty Points (LP)`: Reward points for user engagement

#### Wallets
User and system wallets with balance tracking.
- **System Wallets**: Treasury accounts for fund sources
- **User Wallets**: Individual user balances per asset

#### Transactions
Transaction records with full metadata and status tracking.
- **Types**: `topup`, `bonus`, `purchase`
- **Idempotency**: Optional keys to prevent duplicates

#### Ledger Entries
Double-entry ledger with complete balance snapshots.
- **Audit Trail**: Before/after balances for every transaction
- **Integrity**: Ensures debits always equal credits

## 🔄 Core Transaction Flows

### 1. Wallet Top-up (Purchase)
```json
POST /transaction
{
  "transaction_type": "topup",
  "user_id": "user_001",
  "asset_code": "GC",
  "amount": 100.00,
  "description": "Purchased 100 Gold Coins",
  "idempotency_key": "topup_12345"
}
```
**Flow**: System Treasury → User Wallet

### 2. Bonus/Incentive
```json
POST /transaction
{
  "transaction_type": "bonus",
  "user_id": "user_001", 
  "asset_code": "LP",
  "amount": 50.00,
  "description": "Referral bonus",
  "idempotency_key": "bonus_67890"
}
```
**Flow**: System Treasury → User Wallet

### 3. Purchase/Spend
```json
POST /transaction
{
  "transaction_type": "purchase",
  "user_id": "user_001",
  "asset_code": "GC", 
  "amount": 25.00,
  "description": "Bought in-game item",
  "idempotency_key": "purchase_11111"
}
```
**Flow**: User Wallet → System Treasury

## 🛡️ Concurrency & Reliability Strategy

### Deadlock Avoidance
- **Ordered Locking**: Always acquire wallet locks in ascending ID order
- **Lock Manager**: Centralized lock management with timeout handling
- **Retry Logic**: Automatic retry with exponential backoff for conflicts

### Idempotency Implementation
- **Idempotency Keys**: Optional unique identifiers per request
- **Duplicate Detection**: Pre-transaction validation
- **Consistent Responses**: Return original transaction for duplicates

### ACID Transaction Guarantees
- **Atomicity**: All-or-nothing transaction execution
- **Consistency**: Database always remains in valid state
- **Isolation**: Concurrent transactions don't interfere
- **Durability**: Committed transactions survive failures

## 📡 API Endpoints

### Assets & Balances
- `GET /assets` - List all available assets
- `GET /balance/{user_id}` - Get all user balances
- `GET /balance/{user_id}/{asset_code}` - Get specific balance

### Transactions
- `POST /transaction` - Process wallet transaction
- `GET /transaction/{user_id}/history` - Get transaction history

### System
- `GET /` - Health check
- `GET /health` - Detailed health check with DB status
- `GET /docs` - Interactive API documentation

## 🧪 **Automated Testing**

### Quick Test Script
```bash
python test_api.py
```

This script automatically tests all endpoints and provides a comprehensive report.

### Manual Testing Commands

#### **PowerShell Commands (Recommended for Windows)**
```powershell
# Get all assets
curl http://localhost:8001/assets

# Get user balances
curl http://localhost:8001/balance/user_001

# Top-up transaction
Invoke-WebRequest -Uri http://localhost:8001/transaction -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"transaction_type":"topup","user_id":"user_001","asset_code":"GC","amount":100.00,"description":"Test top-up"}'

# Bonus transaction
Invoke-WebRequest -Uri http://localhost:8001/transaction -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"transaction_type":"bonus","user_id":"user_001","asset_code":"LP","amount":50.00,"description":"Test bonus"}'

# Purchase transaction
Invoke-WebRequest -Uri http://localhost:8001/transaction -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"transaction_type":"purchase","user_id":"user_001","asset_code":"GC","amount":25.00,"description":"Test purchase"}'

# Transaction history
curl http://localhost:8001/transaction/user_001/history
```

#### **Unix/Linux Commands**
```bash
# Get all assets
curl http://localhost:8001/assets

# Get user balances
curl http://localhost:8001/balance/user_001

# Top-up transaction
curl -X POST http://localhost:8001/transaction \
  -H "Content-Type: application/json" \
  -d '{"transaction_type":"topup","user_id":"user_001","asset_code":"GC","amount":100.00,"description":"Test top-up"}'

# Bonus transaction
curl -X POST http://localhost:8001/transaction \
  -H "Content-Type: application/json" \
  -d '{"transaction_type":"bonus","user_id":"user_001","asset_code":"LP","amount":50.00,"description":"Test bonus"}'

# Purchase transaction
curl -X POST http://localhost:8001/transaction \
  -H "Content-Type: application/json" \
  -d '{"transaction_type":"purchase","user_id":"user_001","asset_code":"GC","amount":25.00,"description":"Test purchase"}'

# Transaction history
curl http://localhost:8001/transaction/user_001/history
```

## 🐳 Docker Configuration

### Services
- **postgres**: PostgreSQL 15 with automatic seeding
- **wallet_api**: FastAPI application (runs on port 8001)
- **redis**: Redis for future caching needs

### Volumes
- **postgres_data**: Persistent database storage
- **redis_data**: Redis data persistence

### Health Checks
- Database connectivity checks
- API health endpoint monitoring
- Automatic restart on failures

### Port Configuration
- **API**: Host port 8001 → Container port 8000
- **Database**: Host port 5432 → Container port 5432
- **Redis**: Host port 6379 → Container port 6379

## 📈 Performance Considerations

### Database Optimization
- **Indexes**: Strategic indexing on frequently queried columns
- **Connection Pooling**: Efficient database connection management
- **Query Optimization**: Optimized SQL queries with proper joins

### Concurrency Handling
- **Pessimistic Locking**: Row-level locks for critical operations
- **Deadlock Detection**: Automatic detection and recovery
- **Retry Mechanisms**: Configurable retry policies

### Scalability Features
- **Stateless API**: Easy horizontal scaling
- **Connection Management**: Efficient resource utilization
- **Async Operations**: Non-blocking I/O where applicable

## 🔧 Configuration

### Environment Variables
```bash
DATABASE_URL=postgresql://wallet_user:wallet_password@localhost:5432/wallet_service
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=wallet_service
DATABASE_USER=wallet_user
DATABASE_PASSWORD=wallet_password
```

### Docker Compose Settings
- **Resource Limits**: Configurable memory/CPU limits
- **Network Isolation**: Secure internal networking
- **Volume Management**: Persistent data storage

## 🚀 Deployment

### Local Development
```bash
docker-compose up -d
```

### Production Deployment
The service is containerized and ready for deployment to any container orchestration platform:
- **Docker Swarm**
- **Kubernetes** 
- **Cloud Services** (AWS ECS, Google Cloud Run, Azure Container Instances)

### Railway Deployment (Extra Credit)
The service includes Railway-compatible configuration for easy cloud deployment.

## 🔍 Monitoring & Logging

### Application Logs
- **Structured Logging**: JSON-formatted logs
- **Log Levels**: DEBUG, INFO, WARNING, ERROR
- **Request Tracking**: Unique request IDs for tracing

### Health Monitoring
- **Database Health**: Connection and query performance
- **API Health**: Endpoint availability and response times
- **Resource Usage**: Memory and CPU monitoring

## 🛠️ Development

### Project Structure
```
app/
├── __init__.py
├── main.py              # FastAPI application
├── database.py          # Database configuration
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas
├── wallet_service.py    # Business logic
└── concurrency.py       # Concurrency control
```

### Adding New Features
1. Update models in `models.py`
2. Add schemas in `schemas.py`
3. Implement business logic in `wallet_service.py`
4. Add API endpoints in `main.py`
5. Update tests and documentation

## 🤝 Contributing

### Code Quality
- **Type Hints**: Full type annotation coverage
- **Documentation**: Comprehensive docstrings
- **Error Handling**: Graceful error management
- **Testing**: Unit and integration tests

### Best Practices
- **Security**: Input validation and SQL injection prevention
- **Performance**: Efficient database queries
- **Reliability**: Comprehensive error handling
- **Maintainability**: Clean, modular code structure

## 📄 License

This project is part of the Dino Ventures Backend Engineer Assignment.

## 🎉 **Summary & Verification**

This Internal Wallet Service demonstrates enterprise-grade backend development with:

✅ **Complete Requirements Fulfillment**
- All three transaction flows (topup, bonus, purchase)
- Data seeding with assets, system accounts, and users
- RESTful API with comprehensive endpoints
- ACID compliance and data integrity

✅ **Advanced Engineering Excellence**
- Ledger-based double-entry accounting
- Sophisticated concurrency control with deadlock avoidance
- Full idempotency implementation
- Containerized deployment with Docker Compose

✅ **Production-Ready Features**
- Health monitoring and logging
- Comprehensive error handling
- Performance optimization
- Security best practices

✅ **Verified Working Endpoints**
- **API Base URL**: `http://localhost:8001`
- **Interactive Documentation**: `http://localhost:8001/docs`
- **Health Check**: `http://localhost:8001/health`
- **All Transaction Types**: Tested and working
- **Balance Queries**: Accurate and real-time
- **Transaction History**: Complete audit trail

### 🚀 **Ready for Production**
The service is immediately runnable with:
- Automated setup script (`./setup.sh`)
- Complete Docker configuration
- Comprehensive testing suite
- Railway deployment configuration
- Full documentation

**All endpoints have been tested and verified working correctly!** 🎯
