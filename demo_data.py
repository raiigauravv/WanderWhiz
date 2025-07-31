"""
Demo Trip Data for WanderWhiz
===============================
Pre-configured demo trips to showcase the platform's capabilities
"""

def get_demo_data():
    """Return demo trip data"""
    return {
        "trips": [
            {
                "id": "demo-paris-romantic",
                "title": "💕 Paris Romantic",
                "city": "Paris, France",
                "description": "Romantic spots perfect for couples exploring the City of Love",
                "duration": "3 days",
                "total_distance": 15.2,
                "total_duration": "6 hours",
                "places": [
                    {
                        "name": "Eiffel Tower",
                        "formatted_address": "Champ de Mars, 5 Avenue Anatole France, 75007 Paris, France",
                        "types": ["tourist_attraction", "point_of_interest", "establishment"],
                        "rating": 4.6,
                        "user_ratings_total": 284127,
                        "price_level": 2,
                        "geometry": {
                            "location": {"lat": 48.8583736, "lng": 2.2922873}
                        },
                        "place_id": "ChIJLU7jZClu5kcR4PcOOO6p3I0"
                    },
                    {
                        "name": "Louvre Museum",
                        "formatted_address": "Rue de Rivoli, 75001 Paris, France",
                        "types": ["museum", "tourist_attraction", "point_of_interest", "establishment"],
                        "rating": 4.7,
                        "user_ratings_total": 171435,
                        "price_level": 3,
                        "geometry": {
                            "location": {"lat": 48.8606111, "lng": 2.337644}
                        },
                        "place_id": "ChIJD3uTd9hx5kcR1IQvGfr8dbk"
                    },
                    {
                        "name": "Seine River Cruise",
                        "formatted_address": "Port de la Bourdonnais, 75007 Paris, France",
                        "types": ["tourist_attraction", "travel_agency", "point_of_interest", "establishment"],
                        "rating": 4.3,
                        "user_ratings_total": 12589,
                        "price_level": 2,
                        "geometry": {
                            "location": {"lat": 48.8594, "lng": 2.2972}
                        },
                        "place_id": "ChIJGe5JFyZu5kcRQoa_8GO_a"
                    },
                    {
                        "name": "Sacré-Cœur Basilica",
                        "formatted_address": "35 Rue du Chevalier de la Barre, 75018 Paris, France",
                        "types": ["church", "tourist_attraction", "place_of_worship", "point_of_interest", "establishment"],
                        "rating": 4.5,
                        "user_ratings_total": 97234,
                        "price_level": 1,
                        "geometry": {
                            "location": {"lat": 48.8866969, "lng": 2.3431}
                        },
                        "place_id": "ChIJD7fiBh9u5kcRYJSMaMOCCwQ"
                    }
                ]
            },
            {
                "id": "demo-tokyo-foodie",
                "title": "🍜 Tokyo Foodie",
                "city": "Tokyo, Japan",
                "description": "Authentic Japanese cuisine adventure through Tokyo's best districts",
                "duration": "2 days",
                "total_distance": 12.8,
                "total_duration": "5 hours",
                "places": [
                    {
                        "name": "Tsukiji Outer Market",
                        "formatted_address": "Tsukiji, Chuo City, Tokyo 104-0045, Japan",
                        "types": ["tourist_attraction", "point_of_interest", "establishment"],
                        "rating": 4.2,
                        "user_ratings_total": 15678,
                        "price_level": 2,
                        "geometry": {
                            "location": {"lat": 35.6654, "lng": 139.7707}
                        },
                        "place_id": "ChIJ7T4j5M6LGGAR7hP7UEcfMQI"
                    },
                    {
                        "name": "Shibuya Crossing",
                        "formatted_address": "Shibuya Crossing, Shibuya City, Tokyo, Japan",
                        "types": ["tourist_attraction", "point_of_interest", "establishment"],
                        "rating": 4.3,
                        "user_ratings_total": 89234,
                        "price_level": 1,
                        "geometry": {
                            "location": {"lat": 35.6598, "lng": 139.7006}
                        },
                        "place_id": "ChIJVasFJQGNGGAREYtmYxdj_JM"
                    },
                    {
                        "name": "Senso-ji Temple",
                        "formatted_address": "2-3-1 Asakusa, Taito City, Tokyo 111-0032, Japan",
                        "types": ["buddhist_temple", "tourist_attraction", "place_of_worship", "point_of_interest", "establishment"],
                        "rating": 4.4,
                        "user_ratings_total": 67891,
                        "price_level": 0,
                        "geometry": {
                            "location": {"lat": 35.7147651, "lng": 139.7966553}
                        },
                        "place_id": "ChIJJ7LgqmuOGGARVWb8zaNwz5M"
                    },
                    {
                        "name": "Robot Restaurant",
                        "formatted_address": "1-7-1 Kabukicho, Shinjuku City, Tokyo 160-0021, Japan",
                        "types": ["restaurant", "point_of_interest", "food", "establishment"],
                        "rating": 4.0,
                        "user_ratings_total": 8945,
                        "price_level": 3,
                        "geometry": {
                            "location": {"lat": 35.6943, "lng": 139.7036}
                        },
                        "place_id": "ChIJXfQoRVaNGGARQZeGdV8jxdM"
                    }
                ]
            },
            {
                "id": "demo-nyc-hipster",
                "title": "☕ NYC Hipster",
                "city": "New York, USA",
                "description": "Trendy neighborhoods, artisanal coffee, and Brooklyn vibes",
                "duration": "2 days",
                "total_distance": 18.5,
                "total_duration": "7 hours",
                "places": [
                    {
                        "name": "Brooklyn Bridge",
                        "formatted_address": "Brooklyn Bridge, New York, NY, USA",
                        "types": ["tourist_attraction", "point_of_interest", "establishment"],
                        "rating": 4.6,
                        "user_ratings_total": 134567,
                        "price_level": 0,
                        "geometry": {
                            "location": {"lat": 40.7061, "lng": -73.9969}
                        },
                        "place_id": "ChIJbQGDdBP0woARAOKrOQvxJAQ"
                    },
                    {
                        "name": "DUMBO",
                        "formatted_address": "DUMBO, Brooklyn, NY, USA",
                        "types": ["neighborhood", "political", "sublocality", "sublocality_level_1"],
                        "rating": 4.5,
                        "user_ratings_total": 4578,
                        "price_level": 2,
                        "geometry": {
                            "location": {"lat": 40.7033, "lng": -73.9888}
                        },
                        "place_id": "ChIJpaXhYdPzoAR9_xFgjUvTdoI"
                    },
                    {
                        "name": "Williamsburg",
                        "formatted_address": "Williamsburg, Brooklyn, NY, USA",
                        "types": ["neighborhood", "political", "sublocality", "sublocality_level_1"],
                        "rating": 4.4,
                        "user_ratings_total": 7892,
                        "price_level": 3,
                        "geometry": {
                            "location": {"lat": 40.7081, "lng": -73.9571}
                        },
                        "place_id": "ChIJQSwfnJNYwokRDyYvyU4jCnQ"
                    },
                    {
                        "name": "High Line",
                        "formatted_address": "High Line, New York, NY, USA",
                        "types": ["park", "tourist_attraction", "point_of_interest", "establishment"],
                        "rating": 4.4,
                        "user_ratings_total": 98765,
                        "price_level": 0,
                        "geometry": {
                            "location": {"lat": 40.748, "lng": -74.0048}
                        },
                        "place_id": "ChIJKXbGOmNGwokRnZjUObtBOAI"
                    }
                ]
            }
        ]
    }
