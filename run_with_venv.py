#!/usr/bin/env python3
"""
Start WanderWhiz with .venv activation
"""
import subprocess
import sys
import os

def start_app_with_venv():
    print("🚀 STARTING WANDERWHIZ WITH YOUR .venv")
    print("=" * 40)
    
    # Check if .venv exists
    if not os.path.exists('.venv'):
        print("❌ .venv directory not found")
        return False
    
    print("✅ Found .venv directory")
    
    # Create the activation command
    activate_cmd = "source .venv/bin/activate && python app.py"
    
    print("🔧 Activating .venv and starting app...")
    print("🌐 App will be available at: http://localhost:5000")
    print("🤝 Collaborative features ready for testing!")
    print("-" * 40)
    
    try:
        # Use bash to run the command with venv activation
        result = subprocess.run([
            'bash', '-c', activate_cmd
        ], cwd=os.getcwd())
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error starting app: {e}")
        return False

if __name__ == "__main__":
    print("🎯 Using your .venv virtual environment")
    success = start_app_with_venv()
    
    if not success:
        print("\n💡 Manual commands to try:")
        print("source .venv/bin/activate")
        print("python app.py")
