"""
WanderWhiz - AI-Powered Travel Itinerary Planner
=================================================

A Flask web application that creates personalized travel itineraries using:
- OpenAI GPT for intelligent destination suggestions
- Google Places API for location data and ratings
- Google Routes API for optimized travel routing
- Firebase Firestore for secure trip storage
- Real-time budget estimation with preservation
- PDF export functionality with proper city names

Features:
- AI-powered trip planning based on user interests
- Interactive Google Maps integration
- Budget estimation and preservation across reloads
- Trip saving/loading with Firebase backend
- PDF export with detailed itineraries
- Responsive web interface

Author: WanderWhiz Team
Last Updated: July 30, 2025
"""

# Core Flask and web framework imports
from flask import Flask, render_template, request, jsonify, send_file, session
from dotenv import load_dotenv
import os
import json
from datetime import datetime
import uuid

# External API and service imports
import requests
import openai

# PDF generation imports
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from io import BytesIO

# Firebase integration with graceful fallback
try:
    from firebase_config import get_firebase_manager
    firebase_enabled = True
    print("🔥 Firebase integration enabled!")
except ImportError as e:
    firebase_enabled = False
    print("⚠️ Firebase not available:", e)

# Load environment variables
load_dotenv()

# Initialize Flask application
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your-secret-key-here")

# API Keys configuration
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# =============================================================================
# DATA CLEANING AND VALIDATION UTILITIES
# =============================================================================

def deep_clean_data(obj):
    """
    Recursively clean data to remove non-serializable objects and prepare for JSON.
    
    This function handles:
    - Undefined objects from various sources
    - Non-serializable Python objects
    - Nested dictionaries and lists
    - Type conversion for safe serialization
    
    Args:
        obj: Any Python object to be cleaned
        
    Returns:
        Cleaned object safe for JSON serialization, or None if object was invalid
    """
    if obj is None:
        return None
    
    # Handle Undefined objects by class name or string representation
    if hasattr(obj, '__class__') and 'Undefined' in str(obj.__class__):
        print(f"🧹 Removed Undefined object by class: {obj.__class__}")
        return None
    if str(obj) == 'Undefined' or repr(obj) == 'Undefined':
        print(f"🧹 Removed Undefined object by string: {obj}")
        return None
    if 'Undefined' in str(obj):
        print(f"🧹 Removed object containing 'Undefined': {type(obj)} - {str(obj)[:100]}")
        return None
    
    # Handle different data types
    if isinstance(obj, dict):
        cleaned = {}
        for key, value in obj.items():
            # Skip any key that contains 'Undefined'
            if 'Undefined' in str(key):
                print(f"🧹 Skipped Undefined key: {key}")
                continue
                
            cleaned_key = deep_clean_data(key)
            cleaned_value = deep_clean_data(value)
            
            # Keep the key-value pair if key is valid and either:
            # 1. Value is not None, OR
            # 2. Original value was explicitly None (preserve explicit None values)
            if cleaned_key is not None and (cleaned_value is not None or value is None):
                cleaned[cleaned_key] = cleaned_value
        return cleaned
    
    elif isinstance(obj, list):
        cleaned = []
        for item in obj:
            cleaned_item = deep_clean_data(item)
            if cleaned_item is not None:
                cleaned.append(cleaned_item)
        return cleaned
    
    elif isinstance(obj, tuple):
        cleaned = []
        for item in obj:
            cleaned_item = deep_clean_data(item)
            if cleaned_item is not None:
                cleaned.append(cleaned_item)
        return tuple(cleaned)
    
    elif isinstance(obj, (str, int, float, bool)):
        # Check for string representations of undefined
        if isinstance(obj, str) and obj.lower() in ['undefined', 'null', 'nan']:
            print(f"🧹 Removed undefined string: {obj}")
            return None
        return obj
    
    else:
        # For other types, try to convert to string or return None
        try:
            # Test if it's JSON serializable
            json.dumps(obj)
            return obj
        except (TypeError, ValueError):
            # If not serializable, check if it contains Undefined
            obj_str = str(obj)
            if 'Undefined' in obj_str:
                print(f"🧹 Removed non-serializable Undefined object: {type(obj)} - {obj_str[:100]}")
                return None
            else:
                print(f"🧹 Converting non-serializable object to string: {type(obj)}")
                return obj_str


def clean_budget_data(budget_data):
    """
    Clean and validate budget data to ensure consistent structure and valid values.
    
    This function handles both nested and flat budget structures:
    - Nested: {breakdown: {transportation: 25, food: 45}, total: 105}
    - Flat: {transportation: 25, food: 45, total: 105}
    
    It also validates and sanitizes all numeric values to prevent corruption
    from undefined, NaN, or invalid values that could cause frontend issues.
    
    Args:
        budget_data (dict): Raw budget data from various sources
        
    Returns:
        dict: Clean budget data in flat structure with validated numeric values
    """
    if not isinstance(budget_data, dict):
        return {
            'transportation': 0,
            'food': 0,
            'activities': 0,
            'miscellaneous': 0,
            'total': 0
        }
    
    def safe_budget_value(value, default=0):
        """
        Safely convert any value to a valid budget number.
        
        Handles common corruption cases:
        - 'undefined', 'NaN', 'null' strings
        - Python None, NaN, inf values
        - Invalid numeric strings
        
        Args:
            value: Any value that should represent a budget amount
            default (int): Default value if conversion fails
            
        Returns:
            int: Valid non-negative integer budget amount
        """
        if value is None:
            return default
        if isinstance(value, (int, float)):
            if str(value).lower() in ['nan', 'inf', '-inf'] or value != value:  # Check for NaN
                return default
            return max(0, int(value))
        if isinstance(value, str):
            if value.lower() in ['nan', 'undefined', 'null', 'none', '']:
                return default
            try:
                parsed = float(value)
                if parsed != parsed or parsed == float('inf') or parsed == float('-inf'):
                    return default
                return max(0, int(parsed))
            except (ValueError, TypeError):
                return default
        return default
    
    # Initialize values
    transportation = 0
    food = 0
    activities = 0
    miscellaneous = 0
    total = 0
    
    # Handle nested breakdown structure (what's actually saved)
    breakdown = budget_data.get('breakdown', {})
    if breakdown and isinstance(breakdown, dict):
        transportation = safe_budget_value(breakdown.get('transportation'))
        food = safe_budget_value(breakdown.get('food'))
        # activities might be stored as 'activities' or 'attractions'
        activities = safe_budget_value(breakdown.get('activities', breakdown.get('attractions', 0)))
        # miscellaneous might be stored as various keys
        misc_from_breakdown = (
            safe_budget_value(breakdown.get('other', 0)) +
            safe_budget_value(breakdown.get('entertainment', 0)) +
            safe_budget_value(breakdown.get('accommodation', 0))
        )
        miscellaneous = misc_from_breakdown
    else:
        # Handle flat structure (if it exists)
        transportation = safe_budget_value(budget_data.get('transportation'))
        food = safe_budget_value(budget_data.get('food'))
        activities = safe_budget_value(budget_data.get('activities'))
        miscellaneous = safe_budget_value(budget_data.get('miscellaneous'))
    
    # Add any top-level miscellaneous value
    miscellaneous += safe_budget_value(budget_data.get('miscellaneous'))
    
    # Get the saved total
    saved_total = safe_budget_value(budget_data.get('total'))
    
    # Calculate what the total should be
    calculated_total = transportation + food + activities + miscellaneous
    
    # Use saved total if it's valid and reasonable, otherwise use calculated
    if saved_total > 0 and abs(saved_total - calculated_total) <= calculated_total * 0.5:  # Allow 50% variance
        total = saved_total
        print(f"✅ Using preserved total: ${total}")
    else:
        total = calculated_total
        if saved_total > 0:
            print(f"🔄 Recalculated total from ${saved_total} to ${total}")
    
    result = {
        'transportation': transportation,
        'food': food,
        'activities': activities,
        'miscellaneous': miscellaneous,
        'total': total
    }
    
    print(f"🏦 Budget processed: {result}")
    return result


