# Timing Sweet Spot Strategy

Flight prices fluctuate based on predictable patterns. This strategy identifies optimal booking windows and timing rules to secure the lowest fares.

## Table of Contents

1. [Historical Pricing Patterns](#historical-pricing-patterns)
2. [Demand Cycles by Route Type](#demand-cycles-by-route-type)
3. [Fare Reset Timing](#fare-reset-timing)
4. [Booking Window Recommendations](#booking-window-recommendations)
5. [Implementation Logic](#implementation-logic)

---

## Historical Pricing Patterns

### Day of Week for Booking

| Day | Price Index | Best For | Notes |
|-----|-------------|----------|-------|
| Tuesday | 100 (baseline) | All bookings | Airlines release sales Monday night |
| Wednesday | 101 | All bookings | Sales still active |
| Sunday | 103 | Last-minute | Weekend inventory adjustments |
| Monday | 105 | Business routes | Corporate travel planning |
| Thursday | 106 | Leisure | Weekend trip planners |
| Friday | 108 | Leisure | Last-minute weekend bookings |
| Saturday | 107 | International | Lower search volume |

**Key Insight**: Book Tuesday-Wednesday for best prices. Airlines typically release sales Monday evening to match competitors, prices lowest by Tuesday morning.

### Day of Week for Travel

| Travel Day | Domestic Index | International Index |
|------------|---------------|---------------------|
| Tuesday | 92 | 95 |
| Wednesday | 94 | 93 |
| Saturday | 96 | 98 |
| Monday | 100 | 100 |
| Thursday | 103 | 102 |
| Sunday | 108 | 105 |
| Friday | 112 | 108 |

**Key Insight**: Fly Tuesday-Wednesday for cheapest domestic, Wednesday for international. Avoid Friday departures.

### Time of Day Impact

| Departure Time | Price Index | Why |
|----------------|-------------|-----|
| 5:00 AM - 7:00 AM | 88 | "Red-eye" unpopular |
| 7:00 AM - 9:00 AM | 105 | Business demand |
| 9:00 AM - 12:00 PM | 100 | Standard |
| 12:00 PM - 3:00 PM | 97 | Midday lull |
| 3:00 PM - 6:00 PM | 103 | Business returns |
| 6:00 PM - 9:00 PM | 102 | Evening preference |
| 9:00 PM - 11:59 PM | 92 | Late night discount |

---

## Demand Cycles by Route Type

### Domestic Business Routes

```
Example: NYC ↔ Chicago, LA ↔ San Francisco, Boston ↔ DC

Pattern:
- Monday morning: Peak (index 120)
- Friday evening: Peak (index 115)
- Tuesday-Thursday midday: Low (index 95)
- Saturday: Lowest (index 85)

Booking window: 2-3 weeks out
Best travel days: Tuesday, Wednesday, Saturday
Avoid: Monday AM, Friday PM
```

### Domestic Leisure Routes

```
Example: NYC → Orlando, Chicago → Las Vegas, LA → Hawaii

Pattern:
- Summer (Jun-Aug): Peak season (index 130)
- Spring break (Mar): High (index 120)
- Thanksgiving week: Extreme peak (index 150)
- Jan-Feb: Low season (index 85)
- Sep-Oct: Shoulder (index 90)

Booking window: 6-8 weeks for peak, 3-4 weeks for off-peak
Best travel: Shoulder seasons, mid-week
Avoid: Holiday weekends
```

### Transatlantic Routes

```
Example: NYC → London, Chicago → Paris, LA → Rome

Pattern:
- Peak: Jun 15 - Aug 31 (index 140)
- High: Dec 15 - Jan 5 (index 125)
- Shoulder: Apr-May, Sep-Oct (index 95)
- Low: Nov, Jan 15 - Mar (index 80)

Booking window: 8-12 weeks for summer, 4-6 weeks for winter
Best travel: Shoulder seasons
Currency tip: Watch EUR/GBP rates
```

### Transpacific Routes

```
Example: LA → Tokyo, SF → Sydney, NYC → Singapore

Pattern:
- Peak: Summer + Chinese New Year (index 145)
- High: Cherry blossom season (index 130)
- Shoulder: Mar, Oct-Nov (index 95)
- Low: Feb (post-CNY), Sep (index 85)

Booking window: 10-16 weeks out
Best travel: Shoulder seasons, avoid CNY completely
```

### Latin America Routes

```
Example: Miami → Mexico City, Houston → Bogota

Pattern:
- Peak: Christmas/New Year (index 140)
- High: Easter week (index 125)
- Shoulder: Jun-Jul (index 100)
- Low: Sep-Nov (index 85)

Booking window: 4-8 weeks
Best travel: Shoulder seasons
```

---

## Fare Reset Timing

### How Airlines Update Prices

```
Timeline (typical daily cycle):

12:00 AM - 2:00 AM: Inventory systems batch update
2:00 AM - 4:00 AM: Fare filing with ATPCO
4:00 AM - 6:00 AM: GDS distribution
6:00 AM - 8:00 AM: OTA cache refresh
8:00 AM onwards: New prices visible to consumers
```

### Optimal Search Windows

| Time Window | What's Happening | Action |
|-------------|------------------|--------|
| 12:01 AM local | New fare day begins | Check for overnight sales |
| 3:00 AM local | Systems updating | Avoid - inconsistent prices |
| 6:00 AM local | Fresh inventory | Good time to search |
| Tuesday 3:00 PM | Competitors matched | Best weekly window |
| Midnight Sunday | Weekend fares expire | Last chance for weekly sales |

### Sale Cycles

```
Typical airline sale pattern:

Monday 9 PM EST: Airline X announces sale
Tuesday 9 AM EST: Competitors match prices
Tuesday-Wednesday: Best prices available
Thursday: Sale may extend or prices rise
Friday: Sale typically ends
Saturday-Sunday: Regular pricing returns
```

### Midnight Rule

Flights departing just after midnight are often classified as "previous day" for pricing:

```
Example:
Flight departing 11:59 PM Sunday = Sunday pricing (expensive)
Flight departing 12:05 AM Monday = Monday pricing (cheaper)

The 12:05 AM flight is technically Monday, priced with Monday inventory
```

---

## Booking Window Recommendations

### Optimal Advance Purchase by Route Type

| Route Type | Sweet Spot | Too Early | Too Late |
|------------|------------|-----------|----------|
| Domestic short-haul | 3-4 weeks | >8 weeks | <1 week |
| Domestic long-haul | 4-6 weeks | >10 weeks | <2 weeks |
| Transatlantic | 8-12 weeks | >16 weeks | <4 weeks |
| Transpacific | 10-16 weeks | >20 weeks | <6 weeks |
| Latin America | 4-8 weeks | >12 weeks | <2 weeks |

### Dynamic Booking Window Logic

```javascript
function getOptimalBookingWindow(route) {
  const today = new Date();
  const travelDate = new Date(route.departureDate);
  const daysOut = (travelDate - today) / (1000 * 60 * 60 * 24);

  const windows = {
    domestic: { ideal: [21, 45], early: 60, late: 7 },
    transatlantic: { ideal: [56, 90], early: 120, late: 30 },
    transpacific: { ideal: [70, 120], early: 150, late: 45 },
    latinAmerica: { ideal: [28, 60], early: 90, late: 14 }
  };

  const window = windows[route.type];

  if (daysOut < window.late) {
    return { status: 'late', message: 'Last-minute pricing likely', urgency: 'high' };
  }
  if (daysOut > window.early) {
    return { status: 'early', message: 'Wait for better prices', urgency: 'low' };
  }
  if (daysOut >= window.ideal[0] && daysOut <= window.ideal[1]) {
    return { status: 'optimal', message: 'Ideal booking window', urgency: 'medium' };
  }
  return { status: 'good', message: 'Reasonable timing', urgency: 'medium' };
}
```

### Holiday-Adjusted Windows

```
For peak travel periods, book earlier:

Thanksgiving: 8-10 weeks out (vs normal 3-4)
Christmas/New Year: 10-12 weeks out
Spring Break: 8-10 weeks out
Summer (Jun-Aug): 10-14 weeks out for peak dates
Memorial Day/Labor Day: 6-8 weeks out
```

---

## Implementation Logic

### Price Prediction Model

```javascript
function predictPriceDirection(route, historicalData) {
  const factors = {
    daysToTravel: getDaysUntilTravel(route.date),
    dayOfWeek: new Date().getDay(),
    seasonality: getSeasonFactor(route.date),
    demandTrend: analyzeDemandTrend(historicalData),
    inventoryLevel: estimateInventory(route)
  };

  // Weighted scoring
  let score = 0;

  // Booking window factor
  if (factors.daysToTravel < 14) score += 20;  // Prices rising
  else if (factors.daysToTravel > 90) score -= 10;  // May drop
  else score += 0;  // Stable

  // Day of week factor
  if ([2, 3].includes(factors.dayOfWeek)) score -= 5;  // Tue/Wed cheaper
  if ([5, 0].includes(factors.dayOfWeek)) score += 5;  // Fri/Sun expensive

  // Seasonality
  score += factors.seasonality * 15;  // -1 to +1 scale

  // Demand trend
  if (factors.demandTrend > 0) score += 10;  // Rising demand

  return {
    score: score,
    recommendation: score > 10 ? 'Book now' : score < -10 ? 'Wait' : 'Monitor',
    confidence: Math.abs(score) / 50
  };
}
```

### Timing Recommendation Engine

```javascript
function getTimingRecommendation(origin, destination, preferredDate) {
  const route = classifyRoute(origin, destination);
  const season = getSeason(preferredDate);

  // Calculate optimal booking date
  const bookingWindow = getOptimalBookingWindow(route);
  const optimalBookingDate = new Date(preferredDate);
  optimalBookingDate.setDate(
    optimalBookingDate.getDate() - bookingWindow.ideal[1]
  );

  // Find best travel days within +/- 3 days
  const flexibleDates = [];
  for (let offset = -3; offset <= 3; offset++) {
    const date = new Date(preferredDate);
    date.setDate(date.getDate() + offset);
    flexibleDates.push({
      date: date,
      dayOfWeek: date.toLocaleDateString('en-US', { weekday: 'long' }),
      priceIndex: getDayPriceIndex(date, route.type)
    });
  }

  const bestDate = flexibleDates.reduce((best, current) =>
    current.priceIndex < best.priceIndex ? current : best
  );

  return {
    recommendedTravelDate: bestDate.date,
    recommendedBookingDate: optimalBookingDate,
    potentialSavings: calculateSavings(preferredDate, bestDate.date, route),
    alternativeDates: flexibleDates.sort((a, b) => a.priceIndex - b.priceIndex),
    notes: generateTimingNotes(route, season)
  };
}
```

### Alert Trigger Conditions

```javascript
const ALERT_CONDITIONS = {
  priceDropThreshold: 0.10,      // 10% drop triggers alert
  priceRiseThreshold: 0.15,     // 15% rise triggers urgent alert
  optimalWindowStart: true,     // Alert when entering sweet spot
  saleDetected: true,           // Alert when fare sale found
  inventoryLow: 5               // Alert when < 5 seats at price
};

function shouldTriggerAlert(currentPrice, previousPrice, context) {
  const change = (currentPrice - previousPrice) / previousPrice;

  if (change <= -ALERT_CONDITIONS.priceDropThreshold) {
    return { trigger: true, type: 'PRICE_DROP', urgency: 'high' };
  }

  if (change >= ALERT_CONDITIONS.priceRiseThreshold) {
    return { trigger: true, type: 'PRICE_RISE', urgency: 'urgent' };
  }

  if (context.enteringOptimalWindow) {
    return { trigger: true, type: 'BOOKING_WINDOW', urgency: 'medium' };
  }

  return { trigger: false };
}
```

---

## Quick Reference Card

### When to Book

| I'm flying... | Book this far out |
|---------------|-------------------|
| Domestic next month | 3-4 weeks |
| Domestic this summer | 6-8 weeks |
| Europe this summer | 10-12 weeks |
| Asia any time | 12-16 weeks |
| Holiday travel | +4 weeks to normal |

### When to Search

- **Best day to search**: Tuesday afternoon
- **Best time**: 3 PM - 6 PM Eastern
- **Avoid**: Monday mornings, Friday evenings

### When to Fly

- **Cheapest days**: Tuesday, Wednesday
- **Cheapest times**: 5-7 AM, 9 PM+
- **Most expensive**: Friday PM, Sunday PM

### Quick Rules

1. **21-Day Rule**: Domestic prices jump ~40% inside 21 days
2. **Tuesday Rule**: Book on Tuesday, fly on Tuesday
3. **Midnight Rule**: 12:01 AM flights priced as previous day
4. **6-Week Sweet Spot**: Most routes cheapest 6 weeks out
5. **Shoulder Season**: Best value in Apr-May, Sep-Oct
