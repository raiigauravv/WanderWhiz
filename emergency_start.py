#!/usr/bin/env python3
"""
Emergency app starter - Let's get WanderWhiz running!
"""

import os
import sys
import subprocess
import time

def emergency_start():
    print("🚨 EMERGENCY APP RECOVERY")
    print("=" * 40)
    
    # Check current directory
    current_dir = os.getcwd()
    print(f"📁 Current directory: {current_dir}")
    
    # Check if app.py exists
    if os.path.exists('app.py'):
        print("✅ app.py found")
    else:
        print("❌ app.py NOT found!")
        print("Available files:")
        for f in os.listdir('.'):
            if f.endswith('.py'):
                print(f"  - {f}")
        return False
    
    # Check Python
    try:
        result = subprocess.run([sys.executable, '--version'], 
                              capture_output=True, text=True)
        print(f"🐍 Python: {result.stdout.strip()}")
    except Exception as e:
        print(f"❌ Python check failed: {e}")
        return False
    
    # Try to start the app with detailed output
    print("\n🚀 Attempting to start app...")
    print("⏱️  Waiting 10 seconds to see if it starts...")
    
    try:
        # Start app process
        process = subprocess.Popen(
            [sys.executable, '-u', 'app.py'],  # -u for unbuffered output
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            universal_newlines=True
        )
        
        # Wait a bit and check if process is still running
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ App process started successfully!")
            print("🌐 Try opening: http://localhost:5000")
            print("⌨️  Press Enter to stop the app...")
            
            # Show some output
            try:
                stdout, _ = process.communicate(timeout=2)
                if stdout:
                    print("📋 App output:")
                    print(stdout[:500])  # Show first 500 chars
            except subprocess.TimeoutExpired:
                print("📋 App is running (timeout reached - this is good!)")
                process.kill()
                print("🛑 App stopped")
            
            return True
        else:
            # Process exited, get the output
            stdout, _ = process.communicate()
            print(f"❌ App exited with code: {process.returncode}")
            print("📋 Error output:")
            print(stdout)
            return False
            
    except Exception as e:
        print(f"❌ Failed to start app: {e}")
        return False

if __name__ == "__main__":
    print("🆘 WANDERWHIZ EMERGENCY RECOVERY")
    print("Getting your app running NOW!")
    print("=" * 50)
    
    if emergency_start():
        print("\n🎉 SUCCESS! Your app should be running!")
        print("📱 Open: http://localhost:5000")
    else:
        print("\n❌ FAILED! Let's try manual approach:")
        print("1. Open terminal")
        print("2. cd /Users/gauravvraii/AA_LAST_SEM/CareerBot/WanderWhiz")
        print("3. python3 app.py")
        print("4. If errors, run: pip install -r requirements.txt")
