import { AwardWizQuery, AwardWizScraper, FlightFare, FlightWithFares } from "../awardwiz-types.js"
import type { Trip, UnitedResponse } from "../scraper-types/united.js"
import { ScraperMetadata } from "../../arkalis/arkalis.js"

export const meta: ScraperMetadata = {
  name: "united",
  blockUrls: ["liveperson.net", "tags.tiqcdn.com"],
  defaultTimeoutMs: 45000,
}

/**
 * United scraper using evaluate(fetch()) pattern (same as AA).
 * 
 * Flow:
 * 1. Navigate to united.com to establish session/cookies
 * 2. Use page.evaluate(fetch()) to hit the FetchFlights API directly
 * 3. Parse results from the returned JSON
 * 
 * The anonymous token is automatically included via cookies established
 * during the initial page load. The key is to let the browser handle
 * cookie/session management, then make the API call from within the page context.
 */
export const runScraper: AwardWizScraper = async (arkalis, query) => {
  // Step 1: Navigate to united.com to establish session
  const url = "https://www.united.com/en/us/fsr/choose-flights"
  arkalis.goto(url)
  
  // Wait for the page to load enough to establish cookies/session
  await arkalis.waitFor({
    "success": { type: "url", url: "https://www.united.com/en/us/fsr/choose-flights", onlyStatusCode: 200, othersThrow: false },
    "homepage": { type: "url", url: "https://www.united.com/", onlyStatusCode: 200 },
  })
  
  // Small delay to let JS initialize and set up session tokens
  await new Promise(r => setTimeout(r, 3000))
  
  arkalis.log("fetching flights via evaluate(fetch())")
  
  // Step 2: Build the FetchFlights request body
  const requestBody = {
    CartId: "",
    Characteristics: [
      { Code: "ByPassMBE", Value: "true" },
      { Code: "StopCount", Value: "0,1,2" },
    ],
    Filters: {
      ExcludeConnectingCities: [],
      IncludeAirlines: [],
      MaxConnections: 2,
      MaxDuration: 0,
      MaxPrice: 0,
      MinPrice: 0,
      StopCount: "0,1,2",
    },
    CurrencyCode: "USD",
    MaxTrips: 50,
    SearchTypeSelection: 1,  // 1 = Award
    Trips: [{
      DepartDate: query.departureDate,
      DepartTime: "",
      Destination: query.destination,
      Origin: query.origin,
      SearchFilters: null,
      TripIndex: 1,
    }],
    CalendarOnly: false,
    ClubPremierMemberShipLevel: 0,
    IsAwardTravel: true,
    IsExpertModeEnabled: false,
    IsFlexibleDateSearch: false,
    IsYoungAdult: false,
    IsYoungAdultTravel: false,
    NumberOfAdults: 1,
    NumberOfChildren: 0,
    NumberOfInfants: 0,
    NumberOfLapInfants: 0,
    NumberOfSeniors: 0,
    SortTypes: ["bestmatches"],
    TripType: "OneWay",
    PageIndex: 1,
    PageSize: 50,
    PaxInfoList: [{
      DateOfBirth: "",
      Key: "ADT1",
      PaxType: 1,
      TicketNumber: "",
    }],
  }

  // Step 3: Use evaluate(fetch()) to make the API call from within the page context
  const fetchCmd = `
    fetch("https://www.united.com/api/flight/FetchFlights", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "accept": "application/json",
      },
      body: ${JSON.stringify(JSON.stringify(requestBody))}
    }).then(r => r.text())
  `
  
  void arkalis.evaluate(fetchCmd)
  const xhrResponse = await arkalis.waitFor({
    "search": { type: "url", url: "https://www.united.com/api/flight/FetchFlights" },
  })
  
  let fetchFlights: UnitedResponse
  try {
    fetchFlights = JSON.parse(xhrResponse.response!.body) as UnitedResponse
  } catch {
    arkalis.log("Failed to parse response, trying direct evaluate return")
    // Fallback: try getting the response directly from evaluate
    return []
  }
  
  if (fetchFlights.Error) {
    throw new Error(`United API error: ${JSON.stringify(fetchFlights.Error)}`)
  }

  arkalis.log("parsing results")
  const flightsWithFares: FlightWithFares[] = []
  if ((fetchFlights.data?.Trips || []).length) {
    const flights = standardizeResults(query, fetchFlights.data!.Trips[0]!)
    flightsWithFares.push(...flights)
  }

  return flightsWithFares
}

const standardizeResults = (query: AwardWizQuery, unitedTrip: Trip) => {
  const results: FlightWithFares[] = []
  for (const flight of unitedTrip.Flights) {
    const result: FlightWithFares = {
      departureDateTime: `${flight.DepartDateTime}:00`,
      arrivalDateTime: `${flight.DestinationDateTime}:00`,
      origin: flight.Origin,
      destination: flight.Destination,
      flightNo: `${flight.MarketingCarrier} ${flight.FlightNumber}`,
      duration: flight.TravelMinutes,
      aircraft: flight.EquipmentDisclosures.EquipmentDescription,
      fares: [],
      amenities: {
        hasPods: undefined,
        hasWiFi: undefined
      }
    }

    if (flight.Origin !== (unitedTrip.RequestedOrigin || unitedTrip.Origin))
      continue
    if (flight.Destination !== (unitedTrip.RequestedDestination || unitedTrip.Destination))
      continue
    if (result.departureDateTime.substring(0, 10) !== query.departureDate.substring(0, 10))
      continue

    // Skip multi-segment (connections)
    if (flight.Connections.length > 0)
      continue

    for (const product of flight.Products) {
      if (product.Prices.length === 0)
        continue

      const miles = product.Prices[0]!.Amount
      const cash = product.Prices.length >= 2 ? product.Prices[1]!.Amount : 0
      const currencyOfCash = product.Prices.length >= 2 ? product.Prices[1]!.Currency : ""
      const bookingClass = product.BookingCode

      const cabin = { "United First": "business", "United Economy": "economy", "United Business": "business", Economy: "economy", Business: "business", First: "first", "United Polaris business": "business", "United Premium Plus": "economy" }[product.Description!]
      if (cabin === undefined)
        throw new Error(`Unknown cabin type: ${product.Description!}`)

      let existingFare = result.fares.find((fare) => fare.cabin === cabin)
      if (existingFare !== undefined) {
        if (miles < existingFare.miles)
          existingFare = { cabin, miles, cash, currencyOfCash, bookingClass, scraper: "united" }
      } else {
        result.fares.push({ cabin, miles, cash, currencyOfCash, bookingClass, scraper: "united" })
      }
    }

    results.push(result)
  }

  return results
}
