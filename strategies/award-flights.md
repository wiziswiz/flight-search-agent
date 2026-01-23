# Award Flight Search Strategy

Search for flights bookable with airline miles and credit card points. This strategy uses multiple scrapers to find award availability across loyalty programs.

## Table of Contents

1. [Award Search Tools](#award-search-tools)
2. [Supported Airlines & Programs](#supported-airlines--programs)
3. [Points Valuation](#points-valuation)
4. [Search Patterns](#search-patterns)
5. [Implementation](#implementation)

---

## Award Search Tools

### Integrated Tools

| Tool | Source | Airlines/Programs | Features |
|------|--------|-------------------|----------|
| **Flightplan** | [GitHub](https://github.com/flightplan-tool/flightplan) | AC, AS, BA, CX, KE, NH, SQ | Award inventory scraping |
| **AwardWiz** | [GitHub](https://github.com/lg/awardwiz) | AA, Alaska, Delta, JetBlue, Southwest, United | Low-fare availability (X, I, O classes) |
| **Skiplagged** | [GitHub](https://github.com/krishnaglick/skiplagged-node-api) | All airlines | Cash prices + hidden city |

### Tool Capabilities

```
Flightplan (Award Search):
├── Aeroplan (Air Canada) - Star Alliance awards
├── Alaska Airlines - Partner awards (AA, Emirates, etc.)
├── British Airways - Avios redemptions
├── Cathay Pacific - Asia Miles
├── Korean Air - SKYPASS
├── ANA - Mileage Club (Star Alliance sweet spots)
└── Singapore Airlines - KrisFlyer

AwardWiz (Low-Fare Detection):
├── American Airlines - AAdvantage
├── Delta - SkyMiles
├── United - MileagePlus
├── Southwest - Rapid Rewards
├── JetBlue - TrueBlue
└── Alaska - Mileage Plan
```

---

## Supported Airlines & Programs

### Airline Alliance Map

| Alliance | Key Airlines | Best Award Program |
|----------|--------------|-------------------|
| **Star Alliance** | United, ANA, Lufthansa, Singapore | ANA (lowest fees), Aeroplan (availability) |
| **oneworld** | American, British Airways, Cathay, JAL | Alaska (partner awards), BA (short-haul) |
| **SkyTeam** | Delta, Air France, KLM, Korean | Korean Air (no fuel surcharges) |
| **Independent** | Southwest, JetBlue, Alaska, Emirates | Direct programs |

### Program Sweet Spots

| Route Type | Best Programs | Why |
|------------|---------------|-----|
| US Domestic | Southwest, AA, Alaska | No fuel surcharges, good availability |
| Transatlantic | Aeroplan, ANA | Low fees on partner flights |
| Transpacific | ANA, Korean Air | Excellent business class rates |
| Intra-Asia | Cathay AsiaMiles | Strong regional coverage |
| Intra-Europe | BA Avios | Distance-based pricing |

---

## Points Valuation

### Credit Card Points Transfer Partners

```
Chase Ultimate Rewards:
├── United (1:1)
├── Southwest (1:1)
├── British Airways (1:1)
├── Air France/KLM (1:1)
├── Singapore (1:1)
├── Aeroplan (1:1)
├── Virgin Atlantic (1:1)
└── Hyatt, IHG, Marriott (hotels)

Amex Membership Rewards:
├── Delta (1:1)
├── British Airways (1:1)
├── Air France/KLM (1:1)
├── Singapore (1:1)
├── ANA (1:1)
├── Cathay AsiaMiles (1:1)
├── Virgin Atlantic (1:1)
└── Aeroplan (1:1)

Capital One Miles:
├── Air Canada (1:1)
├── Air France/KLM (1:1)
├── British Airways (1:1)
├── Emirates (1:1)
├── Singapore (1:1)
├── Turkish (1:1)
└── Avianca (1:1)

Citi ThankYou:
├── Singapore (1:1)
├── Virgin Atlantic (1:1)
├── Air France/KLM (1:1)
├── Turkish (1:1)
├── Qatar (1:1)
└── Avianca (1:1)
```

### Points Value Estimates (cents per point)

| Program | Economy | Business | First |
|---------|---------|----------|-------|
| ANA Mileage Club | 1.4¢ | 2.5¢ | 4.0¢ |
| Aeroplan | 1.3¢ | 2.2¢ | 3.5¢ |
| Alaska Mileage Plan | 1.5¢ | 2.0¢ | 2.5¢ |
| AA AAdvantage | 1.2¢ | 1.8¢ | 2.5¢ |
| Delta SkyMiles | 1.1¢ | 1.6¢ | 2.0¢ |
| United MileagePlus | 1.2¢ | 1.7¢ | 2.2¢ |
| BA Avios | 1.3¢ | 1.8¢ | 2.0¢ |
| Southwest RR | 1.4¢ | N/A | N/A |

### Value Calculation

```javascript
function calculatePointsValue(cashPrice, milesRequired, taxes) {
  const netValue = cashPrice - taxes;
  const centsPerPoint = (netValue * 100) / milesRequired;

  return {
    centsPerPoint: centsPerPoint.toFixed(2),
    rating: centsPerPoint > 2.0 ? 'excellent' :
            centsPerPoint > 1.5 ? 'good' :
            centsPerPoint > 1.0 ? 'fair' : 'poor',
    recommendation: centsPerPoint > 1.5 ? 'USE_POINTS' : 'PAY_CASH'
  };
}
```

---

## Search Patterns

### Multi-Program Search

```javascript
async function searchAllPrograms(origin, destination, date, cabin) {
  const searches = [
    // Flightplan - Award inventory
    searchFlightplan('AC', origin, destination, date, cabin),
    searchFlightplan('NH', origin, destination, date, cabin),
    searchFlightplan('SQ', origin, destination, date, cabin),
    searchFlightplan('CX', origin, destination, date, cabin),

    // AwardWiz - US airlines
    searchAwardWiz('aa', origin, destination, date),
    searchAwardWiz('alaska', origin, destination, date),
    searchAwardWiz('united', origin, destination, date),
    searchAwardWiz('delta', origin, destination, date),
    searchAwardWiz('southwest', origin, destination, date),

    // Skiplagged - Cash baseline + hidden city
    searchSkiplagged(origin, destination, date, { partialTrips: true })
  ];

  const results = await Promise.allSettled(searches);
  return normalizeResults(results);
}
```

### Fare Class Detection

Award tickets have specific booking classes that indicate availability:

| Class | Meaning | Value |
|-------|---------|-------|
| **X** | Saver economy award | Best value |
| **I** | Saver business award | Best value |
| **O** | Saver first award | Best value |
| **U/T** | Standard economy award | Higher cost |
| **Z/P** | Standard business award | Higher cost |
| **A** | Standard first award | Higher cost |

```javascript
function isSaverAward(fareClass) {
  const saverClasses = ['X', 'I', 'O', 'XN', 'IN', 'ON'];
  return saverClasses.includes(fareClass.toUpperCase());
}
```

### Partner Award Search

For best availability, search the operating airline's partners:

```javascript
const PARTNER_SEARCH_PRIORITY = {
  // To fly United metal, search these programs:
  'UA': ['Aeroplan', 'ANA', 'Singapore', 'Turkish'],

  // To fly American metal:
  'AA': ['Alaska', 'British Airways', 'Qantas', 'Cathay'],

  // To fly Delta metal:
  'DL': ['Virgin Atlantic', 'Air France', 'Korean Air'],

  // To fly international carriers:
  'LH': ['Aeroplan', 'United', 'ANA'],  // Lufthansa
  'SQ': ['KrisFlyer', 'United', 'ANA'],  // Singapore
  'CX': ['AsiaMiles', 'Alaska', 'AA'],   // Cathay
};
```

---

## Implementation

### Flightplan Integration

```javascript
const fp = require('flightplan-tool');

async function searchFlightplan(airline, from, to, date, cabin) {
  const engine = fp.new(airline.toLowerCase());

  // Initialize with credentials (stored securely)
  await engine.initialize({
    credentials: getCredentials(airline)
  });

  const { responses, error } = await engine.search({
    fromCity: from,
    toCity: to,
    departDate: date,
    cabin: cabin  // 'economy', 'business', 'first'
  });

  if (error) return { error };

  const { awards } = engine.parse(responses);
  return awards.map(a => ({
    airline: a.airline,
    flight: a.flight,
    miles: a.mileage,
    cabin: a.cabin,
    availability: a.quantity,
    fareClass: a.fareClass,
    source: 'flightplan'
  }));
}
```

### Skiplagged Integration (with Hidden City)

```javascript
const skiplagged = require('skiplagged-node-api');

async function searchSkiplagged(from, to, date, options = {}) {
  const results = await skiplagged({
    from: from,
    to: to,
    departureDate: date,
    sort: 'cost',
    resultsCount: 10,
    partialTrips: options.partialTrips || false  // Enable hidden city
  });

  return results.map(flight => ({
    price: flight.price,
    priceCents: flight.price_pennies,
    duration: flight.duration,
    departure: flight.departureTime,
    arrival: flight.arrivalTime,
    legs: flight.legs.map(leg => ({
      airline: leg.airline,
      flight: leg.flightCode,
      from: leg.departingFrom,
      to: leg.arrivingAt
    })),
    isHiddenCity: options.partialTrips &&
      flight.legs[flight.legs.length - 1].arrivingAt !== to,
    source: 'skiplagged'
  }));
}
```

### AwardWiz Scraper Usage

```bash
# Run from integrations/awardwiz directory
just run-scraper aa SFO LAX 2025-03-15
just run-scraper united JFK LHR 2025-04-01
just run-scraper southwest LAX DEN 2025-03-20
```

### Combined Search Output

```json
{
  "query": {
    "origin": "SFO",
    "destination": "NRT",
    "date": "2025-06-15",
    "cabin": "business"
  },
  "cashBaseline": {
    "price": "$4,500",
    "source": "google_flights"
  },
  "awardOptions": [
    {
      "program": "ANA Mileage Club",
      "miles": 85000,
      "taxes": "$85",
      "cabin": "business",
      "fareClass": "I",
      "availability": 2,
      "valuePerPoint": "5.2¢",
      "rating": "excellent",
      "transferFrom": ["Amex MR"]
    },
    {
      "program": "Aeroplan",
      "miles": 75000,
      "taxes": "$120",
      "cabin": "business",
      "fareClass": "I",
      "availability": 4,
      "valuePerPoint": "5.8¢",
      "rating": "excellent",
      "transferFrom": ["Chase UR", "Amex MR", "Capital One"]
    }
  ],
  "hiddenCityOption": {
    "route": "SFO → NRT → HND",
    "price": "$2,800",
    "savings": "38%",
    "warnings": ["One-way only", "No checked bags"]
  },
  "recommendation": "Book via Aeroplan - best availability and value"
}
```

---

## Credential Management

### Secure Storage

```javascript
// Store credentials in environment or secure vault
const CREDENTIALS = {
  AC: process.env.AEROPLAN_CREDENTIALS?.split(':'),
  NH: process.env.ANA_CREDENTIALS?.split(':'),
  BA: process.env.BA_CREDENTIALS?.split(':'),
  // etc.
};

function getCredentials(airline) {
  const creds = CREDENTIALS[airline];
  if (!creds) {
    throw new Error(`No credentials configured for ${airline}`);
  }
  return creds;
}
```

### Rate Limiting

```javascript
const RATE_LIMITS = {
  flightplan: { requestsPerMinute: 2, cooldown: 30000 },
  awardwiz: { requestsPerMinute: 1, cooldown: 60000 },
  skiplagged: { requestsPerMinute: 3, cooldown: 20000 }
};

async function rateLimitedSearch(source, searchFn) {
  const limit = RATE_LIMITS[source];
  await enforceRateLimit(source, limit);
  return searchFn();
}
```

---

## Best Practices

1. **Search partner programs** - Often better availability than direct airline
2. **Check fare class** - Saver awards (X/I/O) are 50%+ cheaper than standard
3. **Flexible dates** - Award availability varies dramatically by day
4. **Book early** - Business/First saver awards release 330 days out
5. **Transfer strategically** - Only transfer points when you see availability
6. **Consider taxes** - BA charges high fuel surcharges; ANA doesn't
