#!/usr/bin/env python3
"""
Quick start script for WanderWhiz with collaborative features
"""

import subprocess
import sys
import os

def start_app():
    print("🚀 Starting WanderWhiz App with Collaborative Features")
    print("=" * 50)
    
    # Check if app.py exists
    if not os.path.exists('app.py'):
        print("❌ app.py not found in current directory")
        print("📁 Current directory:", os.getcwd())
        return False
    
    # Try starting the app
    try:
        print("🔥 Launching Flask application...")
        print("🌐 App will be available at: http://localhost:5000")
        print("🤝 Collaborative features available at: http://localhost:5000/collaborate")
        print("\n" + "=" * 50)
        
        # Set environment variables
        os.environ['FLASK_APP'] = 'app.py'
        os.environ['FLASK_ENV'] = 'development'
        os.environ['FLASK_DEBUG'] = '1'
        
        # Start the app
        subprocess.run([sys.executable, 'app.py'], check=True)
        
    except Exception as e:
        print(f"❌ Error starting app: {e}")
        print("\n🔧 Trying alternative simple test app...")
        
        # Try simple test app as fallback
        if os.path.exists('simple_test_app.py'):
            try:
                subprocess.run([sys.executable, 'simple_test_app.py'], check=True)
            except Exception as e2:
                print(f"❌ Simple test app also failed: {e2}")
                return False
        
        return False
    
    return True

if __name__ == "__main__":
    success = start_app()
    if not success:
        print("\n💡 Manual start instructions:")
        print("1. cd /Users/gauravvraii/AA_LAST_SEM/CareerBot/WanderWhiz")
        print("2. python3 app.py")
        print("3. Open http://localhost:5000 in your browser")
        sys.exit(1)
