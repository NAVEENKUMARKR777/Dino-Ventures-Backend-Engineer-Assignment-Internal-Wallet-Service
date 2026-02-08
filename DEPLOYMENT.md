# Deployment Guide - Railway

This guide walks you through deploying the Dino Ventures Wallet Service to Railway.

## Prerequisites

1. Railway account (sign up at [railway.app](https://railway.app))
2. Railway CLI installed: `npm install -g @railway/cli`
3. Git repository with the project code

## Step 1: Prepare Your Project

Ensure your project has:
- ✅ `Dockerfile`
- ✅ `requirements.txt`
- ✅ `docker-compose.yml` (for local testing)
- ✅ Environment variables properly configured

## Step 2: Install Railway CLI

```bash
npm install -g @railway/cli
```

Verify installation:
```bash
railway --version
```

## Step 3: Login to Railway

```bash
railway login
```

This will open a browser window for authentication.

## Step 4: Initialize Project

In your project directory:

```bash
railway init
```

Choose:
- **Create a new project**: Yes
- **Project name**: `dino-ventures-wallet-service`

## Step 5: Add PostgreSQL Database

```bash
railway add
```

Select:
- **PostgreSQL**

Railway will provision a PostgreSQL database and set the `DATABASE_URL` environment variable.

## Step 6: Set Environment Variables

```bash
# Set environment to production
railway variables set ENVIRONMENT=production

# Set log level
railway variables set LOG_LEVEL=info

# Verify variables
railway variables
```

The `DATABASE_URL` is automatically set by Railway when you add PostgreSQL.

## Step 7: Deploy

```bash
railway up
```

This will:
1. Build your Docker container
2. Push to Railway
3. Deploy the service
4. Run database migrations/seeding automatically

## Step 8: Get Your Service URL

```bash
railway domain
```

Or visit the Railway dashboard to see your service URL.

Your API will be available at:
```
https://your-service.up.railway.app
```

## Step 9: Verify Deployment

Test the health endpoint:

```bash
curl https://your-service.up.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "version": "1.0.0"
}
```

## Step 10: Access API Documentation

Visit:
```
https://your-service.up.railway.app/docs
```

You'll see the full Swagger UI documentation.

## Environment Variables Reference

Railway automatically sets:
- `DATABASE_URL`: PostgreSQL connection string

You should manually set:
- `ENVIRONMENT`: `production`
- `LOG_LEVEL`: `info`
- `SECRET_KEY`: Generate a secure random string
- `ALLOWED_ORIGINS`: Your frontend URL (if applicable)

## Troubleshooting

### Check Logs

```bash
railway logs
```

### Database Connection Issues

Ensure `DATABASE_URL` is set:
```bash
railway variables
```

Should show:
```
DATABASE_URL=postgresql://...
```

### Port Issues

Railway automatically sets the `PORT` environment variable. Our Dockerfile uses port 8000, which Railway will map correctly.

### Seed Script Fails

The seed script runs automatically on container start (in `Dockerfile`). If it fails:

1. Check logs: `railway logs`
2. Manually run seed:
```bash
railway run python -m app.scripts.seed
```

## Continuous Deployment

Railway automatically deploys when you push to your connected Git repository.

### Connect Git Repository

In Railway dashboard:
1. Go to your project
2. Click "Settings"
3. Connect your GitHub repository
4. Select branch (e.g., `main`)

Now every push to `main` will trigger a deployment.

## Database Management

### Connect to Database

Get database credentials:
```bash
railway variables
```

Connect using `psql`:
```bash
railway connect postgres
```

Or use the connection string directly:
```bash
psql $DATABASE_URL
```

### Run Migrations

If you need to manually run migrations:

```bash
railway run python -m app.scripts.seed
```

### Backup Database

Railway provides automatic backups, but you can also manually backup:

```bash
railway run pg_dump $DATABASE_URL > backup.sql
```

## Monitoring

### View Metrics

In Railway dashboard:
- **CPU Usage**
- **Memory Usage**
- **Request Count**
- **Response Times**

### Set Up Alerts

Configure alerts in Railway dashboard for:
- High error rates
- High memory usage
- Service downtime

## Scaling

### Vertical Scaling

In Railway dashboard:
1. Go to "Settings"
2. Adjust resources:
   - **Memory**: 512MB, 1GB, 2GB, etc.
   - **CPU**: Shared, 1 vCPU, 2 vCPU, etc.

### Horizontal Scaling

Railway supports multiple replicas:
1. Go to "Settings"
2. Set **Replicas**: 2, 3, etc.

**Note**: Ensure your application is stateless for horizontal scaling.

## Cost Optimization

### Free Tier

Railway offers:
- $5 free credit monthly
- Sufficient for development/testing

### Production Costs

Estimate costs:
- **Database**: ~$5-10/month
- **API Service**: ~$5-15/month (depends on traffic)

### Optimize Costs

1. **Use appropriate resource sizes**: Don't over-provision
2. **Scale down during low traffic**: Adjust replicas
3. **Monitor usage**: Check Railway dashboard

## Security

### Environment Variables

Never commit secrets to Git. Always use Railway environment variables.

### HTTPS

Railway provides HTTPS automatically for all services.

### Database Security

Railway PostgreSQL is:
- Private by default
- Only accessible from your services
- SSL/TLS encrypted

## Custom Domain

To use a custom domain:

1. In Railway dashboard, go to "Settings"
2. Add custom domain: `api.yourdomain.com`
3. Update DNS records as instructed
4. Railway handles SSL certificate automatically

## CI/CD Pipeline

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Railway

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Install Railway CLI
        run: npm install -g @railway/cli
      
      - name: Deploy to Railway
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: railway up
```

Get `RAILWAY_TOKEN`:
```bash
railway login --browserless
```

Add token to GitHub secrets.

## Rollback

If a deployment fails:

```bash
railway rollback
```

This reverts to the previous deployment.

## Support

- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Community**: [Railway Discord](https://discord.gg/railway)
- **Status**: [railway.statuspage.io](https://railway.statuspage.io)

## Summary Checklist

- ✅ Railway account created
- ✅ CLI installed and logged in
- ✅ Project initialized
- ✅ PostgreSQL added
- ✅ Environment variables set
- ✅ Service deployed
- ✅ Health check passed
- ✅ API documentation accessible
- ✅ (Optional) Custom domain configured
- ✅ (Optional) GitHub auto-deployment enabled

Your Wallet Service is now live! 🚀
