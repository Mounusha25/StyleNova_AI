#!/bin/bash
# Simple setup script for Fashion Recommender with scikit-learn

echo "🚀 Setting up Fashion Recommender System..."

# Create virtual environment if it doesn't exist
if [ ! -d "fashion_venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv fashion_venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source fashion_venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Setup complete!"
echo ""
echo "To get started:"
echo "  1. Activate environment: source fashion_venv/bin/activate"
echo "  2. Run tests: python test_simple.py"
echo "  3. Start API: python api_simple.py"
echo "  4. Visit: http://localhost:8001/docs"