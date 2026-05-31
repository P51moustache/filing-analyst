#!/bin/bash

# 10-K Analysis Backend Start Script

echo "🚀 Starting 10-K Analysis Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run setup first:"
    echo "  python -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please create .env file with your Anthropic API key:"
    echo "  cp .env.example .env"
    echo "  # Then edit .env and add your API key"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if Anthropic API key is set
if grep -q "your_api_key_here" .env; then
    echo "⚠️  Warning: Please set your actual Anthropic API key in .env file"
    echo "The application will not work without a valid API key."
fi

# Create necessary directories
mkdir -p uploads reports

# Start the server
echo "✅ Starting FastAPI server on http://localhost:8000"
echo "📚 API documentation: http://localhost:8000/docs"
echo ""
uvicorn main:app --reload
