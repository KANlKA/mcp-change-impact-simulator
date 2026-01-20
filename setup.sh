#!/bin/bash

# Change Impact Simulator MCP Server - Setup Script

set -e

echo "🚀 Setting up Change Impact Simulator MCP Server..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "📋 Checking Python version..."
python3 --version

# Create virtual environment
echo "🐍 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📦 Installing requirements..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directory structure..."
mkdir -p src/config
mkdir -p docker/custom-configs
mkdir -p docker/logs
mkdir -p tests

# Copy environment template
if [ ! -f docker/.env ]; then
    echo "📝 Creating .env file..."
    cp docker/.env.template docker/.env
    echo "${YELLOW}⚠️  Please edit docker/.env with your configuration${NC}"
fi

# Create test data directory
mkdir -p tests/data

echo ""
echo "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Review and edit docker/.env file"
echo "2. Customize config files in src/config/ if needed"
echo "3. Run the server:"
echo "   ${YELLOW}python src/change_impact_simulator_server.py${NC}"
echo ""
echo "For Docker deployment:"
echo "   ${YELLOW}cd docker && docker-compose up --build${NC}"
echo ""