def clean_place_data(places):
    """Clean the places data to remove any undefined/None values that can't be serialized"""
    if not places or not isinstance(places, list):
        return []
    
    # First apply deep cleaning to remove Undefined objects
    places = deep_clean_data(places)
    if not places:
        return []
    
    cleaned_places = []
    
    for place in places:
        try:
            if not isinstance(place, dict):
                continue
                
            cleaned_place = {}
            
            # Helper function to safely get and clean values
            def safe_get(obj, key, default=None):
                if isinstance(obj, dict) and key in obj:
                    value = obj[key]
                    # Apply deep cleaning to the value
                    cleaned_value = deep_clean_data(value)
                    if cleaned_value is not None:
                        return cleaned_value
                return default
            
            # Clean and validate each field
            name = safe_get(place, 'name')
            if name and isinstance(name, (str, int, float)):
                cleaned_place['name'] = str(name)
            
            place_id = safe_get(place, 'place_id')
            if place_id and isinstance(place_id, (str, int)):
                cleaned_place['place_id'] = str(place_id)
            
            # Handle geometry carefully with extra validation
            geometry = safe_get(place, 'geometry')
            if geometry and isinstance(geometry, dict):
                location = safe_get(geometry, 'location')
                if location and isinstance(location, dict):
                    lat = safe_get(location, 'lat')
                    lng = safe_get(location, 'lng')
                    if lat is not None and lng is not None:
                        try:
                            lat_float = float(lat)
                            lng_float = float(lng)
                            # Validate coordinate ranges
                            if (-90 <= lat_float <= 90 and -180 <= lng_float <= 180 and 
                                lat_float != 0 and lng_float != 0):
                                cleaned_place['geometry'] = {
                                    'location': {
                                        'lat': lat_float,
                                        'lng': lng_float
                                    }
                                }
                        except (ValueError, TypeError):
                            continue  # Skip this place if coordinates are invalid
            
            rating = safe_get(place, 'rating')
            if rating is not None:
                try:
                    rating_float = float(rating)
                    if 0 <= rating_float <= 5:  # Valid rating range
                        cleaned_place['rating'] = rating_float
                except (ValueError, TypeError):
                    pass
            
            vicinity = safe_get(place, 'vicinity')
            if vicinity and isinstance(vicinity, str):
                cleaned_place['vicinity'] = str(vicinity)
            
            formatted_address = safe_get(place, 'formatted_address')
            if formatted_address and isinstance(formatted_address, str):
                cleaned_place['formatted_address'] = str(formatted_address)
            
            price_level = safe_get(place, 'price_level')
            if price_level is not None:
                try:
                    price_int = int(price_level)
                    if 0 <= price_int <= 4:  # Valid price level range
                        cleaned_place['price_level'] = price_int
                except (ValueError, TypeError):
                    pass
            
            types = safe_get(place, 'types')
            if types and isinstance(types, list):
                cleaned_types = []
                for t in types:
                    if t is not None and isinstance(t, str):
                        cleaned_types.append(str(t))
                if cleaned_types:
                    cleaned_place['types'] = cleaned_types
            
            # Only add places that have the essential data and valid coordinates
            if ('name' in cleaned_place and 'geometry' in cleaned_place and 
                'location' in cleaned_place['geometry']):
                cleaned_places.append(cleaned_place)
                
        except Exception as e:
            print(f"⚠️ Error cleaning place data: {e}")
            continue
    
    return cleaned_places

def get_place_details(place_id):
    """Fetch detailed information including formatted address for a place"""
    try:
        details_url = f"https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            'place_id': place_id,
            'fields': 'formatted_address,opening_hours,website,international_phone_number,price_level,photos',
            'key': GOOGLE_MAPS_API_KEY
        }
        
        response = requests.get(details_url, params=params)
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'OK':
                return result.get('result', {})
    except Exception as e:
        print(f"Error fetching place details: {e}")
    
    return {}

def get_address_from_coordinates(lat, lng):
    """Get formatted address from coordinates using reverse geocoding"""
    try:
        geocoding_url = f"https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'latlng': f"{lat},{lng}",
            'key': GOOGLE_MAPS_API_KEY
        }
        
        response = requests.get(geocoding_url, params=params)
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'OK' and result.get('results'):
                return result['results'][0].get('formatted_address', 'Address not available')
    except Exception as e:
        print(f"Error fetching address: {e}")
    
    return 'Address not available'

def estimate_budget(places):
    """Estimate budget for the itinerary based on place types and price levels"""
    total_budget = 0
    budget_breakdown = {
        'transportation': 0,
        'food': 0,
        'activities': 0,
        'accommodation': 0
    }
    
    # Base transportation cost (per day)
    budget_breakdown['transportation'] = 25
    
    for place in places:
        price_level = place.get('price_level', 2)  # Default to moderate
        place_types = place.get('types', [])
        
        # Food costs
        if any(food_type in place_types for food_type in ['restaurant', 'food', 'meal_takeaway', 'cafe']):
            food_cost = [15, 25, 45, 75, 120][min(price_level, 4)]
            budget_breakdown['food'] += food_cost
        
        # Activity costs
        elif any(activity_type in place_types for activity_type in 
                ['tourist_attraction', 'museum', 'amusement_park', 'zoo', 'aquarium']):
            activity_cost = [10, 20, 35, 50, 80][min(price_level, 4)]
            budget_breakdown['activities'] += activity_cost
        
        # Accommodation (if lodging is included)
        elif any(acc_type in place_types for acc_type in ['lodging', 'hotel']):
            acc_cost = [60, 120, 200, 350, 500][min(price_level, 4)]
            budget_breakdown['accommodation'] += acc_cost
    
    # Add miscellaneous costs (10% of total)
    subtotal = sum(budget_breakdown.values())
    miscellaneous = subtotal * 0.1
    total_budget = subtotal + miscellaneous
    
    return {
        'total': round(total_budget),
        'breakdown': {k: round(v) for k, v in budget_breakdown.items()},
        'miscellaneous': round(miscellaneous)
    }


def get_route_directions(places):
    """Get route directions for a list of places"""
    try:
        if len(places) < 2:
            return None
            
        # Build Directions API waypoints
        origin = places[0]["geometry"]["location"]
        destination = places[-1]["geometry"]["location"]
        waypoints = places[1:-1]  # Middle points become waypoints

        # Use the newer Routes API instead of legacy Directions API
        # Build the request body for Routes API
        route_request = {
            "origin": {
                "location": {
                    "latLng": {
                        "latitude": origin['lat'],
                        "longitude": origin['lng']
                    }
                }
            },
            "destination": {
                "location": {
                    "latLng": {
                        "latitude": destination['lat'],
                        "longitude": destination['lng']
                    }
                }
            },
            "travelMode": "DRIVE",
            "routingPreference": "TRAFFIC_AWARE",
            "computeAlternativeRoutes": False,
            "routeModifiers": {
                "avoidTolls": False,
                "avoidHighways": False,
                "avoidFerries": False
            },
            "languageCode": "en-US",
            "units": "IMPERIAL"
        }

        # Add waypoints if any
        if waypoints:
            route_request["intermediates"] = []
            for wp in waypoints:
                route_request["intermediates"].append({
                    "location": {
                        "latLng": {
                            "latitude": wp["geometry"]["location"]["lat"],
                            "longitude": wp["geometry"]["location"]["lng"]
                        }
                    }
                })
            # Enable optimization for waypoints
            route_request["optimizeWaypointOrder"] = True

        # Use Routes API endpoint
        routes_url = "https://routes.googleapis.com/directions/v2:computeRoutes"
        
        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': GOOGLE_MAPS_API_KEY,
            'X-Goog-FieldMask': 'routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline,routes.legs,routes.optimizedIntermediateWaypointIndex'
        }
        
        # Get directions from Google Routes API
        directions_resp = requests.post(routes_url, json=route_request, headers=headers)
        routes_data = directions_resp.json()
        
        if directions_resp.status_code != 200:
            print(f"Routes API error: {routes_data}")
            return None

        # Convert Routes API response to format compatible with our frontend
        if 'routes' not in routes_data or not routes_data['routes']:
            return None

        # Transform the new API response to match the old format for frontend compatibility
        route = routes_data['routes'][0]
        
        # Extract polyline from the route
        polyline_points = ""
        
        # First try to get from route-level polyline (if it exists)
        if 'polyline' in route and 'encodedPolyline' in route['polyline']:
            polyline_points = route['polyline']['encodedPolyline']
        
        # If no route-level polyline, combine leg polylines
        elif 'legs' in route and route['legs']:
            for leg in route['legs']:
                if 'polyline' in leg and 'encodedPolyline' in leg['polyline']:
                    polyline_points += leg['polyline']['encodedPolyline']
        
        directions = {
            "status": "OK",
            "routes": [{
                "legs": route.get('legs', []),
                "overview_polyline": {
                    "points": polyline_points
                },
                "summary": f"Optimized route through {len(places)} places",
                "distance": sum(leg.get('distanceMeters', 0) for leg in route.get('legs', [])),
                "duration": sum(int(leg.get('duration', '0s').replace('s', '')) for leg in route.get('legs', []))
            }]
        }
        
        return directions
        
    except Exception as e:
        print(f"Error getting route directions: {e}")
        return None


# =============================================================================
# MAIN APPLICATION ROUTES
# =============================================================================

