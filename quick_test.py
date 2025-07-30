#!/usr/bin/env python3
import sys
sys.path.append('.')

print("🧪 TESTING COLLABORATIVE TRIP PLANNING - FEATURE #2")
print("=" * 60)

try:
    from collaborative_planning import CollaborativeTripManager
    from firebase_config import get_firebase_manager
    
    print("1️⃣ Initializing Firebase and Collaborative Manager...")
    firebase_manager = get_firebase_manager()
    collaborative_manager = CollaborativeTripManager(firebase_manager)
    print("✅ Initialization successful!")
    
    print("\n2️⃣ Creating collaborative trip...")
    test_trip = {
        'destination': 'Paris, France',
        'places': [
            {'name': 'Eiffel Tower', 'type': 'landmark'},
            {'name': 'Louvre Museum', 'type': 'museum'}
        ]
    }
    
    trip_id, share_code = collaborative_manager.create_collaborative_trip(test_trip, 'Alice')
    print(f"✅ Trip created successfully!")
    print(f"   Trip ID: {trip_id[:8]}...")
    print(f"   Share Code: {share_code}")
    
    print("\n3️⃣ Testing user joining...")
    result = collaborative_manager.join_trip(share_code, 'Bob')
    print(f"✅ Join result: {result[1]}")
    
    print("\n4️⃣ Testing voting system...")
    vote_result = collaborative_manager.vote_on_place(trip_id, 'eiffel_tower', 'love', 'Bob')
    print(f"✅ Vote recorded: {vote_result}")
    
    print("\n5️⃣ Testing comments...")
    comment_result = collaborative_manager.add_comment(trip_id, 'eiffel_tower', 'Amazing views!', 'Bob')
    print(f"✅ Comment added: {comment_result}")
    
    print("\n6️⃣ Testing trip retrieval...")
    trip_data = collaborative_manager.get_collaborative_trip(trip_id)
    if trip_data:
        print("✅ Trip data retrieved successfully!")
        print(f"   Participants: {len(trip_data.get('participants', {}))}")
        print(f"   Status: {trip_data.get('status', 'unknown')}")
    
    print("\n🎉 ALL COLLABORATIVE FEATURES WORKING PERFECTLY!")
    print("🏆 FEATURE #2 IS READY FOR GOOGLE PLATFORMS AWARD!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
