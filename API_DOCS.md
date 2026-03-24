# AJFX Trading Radar API Documentation

## Overview

AJFX Trading Radar exposes a small REST API for checking service health, running a full market scan, pulling supporting macro/news data, and querying a single asset in detail.

**Default local base URL:** `http://localhost:8011`

---

## Authentication

No authentication is currently required.

---

## Content type

All API responses are JSON unless the root route serves a frontend HTML file.

---

## Rate limits

The application does **not** currently enforce explicit server-side rate limiting in code.

That said, practical limits still exist because the API depends on external upstream providers:

- **Yahoo Finance** for market data
- **Forex Factory** for calendar data
- **Reuters / Yahoo Finance pages** for market headlines

### Recommended client behaviour

- Poll `/api/scan` no faster than **once every 30–60 seconds** for dashboard use
- Poll `/api/news` and `/api/calendar` no faster than **once every 2–5 minutes**
- Cache single-asset detail responses when possible
- Expect occasional slow responses or partial fallback data when external sources fail

---

## Endpoints

## 1) Health Check

### `GET /api/health`

Returns a simple health payload so you can verify the backend is online.

#### Parameters
None.

#### Example response

```json
{
  "status": "ok",
  "service": "ajfx-radar",
  "timestamp": "2026-03-24T07:15:42.123456"
}
```

#### Notes
- Useful for uptime monitors and deployment verification
- Timestamp is generated in UTC format from the backend
- No upstream market/news/calendar requests are made here

---

## 2) Full Market Scan

### `GET /api/scan`

Runs the main AJFX scan. This endpoint fetches the watchlist data, economic calendar, and market news, computes HTF levels, scores each asset, sorts them by composite score, and returns the full ranked result.

#### Parameters
None.

#### Response fields

| Field | Type | Description |
|---|---|---|
| `generated_at` | string | UTC timestamp of scan generation |
| `assets` | array | Ranked asset list with full scoring breakdown |
| `economic_events` | array | Economic calendar events used in the scan |
| `news_headlines` | array | Headlines used for sentiment/context |
| `top_pick` | string/null | Highest-ranked asset symbol |
| `error` | string | Present if a scan error occurs |

#### Example response

```json
{
  "generated_at": "2026-03-24T07:15:42.123456Z",
  "top_pick": "ES",
  "assets": [
    {
      "symbol": "ES",
      "name": "S&P 500",
      "price": 5328.75,
      "daily_change_pct": 0.64,
      "atr": 34.2,
      "composite_score": 74.0,
      "atr_proximity_score": 80.0,
      "economic_impact": 20,
      "news_sentiment": 2,
      "momentum": 6,
      "volume_score": 3,
      "direction": "LONG",
      "nearest_level": 5318.0,
      "distance_to_nearest_atr": 0.31,
      "htf_bias": "bullish",
      "zone_classification": "Upper H4 Range — momentum fading",
      "catalysts": [
        "08:30 — Core PCE Price Index (MoM) (HIGH)",
        "10:00 — ISM Manufacturing PMI (HIGH)"
      ],
      "summary": "ES is pressing a key level — ATR proximity is excellent. Strong economic cross-currents adding volatility. Bias: LONG — bullish signals outweigh bearish.",
      "generated_at": "2026-03-24T07:15:42.123456Z"
    }
  ],
  "economic_events": [
    {
      "time": "08:30",
      "currency": "USD",
      "event": "Core PCE Price Index (MoM)",
      "impact": "high",
      "previous": "0.3%",
      "forecast": "0.3%",
      "actual": "",
      "affected_assets": ["NQ=F", "ES=F", "YM=F", "GC=F", "CL=F"]
    }
  ],
  "news_headlines": [
    {
      "title": "Stocks rally as traders digest inflation data",
      "source": "Reuters Markets",
      "url": "https://example.com/article",
      "time": "07:12 UTC",
      "sentiment": "bullish"
    }
  ]
}
```

#### Notes
- This is the most expensive endpoint because it aggregates multiple upstream sources
- Best suited for dashboard refreshes and morning scans
- If upstream fetches fail, the endpoint may return:
  - fallback calendar data
  - empty news lists
  - an error payload with empty arrays
- The watchlist currently includes: `NQ`, `ES`, `YM`, `GC`, `CL`, `6E`

---

## 3) Market News

### `GET /api/news`

Returns the latest fetched market headlines.

#### Parameters
None.

#### Example response

```json
[
  {
    "title": "Oil prices rise after supply concerns return",
    "source": "Reuters Markets",
    "url": "https://example.com/oil-story",
    "time": "07:25 UTC",
    "sentiment": "bullish"
  },
  {
    "title": "Investors cautious ahead of key inflation print",
    "source": "Yahoo Finance",
    "url": "",
    "time": "07:26 UTC",
    "sentiment": "neutral"
  }
]
```

#### Notes
- Headlines are scraped from free public sources
- Sentiment is derived from a lightweight keyword-based classifier
- Results are deduplicated by headline title
- Maximum returned headlines: roughly **15**
- In failure cases, this endpoint returns an empty array

---

## 4) Economic Calendar

### `GET /api/calendar`

Returns today’s economic calendar events relevant to the scanner.