@app.route("/", methods=["GET", "POST"])
def index():
    """
    Main application route that handles the landing page and basic place searches.
    
    GET: Renders the main page with default values
    POST: Processes city/interest form submissions and fetches places
    
    Returns:
        Rendered template with places data and map configuration
    """
    places = []
    lat = 43.65107  # Default: Toronto coordinates
    lng = -79.347015
    city = ""  # Default values for GET requests
    interest = ""

    if request.method == "POST":
        city = request.form["city"]
        interest = request.form["interest"]
        
        print(f"🔍 Searching for '{interest}' in '{city}'")

        try:
            # Use text search instead of geocoding + nearby search
            # This combines both city and interest in one query
            query = f"{interest} in {city}"
            
            place_url = (
                f"https://maps.googleapis.com/maps/api/place/textsearch/json"
                f"?query={query}"
                f"&key={GOOGLE_MAPS_API_KEY}"
            )
            
            print(f"🔗 Places API URL: {place_url}")
            
            place_resp = requests.get(place_url).json()
            
            print(f"🏪 Places API status: {place_resp.get('status')}")
            
            if place_resp.get("status") == "OK":
                raw_places = place_resp.get("results", [])[:10]  # Limit to 10 places per interest for performance
                print(f"🔄 Processing {len(raw_places)} places from search (limited to 10 per interest)")
                
                # Enhance places with detailed information
                enhanced_places = []
                for place in raw_places:
                    try:
                        enhanced_place = place.copy()
                        
                        # Add formatted address if available
                        if not enhanced_place.get('formatted_address') and enhanced_place.get('place_id'):
                            details = get_place_details(enhanced_place['place_id'])
                            if details.get('formatted_address'):
                                enhanced_place['formatted_address'] = details['formatted_address']
                        
                        # If still no address, try reverse geocoding
                        if not enhanced_place.get('formatted_address') and enhanced_place.get('geometry'):
                            geometry = enhanced_place.get('geometry', {})
                            location = geometry.get('location', {}) if isinstance(geometry, dict) else {}
                            if isinstance(location, dict) and 'lat' in location and 'lng' in location:
                                try:
                                    lat_coord = float(location['lat'])
                                    lng_coord = float(location['lng'])
                                    enhanced_place['formatted_address'] = get_address_from_coordinates(lat_coord, lng_coord)
                                except (ValueError, TypeError):
                                    pass
                        
                        enhanced_places.append(enhanced_place)
                    except Exception as enhance_error:
                        print(f"⚠️ Error enhancing place: {enhance_error}")
                        enhanced_places.append(place)  # Add original place if enhancement fails
                
                places = clean_place_data(enhanced_places)
                print(f"✅ Enhanced and cleaned places: {len(places)}")
                
                # Ensure places is valid
                if not places or not isinstance(places, list):
                    places = []
                    print("⚠️ No valid places found after cleaning")
                
                # Filter places to only include those near the searched city
                # Get city coordinates first
                city_lat, city_lng = None, None
                
                # Try to get coordinates from the first valid place result
                for place in places:
                    if place.get('geometry', {}).get('location'):
                        # Check if this place is likely in the searched city by looking at coordinates
                        place_lat = place['geometry']['location']['lat']
                        place_lng = place['geometry']['location']['lng']
                        
                        # Use geocoding to get the actual city coordinates for comparison
                        if not city_lat:
                            try:
                                geocoding_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={city}&key={GOOGLE_MAPS_API_KEY}"
                                geocoding_resp = requests.get(geocoding_url).json()
                                
                                if geocoding_resp.get("status") == "OK" and geocoding_resp.get("results"):
                                    location = geocoding_resp["results"][0]["geometry"]["location"]
                                    city_lat, city_lng = location["lat"], location["lng"]
                                    print(f"📍 City center coordinates: {city_lat}, {city_lng}")
                                    break
                            except Exception as geo_error:
                                print(f"❌ Geocoding failed: {geo_error}")
                
                # Filter places to only include those within reasonable distance of city center
                if city_lat and city_lng:
                    filtered_places = []
                    for place in places:
                        if place.get('geometry', {}).get('location'):
                            place_lat = place['geometry']['location']['lat']
                            place_lng = place['geometry']['location']['lng']
                            
                            # Calculate rough distance (in degrees) - about 30km radius for better filtering
                            lat_diff = abs(place_lat - city_lat)
                            lng_diff = abs(place_lng - city_lng)
                            distance = (lat_diff ** 2 + lng_diff ** 2) ** 0.5
                            
                            # Keep places within ~30km (roughly 0.3 degrees) - tighter filter
                            if distance < 0.3:
                                filtered_places.append(place)
                            else:
                                print(f"🚫 Filtered out {place.get('name', 'Unknown')} - distance: {distance:.3f} degrees")
                    
                    places = filtered_places
                    print(f"🎯 Filtered to {len(places)} places near {city}")
                
                # Get the center coordinates from the first place if available
                if places and places[0].get('geometry', {}).get('location'):
                    lat = places[0]['geometry']['location']['lat']
                    lng = places[0]['geometry']['location']['lng']
                    print(f"📍 Using coordinates from first result: {lat}, {lng}")
                elif city_lat and city_lng:
                    # Use city center if no places found but we have city coordinates
                    lat, lng = city_lat, city_lng
                    print(f"📍 Using city center coordinates: {lat}, {lng}")
                
            else:
                print(f"❌ Places API error: {place_resp.get('status')}")
                print(f"❌ Error message: {place_resp.get('error_message', 'No error message')}")
                
                # If API fails, try to get coordinates for the city at least
                if city:
                    try:
                        geocoding_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={city}&key={GOOGLE_MAPS_API_KEY}"
                        geocoding_resp = requests.get(geocoding_url).json()
                        
                        if geocoding_resp.get("status") == "OK" and geocoding_resp.get("results"):
                            location = geocoding_resp["results"][0]["geometry"]["location"]
                            lat, lng = location["lat"], location["lng"]
                            print(f"📍 Got city coordinates from geocoding: {lat}, {lng}")
                    except Exception as geo_error:
                        print(f"❌ Geocoding also failed: {geo_error}")

        except Exception as e:
            print(f"💥 Error in search: {e}")
            # Continue with default values if there's an error

    return render_template("index.html", 
                         api_key=GOOGLE_MAPS_API_KEY,
                         places=places, 
                         places_json=json.dumps(places),
                         lat=lat, 
                         lng=lng,
                         city=city,
                         interest=interest)


# =============================================================================
# AI-POWERED TRAVEL PLANNING ROUTES
# =============================================================================

