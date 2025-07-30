#!/bin/bash
echo "🐍 ACTIVATING YOUR .venv AND STARTING WANDERWHIZ"
echo "================================================"

# Check if .venv exists
if [ ! -d ".venv" ]; then
    echo "❌ .venv directory not found in current directory"
    echo "📁 Current directory: $(pwd)"
    exit 1
fi

echo "✅ Found .venv directory"
echo "🔧 Activating virtual environment..."

# Activate the virtual environment
source .venv/bin/activate

# Verify activation
echo "✅ Virtual environment activated!"
echo "🐍 Python: $(which python)"
echo "📦 Pip: $(which pip)"

# Show installed packages (first few)
echo ""
echo "📚 Checking key packages..."
python -c "
try:
    import flask
    print('✅ Flask installed')
except ImportError:
    print('❌ Flask missing')

try:
    import openai
    print('✅ OpenAI installed')
except ImportError:
    print('❌ OpenAI missing')

try:
    import requests
    print('✅ Requests installed')
except ImportError:
    print('❌ Requests missing')

try:
    import reportlab
    print('✅ ReportLab installed')
except ImportError:
    print('❌ ReportLab missing')

try:
    import firebase_admin
    print('✅ Firebase installed')
except ImportError:
    print('❌ Firebase missing')
"

echo ""
echo "🚀 Starting WanderWhiz app..."
echo "🌐 App will be available at: http://localhost:5000"
echo "🤝 Collaborative features ready!"
echo ""
echo "=========================================="

# Start the app
python app.py
