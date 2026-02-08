# Setup script for Dino Ventures Wallet Service (Windows PowerShell)
# This script sets up the database and runs the seed script

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "Dino Ventures Wallet Service - Setup Script (Windows)" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

# Check if .env file exists
if (-not (Test-Path .env)) {
    Write-Host "`nCreating .env file from .env.example..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "✓ .env file created" -ForegroundColor Green
    Write-Host "⚠ Please update .env with your database credentials" -ForegroundColor Yellow
}

# Install Python dependencies
Write-Host "`nInstalling Python dependencies..." -ForegroundColor Yellow
try {
    python -m pip install -r requirements.txt
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "⚠ Failed to install dependencies" -ForegroundColor Red
    Write-Host "Please ensure Python 3.11+ is installed" -ForegroundColor Red
    exit 1
}

# Run database migrations and seed
Write-Host "`nRunning database setup..." -ForegroundColor Yellow
try {
    python -m app.scripts.seed
    Write-Host "✓ Database seeded successfully" -ForegroundColor Green
} catch {
    Write-Host "⚠ Database seeding failed" -ForegroundColor Red
    Write-Host "Please ensure PostgreSQL is running" -ForegroundColor Red
    Write-Host "Or use Docker: docker-compose up -d" -ForegroundColor Yellow
}

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "`nTo start the API server:" -ForegroundColor Yellow
Write-Host "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor White
Write-Host "`nOr use Docker:" -ForegroundColor Yellow
Write-Host "  docker-compose up" -ForegroundColor White
Write-Host "`nAPI Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
