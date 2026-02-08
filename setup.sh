#!/bin/bash

# Dino Ventures Internal Wallet Service - Setup Script
# This script sets up the environment and runs the application

set -e

echo "🚀 Setting up Dino Ventures Internal Wallet Service..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please update it with your database credentials."
fi

# Build and start services
echo "🔨 Building Docker images..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Check if services are running
echo "🔍 Checking service status..."
docker-compose ps

# Display service URLs
echo ""
echo "✅ Setup complete! Services are running:"
echo "📍 Wallet API: http://localhost:8000"
echo "📍 API Documentation: http://localhost:8000/docs"
echo "📍 Health Check: http://localhost:8000/health"
echo "📍 Database: localhost:5432"
echo ""
echo "📊 To view logs: docker-compose logs -f"
echo "🛑 To stop services: docker-compose down"
echo "🔄 To restart services: docker-compose restart"

# Run a simple test
echo ""
echo "🧪 Running basic API test..."
sleep 5

if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API is healthy and ready!"
else
    echo "⚠️  API might still be starting up. Please wait a moment and try again."
fi

echo ""
echo "🎉 Dino Ventures Internal Wallet Service is ready to use!"
