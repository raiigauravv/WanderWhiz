# Firebase Configuration for WanderWhiz
import firebase_admin
from firebase_admin import credentials, firestore, storage
import os
from datetime import datetime
import json

class FirebaseManager:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize Firebase connection (singleton pattern)"""
        if self._initialized:
            return
            
        try:
            # Check if Firebase is already initialized
            firebase_admin.get_app()
            print("🔥 Firebase already initialized, reusing connection")
        except ValueError:
            # Initialize Firebase
            self._initialize_firebase()
        
        # Get Firestore client
        self.db = firestore.client()
        self._initialized = True
    
    def _initialize_firebase(self):
        """Initialize Firebase with environment variables or local file"""
        try:
            # Try to use environment variables first (for Vercel/production)
            firebase_config = os.getenv('FIREBASE_CONFIG')
            if firebase_config:
                # Parse the JSON string from environment variable
                cred_dict = json.loads(firebase_config)
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
                print("🔥 Firebase initialized with environment variables!")
                return
        except Exception as e:
            print(f"⚠️ Could not initialize with environment variables: {e}")
        
        # Fallback to local file (for development)
        try:
            cred_path = os.path.join(os.path.dirname(__file__), 'firebase-key.json')
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                print("🔥 Firebase initialized with local file!")
                return
        except Exception as e:
            print(f"⚠️ Could not initialize with local file: {e}")
        
        print("❌ Firebase initialization failed. Please check your configuration.")
        return

    def save_itinerary(self, user_id, itinerary_data):
        """Save itinerary to Firestore"""
        try:
            # Get the trip name from itinerary data
            trip_name = itinerary_data.get('name', f"Trip {datetime.now().strftime('%m/%d/%Y')}")
            
            # Create itinerary document
            doc_data = {
                'user_id': user_id or 'anonymous',
                'name': trip_name,  # Include the trip name
                'city': itinerary_data.get('city', 'Unknown'),
                'places': itinerary_data.get('places', []),
                'total_distance': itinerary_data.get('total_distance', 0),
                'total_duration': itinerary_data.get('total_duration', 0),
                'budget_estimate': itinerary_data.get('budget_estimate', {}),
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'is_favorite': False,
                'tags': itinerary_data.get('tags', []),
                'polyline': itinerary_data.get('polyline', ''),
                'gpt_prompt': itinerary_data.get('gpt_prompt', ''),
                'interests': itinerary_data.get('interests', []),
                'total_places': len(itinerary_data.get('places', [])),
                'route_info': itinerary_data.get('route_info', {})
            }
            
            # Use a meaningful document ID based on the trip name
            # Clean the name to make it Firebase-friendly
            clean_name = ''.join(c for c in trip_name if c.isalnum() or c in (' ', '_', '-')).rstrip()
            clean_name = clean_name.replace(' ', '_')[:50]  # Limit length
            
            # Add timestamp to ensure uniqueness
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            doc_id = f"{clean_name}_{timestamp}"
            
            # Save to Firestore with custom document ID
            doc_ref = self.db.collection('itineraries').document(doc_id)
            doc_ref.set(doc_data)
            
            print(f"🔥 Saved trip '{trip_name}' with ID: {doc_id}")
            return doc_id  # Return meaningful document ID
            
        except Exception as e:
            print(f"❌ Error saving itinerary: {e}")
            return None

    def get_user_itineraries(self, user_id=None, limit=10):
        """Get user's saved itineraries"""
        try:
            query = self.db.collection('itineraries')
            
            if user_id:
                query = query.where('user_id', '==', user_id)
            else:
                query = query.where('user_id', '==', 'anonymous')
            
            # Simple limit without ordering to avoid index requirements
            query = query.limit(limit)
            
            docs = query.stream()
            
            itineraries = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                # Convert Firestore timestamp to string
                if 'created_at' in data:
                    data['created_at'] = data['created_at'].strftime('%Y-%m-%d %H:%M')
                itineraries.append(data)
            
            # Sort in Python instead (newest first)
            itineraries.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            return itineraries
            
        except Exception as e:
            print(f"❌ Error fetching itineraries: {e}")
            return []

    def get_itinerary_by_id(self, itinerary_id):
        """Get specific itinerary by ID"""
        try:
            doc_ref = self.db.collection('itineraries').document(itinerary_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            else:
                return None
                
        except Exception as e:
            print(f"❌ Error fetching itinerary: {e}")
            return None

    def delete_itinerary(self, itinerary_id):
        """Delete itinerary"""
        try:
            self.db.collection('itineraries').document(itinerary_id).delete()
            return True
        except Exception as e:
            print(f"❌ Error deleting itinerary: {e}")
            return False

    def favorite_itinerary(self, itinerary_id, is_favorite=True):
        """Mark/unmark itinerary as favorite"""
        try:
            doc_ref = self.db.collection('itineraries').document(itinerary_id)
            doc_ref.update({
                'is_favorite': is_favorite,
                'updated_at': datetime.now()
            })
            return True
        except Exception as e:
            print(f"❌ Error updating favorite: {e}")
            return False

    def get_popular_destinations(self, limit=5):
        """Get most popular destinations"""
        try:
            docs = self.db.collection('itineraries').stream()
            
            # Count cities
            city_counts = {}
            for doc in docs:
                data = doc.to_dict()
                city = data.get('city', 'Unknown')
                city_counts[city] = city_counts.get(city, 0) + 1
            
            # Sort by popularity
            popular = sorted(city_counts.items(), key=lambda x: x[1], reverse=True)
            return popular[:limit]
            
        except Exception as e:
            print(f"❌ Error fetching popular destinations: {e}")
            return []

    def get_stats(self):
        """Get platform statistics"""
        try:
            # Get total itineraries
            itineraries = list(self.db.collection('itineraries').stream())
            total_trips = len(itineraries)
            
            # Calculate total distance covered
            total_distance = 0
            total_places = 0
            for doc in itineraries:
                data = doc.to_dict()
                total_distance += data.get('total_distance', 0)
                total_places += len(data.get('places', []))
            
            return {
                'total_trips': total_trips,
                'total_distance_km': round(total_distance / 1000, 1),
                'total_places': total_places,
                'avg_places_per_trip': round(total_places / max(total_trips, 1), 1)
            }
            
        except Exception as e:
            print(f"❌ Error fetching stats: {e}")
            return {
                'total_trips': 0,
                'total_distance_km': 0,
                'total_places': 0,
                'avg_places_per_trip': 0
            }

# Global Firebase manager instance
firebase_manager = None

def get_firebase_manager():
    """Get Firebase manager instance"""
    global firebase_manager
    if firebase_manager is None:
        firebase_manager = FirebaseManager()
    return firebase_manager