@app.route("/gpt-assist", methods=["POST"])
def gpt_assist():
    """
    AI-powered travel planning using OpenAI GPT.
    
    Processes natural language travel requests and extracts:
    - Destination city
    - Travel interests/preferences
    - Finds relevant places using Google Places API
    - Returns structured data for itinerary building
    
    Returns:
        JSON response with places data and extracted preferences
    """
    user_prompt = request.form["prompt"]
    print(f"🧠 GPT User prompt: {user_prompt}")
    
    try:
        # Initialize OpenAI client (using new API format)
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        # Use OpenAI to extract city + interests
        gpt_query = f"""
        You are a travel planning assistant. Extract the city name and key interests (like bookstores, parks, cozy cafes, hidden spots, etc.)
        from this prompt: "{user_prompt}". 
        
        Respond in this exact JSON format (no extra text):
        {{
            "city": "city_name",
            "interests": ["keyword1", "keyword2", "keyword3"]
        }}
        
        Make sure to include 2-4 relevant keywords that would work well with Google Places API.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": gpt_query}],
            temperature=0.4
        )

        json_text = response.choices[0].message.content.strip()
        print(f"🤖 GPT response: {json_text}")
        
        # Parse GPT response
        extracted = json.loads(json_text)
        city = extracted["city"]
        interests = extracted["interests"]
        
        print(f"📍 Extracted city: {city}")
        print(f"🎯 Extracted interests: {interests}")

        # Get city coordinates
        geo_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={city}&key={GOOGLE_MAPS_API_KEY}"
        geo_resp = requests.get(geo_url).json()

        if geo_resp["status"] != "OK":
            return render_template("index.html", 
                                 api_key=GOOGLE_MAPS_API_KEY,
                                 error="Could not find the city you mentioned. Please try again.",
                                 lat=43.65107, lng=-79.347015)

        location = geo_resp["results"][0]["geometry"]["location"]
        lat, lng = location["lat"], location["lng"]
        print(f"📍 City coordinates: {lat}, {lng}")

        # Aggregate results across interests using text search
        all_places = []
        for keyword in interests:
            query = f"{keyword} in {city}"
            place_url = (
                f"https://maps.googleapis.com/maps/api/place/textsearch/json"
                f"?query={query}"
                f"&key={GOOGLE_MAPS_API_KEY}"
            )
            print(f"🔍 Searching: {query}")
            
            resp = requests.get(place_url).json()
            if resp.get("status") == "OK":
                results = resp.get("results", [])[:10]  # Limit to 10 places per interest for performance
                print(f"✅ Found {len(results)} places for '{keyword}' (limited to 10)")
                all_places.extend(results)
            else:
                print(f"❌ Search failed for '{keyword}': {resp.get('status')}")

        # Deduplicate by place_id and clean data
        unique_places = {}
        for place in all_places:
            place_id = place.get("place_id")
            if place_id and place_id not in unique_places:
                unique_places[place_id] = place

        raw_places = list(unique_places.values())
        print(f"🔄 Processing {len(raw_places)} unique places")
        
        # Clean and validate places data
        places = clean_place_data(raw_places)
        print(f"✅ Cleaned to {len(places) if places else 0} valid places")
        
        # Ensure places is a list and not None
        if not places or not isinstance(places, list):
            places = []
            print("⚠️ No valid places found after cleaning")
        
        # Filter places to be near the city center (same logic as regular search)
        if lat and lng and places:
            filtered_places = []
            try:
                for place in places:
                    if not isinstance(place, dict):
                        continue
                        
                    geometry = place.get('geometry', {})
                    location = geometry.get('location', {}) if isinstance(geometry, dict) else {}
                    
                    if isinstance(location, dict) and 'lat' in location and 'lng' in location:
                        try:
                            place_lat = float(location['lat'])
                            place_lng = float(location['lng'])
                            
                            # Calculate distance from city center
                            lat_diff = abs(place_lat - lat)
                            lng_diff = abs(place_lng - lng)
                            distance = (lat_diff ** 2 + lng_diff ** 2) ** 0.5
                            
                            # Keep places within ~30km
                            if distance < 0.3:
                                filtered_places.append(place)
                            else:
                                print(f"🚫 Filtered out {place.get('name', 'Unknown')} - distance: {distance:.3f} degrees")
                        except (ValueError, TypeError) as e:
                            print(f"⚠️ Invalid coordinates for {place.get('name', 'Unknown')}: {e}")
                            continue
                
                places = filtered_places
                print(f"🎯 GPT found {len(places)} places total")
            except Exception as filter_error:
                print(f"⚠️ Error filtering places: {filter_error}")
                # Keep original places if filtering fails
                pass

        # Ensure places is valid for JSON serialization
        places = places or []  # Ensure it's never None
        if places:
            try:
                # Test JSON serialization
                json.dumps(places)
            except TypeError as json_error:
                print(f"⚠️ JSON serialization error: {json_error}")
                # Re-clean the data more aggressively
                places = clean_place_data(places) or []

        return render_template("index.html", 
                             api_key=GOOGLE_MAPS_API_KEY,
                             places=places, 
                             places_json=json.dumps(places),
                             lat=lat, 
                             lng=lng,
                             gpt_prompt=user_prompt,
                             city=city,
                             interest=", ".join(interests))

    except Exception as e:
        print(f"💥 GPT Error: {e}")
        import traceback
        traceback.print_exc()
        return render_template("index.html", 
                             api_key=GOOGLE_MAPS_API_KEY,
                             places=[],  # Always provide empty list instead of None
                             places_json=json.dumps([]),
                             lat=43.65107, lng=-79.347015,
                             error=f"Sorry, something went wrong: {str(e)}")


@app.route("/itinerary", methods=["POST"])
def itinerary():
    """Build an optimized itinerary from selected places"""
    selected_ids = request.form.getlist("place_ids")
    all_places_json = request.form.get("all_places_json")
    city_name = request.form.get("city", "")  # Get city from form data
    
    print(f"🎯 Selected place IDs: {selected_ids}")
    print(f"🏙️ City from form: {city_name}")
    
    if not all_places_json:
        return "Error: No places data available", 400
    
    try:
        import json
        import math
        
        # Debug: Print the raw JSON data
        print(f"🔍 Raw all_places_json: {repr(all_places_json[:200])}")
        
        # Try to parse JSON with better error handling
        try:
            places = json.loads(all_places_json)
        except json.JSONDecodeError as json_err:
            print(f"❌ JSON Parse Error: {json_err}")
            print(f"❌ Problematic JSON: {repr(all_places_json[:500])}")
            return f"Error: Invalid JSON data - {str(json_err)}", 400
            
        print(f"📍 Total places available: {len(places)}")
        
        # Clean the places data to remove any undefined/problematic values
        places = clean_place_data(places)
        print(f"✅ Cleaned places data: {len(places)}")
        
        # Validate and filter places with proper coordinates
        def is_valid_coordinate(lat, lng):
            """Check if coordinates are valid"""
            try:
                if lat is None or lng is None:
                    return False
                lat_float = float(lat)
                lng_float = float(lng)
                return (lat_float != 0 and lng_float != 0 and
                       -90 <= lat_float <= 90 and -180 <= lng_float <= 180)
            except (ValueError, TypeError):
                return False
        
        def calculate_distance(lat1, lng1, lat2, lng2):
            """Calculate distance between two points in kilometers"""
            try:
                R = 6371  # Earth's radius in kilometers
                
                lat1_rad = math.radians(float(lat1))
                lat2_rad = math.radians(float(lat2))
                delta_lat = math.radians(float(lat2) - float(lat1))
                delta_lng = math.radians(float(lng2) - float(lng1))
                
                a = (math.sin(delta_lat / 2) ** 2 + 
                     math.cos(lat1_rad) * math.cos(lat2_rad) * 
                     math.sin(delta_lng / 2) ** 2)
                c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
                
                return R * c
            except (ValueError, TypeError) as e:
                print(f"⚠️ Error calculating distance: {e}")
                return float('inf')  # Return large distance on error
        
        # First pass: collect places with valid coordinates and clean data
        valid_places = []
        for idx_str in selected_ids:
            try:
                idx = int(idx_str)
                if idx < len(places):
                    place = places[idx]
                    
                    # Ensure place is a dictionary and has required structure
                    if not isinstance(place, dict):
                        print(f"❌ Place {idx} is not a dictionary: {type(place)}")
                        continue
                    
                    # Clean the place data again to ensure no undefined values
                    cleaned_place = {}
                    for key, value in place.items():
                        if value is not None and str(value).lower() != 'undefined':
                            cleaned_place[key] = value
                    
                    if cleaned_place.get('geometry') and cleaned_place['geometry'].get('location'):
                        lat = cleaned_place['geometry']['location'].get('lat')
                        lng = cleaned_place['geometry']['location'].get('lng')
                        if is_valid_coordinate(lat, lng):
                            valid_places.append(cleaned_place)
                            print(f"✅ Valid place: {cleaned_place.get('name')} at ({lat}, {lng})")
                        else:
                            print(f"❌ Invalid coordinates for: {cleaned_place.get('name')} at ({lat}, {lng})")
                    else:
                        print(f"❌ Missing geometry for place: {cleaned_place.get('name')}")
                else:
                    print(f"❌ Place index {idx} out of range (max: {len(places)-1})")
            except (ValueError, IndexError, TypeError) as e:
                print(f"❌ Error processing place ID {idx_str}: {e}")
                continue
        
        print(f"✅ Selected places with valid coordinates: {len(valid_places)}")
        
        if len(valid_places) < 2:
            return "Please select at least 2 places with valid coordinates to build an itinerary.", 400
            
        # Second pass: filter out places that are too far from the main cluster
        # Calculate center point of all places
        total_lat = sum(place['geometry']['location']['lat'] for place in valid_places)
        total_lng = sum(place['geometry']['location']['lng'] for place in valid_places)
        center_lat = total_lat / len(valid_places)
        center_lng = total_lng / len(valid_places)
        
        # Filter places within reasonable distance from center (max 15km for city-level clustering)
        MAX_DISTANCE_KM = 15
        selected_places = []
        
        for place in valid_places:
            lat = place['geometry']['location']['lat']
            lng = place['geometry']['location']['lng']
            distance = calculate_distance(center_lat, center_lng, lat, lng)
            
            if distance <= MAX_DISTANCE_KM:
                selected_places.append(place)
                print(f"✅ Place within cluster: {place.get('name')} ({distance:.1f}km from center)")
            else:
                print(f"⚠️ Place too far from cluster: {place.get('name')} ({distance:.1f}km from center, skipping)")
        
        print(f"✅ Selected places after clustering: {len(selected_places)}")
        
        # Debug: Print first place to see its structure
        if selected_places:
            print(f"🔍 First place structure: {json.dumps(selected_places[0], indent=2)}")
        
        if len(selected_places) < 2:
            return "After geographic clustering, less than 2 places remain. Please select places that are closer together.", 400

        # Build Directions API waypoints
        origin = selected_places[0]["geometry"]["location"]
        destination = selected_places[-1]["geometry"]["location"]
        waypoints = selected_places[1:-1]  # Middle points become waypoints

        # Use the newer Routes API instead of legacy Directions API
        # Build the request body for Routes API
        route_request = {
            "origin": {
                "location": {
                    "latLng": {
                        "latitude": origin['lat'],
                        "longitude": origin['lng']
                    }
                }
            },
            "destination": {
                "location": {
                    "latLng": {
                        "latitude": destination['lat'],
                        "longitude": destination['lng']
                    }
                }
            },
            "travelMode": "DRIVE",
            "routingPreference": "TRAFFIC_AWARE",
            "computeAlternativeRoutes": False,
            "routeModifiers": {
                "avoidTolls": False,
                "avoidHighways": False,
                "avoidFerries": False
            },
            "languageCode": "en-US",
            "units": "IMPERIAL"
        }

        # Add waypoints if any
        if waypoints:
            route_request["intermediates"] = []
            for wp in waypoints:
                route_request["intermediates"].append({
                    "location": {
                        "latLng": {
                            "latitude": wp["geometry"]["location"]["lat"],
                            "longitude": wp["geometry"]["location"]["lng"]
                        }
                    }
                })
            # Enable optimization for waypoints
            route_request["optimizeWaypointOrder"] = True

        # Use Routes API endpoint
        routes_url = "https://routes.googleapis.com/directions/v2:computeRoutes"
        
        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': GOOGLE_MAPS_API_KEY,
            'X-Goog-FieldMask': 'routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline,routes.legs,routes.optimizedIntermediateWaypointIndex'
        }
        
        print(f"🗺️ Routes API URL: {routes_url}")
        print(f"📦 Request body: {json.dumps(route_request, indent=2)}")

        # Get directions from Google Routes API
        directions_resp = requests.post(routes_url, json=route_request, headers=headers)
        routes_data = directions_resp.json()
        
        print(f"🛣️ Routes API status code: {directions_resp.status_code}")
        print(f"🛣️ Routes API response: {json.dumps(routes_data, indent=2)[:500]}...")
        
        if directions_resp.status_code != 200:
            error_msg = routes_data.get('error', {}).get('message', 'Unknown error')
            return f"Error getting directions: {error_msg}", 400

        # Convert Routes API response to format compatible with our frontend
        if 'routes' not in routes_data or not routes_data['routes']:
            return "No routes found", 400

        # Transform the new API response to match the old format for frontend compatibility
        route = routes_data['routes'][0]
        
        # Extract polyline from the route - Routes API v2 has a different structure
        polyline_points = ""
        
        # First try to get from route-level polyline (if it exists)
        if 'polyline' in route and 'encodedPolyline' in route['polyline']:
            polyline_points = route['polyline']['encodedPolyline']
            print(f"📍 Using route-level polyline")
        
        # If no route-level polyline, combine leg polylines
        elif 'legs' in route and route['legs']:
            print(f"📍 Combining {len(route['legs'])} leg polylines")
            for i, leg in enumerate(route['legs']):
                if 'polyline' in leg and 'encodedPolyline' in leg['polyline']:
                    leg_polyline = leg['polyline']['encodedPolyline']
                    polyline_points += leg_polyline
                    print(f"📍 Added leg {i+1} polyline: {len(leg_polyline)} chars")
        
        # Ensure we have proper place ordering based on optimized route
        ordered_places = selected_places.copy()
        if 'optimizedIntermediateWaypointIndex' in route:
            # Reorder based on Google's optimization
            optimized_indices = route['optimizedIntermediateWaypointIndex']
            print(f"📍 Reordering waypoints: {optimized_indices}")
            
            if len(optimized_indices) == len(selected_places) - 2:  # Excluding origin and destination
                # Keep origin (first) and destination (last), reorder middle points
                reordered_middle = []
                for idx in optimized_indices:
                    if idx + 1 < len(selected_places) - 1:
                        reordered_middle.append(selected_places[idx + 1])
                
                ordered_places = [selected_places[0]] + reordered_middle + [selected_places[-1]]
                print(f"📍 Reordered to: {[p['name'] for p in ordered_places]}")
            
        directions = {
            "status": "OK",
            "routes": [{
                "legs": route.get('legs', []),
                "overview_polyline": {
                    "points": polyline_points
                },
                "summary": f"Optimized route through {len(ordered_places)} places",
                "distance": sum(leg.get('distanceMeters', 0) for leg in route.get('legs', [])),
                "duration": sum(int(leg.get('duration', '0s').replace('s', '')) for leg in route.get('legs', []))
            }]
        }
        
        print(f"🗺️ Final polyline length: {len(polyline_points)} characters")
        print(f"🗺️ Route summary: {directions['routes'][0]['summary']}")
        print(f"🗺️ Total distance: {directions['routes'][0]['distance']} meters")
        print(f"🗺️ Total duration: {directions['routes'][0]['duration']} seconds")

        # Test JSON serialization before passing to template
        try:
            json.dumps(ordered_places)
            json.dumps(directions)
            print("✅ Data serialization test passed")
        except (TypeError, ValueError) as json_error:
            print(f"❌ JSON serialization error: {json_error}")
            # Apply deep cleaning to remove any Undefined objects
            ordered_places = deep_clean_data(ordered_places)
            directions = deep_clean_data(directions)
            print("🔄 Applied deep cleaning to data")

        # Calculate budget estimate
        budget_estimate = estimate_budget(ordered_places)
        budget_estimate = deep_clean_data(budget_estimate)  # Clean budget data too
        
        # Extract basic info for context - use city from form data if available
        city = city_name if city_name else (ordered_places[0].get('vicinity', 'Unknown').split(',')[0] if ordered_places else 'Unknown')
        total_distance = directions['routes'][0]['distance'] if directions and directions.get('routes') else 0
        total_duration = directions['routes'][0]['duration'] if directions and directions.get('routes') else 0

        # Apply deep cleaning to all template variables
        template_data = {
            'directions': directions,
            'places': ordered_places,
            'budget_estimate': budget_estimate,
            'city': city,
            'total_distance': total_distance,
            'total_duration': total_duration,
            'api_key': GOOGLE_MAPS_API_KEY
        }
        
        # Final deep clean of all template data
        template_data = deep_clean_data(template_data)
        
        # Additional verification - try to JSON serialize the data to catch any remaining issues
        try:
            import json
            json.dumps(template_data)
            print("✅ Template data is JSON serializable")
        except Exception as json_error:
            print(f"❌ Template data JSON error: {json_error}")
            # If there's still an issue, remove the problematic parts
            safe_template_data = {
                'places': template_data.get('places', []),
                'budget_estimate': template_data.get('budget_estimate', {}),
                'city': template_data.get('city', 'Unknown'),
                'total_distance': template_data.get('total_distance', 0),
                'total_duration': template_data.get('total_duration', 0),
                'api_key': GOOGLE_MAPS_API_KEY,
                'directions': None  # Skip directions if problematic
            }
            template_data = safe_template_data

        return render_template("itinerary.html", **template_data)
    
    except Exception as e:
        print(f"💥 Error in itinerary: {e}")
        return f"Error building itinerary: {str(e)}", 500


# 📤 Phase 4.4 - Export Trip (PDF + Google Maps link)
@app.route("/estimate-budget", methods=["POST"])
def estimate_budget_api():
    """API endpoint to estimate budget for given places"""
    try:
        data = request.get_json()
        places = data.get('places', [])
        
        if not places:
            return jsonify({"error": "No places provided"}), 400
        
        budget_info = estimate_budget(places)
        return jsonify(budget_info)
        
    except Exception as e:
        print(f"💥 Budget Estimation Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/export-pdf", methods=["POST"])
def export_pdf():
    """Generate and download itinerary as PDF with enhanced styling"""
    try:
        data = request.get_json()
        places = data.get('places', [])
        route_info = data.get('route_info', {})
        city = data.get('city', 'Unknown')  # Get city from request data
        
        # Enhance places with addresses and budget estimation
        enhanced_places = []
        for place in places:
            enhanced_place = place.copy()
            
            # Get address if not available
            if not place.get('vicinity') or place.get('vicinity') == 'Address not available':
                if place.get('place_id'):
                    details = get_place_details(place['place_id'])
                    enhanced_place['formatted_address'] = details.get('formatted_address', 'Address not available')
                elif place.get('geometry'):
                    lat = place['geometry']['location']['lat']
                    lng = place['geometry']['location']['lng']
                    enhanced_place['formatted_address'] = get_address_from_coordinates(lat, lng)
                else:
                    enhanced_place['formatted_address'] = 'Address not available'
            else:
                enhanced_place['formatted_address'] = place.get('vicinity')
            
            enhanced_places.append(enhanced_place)
        
        # Calculate budget
        budget_info = estimate_budget(enhanced_places)
        
        # Create PDF with ReportLab - include city name in filename
        filename = f"WanderWhiz_{city}_Itinerary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = filename
        
        # Create the PDF document
        doc = SimpleDocTemplate(filepath, pagesize=A4, 
                              rightMargin=50, leftMargin=50, 
                              topMargin=60, bottomMargin=50)
        
        # Define styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#7F8C8D'),
            spaceAfter=25,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#E67E22'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        )
        
        place_name_style = ParagraphStyle(
            'PlaceName',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#2980B9'),
            spaceAfter=5,
            fontName='Helvetica-Bold'
        )
        
        detail_style = ParagraphStyle(
            'Details',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#34495E'),
            spaceAfter=3,
            fontName='Helvetica'
        )
        
        # Build PDF content
        story = []
        
        # Header section with gradient-like effect
        story.append(Paragraph(f"🌟 WanderWhiz Travel Itinerary - {city} 🌟", title_style))
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", subtitle_style))
        story.append(Spacer(1, 20))
        
        # Budget Summary Section
        story.append(Paragraph("💰 Budget Estimate", heading_style))
        
        budget_data = [
            ['Category', 'Estimated Cost'],
            ['Transportation', f"${budget_info['breakdown']['transportation']}"],
            ['Food & Dining', f"${budget_info['breakdown']['food']}"],
            ['Activities', f"${budget_info['breakdown']['activities']}"],
            ['Accommodation', f"${budget_info['breakdown']['accommodation']}"],
            ['Miscellaneous', f"${budget_info['miscellaneous']}"],
            ['Total Estimated Cost', f"${budget_info['total']}"]
        ]
        
        budget_table = Table(budget_data, colWidths=[3*inch, 2*inch])
        budget_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#ECF0F1')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E74C3C')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7'))
        ]))
        
        story.append(budget_table)
        story.append(Spacer(1, 20))
        
        # Route Summary
        if route_info:
            story.append(Paragraph("🗺️ Route Overview", heading_style))
            total_distance = route_info.get('distance', 'Unknown')
            total_duration = route_info.get('duration', 'Unknown')
            
            route_data = [
                ['Total Distance', total_distance],
                ['Estimated Duration', total_duration],
                ['Number of Stops', str(len(enhanced_places))]
            ]
            
            route_table = Table(route_data, colWidths=[2.5*inch, 2.5*inch])
            route_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8F9FA')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DEE2E6'))
            ]))
            
            story.append(route_table)
            story.append(Spacer(1, 20))
        
        # Detailed Itinerary
        story.append(Paragraph("📍 Your Detailed Itinerary", heading_style))
        story.append(Spacer(1, 10))
        
        start_time = 9  # 9 AM start
        for i, place in enumerate(enhanced_places, 1):
            time_slot = f"{start_time + (i-1)}:00 {('AM' if start_time + (i-1) < 12 else 'PM')}"
            
            # Place header with time and name
            place_name = place.get('name', f'Stop {i}')
            story.append(Paragraph(f"⏰ {time_slot} - {place_name}", place_name_style))
            
            # Address
            address = place.get('formatted_address', 'Address not available')
            story.append(Paragraph(f"📍 <b>Address:</b> {address}", detail_style))
            
            # Rating
            if place.get('rating'):
                rating = place['rating']
                stars = "⭐" * int(float(rating))
                story.append(Paragraph(f"⭐ <b>Rating:</b> {stars} ({rating}/5.0)", detail_style))
            
            # Price Level
            if place.get('price_level'):
                price_symbols = "$" * place['price_level']
                price_text = ['Budget-Friendly', 'Moderate', 'Expensive', 'Very Expensive', 'Luxury'][min(place['price_level']-1, 4)]
                story.append(Paragraph(f"💰 <b>Price Level:</b> {price_symbols} ({price_text})", detail_style))
            
            # Types (categories)
            if place.get('types'):
                categories = [t.replace('_', ' ').title() for t in place['types'][:3]]
                story.append(Paragraph(f"🏷️ <b>Categories:</b> {', '.join(categories)}", detail_style))
            
            story.append(Spacer(1, 15))
        
        # Travel Tips Section
        story.append(Paragraph("💡 Travel Tips & Recommendations", heading_style))
        
        tips = [
            "📞 Call ahead to confirm opening hours and availability",
            "🌤️ Check weather conditions and dress appropriately",
            "🍽️ Try local specialties at each dining location",
            "📸 Capture memories and share your WanderWhiz experience",
            "💳 Carry both cash and cards for different payment preferences",
            "🚗 Consider traffic conditions for your travel times",
            "📱 Save important contact numbers and addresses offline"
        ]
        
        for tip in tips:
            story.append(Paragraph(tip, detail_style))
            story.append(Spacer(1, 5))
        
        story.append(Spacer(1, 20))
        
        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#95A5A6'),
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'
        )
        
        story.append(Paragraph("Generated by WanderWhiz - Your AI Travel Companion", footer_style))
        story.append(Paragraph("Plan smart, travel better! 🌟", footer_style))
        
        # Build PDF
        doc.build(story)
        
        return send_file(filepath, as_attachment=True, download_name=filename)
        
    except Exception as e:
        print(f"💥 PDF Export Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/generate-maps-link", methods=["POST"])
def generate_maps_link():
    """Generate shareable Google Maps link"""
    try:
        data = request.get_json()
        places = data.get('places', [])
        
        if not places:
            return jsonify({"error": "No places provided"}), 400
        
        # Extract coordinates
        waypoints = []
        for place in places:
            if place.get('geometry', {}).get('location'):
                lat = place['geometry']['location']['lat']
                lng = place['geometry']['location']['lng']
                # Validate coordinates
                if lat and lng and isinstance(lat, (int, float)) and isinstance(lng, (int, float)):
                    waypoints.append(f"{lat},{lng}")
        
        if len(waypoints) < 1:
            return jsonify({"error": "No valid coordinates found"}), 400
        
        if len(waypoints) == 1:
            # Single location - just show the place
            maps_url = f"https://www.google.com/maps/search/?api=1&query={waypoints[0]}"
        else:
            # Multiple locations - create directions
            origin = waypoints[0]
            destination = waypoints[-1]
            
            maps_url = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}"
            
            # Add waypoints if more than 2 places
            if len(waypoints) > 2:
                intermediate_waypoints = "|".join(waypoints[1:-1])
                maps_url += f"&waypoints={intermediate_waypoints}"
            
            maps_url += "&travelmode=driving"
        
        return jsonify({"maps_url": maps_url})
        
    except Exception as e:
        print(f"💥 Maps Link Error: {e}")
        return jsonify({"error": str(e)}), 500


# =============================================================================
# TRIP PERSISTENCE AND STORAGE ROUTES
# =============================================================================

@app.route("/save-itinerary", methods=["POST"])
def save_itinerary():
    """
    Save travel itinerary to Firebase with comprehensive data validation.
    
    Handles:
    - Trip metadata (name, dates, user info)
    - Places data with geocoding
    - Budget estimates with validation
    - Route information and polylines
    - Data cleaning and corruption prevention
    
    Returns:
        JSON response with success status and trip ID
    """
    try:
        data = request.get_json()
        itinerary = {
            "id": str(uuid.uuid4()),
            "name": data.get('name', f"Trip {datetime.now().strftime('%m/%d/%Y')}"),
            "places": data.get('places', []),
            "route_info": data.get('route_info', {}),
            "created_at": datetime.now().isoformat(),
            "city": data.get('city', 'Unknown'),
            "total_places": len(data.get('places', [])),
            "total_distance": data.get('total_distance', 0),
            "total_duration": data.get('total_duration', 0),
            "budget_estimate": data.get('budget_estimate', {}),
            "polyline": data.get('polyline', ''),
            "gpt_prompt": data.get('gpt_prompt', ''),
            "interests": data.get('interests', [])
        }
        
        # Try Firebase first
        if firebase_enabled:
            try:
                firebase_manager = get_firebase_manager()
                user_id = session.get('user_id', 'anonymous')
                firebase_id = firebase_manager.save_itinerary(user_id, itinerary)
                print(f"🔥 Saved to Firebase with ID: {firebase_id}")
                return jsonify({
                    "success": True, 
                    "message": "Itinerary saved to Firebase successfully!",
                    "itinerary_id": firebase_id,
                    "storage": "firebase"
                })
            except Exception as e:
                print(f"🔥 Firebase save failed, falling back to session: {e}")
        
        # Fallback to session storage
        if 'saved_trips' not in session:
            session['saved_trips'] = []
        
        # Add to saved trips
        session['saved_trips'].append(itinerary)
        
        # Keep only last 10 trips to prevent session bloat
        if len(session['saved_trips']) > 10:
            session['saved_trips'] = session['saved_trips'][-10:]
        
        session.modified = True
        
        return jsonify({
            "success": True, 
            "message": "Itinerary saved to session successfully!",
            "itinerary_id": itinerary["id"],
            "storage": "session"
        })
        
    except Exception as e:
        print(f"💥 Save Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/get-saved-itineraries", methods=["GET"])
def get_saved_itineraries():
    """Get all saved itineraries from Firebase or session"""
    try:
        # Try Firebase first
        if firebase_enabled:
            try:
                firebase_manager = get_firebase_manager()
                user_id = session.get('user_id', 'anonymous')
                firebase_trips = firebase_manager.get_user_itineraries(user_id, limit=20)
                print(f"🔥 Retrieved {len(firebase_trips)} trips from Firebase")
                return jsonify({
                    "trips": firebase_trips,
                    "storage": "firebase",
                    "count": len(firebase_trips)
                })
            except Exception as e:
                print(f"🔥 Firebase get failed, falling back to session: {e}")
        
        # Fallback to session storage
        saved_trips = session.get('saved_trips', [])
        print(f"📁 Retrieved {len(saved_trips)} trips from session")
        return jsonify({
            "trips": saved_trips,
            "storage": "session",
            "count": len(saved_trips)
        })
    except Exception as e:
        print(f"💥 Get Saved Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/load-itinerary/<itinerary_id>", methods=["GET"])
def load_itinerary(itinerary_id):
    """Load a specific saved itinerary"""
    try:
        saved_trips = session.get('saved_trips', [])
        
        # Find the itinerary
        for trip in saved_trips:
            if trip['id'] == itinerary_id:
                return jsonify({"success": True, "itinerary": trip})
        
        return jsonify({"error": "Itinerary not found"}), 404
        
    except Exception as e:
        print(f"💥 Load Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/trip/<itinerary_id>", methods=["GET"])
def view_saved_trip(itinerary_id):
    """Display a saved trip on the itinerary page"""
    try:
        trip = None
        
        # Try Firebase first if enabled
        if firebase_enabled:
            try:
                firebase_manager = get_firebase_manager()
                trip = firebase_manager.get_itinerary_by_id(itinerary_id)
                if trip:
                    print(f"🔥 Loaded trip from Firebase: {trip.get('name', 'Unnamed')}")
            except Exception as e:
                print(f"🔥 Firebase load failed: {e}")
        
        # Fallback to session storage if Firebase failed or trip not found
        if not trip:
            saved_trips = session.get('saved_trips', [])
            for session_trip in saved_trips:
                if session_trip['id'] == itinerary_id:
                    trip = session_trip
                    print(f"📁 Loaded trip from session: {trip.get('name', 'Unnamed')}")
                    break
        
        if not trip:
            return render_template('itinerary.html', 
                                 error="Trip not found")
        
        # Get route directions for the saved places
        places = trip['places']
        directions = None
        
        if len(places) >= 2:
            # Get fresh directions for the saved places
            directions = get_route_directions(places)
        
        # Preserve saved budget data - only recalculate if truly corrupted
        budget_estimate = trip.get('budget_estimate', {})
        
        # Check if budget data is valid and complete
        has_valid_total = (budget_estimate.get('total') is not None and 
                          isinstance(budget_estimate.get('total'), (int, float)) and 
                          budget_estimate.get('total') > 0)
        
        has_valid_breakdown = (budget_estimate.get('breakdown') is not None and
                              isinstance(budget_estimate.get('breakdown'), dict) and
                              len(budget_estimate.get('breakdown', {})) > 0)
        
        # Only recalculate if budget is completely missing or corrupted
        if not has_valid_total or not has_valid_breakdown:
            print("🔄 Budget data missing or corrupted - recalculating...")
            budget_estimate = estimate_budget(places)
        else:
            print("✅ Using saved budget data (preserving original prices)")
            # Clean the existing budget data without recalculating
            budget_estimate = clean_budget_data(budget_estimate)
        
        # Calculate distance and duration from directions
        total_distance = trip.get('total_distance', 0)
        total_duration = trip.get('total_duration', 0)
        
        if directions and 'routes' in directions and directions['routes']:
            route = directions['routes'][0]
            if 'distanceMeters' in route:
                total_distance = route['distanceMeters']
            if 'duration' in route:
                duration_value = route['duration']
                if isinstance(duration_value, str):
                    total_duration = int(duration_value.rstrip('s'))
                elif isinstance(duration_value, (int, float)):
                    total_duration = int(duration_value)
                else:
                    total_duration = 0
        
        # Extract city name from saved trip or places
        city = trip.get('city', '')
        
        # If city is empty or looks like an address, extract city from place data
        if not city or ',' in city or any(char.isdigit() for char in city):
            print("🏙️ Extracting city from place data...")
            if places:
                # Try to extract city from the first place's vicinity or formatted_address
                first_place = places[0]
                vicinity = first_place.get('vicinity', '')
                formatted_address = first_place.get('formatted_address', '')
                
                # Extract city from vicinity (usually "Area, City" format)
                if vicinity and ',' in vicinity:
                    city = vicinity.split(',')[-1].strip()
                # Extract from formatted address (get the major city component)
                elif formatted_address:
                    # Try to find a major city name in the address
                    parts = formatted_address.split(',')
                    for part in reversed(parts):
                        part = part.strip()
                        # Skip country codes, postal codes, and numbers
                        if (len(part) > 2 and 
                            not part.isdigit() and 
                            not part.upper() in ['CA', 'US', 'UK', 'FR', 'DE', 'JP', 'AU', 'IN'] and
                            not any(char.isdigit() for char in part)):
                            city = part
                            break
                else:
                    city = 'Unknown'
            
            print(f"🏙️ Extracted city: {city}")
        
        print(f"🏙️ Final city for template: {city}")
        
        # Clean all data before passing to template
        template_data = {
            'places': places,
            'directions': directions,
            'polyline': directions.get('routes', [{}])[0].get('polyline', {}).get('encodedPolyline', '') if directions else '',
            'total_distance': total_distance,
            'total_duration': total_duration,
            'budget_estimate': budget_estimate,
            'city': city,  # Use the cleaned city name
            'route_summary': f"Saved trip with {len(places)} places",
            'api_key': GOOGLE_MAPS_API_KEY,
            'saved_trip_name': trip['name']
        }
        
        print(f"🔍 DEBUG: Budget estimate being passed to template: {budget_estimate}")
        print(f"🔍 DEBUG: Template data keys: {list(template_data.keys())}")
        
        # Clean data but preserve budget_estimate 
        preserved_budget = template_data.get('budget_estimate')
        template_data = deep_clean_data(template_data)
        
        # Restore budget estimate if it was cleaned out
        if template_data.get('budget_estimate') is None and preserved_budget:
            print(f"🔧 Restoring cleaned budget estimate: {preserved_budget}")
            template_data['budget_estimate'] = preserved_budget
        
        return render_template('itinerary.html', **template_data)
        
    except Exception as e:
        print(f"💥 View Saved Trip Error: {e}")
        return render_template('index.html', 
                             api_key=GOOGLE_MAPS_API_KEY,
                             error=f"Error loading saved trip: {str(e)}")


@app.route("/delete-itinerary/<itinerary_id>", methods=["DELETE"])
def delete_itinerary(itinerary_id):
    """Delete a saved trip"""
    try:
        # Try Firebase first if enabled
        if firebase_enabled:
            try:
                firebase_manager = get_firebase_manager()
                success = firebase_manager.delete_itinerary(itinerary_id)
                if success:
                    return jsonify({
                        "success": True,
                        "message": "Trip deleted from Firebase successfully!",
                        "storage": "firebase"
                    })
            except Exception as e:
                print(f"🔥 Firebase delete failed: {e}")
        
        # Fallback to session storage
        saved_trips = session.get('saved_trips', [])
        original_count = len(saved_trips)
        
        # Filter out the trip to delete
        saved_trips = [trip for trip in saved_trips if trip.get('id') != itinerary_id]
        session['saved_trips'] = saved_trips
        session.modified = True
        
        if len(saved_trips) < original_count:
            return jsonify({
                "success": True,
                "message": "Trip deleted from session successfully!",
                "storage": "session"
            })
        else:
            return jsonify({
                "success": False,
                "message": "Trip not found"
            }), 404
            
    except Exception as e:
        print(f"💥 Delete Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/ask", methods=["POST"])
def ask_gpt():
    """Handle Trippi assistant questions with full trip context integration"""
    try:
        data = request.get_json()
        question = data.get("question", "").strip()
        trip_context = data.get("trip_context", None)  # Optional trip context
        
        if not question:
            return jsonify({"error": "No question provided"}), 400
        
        # Create Trippi's enhanced system prompt with full trip integration
        system_prompt = """You are Trippi, WanderWhiz's intelligent travel companion! 🌍✈️ 
        
        I'm your personal travel assistant who knows everything about your current trip plans. I can help you with:
        - Budget optimization and cost-saving tips
        - Place recommendations and local insights  
        - Route optimization and travel logistics
        - Cultural tips and hidden gems
        - Food recommendations and dining advice
        - Transportation and accommodation suggestions
        
        I have access to your current trip details including places, costs, and estimates. I speak in a friendly, 
        enthusiastic tone and provide practical, actionable advice. I use emojis naturally and keep responses 
        helpful and concise (3-5 sentences unless more detail is specifically requested).
        
        If asked about non-travel topics, I'll politely redirect back to travel planning while staying in character as Trippi."""
        
        # Add comprehensive trip context if available
        if trip_context:
            trip_details = []
            
            # Add destination city
            if trip_context.get('city'):
                trip_details.append(f"🏙️ Destination: {trip_context['city']}")
            
            # Add budget estimate with breakdown
            if trip_context.get('budget_estimate'):
                budget = trip_context['budget_estimate']
                total_budget = budget.get('total', 0)
                breakdown = budget.get('breakdown', {})
                
                budget_info = f"💰 Estimated Budget: ${total_budget}"
                if breakdown:
                    budget_breakdown = []
                    if breakdown.get('food', 0) > 0:
                        budget_breakdown.append(f"Food: ${breakdown['food']}")
                    if breakdown.get('activities', 0) > 0:
                        budget_breakdown.append(f"Activities: ${breakdown['activities']}")
                    if breakdown.get('transportation', 0) > 0:
                        budget_breakdown.append(f"Transport: ${breakdown['transportation']}")
                    if breakdown.get('accommodation', 0) > 0:
                        budget_breakdown.append(f"Stay: ${breakdown['accommodation']}")
                    
                    if budget_breakdown:
                        budget_info += f" (Breakdown: {', '.join(budget_breakdown)})"
                
                trip_details.append(budget_info)
            
            # Add places with detailed information
            if trip_context.get('places'):
                places_info = ["📍 Planned Places:"]
                total_places = len(trip_context['places'])
                
                for i, place in enumerate(trip_context['places'][:8]):  # Show up to 8 places
                    place_name = place.get('name', 'Unknown Place')
                    rating = place.get('rating', 'N/A')
                    vicinity = place.get('vicinity', '')
                    price_level = place.get('price_level', None)
                    
                    place_str = f"   {i+1}. {place_name}"
                    
                    # Add rating if available
                    if rating != 'N/A':
                        place_str += f" ({rating}⭐)"
                    
                    # Add price level indicator
                    if price_level is not None:
                        price_symbols = ['💰', '💰💰', '💰💰💰', '💰💰💰💰', '💰💰💰💰💰']
                        if 0 <= price_level <= 4:
                            place_str += f" {price_symbols[price_level]}"
                    
                    # Add location
                    if vicinity:
                        place_str += f" - {vicinity}"
                    
                    places_info.append(place_str)
                
                if total_places > 8:
                    places_info.append(f"   ... and {total_places - 8} more places")
                
                trip_details.append("\n".join(places_info))
            
            # Add route information if available
            if trip_context.get('total_distance') or trip_context.get('total_duration'):
                route_info = "🗺️ Route Details:"
                if trip_context.get('total_distance'):
                    distance_km = round(trip_context['total_distance'] / 1000, 1)
                    route_info += f" {distance_km}km total distance"
                if trip_context.get('total_duration'):
                    duration_hours = round(trip_context['total_duration'] / 3600, 1)
                    route_info += f", ~{duration_hours}h travel time"
                trip_details.append(route_info)
            
            # Add original search prompt if available
            if trip_context.get('gpt_prompt'):
                trip_details.append(f"🎯 Original Request: \"{trip_context['gpt_prompt']}\"")
            
            if trip_details:
                system_prompt += f"\n\n--- CURRENT TRIP CONTEXT ---\n" + "\n".join(trip_details) + "\n--- END CONTEXT ---"
        
        # Use the newer client format for Trippi
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            max_tokens=400,  # Increased for more detailed responses
            temperature=0.8  # Slightly more creative for Trippi's personality
        )
        
        answer = response.choices[0].message.content.strip()
        
        # Add Trippi signature to responses
        if not answer.startswith("Hi!") and not answer.startswith("Hello"):
            # Add Trippi greeting occasionally for personality
            greetings = [
                "Hey there! 👋 ",
                "Great question! 🤔 ",
                "I'd love to help! ✨ ",
                "Let me share some insights! 💡 ",
                ""  # Sometimes no greeting for variety
            ]
            import random
            greeting = random.choice(greetings)
            if greeting:
                answer = greeting + answer
        
        return jsonify({
            "answer": answer,
            "assistant_name": "Trippi",
            "has_trip_context": bool(trip_context)
        })
        
    except Exception as e:
        print(f"Trippi Error: {e}")
        return jsonify({
            "error": "Oops! Trippi is having a moment 🤖💭 Please try asking again!",
            "assistant_name": "Trippi"
        }), 500


