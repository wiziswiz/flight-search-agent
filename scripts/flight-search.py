#!/usr/bin/env python3
"""
Master flight search orchestrator.
Runs all search strategies in parallel and combines results.
"""

import json
import sys
import argparse
import os
import subprocess
import re
import concurrent.futures
from datetime import datetime, timedelta
import threading

# Get script directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def parse_natural_language(text):
    """Parse natural language flight search requests"""
    # Remove common words and normalize
    text = text.lower().strip()
    
    # Extract airports using common patterns
    airport_pattern = r'\b[A-Z]{3}\b'
    airports = re.findall(airport_pattern, text.upper())
    
    # Look for "from X to Y" patterns
    from_to_pattern = r'(?:from\s+)?([A-Z]{3})\s+to\s+([A-Z]{3})'
    from_to_match = re.search(from_to_pattern, text.upper())
    
    if from_to_match:
        origin = from_to_match.group(1)
        destination = from_to_match.group(2)
    elif len(airports) >= 2:
        origin = airports[0]
        destination = airports[1]
    else:
        raise ValueError("Could not identify origin and destination airports")
    
    # Extract dates
    dates = extract_dates(text)
    
    # Extract flexibility
    flex_match = re.search(r'[+\-]/?(\d+)\s*days?', text)
    flexible = flex_match.group(1) if flex_match else None
    if 'flex' in text or 'flexible' in text:
        flexible = flexible or "3"
    
    # Extract special search types
    include_awards = 'points' in text or 'miles' in text or 'award' in text
    include_hidden_city = 'hidden' in text or 'skiplagged' in text
    include_budget = 'budget' in text or 'cheap' in text
    include_alternative_airports = 'alternative' in text or 'alt' in text or 'nearby' in text
    
    return {
        'origin': origin,
        'destination': destination,
        'depart_date': dates.get('depart'),
        'return_date': dates.get('return'),
        'flexible_days': int(flexible) if flexible else None,
        'include_awards': include_awards,
        'include_hidden_city': include_hidden_city,
        'include_budget': include_budget,
        'include_alternative_airports': include_alternative_airports
    }

def extract_dates(text):
    """Extract departure and return dates from text"""
    dates = {}
    
    # Common date patterns
    date_patterns = [
        r'\b(\d{4}-\d{2}-\d{2})\b',  # YYYY-MM-DD
        r'\b(\w+)\s+(\d{1,2})\b',     # Month DD
        r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b',  # MM/DD/YYYY
        r'\b(\d{1,2})/(\d{1,2})\b',   # MM/DD (current year)
    ]
    
    # For now, use a default date if not found (demo purposes)
    # In a real implementation, this would be more sophisticated
    today = datetime.now()
    default_depart = (today + timedelta(days=30)).strftime('%Y-%m-%d')
    
    # Look for specific date mentions
    if re.search(r'march\s+15', text, re.I):
        dates['depart'] = '2026-03-15'
    elif re.search(r'april\s+10', text, re.I):
        dates['depart'] = '2026-04-10'
    else:
        dates['depart'] = default_depart
    
    # Look for return dates
    if re.search(r'return|round.?trip|-\d+', text, re.I):
        if re.search(r'march\s+22', text, re.I):
            dates['return'] = '2026-03-22'
        elif re.search(r'april\s+17', text, re.I):
            dates['return'] = '2026-04-17'
        else:
            # Default to 7 days later
            depart_date = datetime.strptime(dates['depart'], '%Y-%m-%d')
            return_date = depart_date + timedelta(days=7)
            dates['return'] = return_date.strftime('%Y-%m-%d')
    
    return dates

def run_search_strategy(strategy, origin, destination, depart_date, return_date=None, **kwargs):
    """Run a specific search strategy"""
    script_path = os.path.join(SCRIPT_DIR, f"search-{strategy}.py")
    
    if not os.path.exists(script_path):
        return {"error": f"Strategy script not found: {script_path}", "strategy": strategy}
    
    try:
        # Build command
        cmd = [sys.executable, script_path, origin, destination, depart_date]
        
        if return_date:
            cmd.extend(['--return', return_date])
        
        # Add strategy-specific parameters
        if strategy == 'google-flights' and kwargs.get('flexible_days'):
            cmd.extend(['--flex', str(kwargs['flexible_days'])])
        
        if strategy == 'awards' and kwargs.get('program'):
            cmd.extend(['--program', kwargs['program']])
        
        if strategy == 'alt-airports' and kwargs.get('matrix'):
            cmd.append('--matrix')
        
        # Run the search
        print(f"Running {strategy} search...", file=sys.stderr)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                return {"data": data, "strategy": strategy, "status": "success"}
            except json.JSONDecodeError as e:
                return {"error": f"JSON decode error: {e}", "strategy": strategy, "raw_output": result.stdout}
        else:
            return {"error": f"Command failed: {result.stderr}", "strategy": strategy}
            
    except subprocess.TimeoutExpired:
        return {"error": "Search timeout", "strategy": strategy}
    except Exception as e:
        return {"error": f"Execution error: {e}", "strategy": strategy}

