#!/usr/bin/env python3
"""
Alternative airports search script.
Searches nearby alternative airports to find better prices.
"""

import json
import sys
import argparse
import os
from datetime import datetime

# Load airport alternatives database
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AIRPORT_ALTERNATES_FILE = os.path.join(SCRIPT_DIR, '..', 'data', 'airport-alternates.json')

def load_airport_alternates():
    """Load airport alternatives from data file"""
    try:
        with open(AIRPORT_ALTERNATES_FILE, 'r') as f:
            data = json.load(f)
            return data.get('airports', [])
    except FileNotFoundError:
        print(f"Warning: Airport alternatives file not found at {AIRPORT_ALTERNATES_FILE}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Error loading airport alternatives: {e}", file=sys.stderr)
        return []

def get_alternative_airports(airport_code):
    """Get alternative airports for a given airport code"""
    airports = load_airport_alternates()
    
    for airport in airports:
        if airport['code'] == airport_code:
            return airport['alternates']
    
    # If not found, return empty list
    return []

def search_alternative_airports(origin, destination, depart_date, return_date=None):
    """Search alternative airports for better prices"""
    try:
        all_results = []
        
        # Get alternative airports
        origin_alts = get_alternative_airports(origin)
        destination_alts = get_alternative_airports(destination)
        
        # Search combinations
        airport_combinations = []
        
        # Original route
        airport_combinations.append((origin, destination, "direct"))
        
        # Origin alternatives to main destination
        for alt_origin in origin_alts:
            airport_combinations.append((alt_origin, destination, f"alt_origin_{alt_origin}"))
        
        # Main origin to destination alternatives
        for alt_dest in destination_alts:
            airport_combinations.append((origin, alt_dest, f"alt_destination_{alt_dest}"))
        
        # Alternative origin to alternative destination (best savings potential)
        for alt_origin in origin_alts:
            for alt_dest in destination_alts:
                airport_combinations.append((alt_origin, alt_dest, f"alt_both_{alt_origin}_{alt_dest}"))
        
        # Search each combination
        for search_origin, search_dest, route_type in airport_combinations:
            try:
                flights = search_route(search_origin, search_dest, depart_date, return_date, route_type)
                
                # Add route information
                for flight in flights:
                    flight['search_origin'] = search_origin
                    flight['search_destination'] = search_dest
                    flight['route_type'] = route_type
                    flight['requested_origin'] = origin
                    flight['requested_destination'] = destination
                    
                    # Calculate ground transport if using alternate airports
                    add_ground_transport_info(flight, origin, destination, search_origin, search_dest)
                
                all_results.extend(flights)
                
            except Exception as e:
                print(f"Error searching {search_origin} to {search_dest}: {e}", file=sys.stderr)
                continue
        
        # Sort by total cost (flight + estimated ground transport)
        return sorted(all_results, key=lambda x: x.get('total_cost_with_transport', x['price']))
        
    except Exception as e:
        print(f"Error searching alternative airports: {e}", file=sys.stderr)
        return []

def search_route(origin, destination, depart_date, return_date, route_type):
    """Search a specific route and return mock flight data"""
    import random
    
    # Generate mock flight data based on route type
    flights = []
    
    # Base price varies by route type
    if route_type == "direct":
        base_price = random.randint(300, 600)
        price_variance = 0.8  # 20% variance
    elif "alt_origin" in route_type or "alt_destination" in route_type:
        base_price = random.randint(250, 550)  # Slightly cheaper
        price_variance = 0.9  # 10% variance
    else:  # alt_both
        base_price = random.randint(200, 500)  # Potentially much cheaper
        price_variance = 1.2  # 20% more variance
    
    # Generate 2-4 flights for this route
    num_flights = random.randint(2, 4)
    airlines = ["United", "American", "Delta", "Southwest", "JetBlue", "Alaska"]
    
    for i in range(num_flights):
        airline = random.choice(airlines)
        price_multiplier = random.uniform(price_variance - 0.3, price_variance + 0.3)
        price = int(base_price * price_multiplier)
        
        departure_time = f"{random.randint(6, 22):02d}:{random.choice(['00', '15', '30', '45'])}"
        duration_hours = random.randint(2, 8)
        arrival_hour = (int(departure_time[:2]) + duration_hours) % 24
        arrival_time = f"{arrival_hour:02d}:{random.choice(['00', '15', '30', '45'])}"
        
        flight = {
            "price": price,
            "currency": "USD",
            "airline": airline,
            "flight_number": f"{airline[:2].upper()}{random.randint(100, 9999)}",
            "origin": origin,
            "destination": destination,
            "departure_date": depart_date,
            "departure_time": departure_time,
            "arrival_time": arrival_time,
            "duration": f"{duration_hours}h {random.randint(0, 59)}m",
            "stops": random.choice([0, 1]),
            "strategy": "alternative-airports",
            "booking_url": f"https://www.google.com/flights?hl=en#search;f={origin};t={destination};d={depart_date}",
            "confidence": "high"
        }
        
        if return_date:
            flight["return_date"] = return_date
            flight["trip_type"] = "round_trip"
            flight["price"] = int(price * 1.8)
        else:
            flight["trip_type"] = "one_way"
        
        flights.append(flight)
    
    return flights

