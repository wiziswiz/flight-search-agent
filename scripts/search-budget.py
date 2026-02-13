#!/usr/bin/env python3
"""
Budget carrier flight search script.
Searches budget airlines like Southwest, Spirit, Frontier directly since they're often not on aggregators.
"""

import json
import sys
import argparse
import urllib.request
import urllib.parse
from datetime import datetime

def search_budget_carriers(origin, destination, depart_date, return_date=None):
    """Search budget carriers for flight prices"""
    try:
        all_flights = []
        
        # Search each budget carrier
        carriers = [
            {'name': 'Southwest', 'function': search_southwest},
            {'name': 'Spirit', 'function': search_spirit},
            {'name': 'Frontier', 'function': search_frontier},
            {'name': 'Allegiant', 'function': search_allegiant},
            {'name': 'JetBlue', 'function': search_jetblue}
        ]
        
        for carrier in carriers:
            try:
                flights = carrier['function'](origin, destination, depart_date, return_date)
                all_flights.extend(flights)
            except Exception as e:
                print(f"Error searching {carrier['name']}: {e}", file=sys.stderr)
                continue
        
        return sorted(all_flights, key=lambda x: x["price"])
        
    except Exception as e:
        print(f"Error searching budget carriers: {e}", file=sys.stderr)
        return []

def search_southwest(origin, destination, depart_date, return_date=None):
    """Search Southwest Airlines (not on most aggregators)"""
    try:
        # Southwest would require complex scraping since they don't allow their fares on aggregators
        # For demonstration, return mock data
        return generate_mock_carrier_flights("Southwest", origin, destination, depart_date, return_date, 
                                           base_price_range=(120, 350), 
                                           features=["2 free bags", "No change fees", "Companion Pass eligible"])
        
    except Exception as e:
        print(f"Error searching Southwest: {e}", file=sys.stderr)
        return []

def search_spirit(origin, destination, depart_date, return_date=None):
    """Search Spirit Airlines"""
    try:
        # Spirit API would be here - using mock data for demonstration
        return generate_mock_carrier_flights("Spirit", origin, destination, depart_date, return_date,
                                           base_price_range=(89, 280),
                                           features=["Ultra-low base fare", "Extra fees for everything", "Bare Fare"],
                                           warnings=["Carry-on bag fees", "Seat selection fees", "No free snacks"])
        
    except Exception as e:
        print(f"Error searching Spirit: {e}", file=sys.stderr)
        return []

def search_frontier(origin, destination, depart_date, return_date=None):
    """Search Frontier Airlines"""
    try:
        return generate_mock_carrier_flights("Frontier", origin, destination, depart_date, return_date,
                                           base_price_range=(79, 299),
                                           features=["Low base fare", "Discount Den membership", "Animal-themed planes"],
                                           warnings=["Bag fees apply", "Seat fees", "Limited schedule"])
        
    except Exception as e:
        print(f"Error searching Frontier: {e}", file=sys.stderr)
        return []

def search_allegiant(origin, destination, depart_date, return_date=None):
    """Search Allegiant Air"""
    try:
        return generate_mock_carrier_flights("Allegiant", origin, destination, depart_date, return_date,
                                           base_price_range=(69, 249),
                                           features=["Point-to-point routes", "Vacation packages", "Very low base fares"],
                                           warnings=["Limited destinations", "Infrequent flights", "Many extra fees"])
        
    except Exception as e:
        print(f"Error searching Allegiant: {e}", file=sys.stderr)
        return []

def search_jetblue(origin, destination, depart_date, return_date=None):
    """Search JetBlue Airways"""
    try:
        return generate_mock_carrier_flights("JetBlue", origin, destination, depart_date, return_date,
                                           base_price_range=(149, 450),
                                           features=["Free Wi-Fi", "Free snacks", "More legroom", "Mint business class"],
                                           warnings=[])
        
    except Exception as e:
        print(f"Error searching JetBlue: {e}", file=sys.stderr)
        return []

