#!/usr/bin/env python3
"""
Award flight search script — REAL DATA edition.
Searches for award flights using airline miles and credit card points.

Architecture (tiered, zero cost):
  Tier 1: SerpAPI Google Flights — get real cash prices, cross-reference with
          sweet spots DB to compute actual value-per-point.
  Tier 2: Airline website scraping via Playwright (united.com, aa.com, delta.com)
  Tier 3: points.me free-tier scraping via Playwright
  Tier 4: Sweet spots DB estimates (fallback, clearly labeled)

All results include: program, miles_required, taxes_fees, cash_equivalent,
value_per_point, availability, booking_url, confidence, source
"""

import json
import sys
import argparse
import os
import urllib.request
import urllib.parse
import subprocess
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'data')
AWARD_SWEET_SPOTS_FILE = os.path.join(DATA_DIR, 'award-sweet-spots.json')

# ---------------------------------------------------------------------------
# Transfer partner map (source program → bookable airline programs)
# ---------------------------------------------------------------------------
TRANSFER_PARTNERS = {
    # Flexible currency programs
    'chase-ur': {
        'full_name': 'Chase Ultimate Rewards',
        'partners': {
            'united-mileageplus': {'ratio': 1, 'name': 'United MileagePlus'},
            'british-airways-avios': {'ratio': 1, 'name': 'British Airways Avios'},
            'virgin-atlantic': {'ratio': 1, 'name': 'Virgin Atlantic Flying Club'},
            'aeroplan': {'ratio': 1, 'name': 'Air Canada Aeroplan'},
            'singapore-krisflyer': {'ratio': 1, 'name': 'Singapore KrisFlyer'},
            'southwest-rapid-rewards': {'ratio': 1, 'name': 'Southwest Rapid Rewards'},
            'air-france-klm': {'ratio': 1, 'name': 'Air France/KLM Flying Blue'},
            'iberia-avios': {'ratio': 1, 'name': 'Iberia Avios'},
            'emirates-skywards': {'ratio': 1, 'name': 'Emirates Skywards'},
        }
    },
    'amex-mr': {
        'full_name': 'Amex Membership Rewards',
        'partners': {
            'delta-skymiles': {'ratio': 1, 'name': 'Delta SkyMiles'},
            'british-airways-avios': {'ratio': 1, 'name': 'British Airways Avios'},
            'virgin-atlantic': {'ratio': 1, 'name': 'Virgin Atlantic Flying Club'},
            'aeroplan': {'ratio': 1, 'name': 'Air Canada Aeroplan'},
            'singapore-krisflyer': {'ratio': 1, 'name': 'Singapore KrisFlyer'},
            'air-france-klm': {'ratio': 1, 'name': 'Air France/KLM Flying Blue'},
            'emirates-skywards': {'ratio': 1, 'name': 'Emirates Skywards'},
            'ana-mileage-club': {'ratio': 1, 'name': 'ANA Mileage Club'},
        }
    },
    'capital-one': {
        'full_name': 'Capital One Miles',
        'partners': {
            'british-airways-avios': {'ratio': 1, 'name': 'British Airways Avios'},
            'virgin-atlantic': {'ratio': 1, 'name': 'Virgin Atlantic Flying Club'},
            'air-france-klm': {'ratio': 1, 'name': 'Air France/KLM Flying Blue'},
            'turkish-miles-smiles': {'ratio': 1, 'name': 'Turkish Miles&Smiles'},
            'emirates-skywards': {'ratio': 1, 'name': 'Emirates Skywards'},
            'singapore-krisflyer': {'ratio': 1, 'name': 'Singapore KrisFlyer'},
        }
    },
    'citi-typ': {
        'full_name': 'Citi ThankYou Points',
        'partners': {
            'virgin-atlantic': {'ratio': 1, 'name': 'Virgin Atlantic Flying Club'},
            'singapore-krisflyer': {'ratio': 1, 'name': 'Singapore KrisFlyer'},
            'air-france-klm': {'ratio': 1, 'name': 'Air France/KLM Flying Blue'},
            'turkish-miles-smiles': {'ratio': 1, 'name': 'Turkish Miles&Smiles'},
            'emirates-skywards': {'ratio': 1, 'name': 'Emirates Skywards'},
        }
    },
    'bilt': {
        'full_name': 'Bilt Rewards',
        'partners': {
            'american-aadvantage': {'ratio': 1, 'name': 'American AAdvantage'},
            'united-mileageplus': {'ratio': 1, 'name': 'United MileagePlus'},
            'alaska-mileage-plan': {'ratio': 1, 'name': 'Alaska Mileage Plan'},
            'aeroplan': {'ratio': 1, 'name': 'Air Canada Aeroplan'},
            'british-airways-avios': {'ratio': 1, 'name': 'British Airways Avios'},
            'virgin-atlantic': {'ratio': 1, 'name': 'Virgin Atlantic Flying Club'},
            'air-france-klm': {'ratio': 1, 'name': 'Air France/KLM Flying Blue'},
            'turkish-miles-smiles': {'ratio': 1, 'name': 'Turkish Miles&Smiles'},
            'emirates-skywards': {'ratio': 1, 'name': 'Emirates Skywards'},
        }
    },
    # Direct airline programs (no transfer needed)
    'united': {
        'full_name': 'United MileagePlus',
        'partners': {'united-mileageplus': {'ratio': 1, 'name': 'United MileagePlus'}}
    },
    'aa': {
        'full_name': 'American AAdvantage',
        'partners': {'american-aadvantage': {'ratio': 1, 'name': 'American AAdvantage'}}
    },
    'delta': {
        'full_name': 'Delta SkyMiles',
        'partners': {'delta-skymiles': {'ratio': 1, 'name': 'Delta SkyMiles'}}
    },
    'alaska': {
        'full_name': 'Alaska Mileage Plan',
        'partners': {'alaska-mileage-plan': {'ratio': 1, 'name': 'Alaska Mileage Plan'}}
    },
    'southwest': {
        'full_name': 'Southwest Rapid Rewards',
        'partners': {'southwest-rapid-rewards': {'ratio': 1, 'name': 'Southwest Rapid Rewards'}}
    },
}

