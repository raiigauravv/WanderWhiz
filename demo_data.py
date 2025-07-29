# Demo Data for WanderWhiz Hackathon
import json

# Sample impressive trips for demo
DEMO_TRIPS = [
    {
        "id": "demo-paris-romantic",
        "city": "Paris",
        "title": "Romantic Weekend in Paris ❤️",
        "places": [
            {
                "name": "Café de Flore", 
                "rating": 4.4, 
                "category": "cafe",
                "types": ["cafe", "restaurant", "food"],
                "price_level": 3,
                "geometry": {
                    "location": {
                        "lat": 48.8542,
                        "lng": 2.3320
                    }
                },
                "vicinity": "172 Boulevard Saint-Germain, Paris"
            },
            {
                "name": "Louvre Museum", 
                "rating": 4.7, 
                "category": "museum",
                "types": ["museum", "tourist_attraction"],
                "price_level": 3,
                "geometry": {
                    "location": {
                        "lat": 48.8606,
                        "lng": 2.3376
                    }
                },
                "vicinity": "Rue de Rivoli, Paris"
            },
            {
                "name": "Seine River Cruise", 
                "rating": 4.5, 
                "category": "activity",
                "types": ["tourist_attraction", "travel_agency"],
                "price_level": 2,
                "geometry": {
                    "location": {
                        "lat": 48.8584,
                        "lng": 2.3457
                    }
                },
                "vicinity": "Port de la Bourdonnais, Paris"
            },
            {
                "name": "Eiffel Tower", 
                "rating": 4.6, 
                "category": "landmark",
                "types": ["tourist_attraction", "point_of_interest"],
                "price_level": 2,
                "geometry": {
                    "location": {
                        "lat": 48.8584,
                        "lng": 2.2945
                    }
                },
                "vicinity": "Champ de Mars, Paris"
            },
            {
                "name": "Montmartre", 
                "rating": 4.5, 
                "category": "neighborhood",
                "types": ["tourist_attraction", "neighborhood"],
                "price_level": 2,
                "geometry": {
                    "location": {
                        "lat": 48.8867,
                        "lng": 2.3431
                    }
                },
                "vicinity": "Montmartre, Paris"
            },
            {
                "name": "Notre-Dame Cathedral", 
                "rating": 4.4, 
                "category": "landmark",
                "types": ["tourist_attraction", "church", "point_of_interest"],
                "price_level": 1,
                "geometry": {
                    "location": {
                        "lat": 48.8530,
                        "lng": 2.3499
                    }
                },
                "vicinity": "6 Parvis Notre-Dame, Paris"
            },
        ],
        "total_distance": 24500,  # in meters
        "total_duration": 5400,   # in seconds
        "budget_estimate": {"total": 302, "per_person": 151},
        "created_at": "2025-01-20 14:30",
        "tags": ["romantic", "cultural", "historic"],
        "gpt_prompt": "Plan a romantic weekend in Paris with cozy cafes and famous landmarks"
    },
    {
        "id": "demo-tokyo-foodie",
        "city": "Tokyo",
        "title": "Tokyo Food Adventure 🍜",
        "places": [
            {
                "name": "Tsukiji Outer Market", 
                "rating": 4.6, 
                "category": "market",
                "types": ["tourist_attraction", "food", "establishment"],
                "price_level": 2,
                "geometry": {
                    "location": {
                        "lat": 35.6654,
                        "lng": 139.7707
                    }
                },
                "vicinity": "Tsukiji, Chuo City, Tokyo"
            },
            {
                "name": "Ramen Jiro", 
                "rating": 4.3, 
                "category": "restaurant",
                "types": ["restaurant", "food", "meal_takeaway"],
                "price_level": 1,
                "geometry": {
                    "location": {
                        "lat": 35.6895,
                        "lng": 139.6917
                    }
                },
                "vicinity": "Shinjuku City, Tokyo"
            },
            {
                "name": "Sensoji Temple", 
                "rating": 4.3, 
                "category": "temple",
                "types": ["tourist_attraction", "place_of_worship", "establishment"],
                "price_level": 0,
                "geometry": {
                    "location": {
                        "lat": 35.7148,
                        "lng": 139.7967
                    }
                },
                "vicinity": "Asakusa, Taito City, Tokyo"
            },
            {
                "name": "Golden Gai", 
                "rating": 4.2, 
                "category": "bar",
                "types": ["bar", "night_club", "establishment"],
                "price_level": 3,
                "geometry": {
                    "location": {
                        "lat": 35.6938,
                        "lng": 139.7034
                    }
                },
                "vicinity": "Kabukicho, Shinjuku City, Tokyo"
            },
            {
                "name": "Tokyo Skytree", 
                "rating": 4.1, 
                "category": "landmark",
                "types": ["tourist_attraction", "point_of_interest"],
                "price_level": 2,
                "geometry": {
                    "location": {
                        "lat": 35.7101,
                        "lng": 139.8107
                    }
                },
                "vicinity": "Sumida City, Tokyo"
            },
            {
                "name": "Shibuya Crossing", 
                "rating": 4.4, 
                "category": "landmark",
                "types": ["tourist_attraction", "point_of_interest"],
                "price_level": 0,
                "geometry": {
                    "location": {
                        "lat": 35.6598,
                        "lng": 139.7006
                    }
                },
                "vicinity": "Shibuya City, Tokyo"
            },
        ],
        "total_distance": 31200,
        "total_duration": 7200,
        "budget_estimate": {"total": 165, "per_person": 82},
        "created_at": "2025-01-18 09:15",
        "tags": ["food", "culture", "nightlife"],
        "gpt_prompt": "Show me the best street food and authentic restaurants in Tokyo"
    },
    {
        "id": "demo-nyc-hipster",
        "city": "New York",
        "title": "NYC Hipster Vibes ☕",
        "places": [
            {
                "name": "Brooklyn Bridge", 
                "rating": 4.6, 
                "category": "landmark",
                "types": ["tourist_attraction", "point_of_interest"],
                "price_level": 0,
                "geometry": {
                    "location": {
                        "lat": 40.7061,
                        "lng": -73.9969
                    }
                },
                "vicinity": "New York, NY"
            },
            {
                "name": "Blue Bottle Coffee", 
                "rating": 4.2, 
                "category": "cafe",
                "types": ["cafe", "food", "store"],
                "price_level": 2,
                "geometry": {
                    "location": {
                        "lat": 40.7505,
                        "lng": -73.9934
                    }
                },
                "vicinity": "Midtown Manhattan, New York, NY"
            },
            {
                "name": "High Line", 
                "rating": 4.5, 
                "category": "park",
                "types": ["tourist_attraction", "park"],
                "price_level": 0,
                "geometry": {
                    "location": {
                        "lat": 40.7480,
                        "lng": -74.0048
                    }
                },
                "vicinity": "Chelsea, New York, NY"
            },
            {
                "name": "Chelsea Market", 
                "rating": 4.4, 
                "category": "market",
                "types": ["tourist_attraction", "food", "shopping_mall"],
                "price_level": 2,
                "geometry": {
                    "location": {
                        "lat": 40.7424,
                        "lng": -74.0061
                    }
                },
                "vicinity": "75 9th Ave, New York, NY"
            },
            {
                "name": "Central Park", 
                "rating": 4.6, 
                "category": "park",
                "types": ["tourist_attraction", "park"],
                "price_level": 0,
                "geometry": {
                    "location": {
                        "lat": 40.7829,
                        "lng": -73.9654
                    }
                },
                "vicinity": "New York, NY"
            },
            {
                "name": "MOMA", 
                "rating": 4.5, 
                "category": "museum",
                "types": ["museum", "tourist_attraction"],
                "price_level": 3,
                "geometry": {
                    "location": {
                        "lat": 40.7614,
                        "lng": -73.9776
                    }
                },
                "vicinity": "11 W 53rd St, New York, NY"
            },
        ],
        "total_distance": 18700,
        "total_duration": 4800,
        "budget_estimate": {"total": 214, "per_person": 107},
        "created_at": "2025-01-15 16:45",
        "tags": ["hipster", "art", "coffee"],
        "gpt_prompt": "Plan a hipster day in NYC with great coffee shops and art galleries"
    }
]

