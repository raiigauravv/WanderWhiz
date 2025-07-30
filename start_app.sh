#!/bin/bash
echo "🚀 Starting WanderWhiz App with Collaborative Features"
echo "=============================================="

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ app.py not found. Please run from the WanderWhiz directory."
    exit 1
fi

echo "📁 Current directory: $(pwd)"
echo "🐍 Python version: $(python3 --version)"

echo "🔥 Starting Flask app..."
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1

python3 app.py
