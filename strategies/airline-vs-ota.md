# Airline vs OTA: Flight Search Strategy Guide

A comprehensive comparison of direct airline booking versus Online Travel Agency (OTA) platforms for optimal flight search automation.

---

## Table of Contents

1. [Direct Airline Search Automation](#direct-airline-search-automation)
2. [Major OTA Platform Comparison](#major-ota-platform-comparison)
3. [Regional Site Discovery](#regional-site-discovery)
4. [Fee & Markup Analysis](#fee--markup-analysis)
5. [Platform Recommendation Logic](#platform-recommendation-logic)

---

## Direct Airline Search Automation

### When to Book Direct

Direct airline booking is optimal when:
- **Price matching**: Airline matches or beats OTA prices (common for domestic)
- **Complex itineraries**: Multi-city trips with specific routing
- **Loyalty programs**: Accumulating miles/status matters
- **Schedule changes**: Direct bookings get better rebooking treatment
- **Southwest Airlines**: Never appears on OTAs - must book direct

### Airline API/Automation Approaches

#### Tier 1: Official APIs
| Airline | API Type | Access | Notes |
|---------|----------|--------|-------|
| United | REST API | Developer program | NDC-compliant, requires approval |
| Delta | Partner API | Commercial only | Limited public access |
| American | NDC API | Commercial partners | Certification required |
| Lufthansa Group | Open API | Public registration | Covers LH, Swiss, Austrian |
| British Airways | NDC API | Partner program | Requires BA partnership |

#### Tier 2: Scraping Targets (Ethical Use)
```
Primary targets for price monitoring:
├── Southwest.com (essential - no OTA coverage)
├── AlaskaAir.com (Alaska-specific routes)
├── JetBlue.com (often has direct-only deals)
└── Spirit/Frontier (for ultra-low-cost monitoring)
```

#### Tier 3: Aggregated Direct Search
Use Google ITA Matrix for multi-airline direct pricing without booking:
- Queries airline GDS directly
- Shows base fares before fees
- Useful for fare class research

### Direct Booking Automation Workflow

```
1. DISCOVER: Use meta-search to identify best carriers for route
2. VERIFY: Query airline direct for current pricing
3. COMPARE: Calculate true cost (base + fees + opportunity cost)
4. BOOK: Execute on platform offering best total value
```

---

## Major OTA Platform Comparison

### Platform Overview Matrix

| Feature | Google Flights | Kayak | Skyscanner | Expedia |
|---------|---------------|-------|------------|---------|
| **Type** | Meta-search | Meta-search | Meta-search | Full OTA |
| **Booking** | Redirects | Both | Redirects | Direct |
| **Price Alerts** | ✅ Excellent | ✅ Good | ✅ Good | ⚠️ Basic |
| **Fare Calendar** | ✅ Best | ✅ Good | ✅ Good | ⚠️ Limited |
| **Hidden City** | ❌ | ⚠️ Limited | ❌ | ❌ |
| **Hacker Fares** | ❌ | ✅ Yes | ❌ | ❌ |
| **Error Fares** | ❌ | ⚠️ Rare | ✅ Community | ❌ |
| **API Access** | ❌ | Affiliate | Affiliate | Affiliate |
| **Mobile App** | ✅ Excellent | ✅ Good | ✅ Good | ✅ Good |
| **Flexibility Filter** | ✅ Yes | ✅ Yes | ⚠️ Basic | ⚠️ Basic |

### Detailed Platform Analysis

#### Google Flights
**Best For**: Initial price discovery, date flexibility analysis, tracking

**Strengths**:
- Fastest search engine
- Best date matrix/calendar view
- Price trend predictions
- Clean, intuitive interface
- Tracks prices automatically
- Shows "typical" price ranges

**Weaknesses**:
- Cannot book directly (always redirects)
- Missing some budget carriers
- No hacker fare combinations
- Limited to mainstream OTAs for redirects

**Automation Value**: ⭐⭐⭐⭐⭐
- Easy to scrape price data
- Reliable tracking via Google account
- Structured data in page source

#### Kayak
**Best For**: Hacker fares, comprehensive search, price forecasting

**Strengths**:
- "Hacker Fares" combine one-way tickets for savings
- Price forecasting with buy/wait recommendations
- Flexible date grid
- Includes budget carriers
- Trip.com integration
- Explore feature for open-ended search

**Weaknesses**:
- Interface can be cluttered
- Some prices higher than direct
- Price alerts less reliable than Google

**Automation Value**: ⭐⭐⭐⭐
- API available for affiliates
- Hacker fare logic unique value
- Good for price comparison automation

#### Skyscanner
**Best For**: International flights, budget carriers, "Everywhere" search

**Strengths**:
- "Everywhere" feature for cheapest destinations
- Best budget carrier coverage (especially Europe)
- Month-view calendar for flexibility
- Strong international coverage
- Community-reported deals
- Multiple currency support

**Weaknesses**:
- Sometimes shows unavailable fares
- Redirect booking can fail
- Less reliable price accuracy
- Customer support is minimal

**Automation Value**: ⭐⭐⭐⭐⭐
- Affiliate API available
- "Everywhere" API enables deal discovery
- Best for multi-country automation

#### Expedia
**Best For**: Package deals, hotel bundles, one-stop booking

**Strengths**:
- Flight + Hotel bundles often cheaper
- Loyalty program (Expedia Rewards)
- Customer service for issues
- Price match guarantee
- Bundle flexibility

**Weaknesses**:
- Base flight prices 3-8% higher typically
- Less comprehensive search
- Booking changes difficult
- Hidden fees in bundles

**Automation Value**: ⭐⭐⭐
- Affiliate API available
- Better for package automation
- Not ideal for flight-only

### Quick Selection Guide

```
Question: What's your primary goal?

├── "Find cheapest flight anywhere"
│   └── Use: Skyscanner "Everywhere"
│
├── "Specific route, best price"
│   └── Use: Google Flights → Compare at Kayak
│
├── "Need flexibility to change"
│   └── Use: Book direct with airline
│
├── "Complex multi-city trip"
│   └── Use: Kayak Hacker Fares or ITA Matrix
│
├── "Flight + Hotel package"
│   └── Use: Expedia or Priceline
│
└── "Southwest route"
    └── Use: Southwest.com directly
```

---

## Regional Site Discovery

### Europe

| Platform | Coverage | Special Feature | Best For |
|----------|----------|-----------------|----------|
| **Momondo** | Pan-European | Price comparison | Budget airlines |
| **Kiwi.com** | Global | Self-transfer flights | Creative routing |
| **azair.eu** | Europe LCCs | Multi-destination | Budget exploration |
| **Eurowings** | Europe | German base | Lufthansa alternatives |
| **Ryanair** | Europe/N.Africa | Direct only | Ultra-low-cost |
| **easyJet** | Europe | Direct only | UK connections |
| **Transavia** | Europe | Direct only | Netherlands/France |
| **Vueling** | Europe | Spain focus | Iberia connections |
| **Wizz Air** | E.Europe | Direct only | Eastern European routes |

### Asia-Pacific

| Platform | Coverage | Special Feature | Best For |
|----------|----------|-----------------|----------|
| **Trip.com** | Asia-Pacific | China connections | Asian carriers |
| **Ctrip** | China | Domestic China | Chinese routes |
| **Traveloka** | SE Asia | Regional focus | Indonesia/SEA |
| **Webjet** | Australia/NZ | Oceania focus | Aus domestic |
| **Makemytrip** | India | Indian carriers | India routes |
| **AirAsia** | SE Asia | Direct only | ASEAN ultra-LCC |
| **Scoot** | Asia | Direct only | Singapore-based LCC |
| **Cebu Pacific** | Philippines | Direct only | Philippine routes |
| **VietJet** | Vietnam | Direct only | Vietnam domestic |
| **IndiGo** | India | Direct only | India domestic |

### Americas

| Platform | Coverage | Special Feature | Best For |
|----------|----------|-----------------|----------|
| **Hopper** | N.America | Price prediction | Mobile-first users |
| **Priceline** | Americas | Name Your Price | Last-minute deals |
| **Orbitz** | Americas | Expedia-owned | US domestic |
| **StudentUniverse** | Global | Student fares | Students/under-26 |
| **Volaris** | Mexico | Direct only | Mexico routes |
| **LATAM** | S.America | Direct only | South American hub |
| **Avianca** | C/S America | Direct only | Colombia hub |
| **Azul** | Brazil | Direct only | Brazil domestic |
| **Copa** | C.America | Direct only | Panama hub |
| **JetSmart** | S.America | Direct only | Chile ultra-LCC |

### Middle East & Africa

| Platform | Coverage | Special Feature | Best For |
|----------|----------|-----------------|----------|
| **Wego** | MENA | Regional focus | Middle East routes |
| **Cleartrip** | MENA/India | Regional focus | India-Gulf |
| **Almosafer** | Saudi | Saudi focus | KSA routes |
| **flydubai** | MENA | Direct only | Dubai LCC |
| **Air Arabia** | MENA | Direct only | Sharjah LCC |
| **FlySafair** | S.Africa | Direct only | South Africa LCC |
| **Kulula** | S.Africa | Direct only | South Africa |
| **Kenya Airways** | E.Africa | Direct only | East African hub |

### Specialty Platforms

| Platform | Niche | Value Proposition |
|----------|-------|-------------------|
| **SecretFlying** | Error fares | Mistake fare alerts |
| **Scott's Cheap Flights** | Deals | Curated deal alerts |
| **The Points Guy** | Miles | Award travel optimization |
| **AwardHacker** | Miles | Best award redemptions |
| **ExpertFlyer** | Upgrades | Seat/upgrade alerts |
| **Skiplagged** | Hidden city | Hidden city finder |

---

## Fee & Markup Analysis

### True Cost Calculation

The advertised price rarely reflects total cost. Calculate true cost with:

```
TRUE_COST = Base Fare
          + Carrier-Imposed Fees
          + Booking Fees
          + Payment Fees
          + Baggage Fees
          + Seat Selection
          + Taxes & Surcharges
          - Loyalty Value
          - Credit Card Benefits
```

### Fee Comparison by Channel

| Fee Type | Airline Direct | Meta-Search | Full OTA |
|----------|---------------|-------------|----------|
| Base Fare | Reference | Same/Lower | +3-8% |
| Booking Fee | $0 | $0 | $0-35 |
| Payment Fee | 0-2.5% | Varies | 0-3% |
| Change Fee | Standard | N/A | +$25-75 |
| Cancel Fee | Standard | N/A | +$50-100 |
| Customer Service | Direct | None | Intermediary |
| Price Match | Some | N/A | Usually yes |

### OTA Markup Analysis

| Platform | Typical Markup | Notes |
|----------|---------------|-------|
| Google Flights | 0% | Redirects to source |
| Kayak | 0-2% | Redirects mostly |
| Skyscanner | 0-3% | Some partner markups |
| Expedia | 3-8% | Full service included |
| Priceline | 2-5% | Varies by product |
| Orbitz | 3-7% | Similar to Expedia |
| Kiwi.com | 5-15% | Self-transfer risk included |
| Budget OTAs | 10-20% | High-risk platforms |

### Baggage Fee Matrix (Major US Carriers, 2024-2025)

| Carrier | Carry-On | First Checked | Second Checked |
|---------|----------|--------------|----------------|
| **Basic Economy** | | | |
| United | Free | $35-45 | $45-55 |
| Delta | Free | $35-45 | $45-55 |
| American | Free | $35-40 | $45-50 |
| **Main Cabin** | | | |
| United | Free | $0 (CC) or $35 | $45 |
| Delta | Free | $0 (CC) or $35 | $45 |
| American | Free | $0 (CC) or $35 | $45 |
| **Ultra Low-Cost** | | | |
| Spirit | $35-65 | $35-55 | $45-65 |
| Frontier | $35-60 | $35-50 | $45-60 |
| Allegiant | $35-75 | $35-60 | $50-75 |

*Note: CC = Airline co-branded credit card benefit*

### Hidden Fee Red Flags

Watch for these often-overlooked costs:

| Fee Type | Where Hidden | Amount |
|----------|--------------|--------|
| Payment processing | Checkout | 2-3% |
| Travel insurance | Pre-checked | $30-80 |
| SMS notifications | Pre-checked | $1-3 |
| Priority boarding | Upsell | $15-40 |
| Seat selection | Post-booking | $5-150 |
| Name correction | Post-booking | $50-300 |
| Third-party rebooking | Change | $75-200 |

---

## Platform Recommendation Logic

### Decision Algorithm

```python
def recommend_platform(trip_params):
    """
    Returns optimal platform based on trip characteristics.
    """

    # Rule 1: Southwest routes must be direct
    if "WN" in trip_params.preferred_carriers or is_southwest_route(trip_params):
        return "Southwest.com (direct only)"

    # Rule 2: Package deals favor OTAs
    if trip_params.needs_hotel:
        if trip_params.budget_conscious:
            return "Priceline (bundle deals)"
        return "Expedia (package reliability)"

    # Rule 3: European budget carriers
    if trip_params.region == "Europe" and trip_params.budget_conscious:
        return "Skyscanner (best LCC coverage)"

    # Rule 4: Asia-Pacific routes
    if trip_params.region == "Asia":
        if "China" in trip_params.destinations:
            return "Trip.com (best China coverage)"
        return "Skyscanner + Google Flights"

    # Rule 5: Complex itineraries
    if len(trip_params.segments) > 2:
        if trip_params.flexible_dates:
            return "Kayak Hacker Fares"
        return "ITA Matrix → Book direct"

    # Rule 6: Standard search
    if trip_params.needs_flexibility:
        return "Google Flights → Book direct"

    # Rule 7: Price optimization
    return "Google Flights → Kayak → Best price source"
```

### Decision Flowchart

```
                    ┌─────────────────────┐
                    │   START: New Trip   │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Is it a Southwest   │
                    │     route?          │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │ YES                        NO   │
              ▼                                 ▼
    ┌─────────────────┐              ┌─────────────────┐
    │ Southwest.com   │              │ Need hotel too? │
    │ (no alternatives│              └────────┬────────┘
    └─────────────────┘                       │
                                 ┌────────────┼────────────┐
                                 │ YES                 NO  │
                                 ▼                         ▼
                      ┌─────────────────┐      ┌──────────────────┐
                      │ Expedia/        │      │ International?   │
                      │ Priceline       │      └────────┬─────────┘
                      │ (bundles)       │               │
                      └─────────────────┘    ┌──────────┼──────────┐
                                             │ YES              NO │
                                             ▼                     ▼
                                  ┌─────────────────┐   ┌─────────────────┐
                                  │ Which region?   │   │ Google Flights  │
                                  └────────┬────────┘   │ + Kayak         │
                                           │            └─────────────────┘
                    ┌──────────────────────┼──────────────────────┐
                    │ EUROPE          ASIA-PAC            OTHER   │
                    ▼                    ▼                    ▼
          ┌─────────────────┐ ┌─────────────────┐   ┌─────────────────┐
          │ Skyscanner      │ │ Trip.com +      │   │ Google Flights  │
          │ (LCC coverage)  │ │ Skyscanner      │   │ + Regional      │
          └─────────────────┘ └─────────────────┘   └─────────────────┘
```

### Quick Reference Matrix

| Scenario | Primary Platform | Secondary | Avoid |
|----------|-----------------|-----------|-------|
| US Domestic | Google Flights | Kayak | High-markup OTAs |
| Southwest route | Southwest.com | — | All OTAs |
| Europe LCC | Skyscanner | azair.eu | Expedia |
| Asia routes | Trip.com | Skyscanner | US-based OTAs |
| Package deal | Expedia | Priceline | Meta-search |
| Error fares | SecretFlying | Skyscanner | Direct booking |
| Complex routing | ITA Matrix | Kayak | Basic OTAs |
| Last-minute | Google Flights | Hopper | Advance-only OTAs |
| Student travel | StudentUniverse | Kayak | Full-price OTAs |
| Business class | Google Flights | ExpertFlyer | Budget OTAs |
| Award flights | AwardHacker | Airline direct | Cash OTAs |
| Hidden city | Skiplagged | — | OTA tracking |

### Search Workflow Recommendation

**Optimal multi-platform strategy:**

```
Phase 1: DISCOVERY (5 minutes)
├── Google Flights: Check base prices + date flexibility
├── Skyscanner "Everywhere": Identify cheapest options
└── Note: Best 2-3 price points and carriers

Phase 2: DEEP SEARCH (10 minutes)
├── Kayak: Check Hacker Fares for savings
├── Trip.com: If Asia routes, check regional pricing
├── Regional OTAs: If specialty route identified
└── Note: Any price beats from Phase 1

Phase 3: VERIFICATION (5 minutes)
├── Airline direct: Verify price matches OTA best
├── Calculate: True cost including all fees
├── Check: Credit card portal for bonus points
└── Decision: Book on best total-value platform

Phase 4: PROTECTION (2 minutes)
├── Set price alert on Google Flights
├── Know cancellation policy
└── Save confirmation details
```

---

## Summary: Key Principles

1. **Search everywhere, book direct when possible** - OTAs for discovery, airlines for reliability

2. **Southwest is special** - Always check Southwest.com directly; never appears on OTAs

3. **True cost matters** - Base price is meaningless without calculating fees

4. **Region dictates platform** - European LCCs need Skyscanner; Asia needs Trip.com

5. **Hacker fares save money** - Kayak's split-ticket bookings often beat round-trips

6. **Meta-search beats OTA** - Google Flights and Skyscanner redirect without markup

7. **Bundles can win** - Flight+hotel on Expedia sometimes beats separate booking

8. **Loyalty has value** - Factor in miles/status when comparing prices

9. **Flexibility is worth money** - Direct bookings handle changes better

10. **Automate discovery, manual booking** - Use tools for alerts, humans for purchasing

---

*Last updated: January 2025*
*This guide is for informational purposes. Always verify current pricing and policies before booking.*
