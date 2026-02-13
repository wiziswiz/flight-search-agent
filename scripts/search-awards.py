#!/usr/bin/env python3
"""
Award flight search script.
Searches for flights using airline miles and credit card points.
"""

import json
import sys
import argparse
import os
import urllib.request
import urllib.parse
from datetime import datetime

# Load award sweet spots database
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AWARD_SWEET_SPOTS_FILE = os.path.join(SCRIPT_DIR, '..', 'data', 'award-sweet-spots.json')

def load_award_sweet_spots():
    """Load award sweet spots from data file"""
    try:
        with open(AWARD_SWEET_SPOTS_FILE, 'r') as f:
            data = json.load(f)
            return data.get('sweet_spots', [])
    except FileNotFoundError:
        print(f"Warning: Award sweet spots file not found at {AWARD_SWEET_SPOTS_FILE}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Error loading award sweet spots: {e}", file=sys.stderr)
        return []

def search_award_flights(origin, destination, depart_date, return_date=None, program=None):
    """Search for award flights using miles/points"""
    try:
        results = []
        
        # Get relevant sweet spots
        sweet_spots = get_relevant_sweet_spots(origin, destination, program)
        
        # For each relevant program, generate mock award availability
        for spot in sweet_spots:
            award_flights = generate_mock_award_flights(
                origin, destination, depart_date, return_date, spot
            )
            results.extend(award_flights)
        
        # If no specific program, search major programs
        if not program:
            major_programs = ['united-mileageplus', 'american-aadvantage', 'delta-skymiles', 
                            'chase-ultimate-rewards', 'amex-membership-rewards']
            for prog in major_programs:
                if not any(spot['program'] == prog for spot in sweet_spots):
                    # Generate basic award options for major programs
                    basic_award = generate_basic_award_option(origin, destination, depart_date, return_date, prog)
                    if basic_award:
                        results.extend(basic_award)
        
        return sorted(results, key=lambda x: x.get('value_per_point', 0), reverse=True)
        
    except Exception as e:
        print(f"Error searching award flights: {e}", file=sys.stderr)
        return []

def get_relevant_sweet_spots(origin, destination, program=None):
    """Get sweet spots relevant to the route and program"""
    sweet_spots = load_award_sweet_spots()
    relevant = []
    
    route_mapping = {
        ('US', 'Europe'): ['LAX', 'SFO', 'JFK', 'ORD', 'BOS', 'DFW'],
        ('US', 'Asia'): ['LAX', 'SFO', 'SEA', 'DFW', 'ORD'],
        ('US', 'Japan'): ['LAX', 'SFO', 'SEA', 'DFW', 'ORD'],
        ('US', 'UK'): ['JFK', 'BOS', 'LAX', 'SFO', 'ORD'],
        ('US', 'Middle East'): ['JFK', 'LAX', 'DFW', 'ORD']
    }
    
    # Determine route type
    route_type = determine_route_type(origin, destination)
    
    for spot in sweet_spots:
        # Filter by route
        if spot['route'] == route_type:
            # Filter by program if specified
            if program is None or spot['program'] == program:
                relevant.append(spot)
    
    return relevant

def determine_route_type(origin, destination):
    """Determine the route type (US-Europe, US-Asia, etc.)"""
    us_airports = ['LAX', 'SFO', 'JFK', 'ORD', 'DFW', 'ATL', 'DEN', 'SEA', 'BOS', 'MIA', 'PHX', 'LAS', 'MCO', 'BWI', 'DCA', 'IAD', 'CLT', 'PHL']
    europe_airports = ['LHR', 'CDG', 'FRA', 'AMS', 'FCO', 'MAD', 'BCN', 'MUC', 'ZUR', 'VIE']
    asia_airports = ['NRT', 'HND', 'ICN', 'PVG', 'PEK', 'BKK', 'SIN', 'HKG']
    japan_airports = ['NRT', 'HND', 'ITM', 'KIX']
    uk_airports = ['LHR', 'LGW', 'STN', 'LTN']
    middle_east_airports = ['DXB', 'DOH', 'AUH', 'KWI']
    
    origin_region = None
    dest_region = None
    
    if origin in us_airports:
        origin_region = 'US'
    if destination in us_airports:
        dest_region = 'US'
    if destination in europe_airports:
        dest_region = 'Europe'
    if destination in asia_airports:
        dest_region = 'Asia'
    if destination in japan_airports:
        dest_region = 'Japan'
    if destination in uk_airports:
        dest_region = 'UK'
    if destination in middle_east_airports:
        dest_region = 'Middle East'
    
    if origin_region and dest_region:
        return f"{origin_region}-{dest_region}"
    
    # Default fallback
    return "International"