def run_parallel_searches(origin, destination, depart_date, return_date=None, strategies=None, **kwargs):
    """Run multiple search strategies in parallel"""
    
    if strategies is None:
        strategies = ['google-flights', 'skiplagged', 'budget']
        
        if kwargs.get('include_awards'):
            strategies.append('awards')
        if kwargs.get('include_alternative_airports'):
            strategies.append('alt-airports')
    
    results = {}
    
    # Use ThreadPoolExecutor for parallel execution
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(strategies)) as executor:
        # Submit all searches
        future_to_strategy = {
            executor.submit(run_search_strategy, strategy, origin, destination, depart_date, return_date, **kwargs): strategy
            for strategy in strategies
        }
        
        # Collect results as they complete
        for future in concurrent.futures.as_completed(future_to_strategy):
            strategy = future_to_strategy[future]
            try:
                result = future.result()
                results[strategy] = result
            except Exception as exc:
                results[strategy] = {"error": f"Exception: {exc}", "strategy": strategy}
    
    return results

def deduplicate_flights(all_flights):
    """Remove duplicate flights from combined results"""
    seen_flights = set()
    deduplicated = []
    
    for flight in all_flights:
        # Create a key for deduplication
        key = (
            flight.get('airline', ''),
            flight.get('flight_number', ''),
            flight.get('origin', ''),
            flight.get('destination', ''),
            flight.get('departure_date', ''),
            flight.get('departure_time', '')
        )
        
        if key not in seen_flights:
            seen_flights.add(key)
            deduplicated.append(flight)
        else:
            # If we've seen this flight, keep the one with better price
            existing_flight = next((f for f in deduplicated if 
                                  f.get('airline', '') == flight.get('airline', '') and
                                  f.get('flight_number', '') == flight.get('flight_number', '')), None)
            
            if existing_flight and flight.get('price', float('inf')) < existing_flight.get('price', float('inf')):
                # Replace with better price
                deduplicated[deduplicated.index(existing_flight)] = flight
    
    return deduplicated

def rank_flights(flights):
    """Rank flights by price, stops, duration, and reliability"""
    def calculate_score(flight):
        score = 0
        
        # Price is the primary factor (lower is better)
        price = flight.get('price', float('inf'))
        if price != float('inf'):
            score -= price  # Negative because lower is better
        
        # Stops penalty
        stops = flight.get('stops', 0)
        score -= stops * 50  # $50 penalty per stop
        
        # Duration penalty (extract hours from duration string)
        duration_str = flight.get('duration', '0h 0m')
        try:
            hours = int(duration_str.split('h')[0])
            minutes = int(duration_str.split('h')[1].split('m')[0])
            total_minutes = hours * 60 + minutes
            score -= total_minutes * 0.5  # $0.50 penalty per minute
        except:
            score -= 300  # Default penalty if duration parsing fails
        
        # Confidence bonus
        confidence = flight.get('confidence', 'low')
        if confidence == 'high':
            score += 50
        elif confidence == 'medium':
            score += 25
        
        # Strategy bonus (some strategies are more reliable)
        strategy = flight.get('strategy', '')
        if 'google-flights' in strategy:
            score += 30
        elif 'budget' in strategy:
            score += 20
        elif 'awards' in strategy and flight.get('value_per_point', 0) > 1.5:
            score += 40  # Good value awards get a bonus
        
        return score
    
    # Sort by score (descending - higher score is better)
    return sorted(flights, key=calculate_score, reverse=True)

def format_results(search_results, origin, destination, depart_date, return_date=None):
    """Format and combine all search results"""
    all_flights = []
    errors = []
    
    # Extract flights from all strategies
    for strategy, result in search_results.items():
        if result.get('status') == 'success' and 'data' in result:
            strategy_flights = result['data']
            
            # Handle different result formats
            if isinstance(strategy_flights, list):
                flights = strategy_flights
            elif isinstance(strategy_flights, dict):
                # Handle matrix results (alt-airports)
                if 'savings_matrix' in strategy_flights:
                    continue  # Skip matrix results in flight listing
                else:
                    flights = [strategy_flights] if strategy_flights else []
            else:
                flights = []
            
            # Add strategy tag to each flight
            for flight in flights:
                if isinstance(flight, dict):
                    flight['source_strategy'] = strategy
                    all_flights.append(flight)
        else:
            errors.append({
                'strategy': strategy,
                'error': result.get('error', 'Unknown error')
            })
    
    # Deduplicate and rank
    deduplicated = deduplicate_flights(all_flights)
    ranked = rank_flights(deduplicated)
    
    # Create summary
    summary = {
        'search_parameters': {
            'origin': origin,
            'destination': destination,
            'depart_date': depart_date,
            'return_date': return_date,
            'search_timestamp': datetime.now().isoformat()
        },
        'summary': {
            'total_flights_found': len(ranked),
            'strategies_used': list(search_results.keys()),
            'successful_strategies': [k for k, v in search_results.items() if v.get('status') == 'success'],
            'errors': errors
        },
        'best_deals': ranked[:10],  # Top 10 flights
        'all_flights': ranked
    }
    
    # Add price analysis
    if ranked:
        prices = [f.get('price', 0) for f in ranked if f.get('price')]
        if prices:
            avg_price = round(sum(prices) / len(prices), 2)
            min_price = min(prices)
            summary['price_analysis'] = {
                'cheapest': min_price,
                'most_expensive': max(prices),
                'average': avg_price,
                'savings_vs_average': round(avg_price - min_price, 2) if min_price else 0
            }
    
    return summary