# Platform statistics for demo
DEMO_STATS = {
    "total_trips": 1247,
    "total_distance_km": 45632.1,
    "total_places": 8934,
    "avg_places_per_trip": 7.2,
    "cities_covered": 156,
    "countries_covered": 23,
    "time_saved_hours": 3568
}

# Popular destinations
POPULAR_DESTINATIONS = [
    ("Paris", 156),
    ("Tokyo", 142),
    ("New York", 134),
    ("London", 127),
    ("Barcelona", 98),
    ("Rome", 89),
    ("Amsterdam", 76),
    ("Berlin", 71)
]

# Sample testimonials
TESTIMONIALS = [
    {
        "name": "Sarah M.",
        "location": "San Francisco",
        "text": "WanderWhiz planned my perfect day in Barcelona! The AI understood exactly what I wanted - hidden tapas bars and local art galleries. Saved me hours of research!",
        "rating": 5,
        "trip": "Barcelona Art & Food Tour"
    },
    {
        "name": "James K.",
        "location": "London", 
        "text": "The route optimization is incredible. What would have taken me 8 hours of walking was compressed into a perfect 5-hour journey with efficient paths between locations.",
        "rating": 5,
        "trip": "London Historic Walking Tour"
    },
    {
        "name": "Maria L.",
        "location": "Mexico City",
        "text": "As a solo female traveler, having detailed addresses and ratings for each place made me feel so much safer and more confident exploring a new city.",
        "rating": 5,
        "trip": "Solo Mexico City Adventure"
    }
]

# Fun travel facts for loading screens
TRAVEL_FACTS = [
    "🌍 The average person visits 12 countries in their lifetime",
    "✈️ There are over 37,000 flights per day worldwide",
    "🗺️ Paris has more than 130 museums",
    "🍜 Tokyo has more Michelin-starred restaurants than any other city",
    "🎭 New York City has over 500 galleries and museums",
    "🌉 There are over 400 bridges in Amsterdam",
    "🍕 Americans eat 350 slices of pizza per second",
    "🏛️ Rome has more fountains than any other city in the world"
]

def get_demo_data():
    """Get all demo data for display"""
    return {
        "trips": DEMO_TRIPS,
        "stats": DEMO_STATS,
        "popular_destinations": POPULAR_DESTINATIONS,
        "testimonials": TESTIMONIALS,
        "travel_facts": TRAVEL_FACTS
    }

def get_random_travel_fact():
    """Get a random travel fact for loading screens"""
    import random
    return random.choice(TRAVEL_FACTS)
