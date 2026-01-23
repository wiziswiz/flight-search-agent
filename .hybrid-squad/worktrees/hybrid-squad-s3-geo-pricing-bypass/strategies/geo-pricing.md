# Geo-Pricing Bypass Strategy

Geographic pricing (geo-pricing) is a common practice where airlines and OTAs display different prices based on the user's perceived location. This strategy document outlines techniques for identifying and capturing regional price variations to find optimal booking locations.

## Table of Contents

1. [Understanding Geo-Pricing Signals](#understanding-geo-pricing-signals)
2. [Multi-Country Price Simulation](#multi-country-price-simulation)
3. [Currency Conversion Analysis](#currency-conversion-analysis)
4. [Regional Booking Sites](#regional-booking-sites)
5. [Legal VPN Guidance](#legal-vpn-guidance)
6. [Comparison Matrix Output Format](#comparison-matrix-output-format)

---

## Understanding Geo-Pricing Signals

Airlines and OTAs determine user location through multiple signals:

| Signal | Priority | How It's Detected | How to Simulate |
|--------|----------|-------------------|-----------------|
| IP Address | Primary | GeoIP databases | VPN/Proxy |
| Browser Language | High | `Accept-Language` header | Browser settings |
| Currency Setting | High | Explicit selection or cookie | URL parameter/cookie |
| Country/Market Parameter | High | URL path or parameter | Modify `gl`, `market`, `pos` params |
| GPS/Device Location | Medium | Browser Geolocation API | Deny permission or spoof |
| Account Country | Medium | Registration details | Use regional account |
| Payment Method | Low | Card issuing country | Use regional payment |

### Key Parameters by Platform

```
Google Flights:  ?hl=en&gl=AR&curr=ARS  (language, country, currency)
Skyscanner:      /transport/flights/[from]/[to]/?market=AR&currency=ARS&locale=es-AR
Kayak:           kayak.com.ar (regional domain)
Expedia:         ?currency=ARS&langid=1033&siteid=11 (site ID determines market)
Momondo:         momondo.com.ar (regional domain)
```

---

## Multi-Country Price Simulation

### Country Tier System

Based on typical price variation potential, countries are grouped into tiers:

#### Tier 1: High Discount Potential (20-40% savings)

| Country | Currency | Why Cheaper | Best For |
|---------|----------|-------------|----------|
| Argentina | ARS | High inflation, algorithm lag | International flights |
| India | INR | Large domestic market, competitive pricing | Asia-Pacific routes |
| Turkey | TRY | Currency devaluation, regional hub | Europe-Middle East |
| Brazil | BRL | Large market, currency fluctuations | Americas routes |
| Mexico | MXN | Competitive market, peso fluctuations | Americas routes |

#### Tier 2: Moderate Discount Potential (10-25% savings)

| Country | Currency | Why Cheaper | Best For |
|---------|----------|-------------|----------|
| Poland | PLN | Eastern Europe pricing | European routes |
| Thailand | THB | Southeast Asia hub pricing | Asia-Pacific |
| Colombia | COP | Emerging market pricing | Latin America |
| South Africa | ZAR | Regional market pricing | Africa routes |
| Malaysia | MYR | Budget carrier competition | Southeast Asia |

#### Tier 3: Baseline/Reference Markets

| Country | Currency | Notes |
|---------|----------|-------|
| United States | USD | Global baseline reference |
| United Kingdom | GBP | European baseline |
| Australia | AUD | Oceania baseline |
| Japan | JPY | East Asia baseline |
| Germany | EUR | Eurozone baseline |

### Simulation Methodology

```python
# Multi-country price simulation workflow

TIER_1_COUNTRIES = [
    {"code": "AR", "currency": "ARS", "locale": "es-AR", "name": "Argentina"},
    {"code": "IN", "currency": "INR", "locale": "en-IN", "name": "India"},
    {"code": "TR", "currency": "TRY", "locale": "tr-TR", "name": "Turkey"},
    {"code": "BR", "currency": "BRL", "locale": "pt-BR", "name": "Brazil"},
    {"code": "MX", "currency": "MXN", "locale": "es-MX", "name": "Mexico"},
]

TIER_2_COUNTRIES = [
    {"code": "PL", "currency": "PLN", "locale": "pl-PL", "name": "Poland"},
    {"code": "TH", "currency": "THB", "locale": "th-TH", "name": "Thailand"},
    {"code": "CO", "currency": "COP", "locale": "es-CO", "name": "Colombia"},
    {"code": "ZA", "currency": "ZAR", "locale": "en-ZA", "name": "South Africa"},
    {"code": "MY", "currency": "MYR", "locale": "ms-MY", "name": "Malaysia"},
]

async def simulate_geo_pricing(flight_search_params: dict) -> list:
    """
    Simulate searches from multiple countries and collect prices.

    Args:
        flight_search_params: Origin, destination, dates, passengers

    Returns:
        List of prices by country with USD equivalent
    """
    results = []

    # Always include user's home country as baseline
    countries_to_check = TIER_1_COUNTRIES + TIER_2_COUNTRIES

    for country in countries_to_check:
        # Configure browser/request for this country
        config = {
            "vpn_country": country["code"],
            "accept_language": country["locale"],
            "currency": country["currency"],
            "market_param": country["code"],
        }

        # Execute search with geo configuration
        local_price = await search_with_config(flight_search_params, config)

        # Convert to USD for comparison
        usd_price = convert_to_usd(local_price, country["currency"])

        results.append({
            "country": country["name"],
            "country_code": country["code"],
            "local_price": local_price,
            "local_currency": country["currency"],
            "usd_equivalent": usd_price,
        })

    # Sort by USD price
    results.sort(key=lambda x: x["usd_equivalent"])

    return results
```

### Browser Configuration Checklist

When simulating a specific country:

- [ ] Connect to VPN server in target country
- [ ] Clear all cookies and local storage
- [ ] Set browser language to target locale
- [ ] Disable WebRTC to prevent IP leak
- [ ] Set timezone to target country
- [ ] Use regional domain variant if available
- [ ] Set currency parameter explicitly

---

## Currency Conversion Analysis

### Real-Time Exchange Rate Sources

| Source | API | Rate Type | Update Frequency |
|--------|-----|-----------|------------------|
| exchangerate-api.com | Free tier available | Mid-market | Daily |
| Open Exchange Rates | API key required | Mid-market | Hourly |
| XE.com | Scraping only | Mid-market | Real-time |
| Google Finance | No official API | Mid-market | Real-time |
| Wise (TransferWise) | API available | Transfer rate | Real-time |

### Arbitrage Detection Algorithm

```python
import aiohttp
from decimal import Decimal, ROUND_HALF_UP

class CurrencyArbitrageDetector:
    def __init__(self):
        self.exchange_rates = {}
        self.airline_rates = {}

    async def fetch_market_rates(self):
        """Fetch current mid-market exchange rates."""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.exchangerate-api.com/v4/latest/USD"
            ) as resp:
                data = await resp.json()
                self.exchange_rates = data["rates"]

    def calculate_arbitrage(
        self,
        price_local: Decimal,
        currency: str,
        price_usd_displayed: Decimal
    ) -> dict:
        """
        Detect pricing arbitrage between local currency and USD display.

        Args:
            price_local: Price shown in local currency
            currency: Local currency code
            price_usd_displayed: Price shown when viewing in USD

        Returns:
            Arbitrage analysis with savings potential
        """
        market_rate = Decimal(str(self.exchange_rates.get(currency, 1)))

        # Convert local price to USD at market rate
        local_to_usd = (price_local / market_rate).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        # Calculate implied airline exchange rate
        if price_local > 0:
            airline_rate = price_local / price_usd_displayed
        else:
            airline_rate = market_rate

        # Calculate arbitrage
        savings_usd = price_usd_displayed - local_to_usd
        savings_percent = (
            (savings_usd / price_usd_displayed) * 100
        ).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)

        return {
            "local_price": float(price_local),
            "currency": currency,
            "market_rate": float(market_rate),
            "airline_implied_rate": float(airline_rate),
            "rate_difference_percent": float(
                ((airline_rate - market_rate) / market_rate) * 100
            ),
            "local_in_usd_market": float(local_to_usd),
            "usd_displayed": float(price_usd_displayed),
            "potential_savings_usd": float(savings_usd),
            "potential_savings_percent": float(savings_percent),
            "arbitrage_exists": savings_percent > 2,  # >2% threshold
        }


# Usage example
async def analyze_pricing():
    detector = CurrencyArbitrageDetector()
    await detector.fetch_market_rates()

    # Example: Flight shows ARS 150,000 or USD 500
    result = detector.calculate_arbitrage(
        price_local=Decimal("150000"),
        currency="ARS",
        price_usd_displayed=Decimal("500")
    )

    if result["arbitrage_exists"]:
        print(f"Arbitrage opportunity: {result['potential_savings_percent']}% savings")
        print(f"Book in {result['currency']} for ${result['local_in_usd_market']}")
```

### Currency Arbitrage Scenarios

| Scenario | Description | Action |
|----------|-------------|--------|
| Favorable Arbitrage | Local price converts to less USD than displayed USD price | Book in local currency with Wise or similar |
| Unfavorable Arbitrage | Local price converts to more USD than displayed USD price | Book in USD or find better market |
| Neutral | Prices are equivalent within 2% | Book in preferred currency |

### Payment Card Considerations

- **Dynamic Currency Conversion (DCC)**: Always decline; pay in local currency
- **Foreign Transaction Fees**: Use cards with 0% FX fees (Wise, Revolut, Capital One)
- **Exchange Rate Timing**: Lock rate at booking time if possible
- **Chargeback Rights**: Verify consumer protections apply for foreign transactions

---

## Regional Booking Sites

### Momondo Regional Variants

| Region | Domain | Currency | Language |
|--------|--------|----------|----------|
| Argentina | momondo.com.ar | ARS | Spanish |
| Australia | momondo.com.au | AUD | English |
| Brazil | momondo.com.br | BRL | Portuguese |
| Canada | momondo.ca | CAD | English/French |
| Chile | momondo.cl | CLP | Spanish |
| Colombia | momondo.com.co | COP | Spanish |
| Denmark | momondo.dk | DKK | Danish |
| Finland | momondo.fi | EUR | Finnish |
| France | momondo.fr | EUR | French |
| Germany | momondo.de | EUR | German |
| India | momondo.in | INR | English |
| Italy | momondo.it | EUR | Italian |
| Mexico | momondo.com.mx | MXN | Spanish |
| Netherlands | momondo.nl | EUR | Dutch |
| New Zealand | momondo.co.nz | NZD | English |
| Norway | momondo.no | NOK | Norwegian |
| Poland | momondo.pl | PLN | Polish |
| Portugal | momondo.pt | EUR | Portuguese |
| Spain | momondo.es | EUR | Spanish |
| Sweden | momondo.se | SEK | Swedish |
| Turkey | momondo.com.tr | TRY | Turkish |
| United Kingdom | momondo.co.uk | GBP | English |
| United States | momondo.com | USD | English |

### Local OTAs by Region

#### Latin America

| OTA | Countries | Specialization | URL |
|-----|-----------|----------------|-----|
| Despegar | Argentina, LATAM | Full-service regional leader | despegar.com.ar |
| Decolar | Brazil | Brazilian market leader | decolar.com |
| Volaris | Mexico | Budget carrier bookings | volaris.com |
| Avianca LifeMiles | Colombia | Miles redemption | avianca.com |
| LATAM | Chile, Regional | Flag carrier deals | latam.com |
| BestDay | Mexico | Package deals | bestday.com |
| Viajanet | Brazil | Brazilian OTA | viajanet.com.br |

#### Asia-Pacific

| OTA | Countries | Specialization | URL |
|-----|-----------|----------------|-----|
| MakeMyTrip | India | Indian market leader | makemytrip.com |
| Goibibo | India | Budget bookings | goibibo.com |
| Yatra | India | Business travel | yatra.com |
| Traveloka | Indonesia, SEA | Southeast Asia | traveloka.com |
| Tiket.com | Indonesia | Indonesian market | tiket.com |
| Trip.com (Ctrip) | China, Global | Chinese pricing | trip.com |
| Klook | Hong Kong, APAC | Activities + flights | klook.com |
| Webjet | Australia | Australian market | webjet.com.au |
| Wego | Singapore, MEA | Aggregator | wego.com |

#### Europe

| OTA | Countries | Specialization | URL |
|-----|-----------|----------------|-----|
| lastminute.com | UK, Europe | Last-minute deals | lastminute.com |
| Opodo | Spain, Europe | European coverage | opodo.com |
| eDreams | Spain, Europe | European OTA | edreams.com |
| Kiwi.com | Czech, Global | Virtual interlining | kiwi.com |
| Bravofly | Italy | Italian market | bravofly.com |
| Rumbo | Spain | Spanish market | rumbo.es |
| Travellink | Nordics | Scandinavian market | travellink.com |
| Flugladen | Germany | German market | flugladen.de |
| Vayama | Netherlands | Intercontinental | vayama.com |
| Jetcost | France | European aggregator | jetcost.com |

#### Middle East & Africa

| OTA | Countries | Specialization | URL |
|-----|-----------|----------------|-----|
| Wego | UAE, MENA | Regional aggregator | wego.ae |
| Almosafer | Saudi Arabia | Saudi market | almosafer.com |
| Tajawal | UAE | Emirates-based | tajawal.com |
| Rehlat | Kuwait | Gulf region | rehlat.com |
| Travelstart | South Africa | African market | travelstart.co.za |
| Jumia Travel | Nigeria, Africa | Pan-African | travel.jumia.com |
| FlySafair | South Africa | SA budget | flysafair.co.za |

### Airline Regional Websites

Airlines often show different prices on regional sites:

| Airline | Regional Sites | Best Pricing |
|---------|---------------|--------------|
| Emirates | emirates.com/[country] | Book from UAE site |
| Qatar Airways | qatarairways.com/[lang]-[country] | Check Qatar site |
| Turkish Airlines | turkishairlines.com | Book from TR site |
| LATAM | latam.com/[country] | Check origin country |
| Air India | airindia.in | Indian site often cheaper |
| Avianca | avianca.com/[country] | Check Colombia site |

---

## Legal VPN Guidance

### Jurisdiction-Specific Legality

| Jurisdiction | VPN Status | Notes |
|--------------|------------|-------|
| United States | Legal | No restrictions on personal use |
| Canada | Legal | No restrictions |
| United Kingdom | Legal | No restrictions |
| European Union | Legal | GDPR applies to VPN providers |
| Australia | Legal | Metadata retention laws apply |
| Japan | Legal | No restrictions |
| South Korea | Legal | Must be registered provider |
| India | Legal* | 2022 law requires VPN logging |
| UAE | Regulated | Legal for legitimate purposes |
| China | Restricted | Only government-approved VPNs |
| Russia | Restricted | Must be government-approved |
| Turkey | Legal* | Some providers blocked |
| Iran | Restricted | Government-approved only |
| North Korea | Illegal | Complete prohibition |

*Legal but with conditions

### Terms of Service Considerations

While VPN use is legal in most jurisdictions, it may violate Terms of Service:

**Generally Prohibited:**
- Using VPN to circumvent geographic licensing restrictions
- Creating multiple accounts to exploit promotions
- Automated scraping while using VPNs

**Generally Acceptable:**
- Privacy protection during price research
- Comparing prices across markets
- Protecting personal data on public networks

**Best Practices:**
1. Use VPN for research/comparison, book without if prices are equivalent
2. Don't use VPN to circumvent fraud prevention systems
3. Be prepared that transactions may be flagged for manual review
4. Keep records of your actual location and travel intent

### Recommended VPN Providers for Price Research

| Provider | Servers | Speed | No-Log Policy | Price Comparison Features |
|----------|---------|-------|---------------|--------------------------|
| ExpressVPN | 94 countries | Fast | Verified | Wide country coverage |
| NordVPN | 60 countries | Fast | Verified | Specialty servers |
| Surfshark | 100 countries | Good | Verified | Unlimited devices |
| ProtonVPN | 68 countries | Good | Verified | Swiss privacy laws |
| Mullvad | 43 countries | Good | Verified | Anonymous accounts |
| Windscribe | 69 countries | Good | Verified | Free tier available |

### VPN Configuration for Price Research

```yaml
# Recommended VPN configuration for geo-pricing research

connection:
  protocol: WireGuard  # Faster than OpenVPN
  kill_switch: enabled
  dns_leak_protection: enabled

privacy:
  webrtc_block: enabled  # Prevents IP leak via WebRTC
  ipv6_leak_protection: enabled
  split_tunneling: disabled  # Route all traffic through VPN

browser_settings:
  clear_cookies: before_each_search
  private_mode: enabled
  timezone: match_vpn_location
  language: match_target_country
```

---

## Comparison Matrix Output Format

### JSON Output Format

```json
{
  "search_id": "gs-2024-01-15-abc123",
  "search_params": {
    "origin": "JFK",
    "destination": "CDG",
    "departure_date": "2024-03-15",
    "return_date": "2024-03-22",
    "passengers": {
      "adults": 2,
      "children": 0,
      "infants": 0
    },
    "cabin_class": "economy"
  },
  "baseline": {
    "country": "United States",
    "country_code": "US",
    "currency": "USD",
    "price": 1250.00
  },
  "results": [
    {
      "rank": 1,
      "country": "Argentina",
      "country_code": "AR",
      "local_price": 425000.00,
      "local_currency": "ARS",
      "usd_equivalent": 495.35,
      "savings_vs_baseline_usd": 754.65,
      "savings_vs_baseline_percent": 60.4,
      "booking_site": "google.com/travel/flights?gl=AR&curr=ARS",
      "exchange_rate_used": 858.03,
      "rate_source": "market",
      "confidence": "high",
      "notes": "Best price found. High inflation market."
    },
    {
      "rank": 2,
      "country": "India",
      "country_code": "IN",
      "local_price": 52000.00,
      "local_currency": "INR",
      "usd_equivalent": 624.70,
      "savings_vs_baseline_usd": 625.30,
      "savings_vs_baseline_percent": 50.0,
      "booking_site": "makemytrip.com",
      "exchange_rate_used": 83.24,
      "rate_source": "market",
      "confidence": "high",
      "notes": "Competitive domestic market pricing."
    }
  ],
  "summary": {
    "best_country": "Argentina",
    "best_price_usd": 495.35,
    "max_savings_usd": 754.65,
    "max_savings_percent": 60.4,
    "countries_checked": 15,
    "search_timestamp": "2024-01-15T14:30:00Z"
  },
  "alerts": [
    {
      "type": "significant_savings",
      "threshold": 20,
      "triggered": true,
      "message": "Savings of 60.4% found booking from Argentina"
    }
  ]
}
```

### Human-Readable Table Format

```
================================================================================
                    GEO-PRICING COMPARISON RESULTS
================================================================================

Search: JFK → CDG | Mar 15-22, 2024 | 2 Adults | Economy
Baseline (US): $1,250.00 USD

--------------------------------------------------------------------------------
RANK  COUNTRY        LOCAL PRICE      USD EQUIV    SAVINGS     SITE
--------------------------------------------------------------------------------
 1    Argentina      ARS 425,000      $495.35      $754 (60%)  Google Flights AR
 2    India          INR 52,000       $624.70      $625 (50%)  MakeMyTrip
 3    Turkey         TRY 18,500       $687.50      $563 (45%)  Google Flights TR
 4    Brazil         BRL 3,850        $775.20      $475 (38%)  Decolar
 5    Mexico         MXN 15,200       $892.15      $358 (29%)  Despegar MX
 6    Poland         PLN 3,450        $865.40      $385 (31%)  Momondo PL
 7    Thailand       THB 24,500       $698.80      $551 (44%)  Traveloka
 8    Colombia       COP 3,250,000    $812.50      $438 (35%)  Despegar CO
 9    United Kingdom GBP 985          $1,245.80    $4 (0%)     Skyscanner UK
 10   United States  USD 1,250        $1,250.00    $0 (0%)     Google Flights US
--------------------------------------------------------------------------------

RECOMMENDATION: Book from Argentina (AR) to save $754.65 (60.4%)

Booking Instructions:
1. Connect to VPN server in Argentina
2. Clear browser cookies and use incognito mode
3. Navigate to google.com/travel/flights
4. Set currency to ARS if not auto-detected
5. Complete search and verify price of ARS 425,000
6. Use card with no foreign transaction fees

================================================================================
Generated: 2024-01-15 14:30:00 UTC
================================================================================
```

### CSV Export Format

```csv
rank,country,country_code,local_price,local_currency,usd_equivalent,savings_usd,savings_percent,booking_site,exchange_rate,confidence
1,Argentina,AR,425000.00,ARS,495.35,754.65,60.4,google.com/travel/flights?gl=AR,858.03,high
2,India,IN,52000.00,INR,624.70,625.30,50.0,makemytrip.com,83.24,high
3,Turkey,TR,18500.00,TRY,687.50,562.50,45.0,google.com/travel/flights?gl=TR,26.91,high
4,Brazil,BR,3850.00,BRL,775.20,474.80,38.0,decolar.com,4.97,high
5,Mexico,MX,15200.00,MXN,892.15,357.85,28.6,despegar.com.mx,17.04,medium
6,Poland,PL,3450.00,PLN,865.40,384.60,30.8,momondo.pl,3.99,medium
7,Thailand,TH,24500.00,THB,698.80,551.20,44.1,traveloka.com,35.06,medium
8,Colombia,CO,3250000.00,COP,812.50,437.50,35.0,despegar.com.co,4000.00,medium
9,United Kingdom,GB,985.00,GBP,1245.80,4.20,0.3,skyscanner.net,0.79,high
10,United States,US,1250.00,USD,1250.00,0.00,0.0,google.com/travel/flights,1.00,high
```

### Alert Configuration

```yaml
# Alert thresholds for geo-pricing monitoring

alerts:
  savings_threshold:
    enabled: true
    min_percent: 15          # Alert if savings > 15%
    min_absolute_usd: 50     # AND savings > $50

  arbitrage_alert:
    enabled: true
    min_rate_difference: 5   # Alert if exchange rate differs > 5%

  price_spike_alert:
    enabled: true
    max_increase_percent: 20 # Alert if price increased > 20% from baseline

  new_market_alert:
    enabled: true
    notify_on: ["AR", "IN", "TR"]  # Always notify for these markets

notifications:
  channels:
    - type: email
      address: "alerts@example.com"
    - type: webhook
      url: "https://api.example.com/price-alerts"
    - type: slack
      channel: "#flight-deals"
```

---

## Implementation Checklist

### Before Starting Geo-Pricing Search

- [ ] Identify baseline price from home country
- [ ] Select target countries based on route (regional hubs, currency markets)
- [ ] Verify VPN connection and IP location
- [ ] Clear browser data (cookies, cache, local storage)
- [ ] Disable location services and WebRTC
- [ ] Set browser language to match target country

### During Search

- [ ] Verify currency displayed matches target country
- [ ] Note both local price and any USD equivalent shown
- [ ] Capture exchange rate used by site (if displayed)
- [ ] Screenshot results for comparison
- [ ] Check multiple booking sites in same geo
- [ ] Test direct airline sites vs. OTAs

### After Search

- [ ] Convert all prices to common currency (USD)
- [ ] Calculate potential savings vs. baseline
- [ ] Verify savings exceed payment card FX fees
- [ ] Confirm booking site accepts international cards
- [ ] Document best option with booking instructions
- [ ] Set up price alerts for monitoring

---

## Quick Reference Card

### Top 5 Countries to Check First

1. **Argentina (AR)** - High inflation, algorithm lag
2. **India (IN)** - Competitive market, good INR rates
3. **Turkey (TR)** - Currency devaluation benefits
4. **Brazil (BR)** - Large market, peso fluctuations
5. **Poland (PL)** - Eastern Europe pricing

### Essential URL Parameters

```
Google Flights: ?gl=XX&hl=xx&curr=XXX
Skyscanner:     ?market=XX&currency=XXX&locale=xx-XX
Kayak:          kayak.XX domain
Momondo:        momondo.XX domain
```

### Payment Tips

- Use Wise or Revolut for best FX rates
- Always decline Dynamic Currency Conversion
- Book in local currency when arbitrage exists
- Keep 0% FX fee card for international bookings