def add_ground_transport_info(flight, requested_origin, requested_destination, search_origin, search_destination):
    """Add ground transportation cost and time estimates"""
    
    # Ground transport costs (rough estimates)
    transport_costs = {
        # Los Angeles area
        ('LAX', 'SNA'): {'cost': 45, 'time': 60, 'method': 'taxi/uber'},
        ('LAX', 'BUR'): {'cost': 40, 'time': 45, 'method': 'taxi/uber'},
        ('LAX', 'LGB'): {'cost': 35, 'time': 40, 'method': 'taxi/uber'},
        ('LAX', 'ONT'): {'cost': 65, 'time': 75, 'method': 'taxi/uber'},
        
        # New York area  
        ('JFK', 'LGA'): {'cost': 50, 'time': 60, 'method': 'taxi/uber'},
        ('JFK', 'EWR'): {'cost': 75, 'time': 90, 'method': 'taxi/uber'},
        ('JFK', 'SWF'): {'cost': 120, 'time': 120, 'method': 'taxi/bus'},
        ('JFK', 'ISP'): {'cost': 85, 'time': 90, 'method': 'taxi/uber'},
        
        # San Francisco area
        ('SFO', 'SJC'): {'cost': 60, 'time': 75, 'method': 'taxi/uber'},
        ('SFO', 'OAK'): {'cost': 45, 'time': 60, 'method': 'taxi/uber'},
        ('SFO', 'STS'): {'cost': 95, 'time': 120, 'method': 'taxi/bus'},
        
        # Chicago area
        ('ORD', 'MDW'): {'cost': 55, 'time': 75, 'method': 'taxi/uber'},
        ('ORD', 'MKE'): {'cost': 110, 'time': 150, 'method': 'bus/car'},
        ('ORD', 'RFD'): {'cost': 85, 'time': 120, 'method': 'car rental'},
        
        # Washington DC area
        ('DCA', 'IAD'): {'cost': 65, 'time': 90, 'method': 'taxi/uber'},
        ('DCA', 'BWI'): {'cost': 70, 'time': 95, 'method': 'taxi/uber'},
        ('IAD', 'BWI'): {'cost': 85, 'time': 105, 'method': 'taxi/uber'},
        
        # Default estimates
        'default': {'cost': 75, 'time': 90, 'method': 'taxi/uber'}
    }
    
    origin_transport_cost = 0
    origin_transport_time = 0
    origin_transport_method = None
    
    dest_transport_cost = 0
    dest_transport_time = 0
    dest_transport_method = None
    
    # Calculate origin transport
    if search_origin != requested_origin:
        key = (requested_origin, search_origin)
        reverse_key = (search_origin, requested_origin)
        
        if key in transport_costs:
            transport = transport_costs[key]
        elif reverse_key in transport_costs:
            transport = transport_costs[reverse_key]
        else:
            transport = transport_costs['default']
        
        origin_transport_cost = transport['cost']
        origin_transport_time = transport['time']
        origin_transport_method = transport['method']
    
    # Calculate destination transport
    if search_destination != requested_destination:
        key = (search_destination, requested_destination)
        reverse_key = (requested_destination, search_destination)
        
        if key in transport_costs:
            transport = transport_costs[key]
        elif reverse_key in transport_costs:
            transport = transport_costs[reverse_key]
        else:
            transport = transport_costs['default']
        
        dest_transport_cost = transport['cost']
        dest_transport_time = transport['time']
        dest_transport_method = transport['method']
    
    # Add to flight data
    total_transport_cost = origin_transport_cost + dest_transport_cost
    total_transport_time = origin_transport_time + dest_transport_time
    
    flight['ground_transport'] = {
        'origin': {
            'from': requested_origin,
            'to': search_origin,
            'cost': origin_transport_cost,
            'time_minutes': origin_transport_time,
            'method': origin_transport_method
        } if origin_transport_cost > 0 else None,
        'destination': {
            'from': search_destination,
            'to': requested_destination,
            'cost': dest_transport_cost,
            'time_minutes': dest_transport_time,
            'method': dest_transport_method
        } if dest_transport_cost > 0 else None,
        'total_cost': total_transport_cost,
        'total_time_minutes': total_transport_time
    }
    
    flight['total_cost_with_transport'] = flight['price'] + total_transport_cost
    flight['total_travel_time_minutes'] = (
        int(flight['duration'].split('h')[0]) * 60 + 
        int(flight['duration'].split('h')[1].split('m')[0]) +
        total_transport_time
    )
    
    # Calculate savings
    if total_transport_cost > 0:
        flight['airport_savings_analysis'] = {
            'flight_savings': 0,  # Would need comparison flight to calculate
            'transport_cost': total_transport_cost,
            'net_savings': 0,  # Would be calculated in comparison
            'time_penalty_minutes': total_transport_time,
            'recommendation': get_alternate_airport_recommendation(total_transport_cost, total_transport_time)
        }