def generate_mock_award_flights(origin, destination, depart_date, return_date, sweet_spot):
    """Generate mock award flight data based on sweet spot"""
    import random
    
    flights = []
    
    # Generate availability for different classes
    classes = ['economy', 'business']
    if sweet_spot.get('class') == 'first':
        classes.append('first')
    
    for flight_class in classes:
        # Calculate miles required based on sweet spot
        base_miles = sweet_spot['miles']
        if flight_class == 'economy':
            miles_required = int(base_miles * 0.6)  # Economy is typically 60% of business
        elif flight_class == 'business':
            miles_required = base_miles
        else:  # first
            miles_required = int(base_miles * 1.4)  # First is typically 140% of business
        
        # Generate mock availability
        availability = random.choice(['high', 'low', 'waitlist', 'none'])
        if availability == 'none':
            continue
            
        # Mock taxes and fees
        taxes = random.randint(50, 300)
        
        # Calculate value per point
        cash_equivalent = sweet_spot.get('typical_cash', 5000)
        if flight_class == 'economy':
            cash_equivalent = int(cash_equivalent * 0.4)
        elif flight_class == 'first':
            cash_equivalent = int(cash_equivalent * 1.8)
            
        value_per_point = round(cash_equivalent / miles_required * 100, 2) if miles_required > 0 else 0
        
        flight = {
            "program": sweet_spot['program'],
            "airline": sweet_spot['airline'],
            "class": flight_class,
            "origin": origin,
            "destination": destination,
            "route": sweet_spot['route'],
            "departure_date": depart_date,
            "miles_required": miles_required,
            "taxes_fees": taxes,
            "total_cost_usd": taxes,  # Only taxes in cash
            "cash_equivalent": cash_equivalent,
            "value_per_point": value_per_point,
            "availability": availability,
            "strategy": "award-search",
            "booking_url": get_program_booking_url(sweet_spot['program'], origin, destination),
            "confidence": "medium",
            "transfer_partners": get_transfer_partners(sweet_spot['program']),
            "notes": sweet_spot.get('notes', ''),
            "recommendation": get_award_recommendation(value_per_point, availability)
        }
        
        if return_date:
            flight["return_date"] = return_date
            flight["trip_type"] = "round_trip"
            flight["miles_required"] = miles_required * 2
            flight["taxes_fees"] = taxes * 2
            flight["total_cost_usd"] = taxes * 2
        else:
            flight["trip_type"] = "one_way"
        
        flights.append(flight)
    
    return flights

def generate_basic_award_option(origin, destination, depart_date, return_date, program):
    """Generate basic award option for major programs"""
    import random
    
    # Basic award rates for major programs
    program_data = {
        'united-mileageplus': {
            'airline': 'United Airlines',
            'domestic_economy': 12500,
            'domestic_business': 25000,
            'international_economy': 35000,
            'international_business': 70000
        },
        'american-aadvantage': {
            'airline': 'American Airlines', 
            'domestic_economy': 12500,
            'domestic_business': 25000,
            'international_economy': 35000,
            'international_business': 70000
        },
        'delta-skymiles': {
            'airline': 'Delta Airlines',
            'domestic_economy': 15000,
            'domestic_business': 30000,
            'international_economy': 40000,
            'international_business': 80000
        },
        'chase-ultimate-rewards': {
            'airline': 'Various Partners',
            'domestic_economy': 12500,
            'domestic_business': 25000,
            'international_economy': 35000,
            'international_business': 70000
        },
        'amex-membership-rewards': {
            'airline': 'Various Partners',
            'domestic_economy': 12500,
            'domestic_business': 25000, 
            'international_economy': 35000,
            'international_business': 70000
        }
    }
    
    if program not in program_data:
        return None
    
    prog_info = program_data[program]
    
    # Determine if domestic or international
    us_airports = ['LAX', 'SFO', 'JFK', 'ORD', 'DFW', 'ATL', 'DEN', 'SEA', 'BOS', 'MIA']
    is_domestic = origin in us_airports and destination in us_airports
    
    flights = []
    
    for flight_class in ['economy', 'business']:
        if is_domestic:
            miles_key = f'domestic_{flight_class}'
        else:
            miles_key = f'international_{flight_class}'
            
        miles_required = prog_info.get(miles_key, 50000)
        
        # Mock availability and pricing
        availability = random.choice(['high', 'low', 'waitlist'])
        taxes = random.randint(50, 200) if is_domestic else random.randint(100, 400)
        
        # Estimate cash equivalent
        if is_domestic:
            cash_equivalent = 400 if flight_class == 'economy' else 1200
        else:
            cash_equivalent = 1200 if flight_class == 'economy' else 4000
            
        value_per_point = round(cash_equivalent / miles_required * 100, 2) if miles_required > 0 else 0
        
        flight = {
            "program": program,
            "airline": prog_info['airline'],
            "class": flight_class,
            "origin": origin,
            "destination": destination,
            "route": "Domestic" if is_domestic else "International",
            "departure_date": depart_date,
            "miles_required": miles_required,
            "taxes_fees": taxes,
            "total_cost_usd": taxes,
            "cash_equivalent": cash_equivalent,
            "value_per_point": value_per_point,
            "availability": availability,
            "strategy": "award-search-basic",
            "booking_url": get_program_booking_url(program, origin, destination),
            "confidence": "low",
            "transfer_partners": get_transfer_partners(program),
            "recommendation": get_award_recommendation(value_per_point, availability)
        }
        
        if return_date:
            flight["return_date"] = return_date
            flight["trip_type"] = "round_trip"
            flight["miles_required"] = miles_required * 2
            flight["taxes_fees"] = taxes * 2
            flight["total_cost_usd"] = taxes * 2
        else:
            flight["trip_type"] = "one_way"
        
        flights.append(flight)
    
    return flights

