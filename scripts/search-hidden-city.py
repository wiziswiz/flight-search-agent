#!/usr/bin/env python3
"""
Hidden City Flight Search Engine
Finds hidden city ticketing opportunities by looking for flights to destinations beyond the target with layovers.

Usage: search-hidden-city.py LAX DEN 2026-03-15 [--max-searches 10] [--min-savings 50] [--pretty]

Modes:
1. SerpAPI (if SERP_API_KEY env var set) - real-time Google Flights data
2. URL scraping (fallback) - parse Google Flights URLs
3. Estimated (demo mode) - realistic price modeling
"""

import json
import sys
import os
import argparse
import requests
import urllib.parse
from datetime import datetime, timedelta
from math import radians, cos, sin, asin, sqrt
import re
import time

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'data')

# Load hub connections data
HUB_CONNECTIONS_FILE = os.path.join(DATA_DIR, 'hub-connections.json')

def load_hub_connections():
    """Load hub connections database"""
    try:
        with open(HUB_CONNECTIONS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Hub connections file not found at {HUB_CONNECTIONS_FILE}", file=sys.stderr)
        return {}

def get_distance(lat1, lon1, lat2, lon2):
    """Calculate the great circle distance between two points on earth in miles"""
    # Haversine formula
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 3956  # Radius of earth in miles
    return c * r

# Simplified airport coordinates for distance calculations (major airports only)
AIRPORT_COORDINATES = {
    'LAX': (33.9425, -118.4081), 'DEN': (39.8561, -104.6737), 'SLC': (40.7884, -111.9678),
    'ORD': (41.9786, -87.9048), 'ATL': (33.6407, -84.4277), 'JFK': (40.6413, -73.7781),
    'DFW': (32.8968, -97.0380), 'MIA': (25.7959, -80.2870), 'PHX': (33.4342, -112.0116),
    'SEA': (47.4502, -122.3088), 'SFO': (37.6213, -122.3790), 'IAH': (29.9902, -95.3368),
    'BWI': (39.1754, -76.6683), 'LAS': (36.0840, -115.1537), 'MSP': (44.8848, -93.2223),
    'CLT': (35.2144, -80.9473), 'BOS': (42.3656, -71.0096), 'PHL': (39.8729, -75.2437),
    'MCO': (28.4312, -81.3081), 'LGA': (40.7769, -73.8740), 'SAN': (32.7338, -117.1933),
    'PDX': (45.5898, -122.5951), 'OAK': (37.7149, -122.2197), 'SMF': (38.6954, -121.5908),
    'ABQ': (35.0402, -106.6092), 'BOI': (43.5644, -116.2228), 'RNO': (39.4991, -119.7639),
    'HOU': (29.6454, -95.2789), 'AUS': (30.1945, -97.6699), 'SAT': (29.5337, -98.4698)
}

def estimate_flight_price(origin, destination, date_str):
    """Estimate flight price based on distance and route characteristics"""
    if origin not in AIRPORT_COORDINATES or destination not in AIRPORT_COORDINATES:
        return 300  # Default price for unknown routes
    
    distance = get_distance(
        *AIRPORT_COORDINATES[origin],
        *AIRPORT_COORDINATES[destination]
    )
    
    # Base price model: $0.15 per mile + $150 base
    base_price = distance * 0.15 + 150
    
    # Date factors
    try:
        flight_date = datetime.strptime(date_str, '%Y-%m-%d')
        days_ahead = (flight_date - datetime.now()).days
        
        # Advance booking factor
        if days_ahead < 7:
            base_price *= 1.8  # Last minute premium
        elif days_ahead < 14:
            base_price *= 1.5
        elif days_ahead < 30:
            base_price *= 1.2
        elif days_ahead > 90:
            base_price *= 0.9  # Early booking discount
            
        # Day of week factor (simplified)
        day_of_week = flight_date.weekday()
        if day_of_week in [4, 6]:  # Friday, Sunday
            base_price *= 1.3
        elif day_of_week in [1, 2]:  # Tuesday, Wednesday
            base_price *= 0.9
    except:
        pass
    
    # Route popularity adjustments
    popular_routes = {
        ('LAX', 'JFK'): 1.4, ('LAX', 'DEN'): 1.1, ('LAX', 'SFO'): 0.8,
        ('DEN', 'LAX'): 1.1, ('DEN', 'ORD'): 1.0, ('ORD', 'LAX'): 1.3
    }
    
    route = (origin, destination)
    route_reverse = (destination, origin)
    
    if route in popular_routes:
        base_price *= popular_routes[route]
    elif route_reverse in popular_routes:
        base_price *= popular_routes[route_reverse]
    
    return round(base_price, 2)

def calculate_risk_score(target_airport, airline, beyond_city):
    """Calculate risk score for hidden city ticketing"""
    hub_data = load_hub_connections()
    
    # Base risk factors
    risk_level = "medium"
    risk_factors = [
        "Must book one-way only",
        "No checked bags (will go to final destination)",
        "Cannot use frequent flyer number (may flag account)"
    ]
    
    # Airport size factor
    if target_airport in ['DEN', 'ORD', 'ATL', 'LAX', 'JFK', 'DFW', 'SEA']:
        risk_level = "low"
    elif target_airport in hub_data and len(hub_data[target_airport]['beyond_cities']) > 8:
        risk_level = "medium"
    else:
        risk_level = "high"
        risk_factors.append("Small airport with limited connections")
    
    # Airline enforcement factor
    strict_airlines = ['United', 'Delta', 'American']
    if airline in strict_airlines:
        if risk_level == "low":
            risk_level = "medium"
        else:
            risk_level = "high"
        risk_factors.append(f"{airline} may enforce fare rules strictly")
    
    # Route factor
    if beyond_city and beyond_city in AIRPORT_COORDINATES:
        target_coords = AIRPORT_COORDINATES.get(target_airport)
        beyond_coords = AIRPORT_COORDINATES.get(beyond_city)
        
        if target_coords and beyond_coords:
            # If beyond city is very close to target, higher risk of detection
            distance = get_distance(*target_coords, *beyond_coords)
            if distance < 200:
                risk_factors.append("Final destination very close to layover - may raise suspicion")
                if risk_level == "low":
                    risk_level = "medium"
    
    # Additional risks
    risk_factors.extend([
        "If flight cancelled, rebooking goes to final destination",
        "Airline may ban for repeated violations"
    ])
    
    return risk_level, risk_factors

def search_serpapi(origin, beyond_city, date_str):
    """Search using SerpAPI Google Flights engine"""
    api_key = os.getenv('SERP_API_KEY')
    if not api_key:
        return None
    
    try:
        url = "https://serpapi.com/search.json"
        params = {
            'engine': 'google_flights',
            'departure_id': origin,
            'arrival_id': beyond_city,
            'outbound_date': date_str,
            'currency': 'USD',
            'type': 2,  # One-way
            'api_key': api_key
        }
        
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            return data.get('best_flights', []) + data.get('other_flights', [])
        else:
            print(f"SerpAPI error: HTTP {response.status_code}", file=sys.stderr)
            return None
    except Exception as e:
        print(f"SerpAPI error: {e}", file=sys.stderr)
        return None

def search_google_flights_scrape(origin, beyond_city, date_str):
    """Scrape Google Flights URLs (simplified implementation)"""
    try:
        # Construct Google Flights URL
        base_url = "https://www.google.com/travel/flights"
        
        # Format date for Google Flights
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        formatted_date = date_obj.strftime('%Y-%m-%d')
        
        # Build search URL
        search_url = f"{base_url}/search?tfs=CBwQAhopag0IAxIJL20vMDFfZDBfEgoyMDI2LTAzLTE1cgwIAxIIL20vMDJfMjg2HAsSCQgDEgUvbS8waDJAAUgBcAGCAQsI____________AUABSAE&hl=en"
        
        # For now, return None as scraping requires more complex parsing
        # In a real implementation, you would use requests + BeautifulSoup
        # to parse the flight results from the HTML
        print(f"Would scrape: {search_url}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Scraping error: {e}", file=sys.stderr)
        return None

def search_estimated_mode(origin, target, beyond_city, date_str):
    """Generate realistic estimated flight data"""
    # Generate estimated layover flight
    departure_time = "08:30"  # Morning departure
    
    # Estimate flight times based on distance
    origin_coords = AIRPORT_COORDINATES.get(origin)
    target_coords = AIRPORT_COORDINATES.get(target)
    beyond_coords = AIRPORT_COORDINATES.get(beyond_city)
    
    layover_arrival = "12:15"  # Default layover arrival
    if origin_coords and target_coords:
        distance_to_target = get_distance(*origin_coords, *target_coords)
        flight_hours = int(distance_to_target / 500) + 1  # Rough flight time
        layover_hour = 8 + flight_hours
        if layover_hour > 23:
            layover_hour = 23
        layover_arrival = f"{layover_hour:02d}:15"
    
    # Pick a realistic airline based on hub
    hub_data = load_hub_connections()
    airline = "United"
    if target in hub_data:
        airlines = hub_data[target].get('hub_airlines', ['United'])
        airline = airlines[0]
    
    # Generate flight number
    airline_codes = {'United': 'UA', 'American': 'AA', 'Delta': 'DL', 'Southwest': 'WN'}
    code = airline_codes.get(airline, 'UA')
    flight_number = f"{code}{1200 + hash(f'{origin}{beyond_city}{date_str}') % 8000}"
    
    return [{
        'airline': airline,
        'flight_number': flight_number,
        'departure_time': departure_time,
        'arrival_time': "14:45",
        'price': estimate_flight_price(origin, beyond_city, date_str),
        'stops': 1,
        'layover_airports': [target],
        'layover_duration': "1h 30m",
        'total_duration': "6h 15m"
    }]

def find_hidden_city_opportunities(origin, target, date_str, max_searches=10, min_savings=50):
    """Find hidden city opportunities using the core algorithm"""
    hub_data = load_hub_connections()
    results = []
    
    # Step 1: Get direct flight price estimate for comparison
    direct_price = estimate_flight_price(origin, target, date_str)
    
    # Step 2: Find cities that commonly route through target
    beyond_cities = []
    if target in hub_data:
        beyond_cities = hub_data[target]['beyond_cities'][:max_searches]
    else:
        # If target not in hub data, use some common destinations
        beyond_cities = ['LAX', 'DEN', 'ORD', 'ATL', 'DFW'][:max_searches]
    
    print(f"Searching for hidden city routes through {target} to: {', '.join(beyond_cities)}", file=sys.stderr)
    
    # Step 3: Search for flights to each beyond city
    for beyond_city in beyond_cities:
        if beyond_city == origin or beyond_city == target:
            continue
            
        print(f"Searching {origin} → {beyond_city} (via {target})...", file=sys.stderr)
        
        # Try different search methods
        flights = None
        data_source = "estimated"
        
        # Method 1: SerpAPI (if available)
        if os.getenv('SERP_API_KEY'):
            flights = search_serpapi(origin, beyond_city, date_str)
            if flights:
                data_source = "serpapi"
        
        # Method 2: Google Flights scraping (fallback)
        if not flights:
            flights = search_google_flights_scrape(origin, beyond_city, date_str)
            if flights:
                data_source = "scrape"
        
        # Method 3: Estimated mode
        if not flights:
            flights = search_estimated_mode(origin, target, beyond_city, date_str)
            data_source = "estimated"
        
        if flights:
            # Step 4: Check each flight for target as layover
            for flight in flights:
                layover_airports = flight.get('layover_airports', [])
                
                # Check if target is a layover
                if target in layover_airports or (flight.get('stops', 0) > 0 and data_source == "estimated"):
                    hidden_city_price = flight.get('price', 0)
                    
                    # Step 5: Calculate savings
                    savings = direct_price - hidden_city_price
                    if savings >= min_savings:
                        savings_percent = round((savings / direct_price) * 100, 1)
                        
                        # Calculate risk score
                        airline = flight.get('airline', 'Unknown')
                        risk_level, risk_factors = calculate_risk_score(target, airline, beyond_city)
                        
                        # Build booking URL
                        booking_url = f"https://www.google.com/travel/flights/search?tfs=CBwQAhopag0IAxIJL20vMDFfZDBfEgoyMDI2LTAzLTE1cgwIAxIIL20vMDJfMjg2&hl=en"
                        
                        result = {
                            "type": "hidden_city",
                            "origin": origin,
                            "real_destination": target,
                            "ticketed_destination": beyond_city,
                            "layover_airport": target,
                            "direct_price": direct_price,
                            "hidden_city_price": hidden_city_price,
                            "savings": savings,
                            "savings_percent": savings_percent,
                            "airline": airline,
                            "flight_number": flight.get('flight_number', 'N/A'),
                            "departure_time": flight.get('departure_time', 'N/A'),
                            "arrival_at_layover": flight.get('layover_arrival', '12:15'),
                            "risk_score": risk_level,
                            "risks": risk_factors,
                            "booking_url": booking_url,
                            "confidence": "high" if data_source == "serpapi" else "medium" if data_source == "scrape" else "estimated",
                            "data_source": data_source
                        }
                        
                        results.append(result)
                        print(f"Found opportunity: {origin}→{beyond_city} via {target}, saves ${savings:.0f}", file=sys.stderr)
        
        # Add small delay between searches to be respectful
        time.sleep(0.5)
    
    # Sort by savings (highest first)
    results.sort(key=lambda x: x['savings'], reverse=True)
    
    return results

def main():
    parser = argparse.ArgumentParser(
        description='Find hidden city flight opportunities',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  search-hidden-city.py LAX DEN 2026-03-15
  search-hidden-city.py JFK LAX 2026-04-10 --max-searches 15 --min-savings 100
  
Environment Variables:
  SERP_API_KEY - Optional SerpAPI key for real-time data
        """
    )
    
    parser.add_argument('origin', help='Origin airport code (e.g., LAX)')
    parser.add_argument('destination', help='Target destination airport code (e.g., DEN)')
    parser.add_argument('date', help='Departure date (YYYY-MM-DD)')
    parser.add_argument('--max-searches', type=int, default=10, 
                       help='Maximum number of beyond cities to search (default: 10)')
    parser.add_argument('--min-savings', type=float, default=50,
                       help='Minimum savings required in USD (default: 50)')
    parser.add_argument('--pretty', action='store_true',
                       help='Pretty print JSON output')
    
    args = parser.parse_args()
    
    try:
        # Validate date format
        datetime.strptime(args.date, '%Y-%m-%d')
        
        # Check if hub connections data exists
        if not os.path.exists(HUB_CONNECTIONS_FILE):
            print(f"Error: Hub connections data not found at {HUB_CONNECTIONS_FILE}", file=sys.stderr)
            sys.exit(1)
        
        # Run search
        print(f"Searching for hidden city opportunities: {args.origin} → {args.destination} on {args.date}", file=sys.stderr)
        
        api_mode = "SerpAPI" if os.getenv('SERP_API_KEY') else "Estimated"
        print(f"Search mode: {api_mode}", file=sys.stderr)
        
        results = find_hidden_city_opportunities(
            args.origin.upper(),
            args.destination.upper(),
            args.date,
            max_searches=args.max_searches,
            min_savings=args.min_savings
        )
        
        # Output results
        if args.pretty:
            print(json.dumps(results, indent=2, sort_keys=True))
        else:
            print(json.dumps(results))
        
        if not results:
            print(f"No hidden city opportunities found with minimum savings of ${args.min_savings}", file=sys.stderr)
        else:
            print(f"Found {len(results)} hidden city opportunities", file=sys.stderr)
            
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()