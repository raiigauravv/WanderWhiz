#!/usr/bin/env python3
"""
Simple Flask app runner for testing collaborative features
"""

import os
import sys
from flask import Flask, jsonify

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Create simple Flask app for testing
app = Flask(__name__)
app.secret_key = "test-secret-key"

# Initialize collaborative manager
collaborative_manager = None
try:
    from firebase_config import get_firebase_manager
    from collaborative_planning import CollaborativeTripManager
    
    firebase_manager = get_firebase_manager()
    collaborative_manager = CollaborativeTripManager(firebase_manager)
    print("🤝 Collaborative Trip Manager initialized!")
except Exception as e:
    print(f"⚠️ Could not initialize collaborative manager: {e}")

@app.route('/')
def home():
    """Simple home page"""
    return """
    <h1>🧪 WanderWhiz Collaborative Testing</h1>
    <p>Collaborative features are running!</p>
    <ul>
        <li><a href="/api/test-collaborative">Test Collaborative API</a></li>
        <li><a href="/api/create-test-trip">Create Test Trip</a></li>
    </ul>
    """

@app.route('/api/test-collaborative')
def test_collaborative():
    """Test route to verify collaborative features are loaded"""
    return jsonify({
        'collaborative_manager_exists': collaborative_manager is not None,
        'message': 'Collaborative routes are loaded!',
        'status': 'success'
    })

@app.route('/api/create-test-trip')
def create_test_trip():
    """Create a test collaborative trip"""
    if not collaborative_manager:
        return jsonify({'error': 'Collaborative features not available'}), 503
    
    test_trip_data = {
        "destination": "Paris, France",
        "duration": 3,
        "places": [
            {"name": "Eiffel Tower", "type": "landmark"},
            {"name": "Louvre Museum", "type": "museum"},
            {"name": "Notre Dame Cathedral", "type": "landmark"}
        ]
    }
    
    trip_id, share_code = collaborative_manager.create_collaborative_trip(
        test_trip_data, "Test User"
    )
    
    if trip_id and share_code:
        return jsonify({
            'success': True,
            'trip_id': trip_id,
            'share_code': share_code,
            'share_url': f"http://localhost:5000/collaborate/{share_code}",
            'message': 'Test collaborative trip created successfully!'
        })
    else:
        return jsonify({'error': 'Failed to create collaborative trip'}), 500

@app.route('/collaborate/<share_code>')
def collaborate_page(share_code):
    """Simple collaborative trip page"""
    if not collaborative_manager:
        return "Collaborative features not available", 503
    
    # Try to get trip data
    try:
        from firebase_admin import firestore
        db = firestore.client()
        share_ref = db.collection('share_codes').document(share_code)
        share_doc = share_ref.get()
        
        if not share_doc.exists:
            return f"Invalid share code: {share_code}", 404
        
        share_data = share_doc.to_dict()
        trip_id = share_data['trip_id']
        trip_data = collaborative_manager.get_collaborative_trip(trip_id)
        
        if not trip_data:
            return "Trip not found", 404
        
        return f"""
        <h1>🤝 Collaborative Trip: {trip_data.get('trip_data', {}).get('destination', 'Unknown')}</h1>
        <p><strong>Share Code:</strong> {share_code}</p>
        <p><strong>Trip ID:</strong> {trip_id}</p>
        <p><strong>Creator:</strong> {trip_data.get('creator', 'Unknown')}</p>
        <p><strong>Status:</strong> {trip_data.get('status', 'Unknown')}</p>
        <h3>Places:</h3>
        <ul>
        """ + "\n".join([f"<li>{place.get('name', 'Unknown')}</li>" 
                        for place in trip_data.get('trip_data', {}).get('places', [])]) + """
        </ul>
        <p>✅ Collaborative trip is working!</p>
        """
        
    except Exception as e:
        return f"Error loading trip: {e}", 500

if __name__ == "__main__":
    print("🚀 Starting simple collaborative test server...")
    app.run(debug=True, port=5000, threaded=True)