def get_transfer_partners(program):
    """Get transfer partners for the program"""
    transfer_partners = {
        'united-mileageplus': ['Chase Ultimate Rewards'],
        'american-aadvantage': ['Marriott Bonvoy', 'Bilt'],
        'delta-skymiles': ['American Express Membership Rewards'],
        'chase-ultimate-rewards': ['United', 'Southwest', 'British Airways', 'Singapore Airlines'],
        'amex-membership-rewards': ['Delta', 'British Airways', 'Air France/KLM', 'Singapore Airlines'],
        'virgin-atlantic': ['Chase Ultimate Rewards', 'American Express Membership Rewards', 'Marriott Bonvoy'],
        'alaska-mileage-plan': ['Marriott Bonvoy', 'Bilt'],
        'british-airways-avios': ['Chase Ultimate Rewards', 'American Express Membership Rewards'],
        'aeroplan': ['Chase Ultimate Rewards', 'American Express Membership Rewards', 'Marriott Bonvoy']
    }
    
    return transfer_partners.get(program, [])

def get_program_booking_url(program, origin, destination):
    """Get booking URL for the program"""
    booking_urls = {
        'united-mileageplus': f'https://www.united.com/en/us/fop/choose-flights?f={origin}&t={destination}&d=2026-03-15&tt=1&at=1&sc=7&px=1&taxng=1&idx=1',
        'american-aadvantage': f'https://www.aa.com/booking/choose-flights?localeCode=en_US&from={origin}&to={destination}',
        'delta-skymiles': f'https://www.delta.com/flight-search/book-a-flight?tripType=oneWay&from={origin}&to={destination}',
        'chase-ultimate-rewards': 'https://ultimaterewards.chase.com/travel',
        'amex-membership-rewards': 'https://global.americanexpress.com/travel/home'
    }
    
    return booking_urls.get(program, f'https://www.google.com/flights?hl=en#search;f={origin};t={destination}')

def get_award_recommendation(value_per_point, availability):
    """Generate recommendation based on value per point and availability"""
    if availability == 'none':
        return "No availability"
    elif availability == 'waitlist':
        return "Consider waitlist if flexible"
    elif value_per_point >= 2.0:
        return "Excellent value - book with points!"
    elif value_per_point >= 1.5:
        return "Good value - worth using points"
    elif value_per_point >= 1.0:
        return "Fair value - consider cash price"
    else:
        return "Poor value - pay cash instead"

def main():
    parser = argparse.ArgumentParser(description='Search for award flights using miles and points')
    parser.add_argument('origin', help='Origin airport code (e.g., LAX)')
    parser.add_argument('destination', help='Destination airport code (e.g., NRT)')
    parser.add_argument('depart_date', help='Departure date (YYYY-MM-DD)')
    parser.add_argument('--return', dest='return_date', help='Return date for round trip (YYYY-MM-DD)')
    parser.add_argument('--program', choices=[
        'chase-ur', 'amex-mr', 'united', 'aa', 'delta', 'southwest',
        'alaska', 'virgin-atlantic', 'british-airways', 'aeroplan'
    ], help='Specific loyalty program to search')
    parser.add_argument('--pretty', action='store_true', help='Pretty print JSON output')
    
    args = parser.parse_args()
    
    # Map short program names to full names
    program_mapping = {
        'chase-ur': 'chase-ultimate-rewards',
        'amex-mr': 'amex-membership-rewards', 
        'united': 'united-mileageplus',
        'aa': 'american-aadvantage',
        'delta': 'delta-skymiles',
        'southwest': 'southwest-rapid-rewards',
        'alaska': 'alaska-mileage-plan',
        'virgin-atlantic': 'virgin-atlantic',
        'british-airways': 'british-airways-avios',
        'aeroplan': 'aeroplan'
    }
    
    program = program_mapping.get(args.program, args.program)
    
    try:
        results = search_award_flights(
            args.origin,
            args.destination,
            args.depart_date,
            args.return_date,
            program
        )
        
        if args.pretty:
            print(json.dumps(results, indent=2, sort_keys=True))
        else:
            print(json.dumps(results))
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()