#!/usr/bin/env python3
"""
Manual app starter to debug issues
"""

import subprocess
import sys
import os
import time
import signal

def check_dependencies():
    """Check if all required dependencies are available"""
    try:
        import flask
        import openai
        import requests
        import reportlab
        print("✅ Core dependencies available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def check_firebase():
    """Check Firebase configuration"""
    try:
        from firebase_config import get_firebase_manager
        firebase_manager = get_firebase_manager()
        print("✅ Firebase configuration loaded")
        return True
    except Exception as e:
        print(f"⚠️ Firebase issue (app might still work): {e}")
        return False

def start_app_with_timeout():
    """Start the app with a timeout to detect hanging"""
    print("🚀 Starting WanderWhiz app...")
    print("🌐 Expected URL: http://localhost:5002")
    print("⏱️ Timeout: 30 seconds to detect hanging...")
    
    try:
        # Start the app process
        process = subprocess.Popen(
            [sys.executable, 'app.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for 5 seconds to see if it starts
        try:
            stdout, stderr = process.communicate(timeout=5)
            print(f"Process exited early with code: {process.returncode}")
            if stdout:
                print("STDOUT:", stdout)
            if stderr:
                print("STDERR:", stderr)
            return False
        except subprocess.TimeoutExpired:
            # Process is still running - this is good!
            print("✅ App appears to be starting (still running after 5 seconds)")
            print("🔗 Try opening: http://localhost:5002")
            print("⌨️ Press Ctrl+C to stop the app when done testing")
            
            try:
                # Wait indefinitely for user to stop
                process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Stopping app...")
                process.terminate()
                process.wait()
                print("✅ App stopped")
            
            return True
            
    except Exception as e:
        print(f"❌ Failed to start app: {e}")
        return False

def main():
    print("🔍 WANDERWHIZ APP DIAGNOSTICS")
    print("=" * 40)
    
    # Check current directory
    print(f"📁 Current directory: {os.getcwd()}")
    
    # Check if app.py exists
    if not os.path.exists('app.py'):
        print("❌ app.py not found!")
        return
    
    print("✅ app.py found")
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Please install missing dependencies")
        return
    
    # Check Firebase (optional)
    check_firebase()
    
    # Try to start the app
    if start_app_with_timeout():
        print("🎉 App testing session completed!")
    else:
        print("❌ App failed to start properly")
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Check if another app is using port 5002: lsof -i :5002")
        print("2. Try running directly: python3 app.py")
        print("3. Check for Python syntax errors in app.py")

if __name__ == "__main__":
    main()