# ========================================
# FIREBASE & ENHANCED FEATURES ROUTES
# ========================================

@app.route('/firebase-save-itinerary', methods=['POST'])
def firebase_save_itinerary():
    """Enhanced save with Firebase"""
    if not firebase_enabled:
        return jsonify({"error": "Firebase not configured"}), 503
        
    try:
        data = request.get_json()
        firebase_manager = get_firebase_manager()
        
        # Get user ID from session (for now use anonymous)
        user_id = session.get('user_id', 'anonymous')
        
        itinerary_data = {
            'city': data.get('city', ''),
            'places': data.get('places', []),
            'total_distance': data.get('total_distance', 0),
            'total_duration': data.get('total_duration', 0),
            'budget_estimate': data.get('budget_estimate', {}),
            'polyline': data.get('polyline', ''),
            'gpt_prompt': data.get('gpt_prompt', ''),
            'interests': data.get('interests', []),
            'tags': data.get('tags', [])
        }
        
        # Clean data before saving to Firebase
        itinerary_data = deep_clean_data(itinerary_data)
        
        # Save to Firebase
        doc_id = firebase_manager.save_itinerary(user_id, itinerary_data)
        
        if doc_id:
            return jsonify({
                "success": True, 
                "message": "Trip saved to cloud! ☁️",
                "id": doc_id
            })
        else:
            return jsonify({"error": "Failed to save trip"}), 500
            
    except Exception as e:
        print(f"Firebase save error: {e}")
        return jsonify({"error": "Could not save trip"}), 500

