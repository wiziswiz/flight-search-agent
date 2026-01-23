# Fare Rule Exploiter Strategy

A comprehensive guide to understanding and leveraging airline fare structures for optimal booking decisions.

## Fare Class Decoder

Airlines use single-letter booking codes to categorize tickets. Understanding these codes is essential for maximizing value.

### First Class
| Code | Type | Mileage Accrual | Upgradability | Notes |
|------|------|-----------------|---------------|-------|
| **F** | Full Fare First | 150% | Base class | Fully refundable, changeable |
| **A** | Discounted First | 150% | High | Often award ticket class |
| **P** | Premium First | 150% | Varies | Ultra-premium cabin on select carriers |

### Business Class
| Code | Type | Mileage Accrual | Upgradability | Notes |
|------|------|-----------------|---------------|-------|
| **J** | Full Fare Business | 150% | Base class | Maximum flexibility |
| **C** | Business | 125-150% | High | Standard business fare |
| **D** | Business Discount | 125% | Medium | Reduced flexibility |
| **I** | Business Discount | 100-125% | Low | Often partner award class |
| **Z** | Deep Discount Business | 100% | Low | Minimal upgrade eligibility |

### Premium Economy
| Code | Type | Mileage Accrual | Upgradability | Notes |
|------|------|-----------------|---------------|-------|
| **W** | Full Fare Premium Economy | 100-150% | To Business | Dedicated premium economy |
| **P** | Premium Economy | 100% | Varies | Carrier-specific usage |
| **E** | Premium Economy Discount | 75-100% | Limited | Restricted changes |

### Economy Class
| Code | Type | Mileage Accrual | Upgradability | Notes |
|------|------|-----------------|---------------|-------|
| **Y** | Full Fare Economy | 100% | To any class | Maximum flexibility, fully refundable |
| **B** | Economy | 100% | High | Often corporate/discount business fallback |
| **M** | Discounted Economy | 100% | Medium | Mid-tier economy |
| **H** | Economy | 75-100% | Medium | Promotional fare class |
| **K** | Economy | 75-100% | Medium | Capacity controlled |
| **L** | Economy | 50-75% | Low | Leisure/low fare |
| **V** | Economy | 50-75% | Low | Visit fares, restricted |
| **S** | Economy | 50% | Low | Student/special fares |
| **N** | Economy | 50% | Very Low | Night/off-peak fares |
| **Q** | Economy | 25-50% | Very Low | Deep discount |
| **O** | Economy | 0-25% | None | Opaque/last-minute |
| **G** | Economy | 0% | None | Group fares |

### Basic Economy
| Code | Type | Mileage Accrual | Upgradability | Notes |
|------|------|-----------------|---------------|-------|
| **B** | Basic Economy (varies) | 50% or less | None | No changes, last to board |
| **E** | Basic Economy | 0-50% | None | Carrier-specific |
| **N** | Basic Economy | 0-25% | None | Most restricted |

> **Note**: Fare class codes vary by airline. Always verify with the specific carrier.

---

## Routing Rules Explanation

Understanding routing rules helps identify opportunities for stopovers, connections, and alternative routings.

### Maximum Permitted Mileage (MPM)

Airlines calculate fares based on direct distance between cities. MPM allows deviation from the direct route.

```
MPM Formula: Direct Mileage × Multiplier (typically 1.20-1.25)

Example: New York to London
- Direct Distance: 3,459 miles
- MPM (at 120%): 4,150 miles
- This allows routing via Dublin, Paris, or other intermediate cities
```

**MPM Exploitation Strategies:**
1. **Free Stopovers**: Stay 24+ hours at connection points within MPM
2. **City Combinations**: Visit multiple destinations on one fare
3. **Backtracking**: Sometimes cheaper to route through a hub

### Global Routing Indicators

Airlines use routing indicators to control permitted paths:

| Indicator | Meaning | Common Routes |
|-----------|---------|---------------|
| **AT** | Atlantic | Americas ↔ Europe/Africa/Middle East |
| **PA** | Pacific | Americas ↔ Asia/Oceania |
| **WH** | Western Hemisphere | Within Americas |
| **EH** | Eastern Hemisphere | Europe/Asia/Africa/Oceania |
| **AP** | Atlantic/Pacific | Round-the-world permitted |
| **TS** | Trans-Siberian | Via Russia |

**Routing Rule Opportunities:**

