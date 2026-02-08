#!/bin/bash

# Setup script for Dino Ventures Wallet Service
# This script sets up the database and runs the seed script

set -e  # Exit on error

echo "================================================================"
echo "Dino Ventures Wallet Service - Setup Script"
echo "================================================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "✓ .env file created"
    echo "⚠ Please update .env with your database credentials"
fi

# Check if PostgreSQL is running
echo ""
echo "Checking PostgreSQL connection..."
if command -v psql &> /dev/null; then
    # Try to connect to PostgreSQL
    if psql -h localhost -U wallet_user -d wallet_db -c "SELECT 1;" &> /dev/null; then
        echo "✓ PostgreSQL is running and accessible"
    else
        echo "⚠ PostgreSQL connection failed"
        echo "Please ensure PostgreSQL is running and credentials are correct"
        echo "Or use Docker: docker-compose up -d db"
    fi
else
    echo "⚠ psql command not found"
    echo "Using Docker instead: docker-compose up -d"
fi

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
if command -v python3 &> /dev/null; then
    python3 -m pip install -r requirements.txt
    echo "✓ Dependencies installed"
else
    echo "⚠ Python 3 not found"
    echo "Please install Python 3.11 or higher"
    exit 1
fi

# Run database migrations and seed
echo ""
echo "Running database setup..."
python3 -m app.scripts.seed
echo "✓ Database seeded successfully"

echo ""
echo "================================================================"
echo "Setup Complete!"
echo "================================================================"
echo ""
echo "To start the API server:"
echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "Or use Docker:"
echo "  docker-compose up"
echo ""
echo "API Documentation: http://localhost:8000/docs"
echo "================================================================"
