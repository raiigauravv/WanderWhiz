#!/bin/bash
echo "🔍 FINDING AND ACTIVATING YOUR VIRTUAL ENVIRONMENT"
echo "================================================="

# Common venv names and locations
VENV_NAMES=("venv" "env" ".venv" ".env" "CareerBot" "wanderwhiz-env" "myenv")
SEARCH_PATHS=("." ".." "../.." "../../..")

# Function to find venv
find_venv() {
    for path in "${SEARCH_PATHS[@]}"; do
        for name in "${VENV_NAMES[@]}"; do
            if [ -d "$path/$name" ] && [ -f "$path/$name/bin/activate" ]; then
                echo "✅ Found venv at: $path/$name"
                echo "🔧 Activating virtual environment..."
                source "$path/$name/bin/activate"
                echo "✅ Virtual environment activated!"
                echo "🐍 Python: $(which python)"
                return 0
            fi
        done
    done
    return 1
}

# Try to find and activate venv
if find_venv; then
    echo ""
    echo "🚀 Starting WanderWhiz with your venv..."
    echo "🌐 App will be available at: http://localhost:5000"
    echo ""
    
    # Check if requirements are met
    python -c "import flask, openai, requests, reportlab" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✅ All required packages available"
        echo "🔥 Starting app..."
        python app.py
    else
        echo "⚠️ Some packages might be missing. Trying anyway..."
        python app.py
    fi
else
    echo "❌ Could not find virtual environment"
    echo ""
    echo "💡 Please tell me:"
    echo "1. What's your venv directory name?"
    echo "2. Where is it located?"
    echo ""
    echo "Or activate it manually and run:"
    echo "source /path/to/your/venv/bin/activate"
    echo "python app.py"
fi
