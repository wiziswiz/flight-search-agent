# Hidden Route Scanner Strategy

The hidden route scanner finds cheaper flights by exploiting airline pricing quirks: hidden city ticketing, nearby airport alternatives, and creative multi-leg combinations that standard search engines miss.

## Table of Contents

1. [Hidden City Ticketing](#hidden-city-ticketing)
2. [Nearby Airport Alternatives](#nearby-airport-alternatives)
3. [Multi-Leg Combination Discovery](#multi-leg-combination-discovery)
4. [Price Comparison Logic](#price-comparison-logic)
5. [Playwright Automation](#playwright-automation)

---

## Hidden City Ticketing

### What It Is

Hidden city ticketing means booking a flight from A→B→C but intentionally deplaning at B (your actual destination). This works when flights through a hub are cheaper than direct flights to that hub.

### When It Works

| Scenario | Example | Why Cheaper |
|----------|---------|-------------|
| Hub Premium | NYC→DEN costs $400, NYC→DEN→SLC costs $250 | Denver is a hub; connecting traffic is discounted |
| Competition Routes | ORD→MIA direct $500, ORD→MIA→Key West $280 | Competing for Florida traffic |
| Fare Class Mismatch | Direct uses expensive Y class, connection uses cheaper Q class | Inventory management quirk |

### Critical Restrictions

**DO NOT use hidden city if:**
- You have checked bags (they'll go to final destination)
- It's a round trip (return leg will be cancelled)
- You have airline status you want to protect
- The connection is on a separate ticket

### Search Pattern

```
For destination B, search:
1. Direct A→B (baseline price)
2. A→B→[major hubs within 500mi of B]
3. A→B→[popular leisure destinations beyond B]
4. Compare all prices, flag hidden city savings > 15%
```

### Best Hidden City Routes (US Examples)

| If Going To | Search Flights To | Typical Savings |
|-------------|-------------------|-----------------|
| Denver (DEN) | Salt Lake City, Albuquerque | 20-35% |
| Atlanta (ATL) | Florida cities, New Orleans | 15-30% |
| Dallas (DFW) | Austin, San Antonio | 20-40% |
| Chicago (ORD) | Milwaukee, Indianapolis | 15-25% |
| Charlotte (CLT) | Charleston, Raleigh | 20-35% |

---

## Nearby Airport Alternatives

### Search Radius Guidelines

| Origin Type | Search Radius | Examples |
|-------------|---------------|----------|
| Major Metro | 100 miles | NYC: JFK, LGA, EWR, HPN, ISP |
| Medium City | 75 miles | Boston: BOS, PVD, MHT |
| Small City | 150 miles | May need to drive to larger hub |

### Major Metro Airport Groups

```
New York Area: JFK, LGA, EWR, HPN (White Plains), ISP (Long Island)
Los Angeles: LAX, BUR, SNA, ONT, LGB
San Francisco: SFO, OAK, SJC
Chicago: ORD, MDW
Washington DC: DCA, IAD, BWI
London: LHR, LGW, STN, LTN, LCY
Paris: CDG, ORY, BVA
Tokyo: NRT, HND
```

### Cost-Benefit Calculation

```
Total Cost = Flight Price + Ground Transport + Time Value

Ground Transport Estimates:
- Uber/taxi: $2-3 per mile
- Rental car + parking: ~$50-100/day
- Train/bus: varies by route

Time Value (suggested):
- Business traveler: $50-100/hour
- Leisure traveler: $10-25/hour
```

### When Alternate Airports Win

1. **Budget carrier presence**: Spirit at FLL vs AA at MIA
2. **Less congestion fees**: Smaller airports have lower landing fees
3. **Different hub dynamics**: Southwest dominance at MDW vs United at ORD
4. **International routing**: Different codeshare options

---

## Multi-Leg Combination Discovery

### Self-Connect Strategy

Book separate tickets on different airlines when:
- No single airline flies the route
- Combining sales from different carriers
- Using positioning flights to cheaper hubs

### Minimum Connection Times

| Connection Type | Domestic | International |
|-----------------|----------|---------------|
| Same terminal | 1.5 hours | 2.5 hours |
| Different terminal | 2 hours | 3 hours |
| Different airport | 4+ hours | Not recommended |

### Positioning Flight Patterns

```
Example: NYC to Bali

Traditional: JFK→Singapore→Bali on Singapore Air = $1,800

Multi-leg alternative:
1. JFK→LAX on Southwest (cheap domestic) = $150
2. LAX→Taipei→Bali on China Airlines = $800
Total = $950 (47% savings)
```

### Risk Mitigation for Self-Connects

- Book refundable first leg when possible
- Add 4+ hours between separate tickets
- Have backup flight options identified
- Consider travel insurance for missed connections

---

## Price Comparison Logic

### Normalization Algorithm

```python
def normalize_price(price, currency, base_currency="USD"):
    """Convert all prices to common currency for comparison"""
    rate = get_exchange_rate(currency, base_currency)
    return price * rate

def calculate_true_cost(flight):
    """Include hidden costs in comparison"""
    base = flight.price
    bags = estimate_bag_fees(flight.airline, flight.route)
    seat = estimate_seat_selection(flight.airline)
    ground = estimate_ground_transport(flight.airports)
    return base + bags + seat + ground
```

### Scoring Matrix

| Factor | Weight | Scoring |
|--------|--------|---------|
| Price | 40% | Lower is better |
| Duration | 20% | Shorter is better |
| Stops | 15% | Fewer is better |
| Departure time | 10% | Preference-based |
| Airline quality | 10% | Rating-based |
| Risk level | 5% | Lower risk preferred |

### Output Format

```json
{
  "baseline": {
    "route": "JFK → DEN",
    "price": 450,
    "duration": "4h 30m"
  },
  "alternatives": [
    {
      "type": "hidden_city",
      "route": "JFK → DEN → SLC",
      "price": 285,
      "savings": "37%",
      "risk": "medium",
      "warnings": ["No checked bags", "One-way only"]
    },
    {
      "type": "nearby_airport",
      "route": "EWR → DEN",
      "price": 380,
      "savings": "16%",
      "risk": "low",
      "notes": ["Add $40 ground transport"]
    }
  ]
}
```

---

## Playwright Automation

### Google Flights Search

```javascript
// Navigate to Google Flights
await page.goto('https://www.google.com/travel/flights');

// Enter origin
await page.click('[aria-label="Where from?"]');
await page.fill('input[aria-label="Where from?"]', origin);
await page.keyboard.press('Enter');

// Enter destination
await page.click('[aria-label="Where to?"]');
await page.fill('input[aria-label="Where to?"]', destination);
await page.keyboard.press('Enter');

// Select dates
await page.click('[aria-label="Departure"]');
await page.fill('input[placeholder="Departure"]', departDate);
await page.keyboard.press('Enter');

// Wait for results
await page.waitForSelector('[data-price]', { timeout: 15000 });

// Extract prices using locator
const flightElements = await page.locator('[data-price]').all();
const flights = [];
for (const el of flightElements) {
  flights.push({
    price: await el.getAttribute('data-price'),
    airline: await el.locator('.airline-name').textContent(),
    duration: await el.locator('.duration').textContent()
  });
}
```

### Skiplagged Search

```javascript
// Navigate to Skiplagged
await page.goto('https://skiplagged.com/flights/' +
  `${origin}/${destination}/${departDate}`);

// Wait for hidden city results
await page.waitForSelector('.trip-row', { timeout: 20000 });

// Extract hidden city options using locator
const rows = await page.locator('.trip-row').all();
const hiddenCity = [];
for (const row of rows) {
  const classList = await row.getAttribute('class');
  hiddenCity.push({
    price: await row.locator('.price').textContent(),
    route: await row.locator('.route').textContent(),
    type: classList.includes('hidden-city') ? 'hidden_city' : 'direct'
  });
}
```

### Multi-Airport Search Loop

```javascript
async function searchNearbyAirports(origin, destination, date, radius = 100) {
  const nearbyOrigins = await getNearbyAirports(origin, radius);
  const nearbyDests = await getNearbyAirports(destination, radius);

  const results = [];

  for (const org of nearbyOrigins) {
    for (const dest of nearbyDests) {
      const flights = await searchFlights(org, dest, date);
      results.push(...flights.map(f => ({
        ...f,
        originalOrigin: origin,
        originalDest: destination,
        actualOrigin: org,
        actualDest: dest
      })));
    }
  }

  return results.sort((a, b) => a.price - b.price);
}
```

### Rate Limiting Protection

```javascript
const SEARCH_DELAYS = {
  'google.com': 3000,      // 3 seconds between searches
  'skiplagged.com': 5000,  // 5 seconds (more aggressive detection)
  'kayak.com': 4000        // 4 seconds
};

async function rateLimitedSearch(url, site) {
  await delay(SEARCH_DELAYS[site] || 3000);
  return page.goto(url);
}
```

---

## Strategy Execution Flow

```
1. Input: origin, destination, dates
2. Get nearby airports (100mi radius)
3. Parallel searches:
   a. Direct baseline price (Google Flights)
   b. Hidden city via Skiplagged
   c. All nearby airport combinations
4. Normalize all prices to base currency
5. Calculate true cost (+ bags, transport)
6. Rank by total value score
7. Return top 5 options with warnings
```

## Warnings and Disclaimers

- Hidden city ticketing may violate airline terms of service
- Airlines can cancel return flights if you skip a segment
- Frequent flyer miles may be forfeited
- Some airlines have sued Skiplagged (it's still legal for consumers)
- Always verify current airline policies before booking
