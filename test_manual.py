#!/usr/bin/env python3
"""
Manual test for Seattle trip functionality
"""

import requests
import json

def test_seattle_trip():
    # Test building Seattle itinerary via the main form
    url = "http://127.0.0.1:5001/"
    
    # This should be a form submission like the website does
    form_data = {
        "city": "Seattle, WA",
        "interest": "nature food culture sightseeing"
    }
    
    print("🧪 Testing Seattle itinerary via form submission...")
    try:
        response = requests.post(url, data=form_data, timeout=60)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            # Check if it's an HTML response with itinerary
            if "itinerary" in response.text.lower():
                print("✅ Successfully built Seattle itinerary!")
                print("📍 Response contains itinerary data")
                return True
            else:
                print("❌ Response doesn't contain itinerary")
                print(response.text[:500])
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(response.text[:500])
            
    except Exception as e:
        print(f"💥 Error: {e}")
    
    return False

def test_firebase_trips():
    """Test getting trips from Firebase"""
    url = "http://127.0.0.1:5001/get-saved-itineraries"
    
    print("\n🧪 Testing Firebase saved trips...")
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data.get('count', 0)} trips using {data.get('storage', 'unknown')} storage")
            
            for i, trip in enumerate(data.get('trips', [])[:3]):  # Show first 3
                print(f"   {i+1}. {trip.get('city', 'Unknown')} - {trip.get('total_places', 0)} places")
                
            return True
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"💥 Error: {e}")
    
    return False

if __name__ == "__main__":
    print("🚀 Manual WanderWhiz Testing")
    print("=" * 40)
    
    test_firebase_trips()
    test_seattle_trip()
    
    print("\n🌐 Visit http://127.0.0.1:5001 to test the full UI")