# Map sweet-spot program names → canonical keys used above
PROGRAM_CANONICAL = {
    'virgin-atlantic': 'virgin-atlantic',
    'alaska-mileage-plan': 'alaska-mileage-plan',
    'united-mileageplus': 'united-mileageplus',
    'aeroplan': 'aeroplan',
    'american-aadvantage': 'american-aadvantage',
    'chase-ultimate-rewards': 'chase-ur',
    'amex-membership-rewards': 'amex-mr',
    'delta-skymiles': 'delta-skymiles',
    'british-airways-avios': 'british-airways-avios',
}

# ---------------------------------------------------------------------------
# Sweet spots DB
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Route classification
# ---------------------------------------------------------------------------
REGION_AIRPORTS = {
    'US': ['LAX', 'SFO', 'JFK', 'ORD', 'DFW', 'ATL', 'DEN', 'SEA', 'BOS',
           'MIA', 'PHX', 'LAS', 'MCO', 'BWI', 'DCA', 'IAD', 'CLT', 'PHL',
           'EWR', 'IAH', 'MSP', 'DTW', 'SAN', 'TPA', 'SLC', 'HNL', 'AUS',
           'RDU', 'BNA', 'PDX', 'STL', 'SMF', 'SJC', 'OAK', 'FLL', 'PIT'],
    'Europe': ['LHR', 'CDG', 'FRA', 'AMS', 'FCO', 'MAD', 'BCN', 'MUC',
               'ZRH', 'VIE', 'CPH', 'OSL', 'ARN', 'HEL', 'LIS', 'DUB',
               'BRU', 'MXP', 'ATH', 'WAW', 'PRG', 'BUD'],
    'Japan': ['NRT', 'HND', 'ITM', 'KIX', 'CTS', 'FUK', 'NGO'],
    'Asia': ['NRT', 'HND', 'ICN', 'PVG', 'PEK', 'BKK', 'SIN', 'HKG',
             'KUL', 'MNL', 'DEL', 'BOM', 'TPE', 'SGN', 'HAN'],
    'UK': ['LHR', 'LGW', 'STN', 'LTN', 'MAN', 'EDI'],
    'Middle East': ['DXB', 'DOH', 'AUH', 'KWI', 'JED', 'RUH', 'AMM', 'TLV'],
    'Oceania': ['SYD', 'MEL', 'BNE', 'AKL', 'PER'],
    'South America': ['GRU', 'EZE', 'BOG', 'LIM', 'SCL', 'GIG'],
    'Central America': ['CUN', 'MEX', 'SJO', 'PTY'],
    'Africa': ['JNB', 'CPT', 'NBO', 'ADD', 'CAI', 'CMN'],
}


