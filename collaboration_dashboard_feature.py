"""
Collaboration Dashboard for Trip Organizers
==========================================

This module adds a dedicated dashboard where trip organizers can see:
- Recent votes and comments from collaborators
- Activity timeline
- Participant overview
- Real-time notifications
"""

# Add to app.py - New route for organizer dashboard
collaboration_dashboard_route = '''
@app.route('/dashboard/collaborative/<trip_id>')
def collaborative_dashboard(trip_id):
    """Dashboard for trip organizers to see all collaborative activity"""
    
    if not collaborative_manager:
        return jsonify({'error': 'Collaborative features not available'}), 500
    
    try:
        # Get trip data
        trip_data = collaborative_manager.get_collaborative_trip(trip_id)
        
        if not trip_data:
            return render_template('error.html', message='Trip not found')
        
        # Check if user is the organizer
        creator_id = trip_data.get('creator_id')
        current_user = session.get('user_id', 'anonymous')
        
        # Get activity feed
        activity_feed = get_activity_feed(trip_data)
        
        # Get participant stats
        participant_stats = get_participant_stats(trip_data)
        
        # Get voting summary
        voting_summary = get_voting_summary(trip_data)
        
        return render_template('collaborative_dashboard.html', 
                             trip_data=trip_data,
                             activity_feed=activity_feed,
                             participant_stats=participant_stats,
                             voting_summary=voting_summary,
                             is_organizer=(current_user == creator_id))
                             
    except Exception as e:
        print(f"Error loading collaborative dashboard: {e}")
        return render_template('error.html', message='Failed to load dashboard')

def get_activity_feed(trip_data):
    """Generate chronological activity feed"""
    activities = []
    
    # Process votes
    for place_id, votes in trip_data.get('votes', {}).items():
        for vote_data in votes:
            activities.append({
                'type': 'vote',
                'user': vote_data.get('user', 'Anonymous'),
                'action': f"voted {vote_data.get('vote', 'unknown')} on",
                'place': place_id.replace('_', ' ').title(),
                'timestamp': vote_data.get('timestamp', 0),
                'icon': '🗳️'
            })
    
    # Process comments
    for place_id, comments in trip_data.get('comments', {}).items():
        for comment_data in comments:
            activities.append({
                'type': 'comment',
                'user': comment_data.get('user', 'Anonymous'),
                'action': f'commented on',
                'place': place_id.replace('_', ' ').title(),
                'content': comment_data.get('text', ''),
                'timestamp': comment_data.get('timestamp', 0),
                'icon': '💬'
            })
    
    # Sort by timestamp (newest first)
    activities.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
    
    return activities[:20]  # Return last 20 activities

def get_participant_stats(trip_data):
    """Get statistics about participants"""
    participants = trip_data.get('participants', {})
    
    stats = {
        'total_participants': len(participants),
        'active_participants': 0,
        'total_votes': 0,
        'total_comments': 0,
        'participants_list': []
    }
    
    # Count votes and comments per participant
    participant_activity = {}
    
    # Count votes
    for votes in trip_data.get('votes', {}).values():
        for vote_data in votes:
            user = vote_data.get('user', 'Anonymous')
            if user not in participant_activity:
                participant_activity[user] = {'votes': 0, 'comments': 0}
            participant_activity[user]['votes'] += 1
            stats['total_votes'] += 1
    
    # Count comments
    for comments in trip_data.get('comments', {}).values():
        for comment_data in comments:
            user = comment_data.get('user', 'Anonymous')
            if user not in participant_activity:
                participant_activity[user] = {'votes': 0, 'comments': 0}
            participant_activity[user]['comments'] += 1
            stats['total_comments'] += 1
    
    # Create participant list with activity
    for participant_id, participant_data in participants.items():
        user_name = participant_data.get('name', 'Anonymous')
        activity = participant_activity.get(user_name, {'votes': 0, 'comments': 0})
        
        stats['participants_list'].append({
            'name': user_name,
            'role': participant_data.get('role', 'collaborator'),
            'joined_at': participant_data.get('joined_at', ''),
            'votes': activity['votes'],
            'comments': activity['comments'],
            'total_activity': activity['votes'] + activity['comments']
        })
        
        if activity['votes'] > 0 or activity['comments'] > 0:
            stats['active_participants'] += 1
    
    # Sort by activity level
    stats['participants_list'].sort(key=lambda x: x['total_activity'], reverse=True)
    
    return stats

def get_voting_summary(trip_data):
    """Get summary of voting on each place"""
    voting_summary = {}
    
    for place_id, votes in trip_data.get('votes', {}).items():
        place_name = place_id.replace('_', ' ').title()
        
        vote_counts = {'love': 0, 'like': 0, 'meh': 0, 'dislike': 0}
        total_votes = len(votes)
        
        for vote_data in votes:
            vote_type = vote_data.get('vote', 'meh')
            if vote_type in vote_counts:
                vote_counts[vote_type] += 1
        
        # Calculate popularity score
        popularity_score = (vote_counts['love'] * 3 + vote_counts['like'] * 1 - 
                          vote_counts['dislike'] * 2)
        
        voting_summary[place_id] = {
            'place_name': place_name,
            'vote_counts': vote_counts,
            'total_votes': total_votes,
            'popularity_score': popularity_score,
            'consensus_level': get_consensus_level(vote_counts, total_votes)
        }
    
    return voting_summary

def get_consensus_level(vote_counts, total_votes):
    """Calculate how much consensus there is on a place"""
    if total_votes == 0:
        return 'no_votes'
    
    max_votes = max(vote_counts.values())
    consensus_percentage = (max_votes / total_votes) * 100
    
    if consensus_percentage >= 80:
        return 'high_consensus'
    elif consensus_percentage >= 60:
        return 'moderate_consensus'
    else:
        return 'low_consensus'
'''