1. **Circle Trips**: Open-jaw itineraries pricing as round trips
2. **Surface Sectors**: Overland travel between flight segments
3. **Directional Fares**: Different prices for same route in different directions

### Married Segment Logic

Airlines often price segments together ("married") to prevent exploitation:

```
Married Segments: Booked together at combined fare
Divorced Segments: Priced separately (often more expensive)

Example:
NYC-LON-PAR married = $800
NYC-LON separate + LON-PAR separate = $1,400
```

**Exploiting Married Segments:**
- Book entire itinerary to get married pricing
- Add throwaway segments to trigger favorable combinations
- Use codeshare variations for different segment marriages

---

## Pricing Condition Analysis

### Fare Rule Categories (CAT 1-50)

ATPCO defines 50 fare rule categories. Key ones to understand:

| Category | Name | Impact |
|----------|------|--------|
| **CAT 1** | Eligibility | Who can book (age, residency, membership) |
| **CAT 2** | Day/Time | When travel must occur |
| **CAT 3** | Seasonality | Peak/off-peak pricing windows |
| **CAT 4** | Flight Application | Specific flight restrictions |
| **CAT 5** | Advance Purchase | How far ahead to book (AP7, AP14, AP21) |
| **CAT 6** | Minimum Stay | Required time at destination |
| **CAT 7** | Maximum Stay | Deadline for return |
| **CAT 8** | Stopovers | Free or paid intermediate stops |
| **CAT 9** | Transfers | Connection limitations |
| **CAT 10** | Combinations | Mixing fare types |
| **CAT 11** | Blackouts | Dates fare cannot be used |
| **CAT 14** | Travel Restrictions | Route/carrier limitations |
| **CAT 15** | Sales Restrictions | Booking deadlines, channels |
| **CAT 16** | Penalties | Change/cancel fees |
| **CAT 18** | Ticket Endorsements | Transfer restrictions |
| **CAT 19** | Children/Infants | Discounts and rules |
| **CAT 20** | Tour Conductor | Group booking rules |
| **CAT 21** | Agent Discounts | Travel industry rates |
| **CAT 22** | All Other | Miscellaneous rules |
| **CAT 23** | Miscellaneous | Additional provisions |
| **CAT 25** | Fare By Rule | Constructed fare rules |
| **CAT 26** | Groups | Group booking requirements |
| **CAT 27** | Tours | Package tour rules |
| **CAT 28** | Visit Country | Geographic restrictions |
| **CAT 29** | Deposits | Payment requirements |
| **CAT 31** | Voluntary Changes | How changes are handled |
| **CAT 33** | Voluntary Refunds | Refund policies |
| **CAT 35** | Negotiated Fares | Corporate/contract rates |
| **CAT 50** | Application | General fare application |

### Critical Rule Combinations

**Advance Purchase + Saturday Stay:**
```
AP14 + Saturday night stay = 40-60% savings typical
Workaround: Book two one-ways, or sacrifice flexibility
```

**Minimum/Maximum Stay:**
```
Common patterns:
- Min 3 nights for leisure fares
- Max 30 days for discounted business
- Sunday rule: depart Sunday, save money
```

**Seasonality Windows:**
```
Shoulder seasons often unlabeled:
- April 1-15: Often winter pricing
- November 1-20: Often fall pricing
- Check exact cutoff dates in fare rules
```

---

## Hidden Fare Discovery Techniques

### 1. Point of Sale (POS) Arbitrage

Airlines price differently based on booking country:

```
Same Flight: NYC → Tokyo
- Booked from US: $1,200
- Booked from Japan: ¥95,000 (~$890)
- Booked from Brazil: R$4,500 (~$950)
```

**How to Access:**
- Use airline's local website (.jp, .br, .de)
- VPN to simulate local access
- Book through local travel agents
- Set currency/language preferences

**Best POS Markets:**
- Eastern Europe for European travel
- South America for US departures
- Southeast Asia for premium cabins
- Middle East for East Africa routes

### 2. Hidden City Ticketing

Book beyond your destination when it's cheaper:

```
Goal: NYC to Denver
Direct fare: $450

Hidden city option:
NYC → Denver → Phoenix: $280
Deplane in Denver, skip Phoenix segment
```

**Rules:**
- Only works one-way or on final segment
- No checked bags (will go to final destination)
- Risk: airline may cancel return/future bookings
- Never do on outbound of round-trip

### 3. Throwaway Ticketing

Add unused segments to reduce fare:

