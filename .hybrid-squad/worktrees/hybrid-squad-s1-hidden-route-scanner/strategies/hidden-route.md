# Hidden Route Scanner Strategy

A comprehensive guide for discovering alternative flight pricing through hidden city ticketing, nearby airports, multi-leg combinations, and automated search techniques.

## Table of Contents

1. [Hidden City Ticketing](#hidden-city-ticketing)
2. [Nearby Airport Discovery](#nearby-airport-discovery)
3. [Multi-Leg Combination Discovery](#multi-leg-combination-discovery)
4. [Price Comparison Logic](#price-comparison-logic)
5. [Playwright Automation](#playwright-automation)
6. [Risk Assessment & Limitations](#risk-assessment--limitations)

---

## Hidden City Ticketing

### Concept Overview

Hidden city ticketing (also known as "skiplagging") exploits airline pricing inefficiencies where a connecting flight through your desired destination costs less than a direct flight to that destination.

**Example:**
- Desired route: New York (JFK) → Chicago (ORD)
- Direct flight price: $450
- Hidden city route: New York (JFK) → Chicago (ORD) → Denver (DEN): $280
- **Savings: $170** by deplaning at Chicago and skipping the Denver leg

### How It Works

Airlines price routes based on demand, competition, and market dynamics—not distance. Hub cities with heavy competition often have inflated direct prices, while connecting flights through those hubs may be cheaper.

```
Origin (A) ──────────────────────> Final Destination (C)
                                        $450

Origin (A) ────> Target City (B) ────> Throwaway (C)
           Leg 1              Leg 2
                      $280 total
```

### Discovery Algorithm

```javascript
async function findHiddenCityRoutes(origin, destination, date) {
  const routes = [];

  // 1. Get list of common connecting destinations beyond target
  const potentialThrowaways = await getCommonDestinationsBeyond(destination);

  // 2. Search for flights from origin through destination to each throwaway
  for (const throwaway of potentialThrowaways) {
    const connectingFlights = await searchConnectingFlights({
      from: origin,
      via: destination,  // This is where we actually want to go
      to: throwaway,     // We'll skip this leg
      date: date
    });

    // 3. Filter to flights that actually stop at our destination
    const validRoutes = connectingFlights.filter(flight =>
      flight.layovers.some(layover => layover.airport === destination)
    );

    routes.push(...validRoutes);
  }

  // 4. Get direct flight price for comparison
  const directPrice = await getDirectFlightPrice(origin, destination, date);

  // 5. Return routes cheaper than direct
  return routes
    .filter(route => route.price < directPrice)
    .sort((a, b) => a.price - b.price);
}
```

### Best Throwaway Destinations

Effective throwaway cities are typically:
- **Beyond major hubs** (flights continue past the hub)
- **Lower demand markets** (keeps overall price down)
- **Same airline network** (ensures routing through desired hub)

**Common patterns by hub:**

| Hub (Target) | Good Throwaway Destinations |
|--------------|----------------------------|
| Chicago ORD | Denver, Phoenix, Las Vegas, Salt Lake City |
| Atlanta ATL | New Orleans, Jacksonville, Birmingham, Memphis |
| Dallas DFW | Austin, San Antonio, Albuquerque, Oklahoma City |
| Denver DEN | Salt Lake City, Boise, Albuquerque, Colorado Springs |
| Los Angeles LAX | San Diego, Phoenix, Las Vegas, Tucson |
| New York JFK/EWR | Boston, Philadelphia, Washington DC, Hartford |
| San Francisco SFO | San Jose, Sacramento, Portland, Seattle |
| Miami MIA | Tampa, Orlando, Fort Lauderdale, Jacksonville |

### Skiplagged Integration

[Skiplagged](https://skiplagged.com) specializes in finding hidden city routes automatically.

**API-like Search Pattern:**
```javascript
const skiplaggedSearch = {
  baseUrl: 'https://skiplagged.com/flights',
  buildUrl: (origin, dest, date) =>
    `${baseUrl}/${origin}/${dest}/${date}`,

  // Skiplagged returns both direct and hidden city options
  parseResults: (html) => {
    // Results include:
    // - "true destination" routes (hidden city)
    // - Standard direct routes for comparison
  }
};
```

### Critical Rules for Hidden City Tickets

| Rule | Reason |
|------|--------|
| **One-way only** | Return flights get cancelled if outbound isn't completed |
| **Carry-on only** | Checked bags continue to ticketed destination |
| **No frequent flyer** | Airlines may revoke status/miles for skiplagging |
| **Book infrequently** | Repeated patterns can trigger account flags |
| **First leg only** | Never works for second leg of round trip |
| **Non-refundable OK** | You won't need to modify anyway |

---

## Nearby Airport Discovery

### Concept Overview

Major metropolitan areas often have multiple airports with significantly different pricing. Searching nearby alternatives can yield substantial savings.

### Haversine Distance Calculation

Calculate distance between coordinates to find airports within radius:

```javascript
function haversineDistance(lat1, lon1, lat2, lon2) {
  const R = 3959; // Earth's radius in miles
  const dLat = toRadians(lat2 - lat1);
  const dLon = toRadians(lon2 - lon1);

  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(toRadians(lat1)) * Math.cos(toRadians(lat2)) *
            Math.sin(dLon / 2) * Math.sin(dLon / 2);

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c; // Distance in miles
}

function toRadians(degrees) {
  return degrees * (Math.PI / 180);
}

function findNearbyAirports(targetAirport, allAirports, radiusMiles = 100) {
  const target = getAirportCoordinates(targetAirport);

  return allAirports
    .map(airport => ({
      ...airport,
      distance: haversineDistance(
        target.lat, target.lon,
        airport.lat, airport.lon
      )
    }))
    .filter(airport => airport.distance <= radiusMiles)
    .sort((a, b) => a.distance - b.distance);
}
```

### Major Metro Area Airport Clusters

**New York Area (100mi radius)**
| Airport | Code | Distance from JFK | Notes |
|---------|------|-------------------|-------|
| JFK International | JFK | 0 mi | Primary international |
| LaGuardia | LGA | 8 mi | Domestic focus |
| Newark | EWR | 23 mi | United hub |
| Westchester County | HPN | 35 mi | Less crowded alternative |
| Long Island MacArthur | ISP | 47 mi | Southwest hub |
| Stewart | SWF | 65 mi | Budget carriers |
| Trenton-Mercer | TTN | 70 mi | Frontier hub |
| Philadelphia | PHL | 95 mi | American hub |

**Los Angeles Area (100mi radius)**
| Airport | Code | Distance from LAX | Notes |
|---------|------|-------------------|-------|
| LAX International | LAX | 0 mi | Primary hub |
| Burbank | BUR | 26 mi | Southwest focus |
| Long Beach | LGB | 23 mi | JetBlue focus |
| Ontario | ONT | 38 mi | Growing alternative |
| John Wayne (Orange County) | SNA | 40 mi | Premium location |
| San Diego | SAN | 117 mi | Often cheaper |
| Palm Springs | PSP | 107 mi | Seasonal |

**San Francisco Bay Area (100mi radius)**
| Airport | Code | Distance from SFO | Notes |
|---------|------|-------------------|-------|
| SFO International | SFO | 0 mi | United hub |
| Oakland | OAK | 20 mi | Southwest hub |
| San Jose | SJC | 32 mi | Southwest/Alaska |
| Sacramento | SMF | 87 mi | Budget carrier options |

**Chicago Area (100mi radius)**
| Airport | Code | Distance from ORD | Notes |
|---------|------|-------------------|-------|
| O'Hare | ORD | 0 mi | United/American hub |
| Midway | MDW | 17 mi | Southwest hub |
| Gary | GYY | 35 mi | Limited service |
| Rockford | RFD | 75 mi | Allegiant hub |
| Milwaukee | MKE | 82 mi | Good alternative |

**Washington DC Area (100mi radius)**
| Airport | Code | Distance from DCA | Notes |
|---------|------|-------------------|-------|
| Reagan National | DCA | 0 mi | Close to downtown |
| Dulles | IAD | 26 mi | United hub |
| BWI | BWI | 32 mi | Southwest hub |
| Richmond | RIC | 98 mi | Often overlooked |

### Net Savings Calculator

Factor in ground transportation when comparing nearby airports:

```javascript
function calculateNetSavings(options) {
  const {
    primaryAirportPrice,
    alternateAirportPrice,
    alternateAirportDistance,
    transportCostPerMile = 0.50,  // Rental/rideshare estimate
    parkingDaysDiff = 0,
    parkingCostPerDay = 25,
    timeCostPerHour = 25  // Value of time
  } = options;

  // Transportation cost to/from alternate airport
  const transportCost = alternateAirportDistance * transportCostPerMile * 2; // Round trip

  // Time cost (estimate 1.5 min per mile of extra driving)
  const extraDriveMinutes = alternateAirportDistance * 1.5;
  const timeCost = (extraDriveMinutes / 60) * timeCostPerHour * 2;

  // Parking difference (if applicable)
  const parkingDiff = parkingDaysDiff * parkingCostPerDay;

  // Calculate net savings
  const flightSavings = primaryAirportPrice - alternateAirportPrice;
  const additionalCosts = transportCost + timeCost + parkingDiff;
  const netSavings = flightSavings - additionalCosts;

  return {
    flightSavings,
    transportCost,
    timeCost,
    parkingDiff,
    netSavings,
    worthIt: netSavings > 50  // Threshold for recommending alternate
  };
}
```

---

## Multi-Leg Combination Discovery

### Concept Overview

Building custom itineraries by combining flights from different airlines or booking separate legs can yield significant savings over standard round-trip fares.

### Strategy Types

#### 1. Airline Mixing

Book different airlines for outbound and return:

```javascript
async function findMixedAirlineOptions(origin, destination, departDate, returnDate) {
  // Search all airlines for each direction independently
  const outboundOptions = await searchOneWay(origin, destination, departDate);
  const returnOptions = await searchOneWay(destination, origin, returnDate);

  // Generate all combinations
  const combinations = [];
  for (const outbound of outboundOptions) {
    for (const inbound of returnOptions) {
      // Ensure return departs after outbound arrives
      if (inbound.departureTime > outbound.arrivalTime) {
        combinations.push({
          outbound,
          inbound,
          totalPrice: outbound.price + inbound.price,
          airlines: [outbound.airline, inbound.airline]
        });
      }
    }
  }

  return combinations.sort((a, b) => a.totalPrice - b.totalPrice);
}
```

#### 2. Open-Jaw Routing

Fly into one city, out of another:

```
Example: NYC → Los Angeles → San Francisco → NYC
Traditional: $600 round-trip to LA + $200 positioning flight
Open-jaw:    $450 NYC→LA + $150 SFO→NYC + $30 bus LA→SF = $630
             vs $800 for booking each segment separately
```

```javascript
async function findOpenJawOptions(origin, destinations, departDate, returnDate) {
  const options = [];

  // Try each destination as arrival, others as departure for return
  for (let i = 0; i < destinations.length; i++) {
    const arrivalCity = destinations[i];
    const otherCities = destinations.filter((_, idx) => idx !== i);

    for (const departureCity of otherCities) {
      const outbound = await searchOneWay(origin, arrivalCity, departDate);
      const inbound = await searchOneWay(departureCity, origin, returnDate);
      const positioning = await getGroundTransportCost(arrivalCity, departureCity);

      if (outbound.length && inbound.length) {
        options.push({
          type: 'open-jaw',
          outbound: outbound[0],
          inbound: inbound[0],
          positioning,
          totalCost: outbound[0].price + inbound[0].price + positioning.cost,
          route: `${origin}→${arrivalCity}→${departureCity}→${origin}`
        });
      }
    }
  }

  return options.sort((a, b) => a.totalCost - b.totalCost);
}
```

#### 3. Positioning Flights via Budget Hubs

Use budget carriers to position to/from their hub cities:

**Budget Carrier Hub Strategy:**

| Carrier | Major Hubs | Best For |
|---------|-----------|----------|
| Southwest | MDW, DAL, DEN, LAS, BWI, OAK | Domestic, flexible |
| Spirit | FLL, LAS, DFW, ORD, ATL | Ultra-low base fare |
| Frontier | DEN, LAS, MCO, PHX, ATL | Similar to Spirit |
| Allegiant | LAS, SFB, PIE, AZA, BLI | Small city→vacation |
| JetBlue | JFK, BOS, FLL, LAX, SJU | East coast, Caribbean |
| Sun Country | MSP | Midwest departures |

```javascript
async function findPositioningFlight(origin, targetHub, date) {
  const budgetCarriers = ['Spirit', 'Frontier', 'Allegiant', 'Southwest'];

  const options = await searchFlights({
    from: origin,
    to: targetHub,
    date: date,
    airlines: budgetCarriers
  });

  // Add true cost including bags
  return options.map(flight => ({
    ...flight,
    trueCost: flight.price + estimateBagFees(flight.airline, 'carry-on'),
    savings: calculateHubSavings(origin, targetHub, flight.price)
  }));
}
```

#### 4. Multi-City Arbitrage

Some cities are systematically cheaper to fly from:

```javascript
const cheapDepartureCities = {
  domestic: ['LAS', 'DEN', 'PHX', 'DAL', 'AUS', 'MSP'],
  europe: ['BOS', 'JFK', 'EWR', 'IAD', 'MIA'],
  asia: ['LAX', 'SFO', 'SEA'],
  caribbean: ['FLL', 'MIA', 'JFK', 'SJU']
};

async function findArbitrageRoute(origin, finalDestination, region) {
  const cheapHubs = cheapDepartureCities[region];
  const options = [];

  for (const hub of cheapHubs) {
    const positioningToHub = await searchOneWay(origin, hub, departDate);
    const mainFlight = await searchOneWay(hub, finalDestination, departDate);
    const returnToOrigin = await searchOneWay(finalDestination, origin, returnDate);

    // Alternative: return to hub, then position back
    const returnToHub = await searchOneWay(finalDestination, hub, returnDate);
    const positioningHome = await searchOneWay(hub, origin, returnDate);

    options.push({
      type: 'hub-arbitrage',
      hub,
      variant: 'return-direct',
      legs: [positioningToHub[0], mainFlight[0], returnToOrigin[0]],
      total: positioningToHub[0]?.price + mainFlight[0]?.price + returnToOrigin[0]?.price
    });

    options.push({
      type: 'hub-arbitrage',
      hub,
      variant: 'return-via-hub',
      legs: [positioningToHub[0], mainFlight[0], returnToHub[0], positioningHome[0]],
      total: positioningToHub[0]?.price + mainFlight[0]?.price +
             returnToHub[0]?.price + positioningHome[0]?.price
    });
  }

  return options
    .filter(opt => opt.legs.every(leg => leg != null))
    .sort((a, b) => a.total - b.total);
}
```

---

## Price Comparison Logic

### Normalization Across Sources

Different sources display prices differently. Normalize for accurate comparison:

```javascript
class PriceNormalizer {
  constructor() {
    // Typical baggage fees by carrier type
    this.bagFees = {
      legacy: { carryOn: 0, checked: 35 },
      lowCost: { carryOn: 35, checked: 45 },
      ultraLowCost: { carryOn: 45, checked: 55 }
    };

    this.carrierTypes = {
      legacy: ['United', 'American', 'Delta', 'Alaska', 'JetBlue'],
      lowCost: ['Southwest', 'Spirit', 'Frontier'],
      ultraLowCost: ['Allegiant', 'Sun Country', 'Avelo']
    };
  }

  getCarrierType(airline) {
    for (const [type, carriers] of Object.entries(this.carrierTypes)) {
      if (carriers.some(c => airline.includes(c))) return type;
    }
    return 'legacy'; // Default assumption
  }

  normalize(price, options = {}) {
    const {
      source,           // 'google', 'skiplagged', 'direct', 'kayak'
      airline,
      includedBags = { carryOn: true, checked: false },
      passengers = 1,
      isRoundTrip = false
    } = options;

    let normalizedPrice = price;

    // Source adjustments
    switch (source) {
      case 'google':
        // Google Flights includes taxes, usually accurate
        break;
      case 'skiplagged':
        // Skiplagged prices are usually final
        break;
      case 'direct':
        // Direct airline prices need careful review
        // Some show base fare, others total
        break;
      case 'kayak':
        // Similar to Google, includes taxes
        break;
    }

    // Add bag fees if not included
    const carrierType = this.getCarrierType(airline);
    const fees = this.bagFees[carrierType];

    if (!includedBags.carryOn && carrierType !== 'legacy') {
      normalizedPrice += fees.carryOn * passengers * (isRoundTrip ? 2 : 1);
    }

    if (!includedBags.checked) {
      normalizedPrice += fees.checked * passengers * (isRoundTrip ? 2 : 1);
    }

    return normalizedPrice;
  }
}
```

### Value Scoring Algorithm

Rank options by value, not just price:

```javascript
class FlightValueScorer {
  constructor(preferences = {}) {
    this.weights = {
      price: preferences.priceWeight || 0.5,
      duration: preferences.durationWeight || 0.2,
      stops: preferences.stopsWeight || 0.15,
      departureTime: preferences.departureWeight || 0.1,
      airline: preferences.airlineWeight || 0.05
    };

    this.preferredDepartureRange = preferences.preferredDeparture || {
      earliest: '06:00',
      latest: '21:00',
      ideal: '09:00'
    };

    this.preferredAirlines = preferences.preferredAirlines || [];
  }

  score(flight, allFlights) {
    const scores = {};

    // Price score (lower is better, normalized 0-1)
    const prices = allFlights.map(f => f.normalizedPrice);
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    scores.price = 1 - (flight.normalizedPrice - minPrice) / (maxPrice - minPrice || 1);

    // Duration score (shorter is better)
    const durations = allFlights.map(f => f.durationMinutes);
    const minDuration = Math.min(...durations);
    const maxDuration = Math.max(...durations);
    scores.duration = 1 - (flight.durationMinutes - minDuration) / (maxDuration - minDuration || 1);

    // Stops score (fewer is better)
    scores.stops = flight.stops === 0 ? 1 : flight.stops === 1 ? 0.6 : 0.2;

    // Departure time score
    const depHour = parseInt(flight.departureTime.split(':')[0]);
    const idealHour = parseInt(this.preferredDepartureRange.ideal.split(':')[0]);
    const hourDiff = Math.abs(depHour - idealHour);
    scores.departureTime = Math.max(0, 1 - (hourDiff / 12));

    // Airline preference score
    scores.airline = this.preferredAirlines.includes(flight.airline) ? 1 : 0.5;

    // Calculate weighted total
    const totalScore = Object.entries(this.weights).reduce((sum, [key, weight]) => {
      return sum + (scores[key] * weight);
    }, 0);

    return {
      ...flight,
      scores,
      totalScore,
      valueRating: this.getValueRating(totalScore)
    };
  }

  getValueRating(score) {
    if (score >= 0.8) return 'Excellent';
    if (score >= 0.6) return 'Good';
    if (score >= 0.4) return 'Fair';
    return 'Poor';
  }

  rankFlights(flights) {
    return flights
      .map(f => this.score(f, flights))
      .sort((a, b) => b.totalScore - a.totalScore);
  }
}
```

### Comparison Matrix Generator

```javascript
function generateComparisonMatrix(searchResults) {
  const normalizer = new PriceNormalizer();
  const scorer = new FlightValueScorer();

  // Normalize all prices
  const normalized = searchResults.map(result => ({
    ...result,
    normalizedPrice: normalizer.normalize(result.price, {
      source: result.source,
      airline: result.airline,
      includedBags: result.includedBags
    })
  }));

  // Score and rank
  const ranked = scorer.rankFlights(normalized);

  // Generate matrix
  return {
    summary: {
      cheapest: ranked.reduce((min, f) =>
        f.normalizedPrice < min.normalizedPrice ? f : min
      ),
      bestValue: ranked[0],
      fastest: ranked.reduce((min, f) =>
        f.durationMinutes < min.durationMinutes ? f : min
      ),
      fewestStops: ranked.reduce((min, f) =>
        f.stops < min.stops ? f : min
      )
    },
    ranked,
    bySource: groupBy(ranked, 'source'),
    byAirline: groupBy(ranked, 'airline')
  };
}

function groupBy(array, key) {
  return array.reduce((groups, item) => {
    const value = item[key];
    groups[value] = groups[value] || [];
    groups[value].push(item);
    return groups;
  }, {});
}
```

---

## Playwright Automation

### Anti-Detection Best Practices

```javascript
const playwright = require('playwright');

async function createStealthBrowser() {
  const browser = await playwright.chromium.launch({
    headless: false,  // Headed mode is less detectable
    args: [
      '--disable-blink-features=AutomationControlled',
      '--disable-features=IsolateOrigins,site-per-process',
      '--no-sandbox'
    ]
  });

  const context = await browser.newContext({
    userAgent: getRandomUserAgent(),
    viewport: { width: 1920, height: 1080 },
    locale: 'en-US',
    timezoneId: 'America/New_York',
    geolocation: { latitude: 40.7128, longitude: -74.0060 },
    permissions: ['geolocation']
  });

  // Override navigator properties
  await context.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
    Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
  });

  return { browser, context };
}

function getRandomUserAgent() {
  const userAgents = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15'
  ];
  return userAgents[Math.floor(Math.random() * userAgents.length)];
}

// Human-like delays
async function humanDelay(min = 500, max = 2000) {
  const delay = Math.floor(Math.random() * (max - min + 1)) + min;
  await new Promise(resolve => setTimeout(resolve, delay));
}

// Human-like typing
async function humanType(element, text) {
  for (const char of text) {
    await element.type(char, { delay: Math.random() * 100 + 50 });
  }
}
```

### Google Flights Automation

```javascript
class GoogleFlightsSearcher {
  constructor(context) {
    this.context = context;
    this.baseUrl = 'https://www.google.com/travel/flights';
  }

  async search(params) {
    const { origin, destination, departDate, returnDate, passengers = 1 } = params;
    const page = await this.context.newPage();

    try {
      // Navigate to Google Flights
      await page.goto(this.baseUrl);
      await humanDelay(1000, 2000);

      // Handle cookie consent if present
      await this.handleCookieConsent(page);

      // Set trip type (round trip or one way)
      await this.setTripType(page, returnDate ? 'round-trip' : 'one-way');

      // Enter origin
      await this.enterAirport(page, 'origin', origin);

      // Enter destination
      await this.enterAirport(page, 'destination', destination);

      // Enter dates
      await this.enterDates(page, departDate, returnDate);

      // Set passengers if not 1
      if (passengers > 1) {
        await this.setPassengers(page, passengers);
      }

      // Click search
      await this.clickSearch(page);

      // Wait for results
      await this.waitForResults(page);

      // Parse results
      return await this.parseResults(page);

    } finally {
      await page.close();
    }
  }

  async handleCookieConsent(page) {
    try {
      const acceptButton = page.locator('button:has-text("Accept all")');
      if (await acceptButton.isVisible({ timeout: 3000 })) {
        await acceptButton.click();
        await humanDelay();
      }
    } catch {
      // No consent dialog
    }
  }

  async setTripType(page, type) {
    const tripTypeButton = page.locator('[aria-label="Change ticket type"]');
    await tripTypeButton.click();
    await humanDelay(300, 600);

    if (type === 'one-way') {
      await page.locator('li:has-text("One way")').click();
    }
    await humanDelay();
  }

  async enterAirport(page, field, code) {
    const isOrigin = field === 'origin';
    const inputSelector = isOrigin
      ? 'input[aria-label="Where from?"]'
      : 'input[aria-label="Where to?"]';

    // Click the field
    const input = page.locator(inputSelector);
    await input.click();
    await humanDelay(300, 500);

    // Clear and type
    await input.fill('');
    await humanType(input, code);
    await humanDelay(500, 1000);

    // Wait for and click first suggestion
    const suggestion = page.locator(`[data-value="${code}"]`).first();
    await suggestion.waitFor({ timeout: 5000 });
    await suggestion.click();
    await humanDelay();
  }

  async enterDates(page, departDate, returnDate) {
    // Click departure date field
    const dateField = page.locator('[aria-label="Departure"]');
    await dateField.click();
    await humanDelay(500, 800);

    // Select departure date
    await this.selectDate(page, departDate);

    if (returnDate) {
      await humanDelay(300, 500);
      await this.selectDate(page, returnDate);
    }

    // Confirm dates
    const doneButton = page.locator('button:has-text("Done")');
    await doneButton.click();
    await humanDelay();
  }

  async selectDate(page, date) {
    const dateObj = new Date(date);
    const day = dateObj.getDate();
    const monthYear = dateObj.toLocaleDateString('en-US', {
      month: 'long',
      year: 'numeric'
    });

    // Navigate to correct month if needed
    while (true) {
      const currentMonth = await page.locator('.gws-flights-calendar__header').textContent();
      if (currentMonth.includes(monthYear)) break;

      await page.locator('[aria-label="Next month"]').click();
      await humanDelay(200, 400);
    }

    // Click the day
    const daySelector = `[aria-label*="${day}"][role="button"]`;
    await page.locator(daySelector).click();
  }

  async setPassengers(page, count) {
    const passengersButton = page.locator('[aria-label="Passengers"]');
    await passengersButton.click();
    await humanDelay();

    const addButton = page.locator('[aria-label="Add adult"]');
    for (let i = 1; i < count; i++) {
      await addButton.click();
      await humanDelay(200, 400);
    }

    await page.locator('button:has-text("Done")').click();
    await humanDelay();
  }

  async clickSearch(page) {
    const searchButton = page.locator('[aria-label="Search"]');
    await searchButton.click();
  }

  async waitForResults(page) {
    await page.waitForSelector('[role="listitem"]', { timeout: 30000 });
    await humanDelay(1000, 2000);  // Let more results load
  }

  async parseResults(page) {
    const results = [];
    const flightCards = page.locator('[role="listitem"]');
    const count = await flightCards.count();

    for (let i = 0; i < Math.min(count, 20); i++) {
      const card = flightCards.nth(i);

      try {
        const price = await card.locator('[data-gs]').textContent();
        const times = await card.locator('.gws-flights__times').textContent();
        const duration = await card.locator('[aria-label*="Total duration"]').textContent();
        const airline = await card.locator('.gws-flights__airline').textContent();
        const stops = await card.locator('.gws-flights__stops').textContent();

        results.push({
          source: 'google',
          price: this.parsePrice(price),
          departureTime: this.parseTime(times, 'departure'),
          arrivalTime: this.parseTime(times, 'arrival'),
          duration: duration,
          durationMinutes: this.parseDuration(duration),
          airline: airline.trim(),
          stops: this.parseStops(stops),
          includedBags: { carryOn: true, checked: false }
        });
      } catch (e) {
        // Skip malformed cards
        continue;
      }
    }

    return results;
  }

  parsePrice(priceText) {
    const match = priceText.match(/[\d,]+/);
    return match ? parseInt(match[0].replace(',', '')) : null;
  }

  parseTime(timesText, which) {
    const times = timesText.match(/\d{1,2}:\d{2}\s*[AP]M/gi);
    if (!times) return null;
    return which === 'departure' ? times[0] : times[times.length - 1];
  }

  parseDuration(durationText) {
    const hours = durationText.match(/(\d+)\s*hr?/i);
    const minutes = durationText.match(/(\d+)\s*min/i);
    return (parseInt(hours?.[1] || 0) * 60) + parseInt(minutes?.[1] || 0);
  }

  parseStops(stopsText) {
    if (stopsText.toLowerCase().includes('nonstop')) return 0;
    const match = stopsText.match(/(\d+)/);
    return match ? parseInt(match[1]) : 0;
  }
}
```

### Skiplagged Automation

```javascript
class SkiplaggedSearcher {
  constructor(context) {
    this.context = context;
    this.baseUrl = 'https://skiplagged.com';
  }

  async search(params) {
    const { origin, destination, departDate, returnDate } = params;
    const page = await this.context.newPage();

    try {
      // Build URL with search params
      const searchUrl = this.buildSearchUrl(origin, destination, departDate, returnDate);

      // Navigate directly to search results
      await page.goto(searchUrl);
      await humanDelay(2000, 3000);

      // Wait for results to load
      await this.waitForResults(page);

      // Parse both hidden city and regular results
      const results = await this.parseResults(page);

      return results;

    } finally {
      await page.close();
    }
  }

  buildSearchUrl(origin, destination, departDate, returnDate) {
    // Format: https://skiplagged.com/flights/JFK/LAX/2024-03-15
    let url = `${this.baseUrl}/flights/${origin}/${destination}/${departDate}`;
    if (returnDate) {
      url += `/${returnDate}`;
    }
    return url;
  }

  async waitForResults(page) {
    // Skiplagged loads results dynamically
    await page.waitForFunction(() => {
      const results = document.querySelectorAll('.trip');
      return results.length > 0;
    }, { timeout: 30000 });

    // Wait for more results to load
    await humanDelay(2000, 3000);
  }

  async parseResults(page) {
    const results = [];

    // Get all flight options
    const trips = page.locator('.trip');
    const count = await trips.count();

    for (let i = 0; i < Math.min(count, 30); i++) {
      const trip = trips.nth(i);

      try {
        // Check if this is a hidden city route
        const isHiddenCity = await trip.locator('.hidden-city-badge').isVisible()
          .catch(() => false);

        const price = await trip.locator('.price').textContent();
        const route = await trip.locator('.route').textContent();
        const times = await trip.locator('.times').textContent();
        const duration = await trip.locator('.duration').textContent();
        const airline = await trip.locator('.airline').textContent();

        // For hidden city, get the "true destination"
        let trueDestination = null;
        if (isHiddenCity) {
          trueDestination = await trip.locator('.true-destination').textContent()
            .catch(() => null);
        }

        results.push({
          source: 'skiplagged',
          type: isHiddenCity ? 'hidden-city' : 'direct',
          price: this.parsePrice(price),
          route: route.trim(),
          departureTime: this.parseTime(times, 'departure'),
          arrivalTime: this.parseTime(times, 'arrival'),
          duration: duration.trim(),
          durationMinutes: this.parseDuration(duration),
          airline: airline.trim(),
          trueDestination,
          includedBags: { carryOn: true, checked: false }
        });
      } catch (e) {
        continue;
      }
    }

    // Separate hidden city and regular results
    return {
      hiddenCity: results.filter(r => r.type === 'hidden-city'),
      direct: results.filter(r => r.type === 'direct'),
      all: results
    };
  }

  parsePrice(priceText) {
    const match = priceText.match(/[\d,]+/);
    return match ? parseInt(match[0].replace(',', '')) : null;
  }

  parseTime(timesText, which) {
    const times = timesText.match(/\d{1,2}:\d{2}\s*[ap]m?/gi);
    if (!times) return null;
    return which === 'departure' ? times[0] : times[times.length - 1];
  }

  parseDuration(durationText) {
    const hours = durationText.match(/(\d+)\s*h/i);
    const minutes = durationText.match(/(\d+)\s*m(?!o)/i);  // m but not month
    return (parseInt(hours?.[1] || 0) * 60) + parseInt(minutes?.[1] || 0);
  }
}
```

### Search Orchestrator

Coordinate searches across multiple sources:

```javascript
class FlightSearchOrchestrator {
  constructor() {
    this.browser = null;
    this.context = null;
  }

  async initialize() {
    const stealth = await createStealthBrowser();
    this.browser = stealth.browser;
    this.context = stealth.context;

    this.googleSearcher = new GoogleFlightsSearcher(this.context);
    this.skiplaggedSearcher = new SkiplaggedSearcher(this.context);
  }

  async comprehensiveSearch(params) {
    const {
      origin,
      destination,
      departDate,
      returnDate,
      includeNearbyAirports = true,
      searchRadius = 100
    } = params;

    const allResults = {
      primary: [],
      hiddenCity: [],
      nearbyOrigins: {},
      nearbyDestinations: {},
      multiLeg: []
    };

    // 1. Primary route search
    console.log('Searching primary route...');
    const [googleResults, skiplaggedResults] = await Promise.all([
      this.googleSearcher.search({ origin, destination, departDate, returnDate }),
      this.skiplaggedSearcher.search({ origin, destination, departDate, returnDate })
    ]);

    allResults.primary = [...googleResults, ...skiplaggedResults.direct];
    allResults.hiddenCity = skiplaggedResults.hiddenCity;

    // 2. Nearby airport searches
    if (includeNearbyAirports) {
      console.log('Searching nearby airports...');

      const nearbyOrigins = findNearbyAirports(origin, allAirports, searchRadius);
      const nearbyDestinations = findNearbyAirports(destination, allAirports, searchRadius);

      // Search from nearby origins
      for (const nearbyOrigin of nearbyOrigins.slice(0, 3)) {
        const results = await this.googleSearcher.search({
          origin: nearbyOrigin.code,
          destination,
          departDate,
          returnDate
        });
        allResults.nearbyOrigins[nearbyOrigin.code] = {
          distance: nearbyOrigin.distance,
          results
        };
        await humanDelay(3000, 5000);  // Rate limiting
      }

      // Search to nearby destinations
      for (const nearbyDest of nearbyDestinations.slice(0, 3)) {
        const results = await this.googleSearcher.search({
          origin,
          destination: nearbyDest.code,
          departDate,
          returnDate
        });
        allResults.nearbyDestinations[nearbyDest.code] = {
          distance: nearbyDest.distance,
          results
        };
        await humanDelay(3000, 5000);
      }
    }

    // 3. Process and rank all results
    return this.processResults(allResults, params);
  }

  processResults(allResults, params) {
    const normalizer = new PriceNormalizer();
    const scorer = new FlightValueScorer();

    // Flatten and normalize all results
    let allFlights = [];

    // Primary results
    allFlights.push(...allResults.primary.map(f => ({
      ...f,
      routeType: 'primary',
      airports: { origin: params.origin, destination: params.destination }
    })));

    // Hidden city results
    allFlights.push(...allResults.hiddenCity.map(f => ({
      ...f,
      routeType: 'hidden-city',
      airports: { origin: params.origin, destination: params.destination }
    })));

    // Nearby airport results
    for (const [code, data] of Object.entries(allResults.nearbyOrigins)) {
      allFlights.push(...data.results.map(f => ({
        ...f,
        routeType: 'nearby-origin',
        airports: { origin: code, destination: params.destination },
        additionalInfo: { distance: data.distance }
      })));
    }

    for (const [code, data] of Object.entries(allResults.nearbyDestinations)) {
      allFlights.push(...data.results.map(f => ({
        ...f,
        routeType: 'nearby-destination',
        airports: { origin: params.origin, destination: code },
        additionalInfo: { distance: data.distance }
      })));
    }

    // Normalize prices
    allFlights = allFlights.map(f => ({
      ...f,
      normalizedPrice: normalizer.normalize(f.price, {
        source: f.source,
        airline: f.airline,
        includedBags: f.includedBags
      })
    }));

    // Score and rank
    const ranked = scorer.rankFlights(allFlights);

    return {
      bestOverall: ranked[0],
      cheapest: ranked.reduce((min, f) =>
        f.normalizedPrice < min.normalizedPrice ? f : min
      ),
      bestHiddenCity: allResults.hiddenCity[0],
      allOptions: ranked,
      summary: this.generateSummary(ranked, params)
    };
  }

  generateSummary(ranked, params) {
    const byType = {
      primary: ranked.filter(f => f.routeType === 'primary'),
      hiddenCity: ranked.filter(f => f.routeType === 'hidden-city'),
      nearbyOrigin: ranked.filter(f => f.routeType === 'nearby-origin'),
      nearbyDestination: ranked.filter(f => f.routeType === 'nearby-destination')
    };

    return {
      searchParams: params,
      totalOptionsFound: ranked.length,
      byType: {
        primary: byType.primary.length,
        hiddenCity: byType.hiddenCity.length,
        nearbyOrigin: byType.nearbyOrigin.length,
        nearbyDestination: byType.nearbyDestination.length
      },
      priceRange: {
        min: Math.min(...ranked.map(f => f.normalizedPrice)),
        max: Math.max(...ranked.map(f => f.normalizedPrice)),
        median: ranked[Math.floor(ranked.length / 2)]?.normalizedPrice
      },
      potentialSavings: byType.primary[0]
        ? byType.primary[0].normalizedPrice - ranked[0].normalizedPrice
        : 0
    };
  }

  async close() {
    if (this.browser) {
      await this.browser.close();
    }
  }
}
```

### Usage Example

```javascript
async function main() {
  const orchestrator = new FlightSearchOrchestrator();

  try {
    await orchestrator.initialize();

    const results = await orchestrator.comprehensiveSearch({
      origin: 'JFK',
      destination: 'LAX',
      departDate: '2024-04-15',
      returnDate: '2024-04-22',
      includeNearbyAirports: true,
      searchRadius: 100
    });

    console.log('Best Overall:', results.bestOverall);
    console.log('Cheapest:', results.cheapest);
    console.log('Best Hidden City:', results.bestHiddenCity);
    console.log('Summary:', results.summary);

  } finally {
    await orchestrator.close();
  }
}
```

---

## Risk Assessment & Limitations

### Hidden City Ticketing Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Checked bags go to final destination | High | Only use carry-on luggage |
| Return flight may be cancelled | High | Only use for one-way trips |
| Frequent flyer account termination | Medium | Use separate booking account |
| Flight rebooking complications | Medium | Be flexible with alternatives |
| Airline policy violations | Low | Understand terms of service |
| Legal action (rare but possible) | Low | Airlines rarely pursue individuals |

### Technical Limitations

1. **Rate Limiting**: Flight search sites may block rapid automated queries
2. **Dynamic Content**: Prices change frequently; results may be stale
3. **CAPTCHA**: Both sites may present challenges requiring manual intervention
4. **Session Expiration**: Long searches may require re-authentication
5. **Price Accuracy**: Displayed prices may differ from booking prices

### Ethical Considerations

- Hidden city ticketing is legal but against most airline terms of service
- Frequent use may impact the airline industry's pricing models
- Consider the environmental impact of inefficient routing
- Be aware of potential service disruptions to other passengers

---

## Appendix: Airport Database Sample

```javascript
const majorAirports = [
  { code: 'JFK', name: 'John F. Kennedy International', city: 'New York', lat: 40.6413, lon: -73.7781 },
  { code: 'LAX', name: 'Los Angeles International', city: 'Los Angeles', lat: 33.9425, lon: -118.4081 },
  { code: 'ORD', name: "O'Hare International", city: 'Chicago', lat: 41.9742, lon: -87.9073 },
  { code: 'DFW', name: 'Dallas/Fort Worth International', city: 'Dallas', lat: 32.8998, lon: -97.0403 },
  { code: 'DEN', name: 'Denver International', city: 'Denver', lat: 39.8561, lon: -104.6737 },
  { code: 'ATL', name: 'Hartsfield-Jackson Atlanta International', city: 'Atlanta', lat: 33.6407, lon: -84.4277 },
  { code: 'SFO', name: 'San Francisco International', city: 'San Francisco', lat: 37.6213, lon: -122.3790 },
  { code: 'SEA', name: 'Seattle-Tacoma International', city: 'Seattle', lat: 47.4502, lon: -122.3088 },
  { code: 'MIA', name: 'Miami International', city: 'Miami', lat: 25.7959, lon: -80.2870 },
  { code: 'BOS', name: 'Logan International', city: 'Boston', lat: 42.3656, lon: -71.0096 },
  // ... extend with more airports as needed
];
```

---

## Quick Reference

### Search Priority Order

1. **Skiplagged** - Best for hidden city routes
2. **Google Flights** - Comprehensive, reliable pricing
3. **Direct airline sites** - Best for sales and elite pricing
4. **Nearby airports** - Check within 100mi radius
5. **Multi-leg combinations** - Mix airlines and routes

### Key Commands

```bash
# Quick hidden city search
node search.js --hidden-city --from JFK --to ORD --date 2024-04-15

# Nearby airport search
node search.js --nearby --from JFK --to LAX --radius 100 --date 2024-04-15

# Full comprehensive search
node search.js --comprehensive --from JFK --to LAX --depart 2024-04-15 --return 2024-04-22
```

### Savings Expectations

| Strategy | Typical Savings | Best For |
|----------|----------------|----------|
| Hidden City | 20-50% | Hub cities, business routes |
| Nearby Airports | 10-30% | Major metros, leisure travel |
| Airline Mixing | 5-20% | Flexible dates |
| Positioning Flights | 15-40% | International departures |