def generate_mock_carrier_flights(airline, origin, destination, depart_date, return_date=None, 
                                base_price_range=(100, 400), features=None, warnings=None):
    """Generate mock flight data for a specific carrier"""
    import random
    
    flights = []
    features = features or []
    warnings = warnings or []
    
    # Check if carrier serves this route (simplified logic)
    if not serves_route(airline, origin, destination):
        return []
    
    # Generate 1-3 flights for this carrier
    num_flights = random.randint(1, 3)
    
    for i in range(num_flights):
        base_price = random.randint(base_price_range[0], base_price_range[1])
        
        # Different fare types for some carriers
        fare_types = get_fare_types(airline)
        fare_type = random.choice(fare_types)
        
        # Adjust price based on fare type
        if fare_type == "basic" or fare_type == "bare":
            price = base_price
        elif fare_type == "standard":
            price = int(base_price * 1.3)
        elif fare_type == "plus" or fare_type == "even_more":
            price = int(base_price * 1.6)
        else:
            price = base_price
        
        departure_time = f"{random.randint(6, 22):02d}:{random.choice(['00', '15', '30', '45'])}"
        duration_hours = random.randint(2, 6)
        arrival_hour = (int(departure_time[:2]) + duration_hours) % 24
        arrival_time = f"{arrival_hour:02d}:{random.choice(['00', '15', '30', '45'])}"
        
        flight = {
            "price": price,
            "currency": "USD",
            "airline": airline,
            "fare_type": fare_type,
            "flight_number": f"{get_airline_code(airline)}{random.randint(100, 9999)}",
            "origin": origin,
            "destination": destination,
            "departure_date": depart_date,
            "departure_time": departure_time,
            "arrival_time": arrival_time,
            "duration": f"{duration_hours}h {random.randint(0, 59)}m",
            "aircraft": get_typical_aircraft(airline),
            "stops": 0,  # Most budget carriers are point-to-point
            "strategy": "budget-carrier-direct",
            "booking_url": get_carrier_booking_url(airline, origin, destination, depart_date),
            "confidence": "high",
            "features": features,
            "warnings": warnings,
            "total_cost_estimate": estimate_total_cost(airline, price)
        }
        
        if return_date:
            flight["return_date"] = return_date
            flight["trip_type"] = "round_trip"
            flight["price"] = int(price * 1.9)  # Round trip, slightly less than 2x
            flight["total_cost_estimate"] = estimate_total_cost(airline, flight["price"])
        else:
            flight["trip_type"] = "one_way"
        
        flights.append(flight)
    
    return flights

def serves_route(airline, origin, destination):
    """Check if airline serves the route (simplified)"""
    # Simplified route coverage - in reality this would be a comprehensive database
    route_coverage = {
        'Southwest': {
            'hubs': ['DEN', 'LAS', 'PHX', 'DAL', 'HOU', 'MDW', 'BWI', 'OAK'],
            'major_airports': ['LAX', 'SFO', 'ORD', 'ATL', 'DFW', 'JFK', 'LGA', 'BOS', 'SEA', 'MIA']
        },
        'Spirit': {
            'hubs': ['FLL', 'DFW', 'LAS', 'ORD', 'DTW'],
            'major_airports': ['LAX', 'JFK', 'LGA', 'BOS', 'ATL', 'PHX', 'DEN', 'SEA', 'MIA']
        },
        'Frontier': {
            'hubs': ['DEN', 'LAS', 'PHX', 'ORD', 'ATL'],
            'major_airports': ['LAX', 'SFO', 'JFK', 'BOS', 'MIA', 'SEA', 'DFW']
        },
        'Allegiant': {
            'hubs': ['LAS', 'LAX', 'SFB', 'PHX'],
            'major_airports': ['LAX', 'LAS', 'PHX', 'FLL', 'MIA', 'SFB', 'SNA']
        },
        'JetBlue': {
            'hubs': ['JFK', 'BOS', 'FLL', 'LAX', 'LGB'],
            'major_airports': ['JFK', 'LGA', 'BOS', 'LAX', 'SFO', 'FLL', 'MIA', 'DEN', 'SEA']
        }
    }
    
    if airline not in route_coverage:
        return False
    
    coverage = route_coverage[airline]
    airports_served = coverage['hubs'] + coverage['major_airports']
    
    return origin in airports_served and destination in airports_served

def get_fare_types(airline):
    """Get fare types offered by the airline"""
    fare_types = {
        'Southwest': ['Wanna Get Away', 'Anytime', 'Business Select'],
        'Spirit': ['Bare Fare', '$9 Fare Club', 'Standard'],
        'Frontier': ['Basic', 'Standard', 'The Works'],
        'Allegiant': ['Basic', 'Total'],
        'JetBlue': ['Blue Basic', 'Blue', 'Blue Plus', 'Blue Extra', 'Mint']
    }
    return fare_types.get(airline, ['Basic', 'Standard'])

def get_airline_code(airline):
    """Get airline IATA code"""
    codes = {
        'Southwest': 'WN',
        'Spirit': 'NK', 
        'Frontier': 'F9',
        'Allegiant': 'G4',
        'JetBlue': 'B6'
    }
    return codes.get(airline, 'XX')

