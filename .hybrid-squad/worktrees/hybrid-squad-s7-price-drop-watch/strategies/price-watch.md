# Price Drop Watch Strategy

A comprehensive guide to monitoring flight prices safely and effectively without triggering dynamic pricing algorithms.

---

## Table of Contents

1. [Safe Monitoring Patterns](#safe-monitoring-patterns)
2. [Search Frequency Guidelines](#search-frequency-guidelines)
3. [Google Flights Price Tracking Setup](#google-flights-price-tracking-setup)
4. [Behavioral Rules to Avoid Price Triggers](#behavioral-rules-to-avoid-price-triggers)
5. [Tracking Spreadsheet Template](#tracking-spreadsheet-template)
6. [Additional Tools & Resources](#additional-tools--resources)
7. [Quick Reference Card](#quick-reference-card)

---

## Safe Monitoring Patterns

### Daily Search Limits

To avoid triggering dynamic pricing algorithms that may raise prices based on perceived demand:

| Category | Maximum Searches | Notes |
|----------|-----------------|-------|
| **Per Route** | 2 per day | Space at least 6 hours apart |
| **Per Platform** | 5 per day | Rotate between platforms |
| **Total Daily** | 10 per day | Across all platforms combined |

### Risk Levels by Search Frequency

| Risk Level | Searches/Day | Consequence |
|------------|--------------|-------------|
| 🟢 Low | 1-3 | Minimal price impact |
| 🟡 Medium | 4-7 | Possible mild increases |
| 🔴 High | 8+ | Likely price manipulation |

### Platform Rotation Schedule

Rotate between platforms to distribute your search footprint:

**Week 1:**
- Monday/Thursday: Google Flights
- Tuesday/Friday: Skyscanner
- Wednesday/Saturday: Kayak
- Sunday: Hopper (mobile)

**Week 2:**
- Monday/Thursday: Skyscanner
- Tuesday/Friday: Kayak
- Wednesday/Saturday: Google Flights
- Sunday: Momondo

### Time Distribution Strategy

Spread searches throughout the day to appear more organic:

```
Morning (6-9 AM):     ██░░░░░░░░ 20%
Midday (11 AM-2 PM):  ███░░░░░░░ 30%
Evening (6-9 PM):     ███░░░░░░░ 30%
Late Night (10 PM+):  ██░░░░░░░░ 20%
```

---

## Search Frequency Guidelines

### By Time Until Departure

| Timeline | Search Frequency | Rationale |
|----------|-----------------|-----------|
| **6+ months out** | 1x per week | Prices rarely fluctuate significantly |
| **3-6 months out** | 2x per week | Sweet spot begins; monitor trends |
| **6-12 weeks out** | 3x per week | Prime booking window approaching |
| **3-6 weeks out** | Every other day | Active monitoring for deals |
| **1-3 weeks out** | Daily (carefully) | Last chance; prices volatile |
| **< 1 week out** | Book immediately | Prices only increase from here |

### By Route Type

**Domestic Flights (US)**
- Optimal booking window: 3-4 weeks before departure
- Peak monitoring: 4-8 weeks out
- Price volatility: Medium

**International Flights**
- Optimal booking window: 6-8 weeks before departure
- Peak monitoring: 8-16 weeks out
- Price volatility: High

**Budget Airlines**
- Optimal booking window: 2-3 months out
- Peak monitoring: Start early, book when reasonable
- Price volatility: Very High (limited inventory)

### Seasonal Considerations

| Season | Best Time to Book | Price Behavior |
|--------|------------------|----------------|
| Peak Summer (Jun-Aug) | 3-4 months ahead | Prices rise steadily |
| Holidays (Nov-Dec) | 2-3 months ahead | Sharp spikes near dates |
| Shoulder Season | 4-6 weeks ahead | More flexible, better deals |
| Off-Peak | 2-4 weeks ahead | Last-minute deals possible |

---

## Google Flights Price Tracking Setup

### Step 1: Access Google Flights

1. Go to [google.com/flights](https://www.google.com/flights)
2. Sign into your Google account (required for price tracking)
3. Ensure location/currency settings are correct

### Step 2: Set Up Your Search

1. Enter your departure and destination airports
2. Select your travel dates (or use flexible dates feature)
3. Choose passenger count and cabin class
4. Review initial results

### Step 3: Enable Price Tracking

1. Look for **"Track prices"** toggle (usually top-left of results)
2. Click to enable - turns blue when active
3. Confirm notification preferences
4. You'll receive email alerts when prices change

### Step 4: Configure Date Flexibility

For better deals, use Google Flights' flexibility features:

**Date Grid View:**
- Click on departure date
- Select "Flexible dates"
- View price calendar across multiple dates
- Identify cheapest travel windows

**Price Graph:**
- Shows price trends over time
- Helps identify if current price is high/low
- Located below main search results

### Step 5: Manage Your Tracked Flights

1. Click the menu icon (☰) → "Tracked flight prices"
2. View all active price trackers
3. Remove outdated searches (keep list clean)
4. Check price history for each tracked route

### Google Flights Limitations

- **Doesn't include:** Southwest, some budget carriers
- **Tracking duration:** Auto-expires after trip date
- **Alert frequency:** 1-2 emails per day maximum
- **No price guarantee:** Tracked price may change before booking

### Alternative: Google Flights URL Bookmarking

For manual checking without triggering tracking:

```
https://www.google.com/flights?hl=en#flt=
[ORIGIN].[DESTINATION].[DATE]*[RETURN_DATE]
```

Example:
```
https://www.google.com/flights#flt=SFO.JFK.2024-06-15*JFK.SFO.2024-06-22
```

---

## Behavioral Rules to Avoid Price Triggers

### Device & Browser Hygiene

| Practice | Why It Matters |
|----------|---------------|
| **Use incognito/private mode** | Prevents cookie-based tracking |
| **Clear cookies before searching** | Removes prior search history |
| **Use a VPN** | Masks your location and IP |
| **Rotate devices** | Spreads search footprint |
| **Avoid mobile apps for searching** | Apps track more aggressively |

### VPN Best Practices

1. **Location selection:**
   - Search from a "neutral" location (not your departure city)
   - Try the destination country for local pricing
   - Avoid known "high-income" regions for first search

2. **Recommended VPN locations:**
   - For US domestic: Use a different US region
   - For international: Try the destination country first
   - Backup: Singapore, Portugal, or Brazil often show lower prices

3. **Consistency:**
   - Use the same VPN location for booking as searching
   - Sudden location changes may flag fraud concerns

### What NOT to Do

❌ **Never:**
- Search the same route repeatedly in one session
- Use the airline's app to search (tracks more data)
- Leave flight tabs open for extended periods
- Click through to booking without intending to buy
- Search while logged into frequent flyer accounts
- Use your normal browser with saved history

### Recommended Search Protocol

**Before Each Search:**
1. Open new incognito/private window
2. Connect to VPN (if using)
3. Navigate directly to search site
4. Complete search in one session
5. Note prices, then close completely

**Search Session Checklist:**
```
□ Incognito mode active
□ VPN connected (optional but recommended)
□ Cookies cleared (if not incognito)
□ No airline loyalty accounts logged in
□ Search completed in under 5 minutes
□ Prices recorded externally
□ All tabs closed after search
```

---

## Tracking Spreadsheet Template

### Basic Template

Create a Google Sheet or Excel file with these columns:

| Column | Description | Example |
|--------|-------------|---------|
| A: Date Checked | When you searched | 2024-03-15 |
| B: Route | Origin-Destination | SFO-JFK |
| C: Outbound Date | Departure date | 2024-06-15 |
| D: Return Date | Return date | 2024-06-22 |
| E: Airline | Carrier name | United |
| F: Price | Total price | $342 |
| G: Platform | Where found | Google Flights |
| H: Notes | Additional info | Direct flight, good times |

### Advanced Template with Analysis

**Sheet 1: Price Log**

```
| Date    | Route   | Dep Date | Ret Date | Airline | Price | Platform | Stops | Duration |
|---------|---------|----------|----------|---------|-------|----------|-------|----------|
| 3/15/24 | SFO-JFK | 6/15/24  | 6/22/24  | United  | $342  | Google   | 0     | 5h 30m   |
| 3/16/24 | SFO-JFK | 6/15/24  | 6/22/24  | United  | $358  | Kayak    | 0     | 5h 30m   |
| 3/17/24 | SFO-JFK | 6/15/24  | 6/22/24  | Delta   | $329  | Google   | 0     | 5h 45m   |
```

**Sheet 2: Price Analysis Dashboard**

Key metrics to calculate:

```
Lowest Price Seen:     =MIN(F:F)
Highest Price Seen:    =MAX(F:F)
Average Price:         =AVERAGE(F:F)
Current vs. Average:   =(LATEST_PRICE - AVERAGE)/AVERAGE * 100
Price Trend:           =SLOPE(F:F, ROW(F:F))
Days Until Departure:  =DEPARTURE_DATE - TODAY()
```

**Conditional Formatting Rules:**

| Condition | Color | Action |
|-----------|-------|--------|
| Price < 90% of average | 🟢 Green | Strong buy signal |
| Price 90-110% of average | 🟡 Yellow | Monitor closely |
| Price > 110% of average | 🔴 Red | Wait for drop |

### Google Sheets Formulas

**Get lowest price for a route:**
```
=MINIFS(F:F, B:B, "SFO-JFK")
```

**Calculate price change percentage:**
```
=((F2-F1)/F1)*100
```

**Count searches in last 7 days:**
```
=COUNTIFS(A:A, ">="&TODAY()-7, A:A, "<="&TODAY())
```

**Price trend indicator:**
```
=IF(SLOPE(F2:F10, ROW(F2:F10))>0, "📈 Rising", "📉 Falling")
```

**Alert when price drops below threshold:**
```
=IF(F2<300, "🚨 BUY NOW", "Keep watching")
```

### Sample Tracking Workflow

1. **Morning check (optional):** Quick scan of tracked routes
2. **Record findings:** Log to spreadsheet immediately
3. **Weekly review:** Analyze trends, adjust strategy
4. **Price alert action:** When notified, verify and book quickly

---

## Additional Tools & Resources

### Recommended Price Alert Services

| Tool | Best For | Price Alerts | Notes |
|------|----------|--------------|-------|
| **Google Flights** | General tracking | ✅ Email | Free, comprehensive |
| **Hopper** | Mobile predictions | ✅ Push | AI-powered forecasting |
| **Skyscanner** | Budget options | ✅ Email | Good for flexible dates |
| **Kayak** | Price history | ✅ Email | Shows historical trends |
| **Scott's Cheap Flights** | Mistake fares | ✅ Email | Premium finds deals for you |
| **Secret Flying** | Error fares | RSS/Email | Requires quick action |

### Browser Extensions (Use Sparingly)

- **Skyscanner extension:** Passive price monitoring
- **Kayak extension:** Price alerts in browser
- **Capital One Shopping:** Sometimes finds lower prices

⚠️ **Warning:** Extensions can increase tracking—use judiciously.

### Mobile Apps for Alerts Only

Set up alerts but avoid browsing:

1. **Hopper:** Best prediction algorithm
2. **Google Travel:** Syncs with web searches
3. **Skyscanner:** Reliable price alerts

---

## Quick Reference Card

### Daily Limits at a Glance

```
╔════════════════════════════════════════╗
║   SAFE DAILY SEARCH LIMITS             ║
╠════════════════════════════════════════╣
║   Per Route:      2 searches max       ║
║   Per Platform:   5 searches max       ║
║   Total Daily:   10 searches max       ║
╚════════════════════════════════════════╝
```

### Pre-Search Checklist

```
╔════════════════════════════════════════╗
║   BEFORE EVERY SEARCH                  ║
╠════════════════════════════════════════╣
║   □ Incognito/Private mode             ║
║   □ VPN connected (recommended)        ║
║   □ Cookies cleared                    ║
║   □ Not logged into airline accounts   ║
║   □ Ready to record prices             ║
╚════════════════════════════════════════╝
```

### When to Book Decision Matrix

```
╔════════════════════════════════════════════════════════╗
║   BOOKING DECISION GUIDE                               ║
╠════════════════════════════════════════════════════════╣
║   Price < 90% of average      →  BOOK NOW              ║
║   Price 90-100% of average    →  Book if 3-4 wks out   ║
║   Price 100-110% of average   →  Wait if time allows   ║
║   Price > 110% of average     →  Definitely wait       ║
║   < 1 week to departure       →  Book regardless       ║
╚════════════════════════════════════════════════════════╝
```

### Weekly Review Checklist

```
□ Review all tracked routes
□ Update spreadsheet with trends
□ Remove expired/booked routes
□ Adjust tracking frequency based on timeline
□ Clean up Google Flights tracked prices
□ Verify alert email settings still working
```

---

## Summary

Effective price monitoring balances diligence with discretion. By following these safe monitoring patterns, you can track prices effectively without triggering the dynamic pricing algorithms that may artificially inflate costs. Remember:

1. **Limit searches** to avoid detection
2. **Rotate platforms** to spread your footprint
3. **Use privacy tools** like incognito mode and VPNs
4. **Track systematically** with a spreadsheet
5. **Act quickly** when you see a good price
6. **Book within optimal windows** for your route type

The goal is to be informed, not obsessive. Set up automated alerts, check manually only when strategic, and trust your data when it's time to book.

---

*Last updated: January 2025*
