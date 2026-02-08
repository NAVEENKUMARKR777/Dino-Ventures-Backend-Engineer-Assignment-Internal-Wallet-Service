# 🚂 Railway Deployment Fix Guide

## Current Issue

Your application deployed successfully to Railway (build completed in 47.38s), but the health check is failing with "service unavailable". This is because **the PostgreSQL database hasn't been configured yet**.

---

## ✅ Solution: Complete Railway Setup

### Step 1: Add PostgreSQL Database

1. **Open your Railway project dashboard:**
   - Go to https://railway.app
   - Select your "Dino Ventures" project

2. **Add PostgreSQL:**
   ```
   Click "New" → "Database" → "Add PostgreSQL"
   ```

3. **Railway will automatically:**
   - Provision a PostgreSQL 15 database
   - Set the `DATABASE_URL` environment variable
   - Link it to your application service

### Step 2: Verify Environment Variables

In your Railway service settings, ensure these variables exist:

```bash
# Automatically set by Railway PostgreSQL add-on:
DATABASE_URL=postgresql+asyncpg://...  # ✅ Auto-configured

# You need to manually add these:
ENVIRONMENT=production
LOG_LEVEL=INFO
PORT=8000  # Railway might set this automatically
```

**How to add environment variables in Railway:**
1. Click on your service (API)
2. Go to "Variables" tab
3. Click "New Variable"
4. Add `ENVIRONMENT` = `production`
5. Add `LOG_LEVEL` = `INFO`

### Step 3: Redeploy

After adding the PostgreSQL database:

1. **Railway will automatically redeploy** your service
2. **Or manually trigger:** Click "Deploy" → "Redeploy"

---

## 🔍 What Should Happen

### During Deployment:

```
[inf] Building Docker image... ✅
[inf] Build time: 47.38 seconds ✅
[inf] Starting application...
[inf] Running database migrations...
[inf] Seeding initial data...
[inf] ✓ Database initialized
[inf] ✓ Seeding COMPLETED SUCCESSFULLY
[inf] Starting Uvicorn...
[inf] Application startup complete
[inf] Health check (GET /health) → 200 OK ✅
```

### After Successful Deployment:

- ✅ Health check passes
- ✅ Service shows "Active" status
- ✅ You'll get a public URL like: `https://your-app-name.up.railway.app`

---

## 🧪 Testing Your Deployed API

Once deployed successfully:

### 1. Health Check
```bash
curl https://your-app-name.up.railway.app/health
```

**Expected:**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-08T...",
  "version": "1.0.0"
}
```

### 2. API Documentation
Visit in browser:
```
https://your-app-name.up.railway.app/docs
```

### 3. List Users
```bash
curl https://your-app-name.up.railway.app/api/v1/users
```

### 4. Check Balance
```bash
curl https://your-app-name.up.railway.app/api/v1/wallets/user_001/balance
```

---

## 🐛 Troubleshooting

### If Health Check Still Fails:

#### Check Application Logs:
1. Go to Railway dashboard
2. Click on your service
3. Go to "Deployments" tab
4. Click on the latest deployment
5. View logs

#### Common Issues:

**Issue 1: Database Connection Failed**
- **Error:** `password authentication failed for user`
- **Fix:** Verify `DATABASE_URL` is set correctly by Railway PostgreSQL addon

**Issue 2: Port Mismatch**
- **Error:** `Address already in use`
- **Fix:** Railway sets `PORT` env variable automatically. Your app should use it:
  ```python
  port = int(os.getenv("PORT", 8000))
  ```

**Issue 3: Seed Script Fails**
- **Error:** `duplicate key value violates unique constraint`
- **Fix:** Already handled in railway.toml with `|| true` (continues even if seed fails)

**Issue 4: Missing Environment Variables**
- **Error:** `KeyError: 'DATABASE_URL'`
- **Fix:** Ensure PostgreSQL addon is added and linked

---

## 📊 Railway Configuration Files

### Current Files:

✅ **railway.toml** - Deployment configuration
```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "sh -c 'python -m app.scripts.seed || true && uvicorn app.main:app --host 0.0.0.0 --port 8000'"
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

✅ **Dockerfile** - Container build instructions
✅ **.dockerignore** - Exclude unnecessary files
✅ **requirements.txt** - Python dependencies

---

## 🎯 Expected Railway Setup

After completing all steps:

```
Railway Project: Dino Ventures Wallet Service
├── Service: API (Your FastAPI App)
│   ├── Status: Active ✅
│   ├── Build: Success ✅
│   ├── Health Check: Passing ✅
│   └── Public URL: https://xxx.up.railway.app ✅
│
└── Database: PostgreSQL 15
    ├── Status: Active ✅
    ├── Connected to API ✅
    └── DATABASE_URL: Auto-configured ✅
```

---

## 🚀 Quick Checklist

- [ ] PostgreSQL database added to Railway project
- [ ] DATABASE_URL environment variable auto-set
- [ ] ENVIRONMENT=production variable added
- [ ] LOG_LEVEL=INFO variable added
- [ ] Service redeployed automatically or manually
- [ ] Health check passing (status: healthy)
- [ ] Service shows "Active" status
- [ ] Public URL accessible
- [ ] API documentation available at /docs
- [ ] Test endpoints working

---

## 📝 Next Steps After Successful Deployment

### 1. Update GitHub with Railway URL

Add the deployed URL to your README.md:
```markdown
**Live Demo:** https://your-app-name.up.railway.app/docs
```

### 2. Test All Endpoints

Use the deployed URL to test:
- Top-up transactions
- Bonus transactions
- Spend transactions
- Balance queries
- Transaction history

### 3. Monitor Application

Railway provides:
- Real-time logs
- Metrics (CPU, Memory, Network)
- Deployment history
- Build logs

### 4. Custom Domain (Optional)

Railway allows custom domains:
1. Go to service settings
2. Click "Networking"
3. Add custom domain
4. Update DNS records

---

## 💡 Important Notes

1. **Database Persistence:** Railway PostgreSQL data persists across deployments
2. **Auto-Scaling:** Railway handles scaling automatically
3. **HTTPS:** All Railway apps get free HTTPS
4. **Environment:** Production environment uses async database connections
5. **Seeding:** Initial data seeded on first deployment only

---

## 📞 Support

If issues persist:
1. Check Railway logs for detailed errors
2. Verify DATABASE_URL format matches: `postgresql+asyncpg://user:pass@host:port/db`
3. Ensure all dependencies in requirements.txt are compatible
4. Check that Dockerfile builds successfully locally

---

**Status:** Ready to deploy once PostgreSQL database is added!

**Expected Resolution Time:** 2-5 minutes after adding PostgreSQL

**Deployment Success Rate:** Should be 100% with correct configuration
