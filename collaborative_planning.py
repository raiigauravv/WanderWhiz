"""
Real-Time Collaborative Trip Planning System
==========================================

Advanced collaborative features for WanderWhiz that enable:
- Real-time trip sharing with shareable links
- Live collaborative editing across multiple devices
- Group voting and consensus building on places
- Real-time notifications and updates

Uses Firebase Realtime Database for instant synchronization.
"""

import json
import uuid
from datetime import datetime, timedelta
from flask import request, session
import firebase_admin
from firebase_admin import credentials, db
import secrets
import string

class CollaborativeTripManager:
    def __init__(self, firebase_manager):
        """Initialize collaborative trip manager with Firebase connection"""
        self.firebase_manager = firebase_manager
        
        # Initialize Firebase Firestore (not Realtime Database)
        try:
            # Use existing Firebase app and Firestore
            app = firebase_admin.get_app()
            # Get Firestore database from firebase_manager
            if hasattr(firebase_manager, 'db') and firebase_manager.db:
                self.firestore_db = firebase_manager.db
                print("🤝 Collaborative Trip Manager initialized with Firestore")
            else:
                # Fallback: create basic in-memory storage
                self.firestore_db = None
                self.memory_store = {}
                print("🤝 Collaborative Trip Manager initialized with memory storage (fallback)")
        except Exception as e:
            print(f"❌ Error initializing collaborative manager: {e}")
            self.firestore_db = None
            self.memory_store = {}
    
    def create_collaborative_trip(self, trip_data, creator_name="Anonymous", creator_id=None):
        """Create a new collaborative trip that can be shared"""
        try:
            # Generate unique trip ID and share code
            trip_id = str(uuid.uuid4())
            share_code = self._generate_share_code()
            
            # Use creator_id if provided, otherwise use creator_name
            actual_creator_id = creator_id if creator_id else creator_name
            
            # Prepare collaborative trip data
            collaborative_trip = {
                'trip_id': trip_id,
                'share_code': share_code,
                'creator': actual_creator_id,  # Use the creator_id for consistent searching
                'creator_name': creator_name,   # Keep the display name separate
                'creator_id': actual_creator_id,  # Explicit creator_id field
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'participants': {
                    'creator': {
                        'name': creator_name,
                        'id': actual_creator_id,
                        'joined_at': datetime.now().isoformat(),
                        'role': 'owner',
                        'active': True
                    }
                },
                'trip_data': trip_data,
                'votes': {},
                'comments': {},
                'status': 'active',
                'settings': {
                    'allow_editing': True,
                    'require_approval': False,
                    'max_participants': 10
                }
            }
            
            # Store in Firestore or memory
            if self.firestore_db:
                # Use Firestore
                doc_ref = self.firestore_db.collection('collaborative_trips').document(trip_id)
                doc_ref.set(collaborative_trip)
                
                # Also create a share code index
                share_ref = self.firestore_db.collection('share_codes').document(share_code)
                share_ref.set({
                    'trip_id': trip_id,
                    'created_at': datetime.now().isoformat()
                })
                
                print(f"🤝 Created collaborative trip in Firestore: {trip_id} with share code: {share_code}")
            else:
                # Use memory storage as fallback
                if not hasattr(self, 'memory_store'):
                    self.memory_store = {}
                self.memory_store[trip_id] = collaborative_trip
                self.memory_store[f"share_{share_code}"] = {
                    'trip_id': trip_id,
                    'created_at': datetime.now().isoformat()
                }
                print(f"🤝 Created collaborative trip in memory: {trip_id} with share code: {share_code}")
            
            return trip_id, share_code
                
        except Exception as e:
            print(f"❌ Error creating collaborative trip: {e}")
            return None, None
    
    def join_trip(self, share_code, participant_name="Anonymous"):
        """Join an existing collaborative trip using share code"""
        try:
            if not self.firestore_db and not hasattr(self, 'memory_store'):
                return None, "Collaborative features not available"
            
            # Find trip by share code
            if self.firestore_db:
                share_ref = self.firestore_db.collection('share_codes').document(share_code)
                share_doc = share_ref.get()
                if not share_doc.exists:
                    return None, "Invalid share code"
                share_data = share_doc.to_dict()
            else:
                # Use memory storage
                share_data = self.memory_store.get(f"share_{share_code}")
                if not share_data:
                    return None, "Invalid share code"
            
            trip_id = share_data['trip_id']
            
            # Get trip data
            if self.firestore_db:
                trip_ref = self.firestore_db.collection('collaborative_trips').document(trip_id)
                trip_doc = trip_ref.get()
                if not trip_doc.exists:
                    return None, "Trip not found"
                trip_data = trip_doc.to_dict()
            else:
                trip_data = self.memory_store.get(trip_id)
                if not trip_data:
                    return None, "Trip not found"
            
            # Check if user already joined
            participants = trip_data.get('participants', {})
            participant_id = self._generate_participant_id(participant_name)
            
            if participant_id in participants:
                return trip_id, "Already joined"
            
            # Add participant
            participants[participant_id] = {
                'name': participant_name,
                'joined_at': datetime.now().isoformat(),
                'role': 'collaborator',
                'active': True
            }
            
            # Update trip data
            trip_data['participants'] = participants
            trip_data['last_updated'] = datetime.now().isoformat()
            
            if self.firestore_db:
                trip_ref = self.firestore_db.collection('collaborative_trips').document(trip_id)
                trip_ref.update({
                    'participants': participants,
                    'last_updated': datetime.now().isoformat()
                })
            else:
                self.memory_store[trip_id] = trip_data
            
            print(f"🤝 {participant_name} joined trip {trip_id}")
            return trip_id, "Successfully joined"
            
        except Exception as e:
            print(f"❌ Error joining trip: {e}")
            return None, f"Error: {e}"
    
    def update_trip_realtime(self, trip_id, updates, user_name="Anonymous"):
        """Update trip data in real-time"""
        try:
            if self.firestore_db:
                trip_ref = self.firestore_db.collection('collaborative_trips').document(trip_id)
                
                # Update the trip data
                trip_ref.update({
                    'trip_data': updates,
                    'last_updated': datetime.now().isoformat()
                })
                
                # Add update notification
                notification = {
                    'user': user_name,
                    'action': 'updated_trip',
                    'timestamp': datetime.now().isoformat(),
                    'changes': list(updates.keys())
                }
                
                # Add to notifications subcollection
                notifications_ref = trip_ref.collection('notifications')
                notifications_ref.add(notification)
                
                print(f"🔄 Trip {trip_id} updated by {user_name} in Firestore")
                return True
            else:
                # Memory fallback
                if trip_id in self.memory_store:
                    self.memory_store[trip_id]['trip_data'].update(updates)
                    self.memory_store[trip_id]['last_updated'] = datetime.now().isoformat()
                    
                    # Add notification to memory
                    if 'notifications' not in self.memory_store[trip_id]:
                        self.memory_store[trip_id]['notifications'] = []
                    
                    notification = {
                        'user': user_name,
                        'action': 'updated_trip',
                        'timestamp': datetime.now().isoformat(),
                        'changes': list(updates.keys())
                    }
                    self.memory_store[trip_id]['notifications'].append(notification)
                    
                    print(f"🔄 Trip {trip_id} updated by {user_name} in memory")
                    return True
                
                return False
            
        except Exception as e:
            print(f"❌ Error updating trip: {e}")
            return False
    
    def vote_on_place(self, trip_id, place_id, vote, user_name="Anonymous"):
        """Vote on a place in the trip"""
        try:
            if not self.firestore_db and not hasattr(self, 'memory_store'):
                return False
            
            # Get trip data
            if self.firestore_db:
                trip_ref = self.firestore_db.collection('collaborative_trips').document(trip_id)
                trip_doc = trip_ref.get()
                if not trip_doc.exists:
                    return False
                trip_data = trip_doc.to_dict()
            else:
                trip_data = self.memory_store.get(trip_id)
                if not trip_data:
                    return False
            
            # Update votes
            votes = trip_data.get('votes', {})
            place_votes = votes.get(place_id, {})
            
            user_id = self._generate_participant_id(user_name)
            place_votes[user_id] = {
                'vote': vote,  # 'like', 'dislike', 'love'
                'user': user_name,
                'timestamp': datetime.now().isoformat()
            }
            
            # Calculate vote summary
            vote_summary = self._calculate_vote_summary(place_votes)
            place_votes['summary'] = vote_summary
            
            votes[place_id] = place_votes
            trip_data['votes'] = votes
            trip_data['last_updated'] = datetime.now().isoformat()
            
            # Update in storage
            if self.firestore_db:
                trip_ref.update({
                    'votes': votes,
                    'last_updated': datetime.now().isoformat()
                })
            else:
                self.memory_store[trip_id] = trip_data
            
            print(f"🗳️ {user_name} voted {vote} on place {place_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error voting: {e}")
            return False
    
    def add_comment(self, trip_id, place_id, comment, user_name="Anonymous"):
        """Add a comment to a place"""
        try:
            if not self.firestore_db and not hasattr(self, 'memory_store'):
                return False
            
            # Get trip data
            if self.firestore_db:
                trip_ref = self.firestore_db.collection('collaborative_trips').document(trip_id)
                trip_doc = trip_ref.get()
                if not trip_doc.exists:
                    return False
                trip_data = trip_doc.to_dict()
            else:
                trip_data = self.memory_store.get(trip_id)
                if not trip_data:
                    return False
            
            comment_data = {
                'user': user_name,
                'comment': comment,
                'timestamp': datetime.now().isoformat(),
                'id': str(uuid.uuid4())[:8]
            }
            
            # Add comment to trip data
            comments = trip_data.get('comments', {})
            place_comments = comments.get(place_id, {})
            
            comment_id = str(uuid.uuid4())[:8]
            place_comments[comment_id] = comment_data
            
            comments[place_id] = place_comments
            trip_data['comments'] = comments
            trip_data['last_updated'] = datetime.now().isoformat()
            
            # Update in storage
            if self.firestore_db:
                trip_ref.update({
                    'comments': comments,
                    'last_updated': datetime.now().isoformat()
                })
            else:
                self.memory_store[trip_id] = trip_data
            
            print(f"💬 {user_name} commented on place {place_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error adding comment: {e}")
            return False
    
    def get_collaborative_trip(self, trip_id):
        """Get collaborative trip data"""
        try:
            if self.firestore_db:
                trip_ref = self.firestore_db.collection('collaborative_trips').document(trip_id)
                trip_doc = trip_ref.get()
                if trip_doc.exists:
                    return trip_doc.to_dict()
            elif hasattr(self, 'memory_store'):
                return self.memory_store.get(trip_id)
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting trip: {e}")
            return None
    
    def get_trip_participants(self, trip_id):
        """Get list of active participants"""
        try:
            trip_data = self.get_collaborative_trip(trip_id)
            if trip_data:
                return trip_data.get('participants', {})
            return {}
        except Exception as e:
            print(f"❌ Error getting participants: {e}")
            return {}
    
    def _generate_share_code(self):
        """Generate a unique 6-character share code"""
        return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    
    def _generate_participant_id(self, name):
        """Generate a consistent participant ID from name"""
        return name.lower().replace(' ', '_')[:20]
    
    def _calculate_vote_summary(self, votes):
        """Calculate vote summary statistics"""
        if not votes:
            return {'total': 0, 'likes': 0, 'dislikes': 0, 'loves': 0, 'score': 0}
        
        # Filter out summary if it exists
        vote_data = {k: v for k, v in votes.items() if k != 'summary'}
        
        likes = sum(1 for v in vote_data.values() if v.get('vote') == 'like')
        dislikes = sum(1 for v in vote_data.values() if v.get('vote') == 'dislike')
        loves = sum(1 for v in vote_data.values() if v.get('vote') == 'love')
        
        total = len(vote_data)
        score = (loves * 2 + likes - dislikes) / max(total, 1)
        
        return {
            'total': total,
            'likes': likes,
            'dislikes': dislikes,
            'loves': loves,
            'score': round(score, 2)
        }
