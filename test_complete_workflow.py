#!/usr/bin/env python3
"""
Complete WanderWhiz Testing Script
Tests all major functionalities to ensure everything works correctly.
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:5001"

def test_endpoint(name, url, method="GET", data=None):
    """Test an endpoint and report results"""
    print(f"\n🧪 Testing {name}")
    print(f"   URL: {url}")
    
    try:
        if method == "POST":
            response = requests.post(url, json=data, timeout=30)
        else:
            response = requests.get(url, timeout=30)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"   ✅ Success: {json.dumps(result, indent=2)[:200]}...")
                return result
            except:
                print(f"   ✅ Success: {response.text[:200]}...")
                return response.text
        else:
            print(f"   ❌ Failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"   💥 Error: {e}")
        return None

def main():
    print("🚀 WanderWhiz Complete Functionality Test")
    print("=" * 50)
    
    # Test 1: Home page
    test_endpoint("Home Page", f"{BASE_URL}/")
    
    # Test 2: Get saved itineraries (should work with Firebase)
    saved_trips = test_endpoint("Get Saved Trips", f"{BASE_URL}/get-saved-itineraries")
    
    # Test 3: Build an itinerary for Seattle
    build_data = {
        "city": "Seattle",
        "interests": ["nature", "food", "culture"],
        "budget": "medium",
        "duration": "1 day"
    }
    
    itinerary_result = test_endpoint("Build Seattle Itinerary", f"{BASE_URL}/build-itinerary", "POST", build_data)
    
    if itinerary_result and itinerary_result.get('success'):
        print(f"   🎯 Built itinerary with {len(itinerary_result.get('places', []))} places")
        
        # Test 4: Save the itinerary to Firebase
        save_data = {
            "name": "Test Seattle Trip",
            "city": "Seattle", 
            "places": itinerary_result.get('places', []),
            "route_info": itinerary_result.get('route_info', {}),
            "total_distance": itinerary_result.get('total_distance', 0),
            "total_duration": itinerary_result.get('total_duration', 0),
            "budget_estimate": itinerary_result.get('budget_estimate', {}),
            "interests": ["nature", "food", "culture"]
        }
        
        save_result = test_endpoint("Save Itinerary to Firebase", f"{BASE_URL}/save-itinerary", "POST", save_data)
        
        if save_result and save_result.get('success'):
            print(f"   💾 Saved with storage: {save_result.get('storage', 'unknown')}")
            
            # Test 5: Verify it appears in saved trips
            time.sleep(1)  # Give Firebase a moment
            updated_trips = test_endpoint("Verify Saved Trip", f"{BASE_URL}/get-saved-itineraries")
            
            if updated_trips:
                trip_count = updated_trips.get('count', 0)
                storage_type = updated_trips.get('storage', 'unknown')
                print(f"   📊 Total trips: {trip_count} (using {storage_type})")
    
    # Test 6: Demo data endpoint
    test_endpoint("Demo Data", f"{BASE_URL}/demo-data")
    
    print(f"\n🏁 Testing Complete!")
    print("Check the browser at http://127.0.0.1:5001 to verify UI functionality")

if __name__ == "__main__":
    main()