```
Goal: NYC → London one-way
One-way fare: $1,800

Throwaway option:
NYC → London → Dublin: $650
Discard Dublin segment
```

**Ideal Scenarios:**
- One-way international travel
- Last-minute bookings
- Premium cabin positioning

### 4. Fuel Dump Routes

Add segments that eliminate fuel surcharges:

```
Standard: NYC → London = $800 fare + $600 fuel surcharge

Fuel dump routing:
NYC → Bucharest → London (on separate ticket return)
Eliminates carrier fuel surcharge through routing rules
```

**Known Fuel Dump Gateways:**
- Bucharest (OTP) - many European carriers
- Belgrade (BEG) - effective for Lufthansa Group
- Cairo (CAI) - Middle Eastern routing
- Addis Ababa (ADD) - African connections

> **Caution**: Airlines actively combat fuel dumping. Rules change frequently.

### 5. Ex-Destination Pricing

Price itinerary starting from destination:

```
Goal: NYC → Paris round trip
Standard booking: $1,200

Ex-Paris booking:
Paris → NYC → Paris: $800
Start trip from return segment
```

**Requirements:**
- Must position to start point (or have separate reason to be there)
- Price difference must justify positioning cost
- Check if fare allows beginning from second city

### 6. Sixth Freedom Arbitrage

Use connecting carriers' pricing advantages:

```
Goal: NYC → Bangkok

Direct carriers (United, Thai): $1,400

Sixth freedom options:
- NYC → Istanbul → Bangkok (Turkish): $850
- NYC → Doha → Bangkok (Qatar): $900
- NYC → Dubai → Bangkok (Emirates): $880
```

**Top Sixth Freedom Carriers:**
- Turkish Airlines (IST hub)
- Qatar Airways (DOH hub)
- Emirates (DXB hub)
- Ethiopian Airlines (ADD hub)
- Finnair (HEL hub - Asia routes)

---

## Booking Class Selection Strategy

### Decision Framework

```
┌─────────────────────────────────────────────────────────┐
│                 BOOKING CLASS SELECTOR                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. What's your FLEXIBILITY need?                       │
│     ├─ High: Book Y/J/F (full fare)                     │
│     ├─ Medium: Book B/M/H                               │
│     └─ Low: Accept Q/V/L restrictions                   │
│                                                          │
│  2. What's your MILEAGE priority?                       │
│     ├─ Earning status: Target 100%+ classes             │
│     ├─ Maintaining status: Calculate MPQ impact         │
│     └─ Award booking: Any class works                   │
│                                                          │
│  3. What's your UPGRADE strategy?                       │
│     ├─ Complimentary: Need Y/B/M minimum                │
│     ├─ Paid upgrade: Most economy classes work          │
│     └─ Instrument upgrade: Check class eligibility      │
│                                                          │
│  4. What's your CHANGE likelihood?                      │
│     ├─ Certain trip: Book deepest discount              │
│     ├─ Possible change: Factor change fee into fare     │
│     └─ Likely change: Book flexible fare class          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Airline-Specific Variations

#### United Airlines
| Class | Cabin | PQP | PQF Credit | Upgrade Priority |
|-------|-------|-----|------------|------------------|
| Y/B | Economy | Full | Yes | Highest |
| M/E/U/H | Economy | Full | Yes | High |
| Q/V/W | Economy | Full | Yes | Medium |
| S/T/L/K/G | Economy | Full | Yes | Low |
| N | Basic | Reduced | No | None |

#### American Airlines
| Class | Cabin | AAdvantage | Upgrade List |
|-------|-------|------------|--------------|
| Y/B/M | Economy | 100% | Priority |
| H/K/Q | Economy | 100% | Standard |
| V/L/G | Economy | 100% | Low |
| O/S/N | Discount | 50-100% | Limited |

#### Delta Air Lines
| Class | Cabin | MQM | MQD | Upgrade |
|-------|-------|-----|-----|---------|
| Y/B/M | Economy | Full | Full | Yes |
| H/Q/K | Economy | Full | Full | Yes |
| L/U/T | Economy | Full | Full | Limited |
| X/V | Economy | Full | Full | No |
| E | Basic | Reduced | Reduced | No |

#### British Airways
| Class | Cabin | Avios | Tier Points |
|-------|-------|-------|-------------|
| J/C/D | Club | 150% | 140 |
| I/R | Club | 125% | 80 |
| Y/B/H | Economy | 100% | 40 |
| K/M/L | Economy | 50% | 25 |
| V/N/Q/O | Economy | 25% | 10 |
| G | Group | 25% | 10 |

#### Emirates
| Class | Cabin | Skywards | Tier Miles |
|-------|-------|----------|------------|
| F/A | First | 200% | 200% |
| J/C | Business | 175% | 175% |
| I/O | Business | 150% | 150% |
| Y/B/H | Economy | 100% | 100% |
| K/M/Q | Economy | 75% | 75% |
| L/V/U | Economy | 50% | 50% |
| T/W | Economy | 25% | 25% |
| X/E/G | Saver | 25% | 0% |

#### Singapore Airlines
| Class | Cabin | KrisFlyer | Elite Miles |
|-------|-------|-----------|-------------|
| F/A/R | Suites/First | 150% | 150% |
| J/C/D | Business | 150% | 150% |
| Z/I | Business | 125% | 125% |
| Y/B/M | Economy | 100% | 100% |
| H/Q | Economy | 75% | 50% |
| K/L/V | Economy | 50% | 25% |
| S/N/T | Economy | 25% | 0% |

---

## Advanced Techniques

### Mixed-Cabin Bookings

```
Scenario: Need business class on longest segment only