@app.route('/firebase-get-itineraries')
def firebase_get_itineraries():
    """Get user's saved itineraries from Firebase"""
    if not firebase_enabled:
        # Return demo data if Firebase not available
        from demo_data import get_demo_data
        demo = get_demo_data()
        return jsonify({"itineraries": demo["trips"]})
        
    try:
        firebase_manager = get_firebase_manager()
        user_id = session.get('user_id', 'anonymous')
        
        itineraries = firebase_manager.get_user_itineraries(user_id, limit=20)
        return jsonify({"itineraries": itineraries})
        
    except Exception as e:
        print(f"Firebase fetch error: {e}")
        return jsonify({"itineraries": []})

@app.route('/platform-stats')
def platform_stats():
    """Get platform statistics for demo"""
    if firebase_enabled:
        try:
            firebase_manager = get_firebase_manager()
            stats = firebase_manager.get_stats()
            popular = firebase_manager.get_popular_destinations(8)
        except:
            # Fallback to demo data
            from demo_data import get_demo_data
            demo = get_demo_data()
            stats = demo["stats"]
            popular = demo["popular_destinations"]
    else:
        # Use demo data
        from demo_data import get_demo_data
        demo = get_demo_data()
        stats = demo["stats"]
        popular = demo["popular_destinations"]
    
    return jsonify({
        "stats": stats,
        "popular_destinations": popular
    })