def get_alternate_airport_recommendation(transport_cost, transport_time):
    """Generate recommendation for using alternate airports"""
    if transport_cost == 0:
        return "Direct route - no additional costs"
    elif transport_cost < 50 and transport_time < 60:
        return "Good alternative - low cost and time penalty"
    elif transport_cost < 100 and transport_time < 120:
        return "Consider if flight savings > $100"
    else:
        return "High transport cost/time - only worthwhile for major savings"

def generate_savings_matrix(results, requested_origin, requested_destination):
    """Generate a savings matrix comparing all route options"""
    
    # Find baseline (direct route) price
    baseline_flights = [f for f in results if f.get('route_type') == 'direct']
    baseline_price = min(f['price'] for f in baseline_flights) if baseline_flights else 0
    
    matrix = []
    
    # Group by airport combination
    route_groups = {}
    for flight in results:
        route_key = f"{flight['search_origin']}-{flight['search_destination']}"
        if route_key not in route_groups:
            route_groups[route_key] = []
        route_groups[route_key].append(flight)
    
    # Create matrix entries
    for route_key, flights in route_groups.items():
        min_flight = min(flights, key=lambda x: x['price'])
        
        flight_savings = baseline_price - min_flight['price'] if baseline_price > 0 else 0
        transport_cost = min_flight['ground_transport']['total_cost']
        net_savings = flight_savings - transport_cost
        transport_time = min_flight['ground_transport']['total_time_minutes']
        
        matrix.append({
            'route': route_key,
            'origin_airport': min_flight['search_origin'],
            'destination_airport': min_flight['search_destination'],
            'min_price': min_flight['price'],
            'transport_cost': transport_cost,
            'total_cost': min_flight['total_cost_with_transport'],
            'flight_savings': flight_savings,
            'net_savings': net_savings,
            'transport_time_minutes': transport_time,
            'recommended': net_savings > 50 and transport_time < 120
        })
    
    return sorted(matrix, key=lambda x: x['total_cost'])

def main():
    parser = argparse.ArgumentParser(description='Search alternative airports for better flight prices')
    parser.add_argument('origin', help='Origin airport code (e.g., LAX)')
    parser.add_argument('destination', help='Destination airport code (e.g., JFK)')
    parser.add_argument('depart_date', help='Departure date (YYYY-MM-DD)')
    parser.add_argument('--return', dest='return_date', help='Return date for round trip (YYYY-MM-DD)')
    parser.add_argument('--matrix', action='store_true', help='Show savings matrix instead of individual flights')
    parser.add_argument('--pretty', action='store_true', help='Pretty print JSON output')
    
    args = parser.parse_args()
    
    try:
        results = search_alternative_airports(
            args.origin,
            args.destination,
            args.depart_date,
            args.return_date
        )
        
        if args.matrix:
            # Show savings matrix
            matrix = generate_savings_matrix(results, args.origin, args.destination)
            output = {
                "requested_route": f"{args.origin} to {args.destination}",
                "date": args.depart_date,
                "return_date": args.return_date,
                "savings_matrix": matrix
            }
        else:
            # Show individual flights
            output = results
        
        if args.pretty:
            print(json.dumps(output, indent=2, sort_keys=True))
        else:
            print(json.dumps(output))
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()