# HTML Template for the dashboard
dashboard_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Collaboration Dashboard - WanderWhiz</title>
    <link rel="stylesheet" href="/static/css/styles.css">
    <style>
        .dashboard-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .dashboard-header {
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: bold;
            color: #3498db;
            margin-bottom: 10px;
        }
        
        .activity-feed {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .activity-item {
            display: flex;
            align-items: center;
            padding: 15px 0;
            border-bottom: 1px solid #eee;
        }
        
        .activity-icon {
            font-size: 1.5rem;
            margin-right: 15px;
            width: 40px;
            text-align: center;
        }
        
        .activity-content {
            flex: 1;
        }
        
        .activity-time {
            color: #7f8c8d;
            font-size: 0.9rem;
        }
        
        .participant-list {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .participant-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 0;
            border-bottom: 1px solid #eee;
        }
        
        .participant-name {
            font-weight: bold;
            color: #2c3e50;
        }
        
        .participant-activity {
            color: #7f8c8d;
            font-size: 0.9rem;
        }
        
        .voting-summary {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .place-vote-item {
            margin-bottom: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
        }
        
        .vote-bar {
            display: flex;
            height: 20px;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        
        .vote-love { background: #e74c3c; }
        .vote-like { background: #f39c12; }
        .vote-meh { background: #95a5a6; }
        .vote-dislike { background: #7f8c8d; }
        
        .notification-badge {
            background: #e74c3c;
            color: white;
            border-radius: 50%;
            padding: 5px 10px;
            font-size: 0.8rem;
            margin-left: 10px;
        }
        
        .refresh-button {
            background: #27ae60;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <div class="dashboard-header">
            <h1>🤝 Collaboration Dashboard</h1>
            <p>{{ trip_data.trip_data.destination }} - Real-time Activity</p>
            <button class="refresh-button" onclick="location.reload()">🔄 Refresh Activity</button>
        </div>
        
        <!-- Quick Stats -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{{ participant_stats.total_participants }}</div>
                <div>Total Participants</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ participant_stats.active_participants }}</div>
                <div>Active Participants</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ participant_stats.total_votes }}</div>
                <div>Total Votes</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ participant_stats.total_comments }}</div>
                <div>Total Comments</div>
            </div>
        </div>
        
        <!-- Recent Activity Feed -->
        <div class="activity-feed">
            <h2>📋 Recent Activity 
                {% if activity_feed|length > 0 %}
                    <span class="notification-badge">{{ activity_feed|length }}</span>
                {% endif %}
            </h2>
            
            {% if activity_feed %}
                {% for activity in activity_feed %}
                <div class="activity-item">
                    <div class="activity-icon">{{ activity.icon }}</div>
                    <div class="activity-content">
                        <div><strong>{{ activity.user }}</strong> {{ activity.action }} <strong>{{ activity.place }}</strong></div>
                        {% if activity.content %}
                            <div style="color: #7f8c8d; margin-top: 5px;">"{{ activity.content }}"</div>
                        {% endif %}
                        <div class="activity-time">{{ activity.timestamp|timestamp_to_time }}</div>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <p style="color: #7f8c8d; text-align: center; padding: 20px;">
                    No collaborative activity yet. Share your trip to get started!
                </p>
            {% endif %}
        </div>
        
        <!-- Voting Summary -->
        <div class="voting-summary">
            <h2>🗳️ Voting Summary</h2>
            {% for place_id, voting_data in voting_summary.items() %}
            <div class="place-vote-item">
                <h4>{{ voting_data.place_name }}</h4>
                <div class="vote-bar">
                    {% set total = voting_data.total_votes %}
                    {% if total > 0 %}
                        <div class="vote-love" style="width: {{ (voting_data.vote_counts.love / total * 100)|round(1) }}%"></div>
                        <div class="vote-like" style="width: {{ (voting_data.vote_counts.like / total * 100)|round(1) }}%"></div>
                        <div class="vote-meh" style="width: {{ (voting_data.vote_counts.meh / total * 100)|round(1) }}%"></div>
                        <div class="vote-dislike" style="width: {{ (voting_data.vote_counts.dislike / total * 100)|round(1) }}%"></div>
                    {% endif %}
                </div>
                <div style="font-size: 0.9rem; color: #7f8c8d;">
                    {{ voting_data.vote_counts.love }} Love, 
                    {{ voting_data.vote_counts.like }} Like, 
                    {{ voting_data.vote_counts.meh }} Meh, 
                    {{ voting_data.vote_counts.dislike }} Dislike
                    (Score: {{ voting_data.popularity_score }})
                </div>
            </div>
            {% endfor %}
        </div>
        
        <!-- Participants List -->
        <div class="participant-list">
            <h2>👥 Participants ({{ participant_stats.total_participants }})</h2>
            {% for participant in participant_stats.participants_list %}
            <div class="participant-item">
                <div>
                    <div class="participant-name">{{ participant.name }}</div>
                    <div class="participant-activity">
                        {{ participant.votes }} votes, {{ participant.comments }} comments
                    </div>
                </div>
                <div style="color: #3498db;">{{ participant.role }}</div>
            </div>
            {% endfor %}
        </div>
        
        <div style="text-align: center; margin-top: 30px;">
            <a href="/itinerary" class="refresh-button">← Back to Trip</a>
        </div>
    </div>
    
    <script>
        // Auto-refresh every 30 seconds
        setTimeout(() => location.reload(), 30000);
        
        // Show notification count in title
        const activityCount = {{ activity_feed|length }};
        if (activityCount > 0) {
            document.title = `(${activityCount}) Collaboration Dashboard - WanderWhiz`;
        }
    </script>
</body>
</html>
'''

print("📊 COLLABORATION DASHBOARD CREATED!")
print("=" * 50)
print("🎯 FEATURES ADDED:")
print("✅ Real-time activity feed")
print("✅ Participant statistics")
print("✅ Voting summary with visual bars")
print("✅ Recent comments display") 
print("✅ Auto-refresh every 30 seconds")
print("✅ Notification badges")
print("✅ Popularity scoring")
print("")
print("🔗 ORGANIZER ACCESS:")
print("URL: http://localhost:5000/dashboard/collaborative/{trip_id}")
print("")
print("💡 WHAT ORGANIZER WILL SEE:")
print("- Who voted on what places")
print("- All recent comments") 
print("- Participant activity levels")
print("- Real-time updates")
print("- Visual voting summaries")
