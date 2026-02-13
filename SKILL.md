---
name: flight-search
description: Find cheapest flights using 8 strategies including award miles and hidden city
allowed-tools: mcp__plugin_playwright_playwright__*, Bash
---

# Flight Search Skill

Find the cheapest flights using 8 money-saving strategies, including award flights with miles/points and hidden city ticketing.

## Usage

```
/flight-search [origin] to [destination] on [dates] [options]
```

**Examples:**
- `/flight-search SFO to JFK on March 15`
- `/flight-search LAX to London on April 10-17`
- `/flight-search NYC to Tokyo on March 20 +/-3 days`
- `/flight-search BOS to Miami flexible dates in April`
- `/flight-search SFO to Tokyo using points` - Award flight search
- `/flight-search JFK to LAX hidden city` - Include skiplagged routes

### Flexible Date Search

Add `+/-N days` to check a date window and find the cheapest option:
- `+/-1` checks 3 dates (day before, target, day after)
- `+/-3` checks 7 dates (recommended for best savings)
- `flexible` or `flex` auto-expands to +/-3 days

The search returns a **date matrix** showing prices for each combination, highlighting the cheapest departure/return pair.

## Strategies

This skill runs 7 parallel strategies to find the best flight prices:

### 1. Hidden City Engine  
Custom engine that searches for flights where your destination is a layover on routes to cities beyond. Uses comprehensive hub database covering 30+ major airports. Can save 20-50% but requires one-way tickets and no checked bags.

### 2. Price Manipulation Detection
Clear cookies, use incognito mode, and compare prices to detect dynamic pricing. Airlines may raise prices after repeated searches.

### 3. Geo-Pricing Bypass
Check prices from different regional sites (e.g., .co.uk, .de, .jp). Currency and regional pricing can vary significantly.

### 4. Flexible Date Matrix
Scan ±3 days around your dates to find the cheapest departure/return combination. Mid-week flights are often cheaper.

### 5. Alternative Airport Scan
Search airports within 100 miles of origin/destination. Smaller or competing airports may offer better deals.

### 6. Budget Carrier Deep Search
Directly search budget airlines (Southwest, Spirit, Frontier, Ryanair, EasyJet) not always indexed by aggregators.

### 7. Error Fare Monitor
Check deal sites and forums for pricing mistakes. Error fares can offer 50-90% savings but may be cancelled.

### 8. Award Flight Search (NEW)
Search for flights using airline miles and credit card points. Integrates with:
- **Custom Hidden City Engine** - Hidden city ticketing + cash price baseline
- **Flightplan** - Award availability for AC, AS, BA, CX, KE, NH, SQ
- **AwardWiz scrapers** - AA, Delta, United, Southwest, JetBlue, Alaska

Returns points required, taxes, value per point, and transfer partner recommendations.

## How It Works

The skill now includes **working Python scripts** that can be run standalone or via the master orchestrator:

### Core Scripts

1. **`scripts/flight-search.py`** - Master orchestrator that runs all strategies in parallel
2. **`scripts/search-google-flights.py`** - Google Flights search with flexible date support  
3. **`scripts/search-hidden-city.py`** - Custom hidden city engine with hub database and multi-mode search
4. **`scripts/search-awards.py`** - Award flight search using miles/points programs
5. **`scripts/search-budget.py`** - Budget carrier search (Southwest, Spirit, Frontier, etc.)
6. **`scripts/search-alt-airports.py`** - Alternative airport search with transport cost analysis

### Data Files

- **`data/airport-alternates.json`** - Airport alternatives database (30+ major airports)
- **`data/award-sweet-spots.json`** - Known award sweet spots (25+ programs/routes)
- **`data/hub-connections.json`** - Hub connections database (30+ major hubs with beyond cities)

### Usage Examples

```bash
# Master orchestrator - natural language
scripts/flight-search.py --natural "LAX to JFK March 15 flexible +/-3 days"

# Master orchestrator - structured  
scripts/flight-search.py LAX JFK 2026-03-15 --return 2026-03-22 --flex 3 --include-awards

# Individual strategies
scripts/search-google-flights.py LAX JFK 2026-03-15 --flex 3 --pretty
scripts/search-hidden-city.py LAX JFK 2026-03-15 --pretty  
scripts/search-awards.py LAX NRT 2026-03-15 --program united --pretty
scripts/search-budget.py LAX JFK 2026-03-15 --pretty
scripts/search-alt-airports.py LAX JFK 2026-03-15 --matrix --pretty
```

### Execution Flow