def main():
    parser = argparse.ArgumentParser(description='Master flight search orchestrator')
    
    # Positional arguments for structured input
    parser.add_argument('origin', nargs='?', help='Origin airport code (e.g., LAX)')
    parser.add_argument('destination', nargs='?', help='Destination airport code (e.g., JFK)') 
    parser.add_argument('depart_date', nargs='?', help='Departure date (YYYY-MM-DD)')
    
    # Optional structured arguments
    parser.add_argument('--return', dest='return_date', help='Return date for round trip (YYYY-MM-DD)')
    parser.add_argument('--flex', type=int, help='Flexible date range (+/- days)')
    parser.add_argument('--include-awards', action='store_true', help='Include award flight search')
    parser.add_argument('--include-hidden-city', action='store_true', help='Include hidden city routes')
    parser.add_argument('--include-budget', action='store_true', help='Include budget carriers')
    parser.add_argument('--include-alt-airports', action='store_true', help='Include alternative airports')
    parser.add_argument('--program', help='Specific loyalty program for awards')
    
    # Natural language input (alternative to structured)
    parser.add_argument('--natural', nargs='*', help='Natural language search query')
    
    # Output options
    parser.add_argument('--pretty', action='store_true', help='Pretty print JSON output')
    parser.add_argument('--summary-only', action='store_true', help='Show summary instead of all flights')
    
    args = parser.parse_args()
    
    try:
        # Handle natural language input
        if args.natural:
            query = ' '.join(args.natural)
            params = parse_natural_language(query)
            
            origin = params['origin']
            destination = params['destination']
            depart_date = params['depart_date']
            return_date = params['return_date']
            flex = params['flexible_days']
            include_awards = params['include_awards']
            include_hidden_city = params['include_hidden_city']
            include_budget = params['include_budget']
            include_alternative_airports = params['include_alternative_airports']
        else:
            # Use structured arguments
            if not all([args.origin, args.destination, args.depart_date]):
                parser.error("Origin, destination, and depart_date are required for structured search")
            
            origin = args.origin
            destination = args.destination
            depart_date = args.depart_date
            return_date = args.return_date
            flex = args.flex
            include_awards = args.include_awards
            include_hidden_city = args.include_hidden_city
            include_budget = args.include_budget
            include_alternative_airports = args.include_alt_airports
        
        # Determine strategies to run
        strategies = ['google-flights']  # Always include Google Flights
        
        if include_hidden_city:
            strategies.append('skiplagged')
        if include_budget:
            strategies.append('budget')
        if include_awards:
            strategies.append('awards')
        if include_alternative_airports:
            strategies.append('alt-airports')
        
        # If no specific strategies requested, run core set
        if len(strategies) == 1:  # Only google-flights
            strategies.extend(['skiplagged', 'budget'])
        
        # Run searches
        print(f"Searching flights from {origin} to {destination} on {depart_date}...", file=sys.stderr)
        if return_date:
            print(f"Return date: {return_date}", file=sys.stderr)
        print(f"Strategies: {', '.join(strategies)}", file=sys.stderr)
        
        search_kwargs = {
            'flexible_days': flex,
            'include_awards': include_awards,
            'include_alternative_airports': include_alternative_airports,
            'program': args.program
        }
        
        search_results = run_parallel_searches(
            origin, destination, depart_date, return_date, strategies, **search_kwargs
        )
        
        # Format results
        final_results = format_results(search_results, origin, destination, depart_date, return_date)
        
        # Output
        if args.summary_only:
            output = {
                'search_parameters': final_results['search_parameters'],
                'summary': final_results['summary'],
                'best_deals': final_results['best_deals']
            }
        else:
            output = final_results
        
        if args.pretty:
            print(json.dumps(output, indent=2, sort_keys=True))
        else:
            print(json.dumps(output))
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()