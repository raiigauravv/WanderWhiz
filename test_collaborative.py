#!/usr/bin/env python3
"""
Quick test script for collaborative trip functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_collaborative_import():
    """Test if collaborative planning can be imported"""
    try:
        from collaborative_planning import CollaborativeTripManager
        print("✅ CollaborativeTripManager imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_firebase_import():
    """Test if Firebase can be imported"""
    try:
        from firebase_config import get_firebase_manager
        firebase_manager = get_firebase_manager()
        print("✅ Firebase manager imported successfully")
        return firebase_manager
    except ImportError as e:
        print(f"❌ Firebase import error: {e}")
        return None

def test_collaborative_manager():
    """Test creating collaborative manager"""
    try:
        from collaborative_planning import CollaborativeTripManager
        from firebase_config import get_firebase_manager
        
        firebase_manager = get_firebase_manager()
        collaborative_manager = CollaborativeTripManager(firebase_manager)
        print("✅ Collaborative manager created successfully")
        
        # Test creating a simple trip
        test_trip_data = {
            "destination": "Test City",
            "places": [
                {"name": "Test Place 1", "type": "restaurant"},
                {"name": "Test Place 2", "type": "museum"}
            ]
        }
        
        trip_id, share_code = collaborative_manager.create_collaborative_trip(
            test_trip_data, "Test User"
        )
        
        if trip_id and share_code:
            print(f"✅ Test trip created! ID: {trip_id}, Share Code: {share_code}")
            return True
        else:
            print("❌ Failed to create test trip")
            return False
            
    except Exception as e:
        print(f"❌ Collaborative manager test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 Testing WanderWhiz Collaborative Features")
    print("=" * 50)
    
    # Test 1: Import collaborative planning
    print("Test 1: Import Collaborative Planning")
    if not test_collaborative_import():
        return False
    
    # Test 2: Import Firebase
    print("\nTest 2: Import Firebase")
    firebase_manager = test_firebase_import()
    if not firebase_manager:
        print("⚠️ Firebase not available, will use memory fallback")
    
    # Test 3: Test collaborative manager
    print("\nTest 3: Test Collaborative Manager")
    if test_collaborative_manager():
        print("\n🎉 All tests passed! Collaborative features are working!")
        return True
    else:
        print("\n❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
