# Quick Start Guide

Get the Dino Ventures Wallet Service running in just a few minutes!

## 🐳 Option 1: Docker (Fastest)

**Recommended for quickest setup**

### Prerequisites
- Docker Desktop installed and running

### Steps

1. **Clone repository** (if applicable)
   ```bash
   cd "Dino Ventures Backend Engineer Assignment Internal Wallet Service"
   ```

2. **Start all services**
   ```bash
   docker-compose up -d
   ```

3. **Check logs**
   ```bash
   docker-compose logs -f api
   ```

4. **Verify it's running**
   ```bash
   curl http://localhost:8000/health
   ```

5. **Open API docs in browser**
   ```
   http://localhost:8000/docs
   ```

That's it! The service is now running with a seeded database.

### Test the API

**Get user balances:**
```bash
curl http://localhost:8000/api/v1/wallets/user_001/balance
```

**Create a transaction:**
```bash
curl -X POST http://localhost:8000/api/v1/transactions/topup \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "asset_type": "GOLD_COINS",
    "amount": "50.00",
    "idempotency_key": "quickstart_test_001",
    "metadata": {"test": true}
  }'
```

### Stop services
```bash
docker-compose down
```

---

## 🐍 Option 2: Local Python

**For development and customization**

### Prerequisites
- Python 3.11 or higher
- PostgreSQL 15 or higher

### Steps

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**
   
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   
   Update `DATABASE_URL` in `.env` with your PostgreSQL credentials.

3. **Start PostgreSQL**
   
   Make sure PostgreSQL is running on `localhost:5432`.

4. **Run setup script**
   
   **Windows (PowerShell):**
   ```powershell
   .\setup.ps1
   ```
   
   **Linux/Mac:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

5. **Start the API server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Open API docs**
   ```
   http://localhost:8000/docs
   ```

---

## ☁️ Option 3: Railway (Cloud Deployment)

**For production deployment**

### Prerequisites
- Railway account: [railway.app](https://railway.app)
- Railway CLI: `npm install -g @railway/cli`

### Steps

1. **Login to Railway**
   ```bash
   railway login
   ```

2. **Initialize project**
   ```bash
   railway init
   ```

3. **Add PostgreSQL**
   ```bash
   railway add
   ```
   Select PostgreSQL.

4. **Set environment variables**
   ```bash
   railway variables set ENVIRONMENT=production
   railway variables set LOG_LEVEL=info
   ```

5. **Deploy**
   ```bash
   railway up
   ```

6. **Get your URL**
   ```bash
   railway domain
   ```

Your API is now live! 🚀

Visit: `https://your-service.up.railway.app/docs`

---

## 📚 What's Next?

### Explore the API
- Visit `/docs` for interactive Swagger UI
- Visit `/redoc` for ReDoc documentation

### Read the Documentation
- **README.md**: Overview and detailed setup
- **ARCHITECTURE.md**: Deep dive into design decisions
- **API_EXAMPLES.md**: Comprehensive API examples
- **DEPLOYMENT.md**: Complete Railway deployment guide

### Run Tests
```bash
pytest tests/ -v
```

### Try Different Transactions

**Wallet Top-up:**
```bash
POST /api/v1/transactions/topup
```

**Bonus/Incentive:**
```bash
POST /api/v1/transactions/bonus
```

**Purchase/Spend:**
```bash
POST /api/v1/transactions/spend
```

See **API_EXAMPLES.md** for detailed examples.

---

## 🎯 Pre-seeded Data

The system comes with:

**Asset Types:**
- GOLD_COINS (in-game currency)
- DIAMONDS (premium currency)
- LOYALTY_POINTS (rewards)

**System Account:**
- SYSTEM_TREASURY (manages all funds)

**Demo Users:**
- **user_001** (Alice): 1000 Gold Coins, 100 Diamonds
- **user_002** (Bob): 500 Gold Coins, 50 Loyalty Points

---

## 🆘 Troubleshooting

### Docker Issues

**Port already in use:**
```bash
docker-compose down
# Change ports in docker-compose.yml if needed
```

**Database connection failed:**
```bash
docker-compose logs db
# Wait for database to be ready
```

### Local Python Issues

**Module not found:**
```bash
pip install -r requirements.txt
```

**Database connection error:**
- Verify PostgreSQL is running
- Check DATABASE_URL in `.env`
- Try: `psql -U wallet_user -d wallet_db`

### Railway Issues

**Check deployment logs:**
```bash
railway logs
```

**Verify environment variables:**
```bash
railway variables
```

---

## 🎉 Success Checklist

- ✅ Service is running
- ✅ Health check returns `{"status": "healthy"}`
- ✅ Can access `/docs` in browser
- ✅ Can list users: `/api/v1/users`
- ✅ Can get balance: `/api/v1/wallets/user_001/balance`
- ✅ Can create transaction: `POST /api/v1/transactions/topup`

**You're all set!** Start building on top of the wallet service. 🚀
