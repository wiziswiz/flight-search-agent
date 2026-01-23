---
name: flight-search
description: Find cheapest flights using 7 strategies
allowed-tools: mcp__plugin_playwright_playwright__*
---

# Flight Search Skill

Find the cheapest flights by executing 7 money-saving strategies in parallel.

## Usage

```
/flight-search [origin] to [destination] on [dates] [options]
```

**Examples:**
- `/flight-search SFO to JFK on March 15`
- `/flight-search LAX to London on April 10-17`
- `/flight-search NYC to Tokyo on March 20 +/-3 days`
- `/flight-search BOS to Miami flexible dates in April`

### Flexible Date Search

Add `+/-N days` to check a date window and find the cheapest option:
- `+/-1` checks 3 dates (day before, target, day after)
- `+/-3` checks 7 dates (recommended for best savings)
- `flexible` or `flex` auto-expands to +/-3 days

The search returns a **date matrix** showing prices for each combination, highlighting the cheapest departure/return pair.

## Strategies

This skill runs 7 parallel strategies to find the best flight prices:

### 1. Hidden City / Skiplagging
Search for flights where your destination is a layover on a cheaper route. Can save 20-50% but requires one-way tickets and no checked bags.

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

## How It Works

1. **Parse Input** - Extract origin, destination, dates, and flexibility window
2. **Build Date Matrix** - If flexible dates specified, generate all date combinations
3. **Execute Strategies** - Run strategies in parallel across date combinations
4. **Price Comparison** - Build matrix showing price by departure/return date
5. **Aggregate Results** - Deduplicate and score by price, stops, duration, reliability
6. **Present Findings** - Show cheapest dates + top 10 results with booking links

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