#### Parameters
None.

#### Example response

```json
[
  {
    "time": "08:30",
    "currency": "USD",
    "event": "Core PCE Price Index (MoM)",
    "impact": "high",
    "previous": "0.3%",
    "forecast": "0.3%",
    "actual": "",
    "affected_assets": ["NQ=F", "ES=F", "YM=F", "GC=F", "CL=F"]
  },
  {
    "time": "All Day",
    "currency": "EUR",
    "event": "ECB President Lagarde Speaks",
    "impact": "medium",
    "previous": "",
    "forecast": "",
    "actual": "",
    "affected_assets": ["6E=F"]
  }
]
```

#### Notes
- Primary source is Forex Factory
- If the main page fetch fails, the code attempts an RSS fallback
- If both fail, sample events are returned instead of hard failure
- Maximum returned events: roughly **20**

---

## 5) Asset Detail

### `GET /api/asset/{symbol}`

Returns a detailed payload for one asset symbol from the watchlist.

#### Path parameters

| Name | Type | Required | Description |
|---|---|---|---|
| `symbol` | string | Yes | Asset symbol such as `NQ`, `ES`, `YM`, `GC`, `CL`, or `6E` |

#### Example request

```http
GET /api/asset/NQ HTTP/1.1
Host: localhost:8011
```

#### Example response

```json
{
  "symbol": "NQ",
  "name": "Nasdaq 100",
  "description": "Nasdaq futures",
  "price": 20125.5,
  "daily_change_pct": 0.82,
  "atr": 185.2,
  "atr_distance": 0.24,
  "atr_pct_of_price": 0.92,
  "volume_ratio": 1.48,
  "nearest_level": 20080.0,
  "distance_to_nearest_atr": 0.24,
  "pivot_levels": {
    "pivot": 20104.5,
    "r1": 20142.0,
    "s1": 20068.0,
    "r2": 20178.5,
    "s2": 20030.5
  },
  "h4_levels": {
    "h4_high": 20190.0,
    "h4_low": 19985.0,
    "h4_close": 20125.5,
    "swing_high_date": "2026-03-24 00:00:00",
    "swing_low_date": "2026-03-23 08:00:00"
  },
  "htf_levels": {
    "h4": {
      "high": 20190.0,
      "low": 19985.0,
      "close": 20125.5,
      "bias": "bullish",
      "range_pct": 1.03
    },
    "h1": {
      "high": 20140.0,
      "low": 20072.0,
      "close": 20125.5,
      "bias": "neutral",
      "range_pct": 0.34
    },
    "swings": {
      "swing_high": 20188.0,
      "swing_high_idx": 14,
      "swing_low": 20010.0,
      "swing_low_idx": 5
    },
    "atr_current": 52.0,
    "dist_to_h4_high_atr": 1.24,
    "dist_to_h4_low_atr": 2.7,
    "zone_classification": "Upper H4 Range — momentum fading"
  },
  "generated_at": "2026-03-24T07:15:42.123456Z"
}
```

#### Error example

```json
{
  "error": "Symbol ABC not found"
}
```

#### Notes
- Symbol matching is case-insensitive
- The endpoint fetches the full watchlist and then filters the requested symbol
- If a symbol is not found, the response returns an error object
- This endpoint is useful for detail drawers or per-instrument cards in the frontend

---

## 6) Frontend Root

### `GET /`

Serves the frontend dashboard if a built frontend exists at `backend/frontend/index.html`.

#### Parameters
None.

#### Possible response A: HTML file
If the frontend exists, the route serves the dashboard HTML.

#### Possible response B: JSON placeholder

```json
{
  "message": "Frontend not built yet. POST to /api/scan for data."
}
```

#### Notes
- Despite the placeholder message text, the scan route in the current implementation is a **GET** endpoint, not POST
- This route is mainly for browser-based dashboard access

---

## Asset schema summary

Each ranked asset returned by `/api/scan` may include fields such as:

| Field | Description |
|---|---|
| `symbol` | Watchlist symbol |
| `name` | Human-readable instrument name |
| `price` | Latest price |
| `daily_change_pct` | Recent percentage move |
| `atr` | Average True Range estimate |
| `composite_score` | Total score clamped to 0–100 |
| `atr_proximity_score` | Normalised ATR-proximity score in percent |
| `economic_impact` | Score contribution from macro calendar |
| `news_sentiment` | Score contribution from headlines |
| `momentum` | Score contribution from recent move |
| `volume_score` | Score contribution from volume ratio |
| `direction` | `LONG`, `SHORT`, or `NEUTRAL` |
| `nearest_level` | Closest relevant level |
| `distance_to_nearest_atr` | Distance to level expressed in ATR |
| `htf_bias` | H4 directional bias |
| `zone_classification` | Current range/zone description |
| `catalysts` | Relevant calendar catalysts |
| `summary` | Human-readable brief |
| `generated_at` | Per-asset generation time |

---

## Operational notes

- The app is designed for lightweight dashboard use, not high-frequency trading execution
- Results should be treated as **decision support**, not automated trade advice
- Upstream scraping dependencies may occasionally change markup and break data extraction
- Consider adding caching if you later expose this publicly or refresh it aggressively
