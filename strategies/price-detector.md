# Price Manipulation Detector Strategy

Airlines and OTAs use sophisticated tracking to personalize (often increase) prices based on your browsing history. This strategy ensures clean searches that avoid price manipulation signals.

## Table of Contents

1. [How Price Manipulation Works](#how-price-manipulation-works)
2. [Cookie Clearing Automation](#cookie-clearing-automation)
3. [Incognito Browsing Patterns](#incognito-browsing-patterns)
4. [IP/Location Detection Avoidance](#iplocation-detection-avoidance)
5. [Device Fingerprint Mitigation](#device-fingerprint-mitigation)
6. [Clean Search Method](#clean-search-method)

---

## How Price Manipulation Works

### Tracking Signals Airlines Use

| Signal | What It Reveals | Impact on Price |
|--------|-----------------|-----------------|
| Cookies | Search history, frequency | +5-15% for repeat searches |
| Local Storage | Saved searches, preferences | +3-10% personalization |
| Browser Fingerprint | Device type, screen size | Premium device = higher prices |
| IP Address | Location, ISP type | Business ISP = +5-10% |
| Search Timing | Time of day, day of week | Peak hours = +2-5% |
| Referrer | Where you came from | Price comparison site = lower |

### Price Increase Patterns

```
First search:      $350 (clean baseline)
Second search:     $365 (+4% - you're interested)
Third search:      $385 (+10% - urgency signaling)
After 24 hours:    $420 (+20% - "prices rising" trigger)
```

### Sites Known for Aggressive Tracking

| Site | Tracking Level | Cookie Lifetime |
|------|----------------|-----------------|
| Expedia | High | 30 days |
| Booking.com | High | 365 days |
| Airlines (direct) | Medium-High | 30-90 days |
| Google Flights | Medium | Session + account |
| Kayak | Medium | 14 days |
| Skyscanner | Low-Medium | 7 days |

---

## Cookie Clearing Automation

### Playwright Cookie Management

```javascript
// Clear all cookies before search
await context.clearCookies();

// Clear cookies for specific domains
await context.clearCookies({
  domain: '.expedia.com'
});

// Block cookie-setting scripts
await page.route('**/*', route => {
  const url = route.request().url();
  if (url.includes('tracking') || url.includes('analytics')) {
    return route.abort();
  }
  return route.continue();
});
```

### Local Storage Clearing

```javascript
// Clear all local storage
await page.evaluate(() => {
  localStorage.clear();
  sessionStorage.clear();
});

// Clear IndexedDB
await page.evaluate(async () => {
  const databases = await indexedDB.databases();
  for (const db of databases) {
    indexedDB.deleteDatabase(db.name);
  }
});
```

### Complete Clean Slate Function

```javascript
async function createCleanContext(browser) {
  const context = await browser.newContext({
    // No persistent storage
    storageState: undefined,

    // Clear all permissions
    permissions: [],

    // Randomize viewport slightly
    viewport: {
      width: 1280 + Math.floor(Math.random() * 200),
      height: 720 + Math.floor(Math.random() * 100)
    },

    // Generic user agent
    userAgent: getRandomUserAgent()
  });

  return context;
}
```

---

## Incognito Browsing Patterns

### Playwright Incognito Context

```javascript
// Launch with incognito-equivalent settings
const browser = await chromium.launch({
  args: [
    '--disable-extensions',
    '--disable-plugins',
    '--disable-sync',
    '--no-first-run',
    '--disable-default-apps'
  ]
});

// Each search gets fresh context
const context = await browser.newContext({
  // No saved state
  storageState: undefined,

  // Disable features that leak identity
  javaScriptEnabled: true,
  bypassCSP: false,
  ignoreHTTPSErrors: false
});
```

### Session Isolation Pattern

```javascript
async function isolatedSearch(searchParams) {
  // New context per search
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Perform search
    const results = await performSearch(page, searchParams);
    return results;
  } finally {
    // Always clean up
    await context.close();
  }
}
```

### Multiple Context Comparison

```javascript
async function compareWithFreshContext(url) {
  const results = [];

  // Search 3 times with fresh contexts
  for (let i = 0; i < 3; i++) {
    const context = await browser.newContext();
    const page = await context.newPage();

    await page.goto(url);
    const price = await extractPrice(page);
    results.push(price);

    await context.close();
    await delay(5000); // Wait between searches
  }

  // Flag if prices vary > 5%
  const variance = calculateVariance(results);
  return {
    prices: results,
    variance: variance,
    manipulationDetected: variance > 0.05
  };
}
```

---

## IP/Location Detection Avoidance

### Residential vs Datacenter IPs

| IP Type | Detection Rate | Price Impact |
|---------|----------------|--------------|
| Datacenter (AWS, GCP) | High (90%+) | Often blocked |
| VPN (popular services) | Medium (60%) | +0-5% |
| Residential proxy | Low (20%) | Baseline prices |
| Mobile carrier | Very Low (5%) | Sometimes lower |

### Playwright Proxy Configuration

```javascript
// Use proxy for clean IP
const browser = await chromium.launch({
  proxy: {
    server: 'http://proxy.example.com:8080',
    username: 'user',
    password: 'pass'
  }
});

// Or per-context proxy
const context = await browser.newContext({
  proxy: {
    server: 'socks5://proxy.example.com:1080'
  }
});
```

### Geolocation Spoofing

```javascript
// Set consistent geolocation
await context.grantPermissions(['geolocation']);
await context.setGeolocation({
  latitude: 40.7128,   // New York
  longitude: -74.0060,
  accuracy: 100
});

// Or deny geolocation entirely
await context.clearPermissions();
```

### Timezone Consistency

```javascript
// Match timezone to spoofed location
const context = await browser.newContext({
  timezoneId: 'America/New_York',
  locale: 'en-US'
});
```

---

## Device Fingerprint Mitigation

### Browser Fingerprint Components

| Component | Uniqueness | Mitigation |
|-----------|------------|------------|
| User Agent | High | Rotate common agents |
| Screen Resolution | Medium | Use standard sizes |
| Installed Fonts | Very High | Use system defaults |
| Canvas Fingerprint | Very High | Add noise |
| WebGL Renderer | High | Block or randomize |
| Audio Context | Medium | Block |
| Timezone | Low | Match to IP location |

### User Agent Rotation

```javascript
const USER_AGENTS = [
  // Chrome on Windows (most common)
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  // Chrome on Mac
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  // Firefox on Windows
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
  // Safari on Mac
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15'
];

function getRandomUserAgent() {
  return USER_AGENTS[Math.floor(Math.random() * USER_AGENTS.length)];
}
```

### Canvas Fingerprint Protection

```javascript
// Inject script to add noise to canvas
await page.addInitScript(() => {
  const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
  HTMLCanvasElement.prototype.toDataURL = function(type) {
    const context = this.getContext('2d');
    if (context) {
      // Add imperceptible noise
      const imageData = context.getImageData(0, 0, this.width, this.height);
      for (let i = 0; i < imageData.data.length; i += 4) {
        imageData.data[i] ^= (Math.random() * 2) | 0;
      }
      context.putImageData(imageData, 0, 0);
    }
    return originalToDataURL.apply(this, arguments);
  };
});
```

### WebGL Spoofing

```javascript
// Block WebGL fingerprinting
await page.addInitScript(() => {
  const getParameter = WebGLRenderingContext.prototype.getParameter;
  WebGLRenderingContext.prototype.getParameter = function(parameter) {
    // Return generic values for fingerprinting parameters
    if (parameter === 37445) return 'Intel Inc.';  // UNMASKED_VENDOR
    if (parameter === 37446) return 'Intel Iris OpenGL Engine';  // UNMASKED_RENDERER
    return getParameter.apply(this, arguments);
  };
});
```

---

## Clean Search Method

### Complete Clean Search Implementation

```javascript
async function cleanFlightSearch(origin, destination, date, options = {}) {
  // Step 1: Create isolated browser context
  const context = await browser.newContext({
    viewport: { width: 1366, height: 768 },
    userAgent: getRandomUserAgent(),
    locale: 'en-US',
    timezoneId: 'America/New_York',
    permissions: [],
    geolocation: null
  });

  // Step 2: Block tracking scripts
  await context.route('**/*', route => {
    const url = route.request().url().toLowerCase();
    const blockedPatterns = [
      'google-analytics',
      'googletagmanager',
      'facebook.net',
      'doubleclick',
      'hotjar',
      'segment.io',
      'optimizely',
      'amplitude'
    ];

    if (blockedPatterns.some(p => url.includes(p))) {
      return route.abort();
    }
    return route.continue();
  });

  // Step 3: Add fingerprint protection
  const page = await context.newPage();
  await addFingerprintProtection(page);

  // Step 4: Navigate with referrer masking
  await page.goto(buildSearchUrl(origin, destination, date), {
    referer: 'https://www.google.com/',  // Appear from organic search
    waitUntil: 'networkidle'
  });

  // Step 5: Extract results
  const results = await extractFlightResults(page);

  // Step 6: Clean up immediately
  await context.close();

  return results;
}
```

### Price Verification Pattern

```javascript
async function verifyPrice(searchParams) {
  // Search 3 times with different contexts
  const prices = [];

  for (let i = 0; i < 3; i++) {
    const result = await cleanFlightSearch(
      searchParams.origin,
      searchParams.destination,
      searchParams.date
    );
    prices.push(result.lowestPrice);

    // Random delay 3-7 seconds
    await delay(3000 + Math.random() * 4000);
  }

  return {
    prices: prices,
    median: calculateMedian(prices),
    variance: calculateVariance(prices),
    reliable: calculateVariance(prices) < 0.03  // < 3% variance
  };
}
```

### Optimal Search Timing

```javascript
const OPTIMAL_SEARCH_TIMES = {
  // Based on historical data, prices tend to be lower at these times
  bestDays: ['Tuesday', 'Wednesday'],
  bestHours: [1, 2, 3, 4, 5, 6],  // 1 AM - 6 AM local
  avoidDays: ['Friday', 'Sunday'],
  avoidHours: [8, 9, 10, 17, 18, 19, 20]  // Business hours
};

function isOptimalSearchTime() {
  const now = new Date();
  const day = now.toLocaleDateString('en-US', { weekday: 'long' });
  const hour = now.getHours();

  return OPTIMAL_SEARCH_TIMES.bestDays.includes(day) &&
         OPTIMAL_SEARCH_TIMES.bestHours.includes(hour);
}
```

---

## Execution Checklist

Before every search:
- [ ] New browser context created
- [ ] Cookies cleared
- [ ] Local storage cleared
- [ ] Random user agent set
- [ ] Viewport slightly randomized
- [ ] Tracking scripts blocked
- [ ] Fingerprint protection injected
- [ ] Geolocation denied/spoofed
- [ ] Referrer set to organic search

After search:
- [ ] Results extracted
- [ ] Context immediately closed
- [ ] Wait before next search (3-7 seconds random)

## Warning Signs of Manipulation

Watch for these indicators that prices are being manipulated:
- Price increased since your last search
- "Only X seats left at this price" urgency messaging
- Prices higher than comparison sites
- Different prices when logged in vs logged out
- Prices vary by > 5% between fresh searches