def _airport_region(code):
    """Return the region for an airport code. More specific wins (Japan > Asia)."""
    # Check specific regions first
    for region in ['Japan', 'UK', 'Middle East', 'Central America']:
        if code in REGION_AIRPORTS.get(region, []):
            return region
    for region in ['US', 'Europe', 'Asia', 'Oceania', 'South America', 'Africa']:
        if code in REGION_AIRPORTS.get(region, []):
            return region
    return 'Other'


def determine_route_type(origin, destination):
    """e.g. 'US-Japan', 'US-Europe', 'Domestic'"""
    o = _airport_region(origin)
    d = _airport_region(destination)
    if o == d == 'US':
        return 'Domestic'
    if o == d:
        return f'{o}-{o}'
    return f'{o}-{d}'


def get_relevant_sweet_spots(origin, destination, program=None):
    """Return sweet-spot entries relevant to this route and optional program."""
    sweet_spots = load_award_sweet_spots()
    route_type = determine_route_type(origin, destination)

    relevant = []
    for spot in sweet_spots:
        # Match route (exact or reverse)
        sr = spot.get('route', '')
        parts = sr.split('-', 1)
        reverse = f"{parts[1]}-{parts[0]}" if len(parts) == 2 else ''
        if sr != route_type and reverse != route_type:
            continue
        if program and spot['program'] != program:
            continue
        relevant.append(spot)
    return relevant


# ---------------------------------------------------------------------------
# Tier 1 — SerpAPI Google Flights (cash prices)
# ---------------------------------------------------------------------------

def serpapi_search(origin, destination, depart_date, return_date=None, travel_class=1):
    """
    Hit SerpAPI Google Flights engine.  Returns (best_flights, other_flights) lists
    or (None, None) on failure.
    travel_class: 1=economy, 2=premium_economy, 3=business, 4=first
    """
    api_key = os.getenv('SERP_API_KEY')
    if not api_key:
        print("Tier 1: SERP_API_KEY not set — skipping SerpAPI", file=sys.stderr)
        return None, None

    try:
        import requests
    except ImportError:
        # Fallback to urllib
        return _serpapi_search_urllib(origin, destination, depart_date, return_date, travel_class, api_key)

    try:
        params = {
            'engine': 'google_flights',
            'departure_id': origin,
            'arrival_id': destination,
            'outbound_date': depart_date,
            'currency': 'USD',
            'hl': 'en',
            'travel_class': travel_class,
            'api_key': api_key,
        }
        if return_date:
            params['return_date'] = return_date
            params['type'] = 1  # round trip
        else:
            params['type'] = 2  # one-way

        print(f"Tier 1: SerpAPI {origin}→{destination} class={travel_class} ...", file=sys.stderr)
        resp = requests.get('https://serpapi.com/search.json', params=params, timeout=20)
        if resp.status_code != 200:
            print(f"Tier 1: SerpAPI HTTP {resp.status_code}", file=sys.stderr)
            return None, None

        data = resp.json()
        best = data.get('best_flights', [])
        other = data.get('other_flights', [])
        print(f"Tier 1: Got {len(best)} best + {len(other)} other flights", file=sys.stderr)
        return best, other

    except Exception as e:
        print(f"Tier 1 error: {e}", file=sys.stderr)
        return None, None