@app.route('/travel-fact')
def travel_fact():
    """Get random travel fact for loading screens"""
    from demo_data import get_random_travel_fact
    return jsonify({"fact": get_random_travel_fact()})

@app.route('/testimonials')
def testimonials():
    """Get user testimonials for social proof"""
    from demo_data import get_demo_data
    demo = get_demo_data()
    return jsonify({"testimonials": demo["testimonials"]})

@app.route('/demo-trip/<trip_id>')
def demo_trip(trip_id):
    """Load a pre-made demo trip"""
    from demo_data import get_demo_data
    demo = get_demo_data()
    
    # Find the demo trip
    trip = None
    for t in demo["trips"]:
        if t["id"] == trip_id:
            trip = t
            break
    
    if not trip:
        return "Demo trip not found", 404
    
    # Generate route directions for demo trip
    directions = None
    if len(trip["places"]) >= 2:
        try:
            directions = get_route_directions(trip["places"])
        except Exception as e:
            print(f"Could not generate directions for demo trip: {e}")
            directions = None

    # Always calculate fresh budget for consistency
    calculated_budget = estimate_budget(trip["places"])

    # Clean demo data before passing to template
    template_data = {
        'places': trip["places"],
        'directions': directions,
        'polyline': directions.get('routes', [{}])[0].get('polyline', {}).get('encodedPolyline', '') if directions else '',
        'total_distance': trip["total_distance"],
        'total_duration': trip["total_duration"],
        'budget_estimate': calculated_budget,  # Use calculated budget for consistency
        'city': trip["city"],
        'route_summary': f"Demo route through {len(trip['places'])} amazing places",
        'saved_trip_name': trip["title"],  # Add the trip title for template
        'api_key': GOOGLE_MAPS_API_KEY
    }
    template_data = deep_clean_data(template_data)
    
    # Render the trip as if it were a real itinerary
    return render_template("itinerary.html", **template_data)