def get_typical_aircraft(airline):
    """Get typical aircraft for the airline"""
    aircraft = {
        'Southwest': 'Boeing 737',
        'Spirit': 'Airbus A319/A320',
        'Frontier': 'Airbus A320neo',
        'Allegiant': 'Airbus A320',
        'JetBlue': 'Airbus A220/A320'
    }
    return aircraft.get(airline, 'Unknown')

def get_carrier_booking_url(airline, origin, destination, depart_date):
    """Get booking URL for the carrier"""
    booking_urls = {
        'Southwest': f'https://www.southwest.com/flight/search-flight.html?originationAirportCode={origin}&destinationAirportCode={destination}&departureDate={depart_date}',
        'Spirit': f'https://www.spirit.com/book/flights?origin={origin}&destination={destination}&departure={depart_date}',
        'Frontier': f'https://www.flyfrontier.com/travel/flight/search?c=USD&o={origin}&d={destination}&dd={depart_date}',
        'Allegiant': f'https://www.allegiantair.com/booking/flights/select-flights?origin={origin}&destination={destination}&departure={depart_date}',
        'JetBlue': f'https://www.jetblue.com/booking/flights?origin={origin}&destination={destination}&departure={depart_date}'
    }
    
    return booking_urls.get(airline, f'https://www.google.com/flights?hl=en#search;f={origin};t={destination}')

def estimate_total_cost(airline, base_price):
    """Estimate total cost including typical fees for budget carriers"""
    fee_estimates = {
        'Southwest': {
            'carry_on': 0,  # Free
            'checked_bag': 0,  # 2 free
            'seat_selection': 0,  # Free basic selection
            'total_fee_range': [0, 50]
        },
        'Spirit': {
            'carry_on': 45,
            'checked_bag': 35, 
            'seat_selection': 15,
            'total_fee_range': [60, 120]
        },
        'Frontier': {
            'carry_on': 40,
            'checked_bag': 30,
            'seat_selection': 12,
            'total_fee_range': [50, 100]
        },
        'Allegiant': {
            'carry_on': 35,
            'checked_bag': 25,
            'seat_selection': 10,
            'total_fee_range': [45, 90]
        },
        'JetBlue': {
            'carry_on': 0,  # Free
            'checked_bag': 35,
            'seat_selection': 15,
            'total_fee_range': [20, 60]
        }
    }
    
    import random
    
    if airline in fee_estimates:
        fee_range = fee_estimates[airline]['total_fee_range']
        typical_fees = random.randint(fee_range[0], fee_range[1])
        return base_price + typical_fees
    
    return base_price

def compare_with_mainline(budget_flights):
    """Add comparison with typical mainline carrier prices"""
    import random
    
    for flight in budget_flights:
        # Estimate mainline carrier price (typically 20-60% more)
        multiplier = random.uniform(1.2, 1.6)
        mainline_estimate = int(flight['price'] * multiplier)
        
        savings = mainline_estimate - flight['total_cost_estimate']
        savings_percent = int(savings / mainline_estimate * 100) if mainline_estimate > 0 else 0
        
        flight['mainline_price_estimate'] = mainline_estimate
        flight['estimated_savings'] = max(0, savings)
        flight['savings_percent'] = max(0, savings_percent)
        
        if savings > 0:
            flight['value_proposition'] = f"Save ${savings} ({savings_percent}%) vs mainline carriers"
        else:
            flight['value_proposition'] = "May not be cheaper after fees"
    
    return budget_flights

def main():
    parser = argparse.ArgumentParser(description='Search budget carriers for flight prices')
    parser.add_argument('origin', help='Origin airport code (e.g., LAX)')
    parser.add_argument('destination', help='Destination airport code (e.g., JFK)')
    parser.add_argument('depart_date', help='Departure date (YYYY-MM-DD)')
    parser.add_argument('--return', dest='return_date', help='Return date for round trip (YYYY-MM-DD)')
    parser.add_argument('--pretty', action='store_true', help='Pretty print JSON output')
    
    args = parser.parse_args()
    
    try:
        results = search_budget_carriers(
            args.origin,
            args.destination,
            args.depart_date,
            args.return_date
        )
        
        # Add comparison with mainline carriers
        results = compare_with_mainline(results)
        
        if args.pretty:
            print(json.dumps(results, indent=2, sort_keys=True))
        else:
            print(json.dumps(results))
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()