def _serpapi_search_urllib(origin, destination, depart_date, return_date, travel_class, api_key):
    """Fallback SerpAPI search using only stdlib urllib."""
    try:
        params = {
            'engine': 'google_flights',
            'departure_id': origin,
            'arrival_id': destination,
            'outbound_date': depart_date,
            'currency': 'USD',
            'hl': 'en',
            'travel_class': str(travel_class),
            'api_key': api_key,
        }
        if return_date:
            params['return_date'] = return_date
            params['type'] = '1'
        else:
            params['type'] = '2'

        url = 'https://serpapi.com/search.json?' + urllib.parse.urlencode(params)
        print(f"Tier 1: SerpAPI (urllib) {origin}→{destination} class={travel_class} ...", file=sys.stderr)

        req = urllib.request.Request(url, headers={'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode())

        best = data.get('best_flights', [])
        other = data.get('other_flights', [])
        print(f"Tier 1: Got {len(best)} best + {len(other)} other flights", file=sys.stderr)
        return best, other
    except Exception as e:
        print(f"Tier 1 urllib error: {e}", file=sys.stderr)
        return None, None


def parse_serpapi_flights(flights_list, depart_date, return_date, origin, destination):
    """
    Parse SerpAPI flight result objects into our standardised cash-price dicts.
    Each item in flights_list is a SerpAPI flight group.
    """
    parsed = []
    for group in flights_list:
        price = group.get('price')
        if not price:
            continue

        legs = group.get('flights', [])
        if not legs:
            continue

        first_leg = legs[0]
        last_leg = legs[-1]

        airline = first_leg.get('airline', 'Unknown')
        flight_number = first_leg.get('flight_number', '')
        travel_class = first_leg.get('travel_class', 'Economy')
        dep_time = first_leg.get('departure_airport', {}).get('time', '')
        arr_time = last_leg.get('arrival_airport', {}).get('time', '')
        total_duration = group.get('total_duration', 0)
        stops = len(legs) - 1

        hours = total_duration // 60
        minutes = total_duration % 60

        parsed.append({
            'price': price,
            'currency': 'USD',
            'airline': airline,
            'flight_number': flight_number,
            'travel_class': travel_class,
            'origin': origin,
            'destination': destination,
            'departure_date': depart_date,
            'return_date': return_date,
            'departure_time': dep_time,
            'arrival_time': arr_time,
            'duration': f"{hours}h {minutes}m",
            'stops': stops,
        })

    return parsed


# ---------------------------------------------------------------------------
# Tier 2 — Airline website scraping (framework — Playwright)
# ---------------------------------------------------------------------------

def tier2_airline_scrape(origin, destination, depart_date, return_date=None):
    """
    Attempt to scrape award availability from airline websites using Playwright.
    Returns a list of award result dicts, or [] if unavailable.
    
    NOTE: Airline websites actively resist scraping. This tier is structured as
    a framework; actual scraping commands would be invoked via Playwright MCP
    in the orchestrator. For CLI usage, this returns [] and logs a skip message.
    """
    results = []

    # Check if playwright is available
    try:
        playwright_check = subprocess.run(
            ['which', 'playwright'], capture_output=True, text=True, timeout=5
        )
        if playwright_check.returncode != 0:
            print("Tier 2: Playwright not found — skipping airline scraping", file=sys.stderr)
            return results
    except Exception:
        print("Tier 2: Could not check for Playwright — skipping", file=sys.stderr)
        return results

    # United.com award search
    united_results = _scrape_united_awards(origin, destination, depart_date, return_date)
    results.extend(united_results)

    return results


def _scrape_united_awards(origin, destination, depart_date, return_date=None):
    """
    Scrape united.com award search.
    Uses Playwright CLI if available; returns parsed award results.
    """
    try:
        trip_type = 'roundtrip' if return_date else 'oneway'
        url = (
            f"https://www.united.com/en/us/fop/choose-flights"
            f"?f={origin}&t={destination}&d={depart_date}"
            f"&tt=1&at=1&sc=7&px=1&taxng=1&idx=1"
        )

        print(f"Tier 2: Would scrape united.com: {url}", file=sys.stderr)
        # Playwright scraping would happen here via MCP in the orchestrator.
        # For standalone CLI, we skip and let Tier 4 handle it.
        return []

    except Exception as e:
        print(f"Tier 2 United error: {e}", file=sys.stderr)
        return []


# ---------------------------------------------------------------------------
# Tier 3 — points.me free-tier scraping
# ---------------------------------------------------------------------------

def tier3_pointsme_scrape(origin, destination, depart_date, return_date=None):
    """
    Scrape points.me for award availability.
    Returns list of award result dicts, or [].
    """
    try:
        playwright_check = subprocess.run(
            ['which', 'playwright'], capture_output=True, text=True, timeout=5
        )
        if playwright_check.returncode != 0:
            print("Tier 3: Playwright not found — skipping points.me", file=sys.stderr)
            return []
    except Exception:
        print("Tier 3: Could not check for Playwright — skipping", file=sys.stderr)
        return []

    url = (
        f"https://points.me/search?"
        f"origin={origin}&destination={destination}"
        f"&date={depart_date}&passengers=1"
    )
    print(f"Tier 3: Would scrape points.me: {url}", file=sys.stderr)
    # Playwright scraping would happen here via MCP.
    return []


# ---------------------------------------------------------------------------
# Tier 4 — Sweet spots DB estimates (fallback)
# ---------------------------------------------------------------------------

def tier4_sweet_spot_estimates(origin, destination, depart_date, return_date=None,
                               cash_prices=None):
    """
    Use our sweet spots database to generate award recommendations.
    If cash_prices are available (from Tier 1), use real cash values for CPP.
    Otherwise use the typical_cash field from the DB.
    """
    sweet_spots = get_relevant_sweet_spots(origin, destination)
    results = []

    # Find best cash price by travel class from Tier 1
    cash_by_class = {}
    if cash_prices:
        for cp in cash_prices:
            tc = cp.get('travel_class', 'Economy').lower()
            price = cp.get('price', 0)
            if tc not in cash_by_class or price < cash_by_class[tc]:
                cash_by_class[tc] = price

    for spot in sweet_spots:
        spot_class = spot.get('class', 'business').lower()
        miles = spot['miles']

        # Use real cash price if available, otherwise estimate
        if spot_class in cash_by_class:
            cash_equiv = cash_by_class[spot_class]
            source = 'serpapi-validated'
            confidence = 'high'
        elif 'business' in cash_by_class and spot_class in ('first', 'suites'):
            # Estimate first class from business price
            cash_equiv = int(cash_by_class['business'] * 1.6)
            source = 'serpapi-estimated'
            confidence = 'medium'
        elif 'economy' in cash_by_class:
            # Scale from economy
            multiplier = {'economy': 1, 'business': 3.5, 'first': 5.5, 'suites': 7, 'upper': 3.2}
            cash_equiv = int(cash_by_class['economy'] * multiplier.get(spot_class, 3))
            source = 'serpapi-estimated'
            confidence = 'medium'
        else:
            cash_equiv = spot.get('typical_cash', 5000)
            source = 'estimated'
            confidence = 'low'

        # Estimated taxes (international J/F = ~$100-300, economy = ~$50-150)
        taxes = 150 if spot_class in ('business', 'first', 'suites', 'upper') else 75

        value_per_point = round(cash_equiv / miles * 100, 2) if miles > 0 else 0

        # Build transfer partners list
        transfer_partners = _find_transfer_paths(spot['program'])

        result = {
            'program': spot['program'],
            'airline': spot['airline'],
            'class': spot_class,
            'origin': origin,
            'destination': destination,
            'route': spot.get('route', determine_route_type(origin, destination)),
            'departure_date': depart_date,
            'miles_required': miles * (2 if return_date else 1),
            'taxes_fees': taxes * (2 if return_date else 1),
            'cash_equivalent': cash_equiv * (2 if return_date else 1),
            'value_per_point': value_per_point,
            'availability': 'check-airline',
            'strategy': 'award-search',
            'booking_url': _get_booking_url(spot['program'], origin, destination, depart_date),
            'confidence': confidence,
            'source': source,
            'transfer_partners': transfer_partners,
            'notes': spot.get('notes', ''),
            'recommendation': _get_recommendation(value_per_point, source),
            'trip_type': 'round_trip' if return_date else 'one_way',
        }
        if return_date:
            result['return_date'] = return_date

        results.append(result)

    return results


# ---------------------------------------------------------------------------
# Award search orchestrator
# ---------------------------------------------------------------------------

def search_award_flights(origin, destination, depart_date, return_date=None,
                         program=None, programs=None, balances=None):
    """
    Master award search: runs tiers in order, merges results.

    Args:
        origin/destination: airport codes
        depart_date: YYYY-MM-DD
        return_date: optional YYYY-MM-DD
        program: single program filter (legacy)
        programs: list of user's programs for filtering
        balances: dict mapping program → balance (int)
    """
    all_results = []
    cash_prices = []

    # -----------------------------------------------------------------------
    # Tier 1: SerpAPI — get real cash prices for economy and business
    # -----------------------------------------------------------------------
    for travel_class, class_name in [(1, 'economy'), (3, 'business')]:
        best, other = serpapi_search(origin, destination, depart_date, return_date, travel_class)
        if best is not None:
            parsed = parse_serpapi_flights(best + (other or []), depart_date, return_date, origin, destination)
            cash_prices.extend(parsed)

    if cash_prices:
        print(f"Tier 1: {len(cash_prices)} cash price data points collected", file=sys.stderr)

    # -----------------------------------------------------------------------
    # Tier 2: Airline website scraping
    # -----------------------------------------------------------------------
    tier2_results = tier2_airline_scrape(origin, destination, depart_date, return_date)
    for r in tier2_results:
        r['source'] = 'airline-direct'
    all_results.extend(tier2_results)

    # -----------------------------------------------------------------------
    # Tier 3: points.me scraping
    # -----------------------------------------------------------------------
    tier3_results = tier3_pointsme_scrape(origin, destination, depart_date, return_date)
    for r in tier3_results:
        r['source'] = 'points-me'
    all_results.extend(tier3_results)

    # -----------------------------------------------------------------------
    # Tier 4: Sweet spots DB + cash prices from Tier 1
    # -----------------------------------------------------------------------
    tier4_results = tier4_sweet_spot_estimates(
        origin, destination, depart_date, return_date, cash_prices
    )
    all_results.extend(tier4_results)

    # -----------------------------------------------------------------------
    # Filter by program if specified
    # -----------------------------------------------------------------------
    if program:
        all_results = [r for r in all_results if r.get('program') == program]

    # -----------------------------------------------------------------------
    # If user specified programs + balances, annotate affordability
    # -----------------------------------------------------------------------
    if programs and balances:
        all_results = _annotate_user_profile(all_results, programs, balances)

    # -----------------------------------------------------------------------
    # Sort by value_per_point descending
    # -----------------------------------------------------------------------
    all_results.sort(key=lambda x: x.get('value_per_point', 0), reverse=True)

    return all_results


# ---------------------------------------------------------------------------
# User profile: filter and annotate with transfer paths + affordability
# ---------------------------------------------------------------------------

def _annotate_user_profile(results, programs, balances):
    """
    Annotate each result with whether the user can book it and how.
    programs: list of program keys like ['chase-ur', 'united']
    balances: dict like {'chase-ur': 80000, 'united': 45000}
    """
    annotated = []

    for r in results:
        r_program = r.get('program', '')
        miles_needed = r.get('miles_required', 0)

        # Find all ways the user can book this
        booking_paths = []

        for user_prog in programs:
            user_balance = balances.get(user_prog, 0)
            prog_info = TRANSFER_PARTNERS.get(user_prog, {})
            prog_partners = prog_info.get('partners', {})
            prog_name = prog_info.get('full_name', user_prog)

            # Direct match: user has this exact program
            canonical = PROGRAM_CANONICAL.get(r_program)
            if user_prog == canonical or _program_matches(user_prog, r_program):
                affordable = user_balance >= miles_needed
                booking_paths.append({
                    'source_program': user_prog,
                    'source_name': prog_name,
                    'balance': user_balance,
                    'miles_needed': miles_needed,
                    'transfer_to': None,
                    'affordable': affordable,
                    'action': f"Book directly with {prog_name}" if affordable else f"Need {miles_needed - user_balance:,} more {prog_name} miles",
                })
                continue

            # Transfer partner match
            for partner_key, partner_info in prog_partners.items():
                if _partner_matches(partner_key, r_program):
                    ratio = partner_info.get('ratio', 1)
                    points_needed = int(miles_needed / ratio)
                    affordable = user_balance >= points_needed
                    booking_paths.append({
                        'source_program': user_prog,
                        'source_name': prog_name,
                        'balance': user_balance,
                        'points_needed': points_needed,
                        'transfer_to': partner_info['name'],
                        'transfer_ratio': f"{ratio}:1",
                        'affordable': affordable,
                        'action': (
                            f"Transfer {points_needed:,} {prog_name} → {partner_info['name']}"
                            if affordable else
                            f"Need {points_needed - user_balance:,} more {prog_name} points"
                        ),
                    })

        r['booking_paths'] = booking_paths
        r['user_can_book'] = any(bp['affordable'] for bp in booking_paths)
        annotated.append(r)

    return annotated


def _program_matches(user_prog, sweet_spot_prog):
    """Check if user program matches sweet spot program."""
    mapping = {
        'united': 'united-mileageplus',
        'aa': 'american-aadvantage',
        'delta': 'delta-skymiles',
        'alaska': 'alaska-mileage-plan',
        'southwest': 'southwest-rapid-rewards',
        'chase-ur': 'chase-ultimate-rewards',
        'amex-mr': 'amex-membership-rewards',
    }
    return mapping.get(user_prog) == sweet_spot_prog


def _partner_matches(partner_key, sweet_spot_program):
    """Check if a transfer partner key matches the sweet spot's booking program."""
    # Direct name match
    if partner_key == sweet_spot_program:
        return True
    # Map sweet spot program names to partner keys
    mapping = {
        'united-mileageplus': 'united-mileageplus',
        'american-aadvantage': 'american-aadvantage',
        'delta-skymiles': 'delta-skymiles',
        'alaska-mileage-plan': 'alaska-mileage-plan',
        'british-airways-avios': 'british-airways-avios',
        'virgin-atlantic': 'virgin-atlantic',
        'aeroplan': 'aeroplan',
        'amex-membership-rewards': None,  # Not a transfer target
        'chase-ultimate-rewards': None,   # Not a transfer target
    }
    return mapping.get(sweet_spot_program) == partner_key


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_transfer_paths(program):
    """Find all flexible currencies that transfer to this program."""
    paths = []
    for src_key, src_info in TRANSFER_PARTNERS.items():
        for partner_key, partner_info in src_info.get('partners', {}).items():
            if _partner_matches(partner_key, program):
                paths.append({
                    'from': src_info['full_name'],
                    'from_key': src_key,
                    'ratio': partner_info['ratio'],
                })
    return paths


def _get_booking_url(program, origin, destination, depart_date):
    """Build booking URL for an airline program."""
    urls = {
        'united-mileageplus': f'https://www.united.com/en/us/fop/choose-flights?f={origin}&t={destination}&d={depart_date}&tt=1&at=1&sc=7&px=1&taxng=1&idx=1',
        'american-aadvantage': f'https://www.aa.com/booking/find-flights?origin={origin}&destination={destination}&departureDate={depart_date}&tripType=oneWay&passengers=1&awardBooking=true',
        'delta-skymiles': f'https://www.delta.com/flight-search/book-a-flight?tripType=oneWay&originCity={origin}&destinationCity={destination}&departureDate={depart_date}&paxCount=1&awardTravel=true',
        'alaska-mileage-plan': f'https://www.alaskaair.com/shopping/flights?origins={origin}&destinations={destination}&dates={depart_date}&awardBooking=true',
        'virgin-atlantic': f'https://www.virginatlantic.com/book/flights?origin={origin}&destination={destination}&date={depart_date}&awardBooking=true',
        'aeroplan': f'https://www.aircanada.com/aeroplan/redeem/availability/outbound?org0={origin}&dest0={destination}&departureDate0={depart_date}&ADT=1&marketCode=INT',
        'british-airways-avios': f'https://www.britishairways.com/travel/redeem/execclub?origin={origin}&destination={destination}&outboundDate={depart_date}',
        'chase-ultimate-rewards': 'https://ultimaterewards.chase.com/travel',
        'amex-membership-rewards': 'https://global.americanexpress.com/travel/home',
    }
    return urls.get(program, f'https://www.google.com/travel/flights?q={origin}+to+{destination}')


def _get_recommendation(value_per_point, source):
    """Generate recommendation text."""
    label = " (real cash price)" if 'serpapi' in source else " (estimated)"
    if value_per_point >= 3.0:
        return f"🔥 Outstanding value{label} — book with points!"
    elif value_per_point >= 2.0:
        return f"✅ Excellent value{label} — use points"
    elif value_per_point >= 1.5:
        return f"👍 Good value{label} — worth using points"
    elif value_per_point >= 1.0:
        return f"⚖️ Fair value{label} — compare with cash"
    else:
        return f"💵 Below average{label} — consider paying cash"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='Search for award flights using miles and points (real data)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s LAX NRT 2026-03-15 --pretty
  %(prog)s SFO LHR 2026-04-10 --return 2026-04-17 --pretty
  %(prog)s JFK NRT 2026-05-01 --programs chase-ur,united --balances 80000,45000 --pretty
  %(prog)s LAX CDG 2026-06-15 --program united --pretty

Data sources (tiered):
  1. SerpAPI Google Flights (real cash prices → value-per-point calc)
  2. Airline website scraping via Playwright (when available)
  3. points.me free-tier scraping via Playwright (when available)
  4. Sweet spots DB estimates (fallback, clearly labeled)
        """
    )

    parser.add_argument('origin', help='Origin airport code (e.g., LAX)')
    parser.add_argument('destination', help='Destination airport code (e.g., NRT)')
    parser.add_argument('depart_date', help='Departure date (YYYY-MM-DD)')
    parser.add_argument('--return', dest='return_date',
                        help='Return date for round trip (YYYY-MM-DD)')
    parser.add_argument('--program', choices=[
        'chase-ur', 'amex-mr', 'united', 'aa', 'delta', 'southwest',
        'alaska', 'virgin-atlantic', 'british-airways', 'aeroplan',
    ], help='Filter to a specific loyalty program')
    parser.add_argument('--programs',
                        help='Comma-separated list of programs you have (e.g., "chase-ur,united,amex-mr")')
    parser.add_argument('--balances',
                        help='Comma-separated balances matching --programs (e.g., "80000,45000,120000")')
    parser.add_argument('--pretty', action='store_true', help='Pretty print JSON output')

    args = parser.parse_args()

    # Map short program names
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
        'aeroplan': 'aeroplan',
    }
    program = program_mapping.get(args.program, args.program) if args.program else None

    # Parse user profile
    user_programs = None
    user_balances = None
    if args.programs:
        user_programs = [p.strip() for p in args.programs.split(',')]
        if args.balances:
            balance_list = [int(b.strip()) for b in args.balances.split(',')]
            user_balances = dict(zip(user_programs, balance_list))
        else:
            user_balances = {p: 0 for p in user_programs}

    try:
        results = search_award_flights(
            args.origin,
            args.destination,
            args.depart_date,
            args.return_date,
            program,
            user_programs,
            user_balances,
        )

        if args.pretty:
            print(json.dumps(results, indent=2))
        else:
            print(json.dumps(results))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