# ========================================
# ENHANCED SAVE ROUTE (with Firebase fallback)
# ========================================

@app.route("/enhanced-save-itinerary", methods=["POST"])
def enhanced_save_itinerary():
    """Enhanced save with both local and Firebase storage"""
    try:
        data = request.get_json()
        trip_id = str(uuid.uuid4())
        
        # Prepare trip data
        trip_data = {
            "id": trip_id,
            "city": data.get("city", ""),
            "places": data.get("places", []),
            "total_distance": data.get("total_distance", 0),
            "total_duration": data.get("total_duration", 0),
            "budget_estimate": data.get("budget_estimate", {}),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "polyline": data.get("polyline", ""),
            "gpt_prompt": data.get("gpt_prompt", ""),
            "interests": data.get("interests", [])
        }
        
        # Clean data before saving
        trip_data = deep_clean_data(trip_data)
        
        # Try Firebase first
        firebase_success = False
        if firebase_enabled:
            try:
                firebase_manager = get_firebase_manager()
                user_id = session.get('user_id', 'anonymous')
                doc_id = firebase_manager.save_itinerary(user_id, trip_data)
                if doc_id:
                    firebase_success = True
                    trip_data["firebase_id"] = doc_id
            except Exception as e:
                print(f"Firebase save failed: {e}")
        
        # Also save locally as backup
        if 'saved_trips' not in session:
            session['saved_trips'] = []
        
        session['saved_trips'].append(trip_data)
        session.modified = True
        
        response_msg = "Trip saved"
        if firebase_success:
            response_msg += " to cloud ☁️"
        else:
            response_msg += " locally 💾"
        
        return jsonify({
            "success": True,
            "message": response_msg,
            "id": trip_id,
            "firebase_saved": firebase_success
        })
        
    except Exception as e:
        print(f"Enhanced save error: {e}")
        return jsonify({"error": "Could not save trip"}), 500


if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, port=port)

# 🧹 Debug route to clear session data
@app.route("/clear-session")
def clear_session():
    """Clear session data for debugging"""
    session.clear()
    return "Session cleared! <a href='/'>Go back to home</a>"