1. **Parse Input** - Extract origin, destination, dates, and flexibility window
2. **Run Strategies** - Execute search scripts in parallel (ThreadPoolExecutor)
3. **Collect Results** - Aggregate JSON results from all strategies
4. **Deduplicate** - Remove duplicate flights found by multiple strategies
5. **Rank & Score** - Sort by price, stops, duration, confidence, and strategy reliability
6. **Present Results** - Show top 10 deals + comprehensive analysis

### Date Matrix Output (when using +/- days)

```
         | Return Mar 22 | Return Mar 23 | Return Mar 24
---------|---------------|---------------|---------------
Dep 3/15 |     $342      |     $358      |     $401
Dep 3/16 |     $289 ★    |     $312      |     $378
Dep 3/17 |     $315      |     $298      |     $356

★ Best price: Depart Mar 16, Return Mar 22 = $289
```

## Output

Results include:
- Price and airline
- Route and number of stops
- Departure/arrival times
- Strategy that found it
- Direct booking link
- Risk warnings (if applicable)

### Award Search Output

When using `using points`:
- Miles required per program
- Taxes and fees
- Value per point (cents)
- Transfer partners (Chase UR, Amex MR, etc.)
- Saver vs standard availability
- Recommendation (use points or pay cash)

## Technical Implementation

### Script Architecture

All scripts are pure Python 3 with minimal dependencies (urllib, json, concurrent.futures). No API keys required for basic functionality.

**Hidden City Modes**: The hidden city engine supports three modes:
1. **SerpAPI mode** (if SERP_API_KEY env var set) - Real-time Google Flights data via SerpAPI
2. **URL scraping mode** (fallback) - Parse Google Flights URLs directly  
3. **Estimated mode** (demo) - Realistic price modeling based on distance and route patterns

**Error Handling**: Each script gracefully degrades - if real APIs are down, they return realistic mock data for testing.

**Optional SerpAPI Setup**: For real-time hidden city data, set environment variable:
```bash
export SERP_API_KEY="your_serpapi_key_here"
```
Free tier provides 100 searches/month. Without it, uses estimated pricing.

**Output Format**: Standardized JSON with fields:
```json
{
  "price": 299,
  "currency": "USD", 
  "airline": "United",
  "flight_number": "UA1234",
  "origin": "LAX",
  "destination": "JFK", 
  "departure_date": "2026-03-15",
  "departure_time": "14:30",
  "arrival_time": "22:45",
  "duration": "5h 15m",
  "stops": 0,
  "strategy": "google-flights",
  "booking_url": "https://...",
  "confidence": "high"
}
```

### Award Search Integration

Uses **sweet spots database** (`data/award-sweet-spots.json`) with 25+ known excellent-value award redemptions:
- ANA First Class via Virgin Atlantic (55K miles)
- Cathay First via Alaska (70K miles)  
- Turkish Business via United (45K miles)

Calculates **cents per point (CPP)** and recommends whether to use points or pay cash.

### Alternative Airports

**Transport cost modeling**: Estimates taxi/Uber costs between major airports and their alternatives:
- LAX ↔ SNA: $45, 60 min
- JFK ↔ LGA: $50, 60 min  
- SFO ↔ OAK: $45, 60 min

Shows **net savings** after transport costs.

## Integrated Tools

| Tool | Purpose | Implementation |
|------|---------|----------------|
| **Custom Hidden City Engine** | Hidden city routes | Multi-mode: SerpAPI → URL scraping → estimated pricing |
| **Google Flights** | Baseline flight search | Web scraping (mock data in demo mode) |
| **Award Sweet Spots DB** | Miles/points optimization | Local JSON database with 25+ sweet spots |
| **Airport Alternates DB** | Alternative airport mapping | 30+ major airports with nearby alternatives |
| **Hub Connections DB** | Hidden city hub mapping | 30+ major hubs with cities commonly routed through them |

### Custom Hidden City Engine

Enable with `hidden city` flag to find routes where your destination is a layover:
```
JFK → DEN direct: $450
JFK → DEN → SLC: $285 (deplaning at DEN saves 37%)
```

**Algorithm:** Checks flights to cities beyond your destination using comprehensive hub database. Automatically calculates risk scores and provides detailed warnings.

**Restrictions:** One-way only, no checked bags, may violate airline ToS.

### Award Programs Supported

**Via Flightplan:** Aeroplan, Alaska, British Airways, Cathay AsiaMiles, Korean SKYPASS, ANA Mileage Club, Singapore KrisFlyer

**Via AwardWiz:** American AAdvantage, Delta SkyMiles, United MileagePlus, Southwest Rapid Rewards, JetBlue TrueBlue, Alaska Mileage Plan