Strategy:
Book: Economy → Business → Economy
Price often cheaper than business round-trip
Mileage accrual varies by segment
```

### Split Ticketing

```
Scenario: Round-trip with different carriers optimal each direction

Strategy:
Outbound: Carrier A one-way
Return: Carrier B one-way
Often $200-500 savings vs. forced round-trip
```

### Positioning Flights

```
Scenario: Better fares from nearby city

Strategy:
Instead of: Home City → Destination ($1,200)
Book: Nearby Hub → Destination ($650)
Add: Home → Nearby Hub ($150 positioning)
Total: $800 (save $400)
```

### Saturday Night Straddle

```
Scenario: Business trip requires Saturday stay for discount

Workaround:
Trip 1: Depart Tue, Return following Mon
Trip 2: Depart Tue, Return following Mon
Offset trips to create artificial Saturday stays
```

---

## Quick Reference Card

### Fare Class Hierarchy (Typical)

```
Premium                          Economy
   ↓                                ↓
F → A → J → C → D → I → Z → W → Y → B → M → H → K → L → V → S → N → Q → O → G
|___|   |___________________|   |___|   |___________________________|   |___|
First        Business          Prem.            Economy               Basic
```

### Decision Checklist

Before booking any fare:

- [ ] **Compare POS**: Check pricing from 3+ countries
- [ ] **Check routing**: Can MPM enable a free stopover?
- [ ] **Verify class**: Confirm mileage earning rate
- [ ] **Calculate value**: Price ÷ miles earned = cents per mile
- [ ] **Review rules**: Note change/cancel policies
- [ ] **Consider timing**: AP requirements met?
- [ ] **Check alternatives**: Hidden city, throwaway, fuel dump viable?
- [ ] **Validate upgrade path**: Is class upgrade-eligible?

### Red Flags in Fare Rules

- "NON-REFUNDABLE" in CAT 33
- "CHANGES NOT PERMITTED" in CAT 31
- "NO SHOW" penalties exceeding ticket value
- "COMBINABILITY: NONE" limiting connections
- Specific carrier restrictions in CAT 14
- Blackout dates spanning your travel window

### Money-Saving Priority

1. **POS arbitrage** - Easiest, safest, often 15-30% savings
2. **Sixth freedom routing** - Reliable, adds travel time
3. **Throwaway ticketing** - Moderate risk, effective for one-ways
4. **Hidden city** - Higher risk, one-way only
5. **Fuel dumping** - Complex, rules change frequently

---

## Glossary

| Term | Definition |
|------|------------|
| **AP** | Advance Purchase requirement |
| **ATPCO** | Airline Tariff Publishing Company |
| **Bucket** | Inventory allocation for fare class |
| **Fare Basis** | Full code describing fare rules (e.g., YOW14) |
| **GDS** | Global Distribution System (Sabre, Amadeus, Travelport) |
| **Married Segment** | Flights priced together as unit |
| **MPM** | Maximum Permitted Mileage |
| **POS** | Point of Sale (booking location) |
| **PQM/PQP** | Premier Qualifying Miles/Points |
| **RBD** | Revenue Booking Designator (fare class letter) |
| **YQ/YR** | Carrier-imposed surcharges (often fuel) |

---

*Last updated: January 2026*
