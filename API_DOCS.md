# AJFX Trading Radar — API Documentation

Base URL: `https://ajfx-radar.onrender.com`  
Local URL: `http://localhost:8011`

---

## GET /api/health

Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "service": "ajfx-radar",
  "timestamp": "2026-03-24T07:30:00.000Z"
}
```

---

## GET /api/scan

Main endpoint — returns all assets ranked by composite trade quality score.

**Response:**
```json
{
  "generated_at": "2026-03-24T07:30:00.000Z",
  "top_pick": "GC",
  "assets": [
    {
      "symbol": "GC",
      "name": "Gold",
      "price": 2043.20,
      "daily_change_pct": 0.42,
      "atr": 18.50,
      "composite_score": 87,
      "atr_proximity_score": 95,
      "economic_impact": 18,
      "news_sentiment": 4,
      "momentum": 4,
      "volume_score": 2,
      "direction": "LONG",
      "nearest_level": 2045.00,
      "distance_to_nearest_atr": 0.08,
      "htf_bias": "bullish",
      "zone_classification": "H4 Resistance Zone — potential reversal",
      "catalysts": [
        "14:30 — Core PCE Price Index (HIGH)",
        "18:00 — FOMC Meeting Minutes (HIGH)"
      ],
      "summary": "GC is pressing a key H4 resistance at $2,045. ATR proximity is excellent. Strong economic cross-currents adding volatility. Bias: LONG — bullish signals outweigh bearish.",
      "pivot_levels": {
        "pivot": 2038.50,
        "r1": 2045.00,
        "s1": 2032.00,
        "r2": 2050.00,
        "s2": 2025.50
      },
      "h4_levels": {
        "high": 2045.00,
        "low": 2018.50,
        "close": 2043.20,
        "bias": "bullish"
      }
    }
  ],
  "economic_events": [
    {
      "time": "14:30",
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
      "title": "Gold prices surge on Fed rate cut speculation",
      "source": "Reuters",
      "time": "07:15 UTC",
      "sentiment": "bullish"
    }
  ]
}
```

**Scoring breakdown:**
| Field | Range | Description |
|-------|-------|-------------|
| `composite_score` | 0-100 | Overall trade quality |
| `atr_proximity_score` | 0-100 | ATR-based level proximity |
| `economic_impact` | -20 to +20 | High-impact events today |
| `news_sentiment` | -10 to +10 | News bullish/bearish score |
| `momentum` | -10 to +10 | Intraday % vs average |
| `volume_score` | -5 to +5 | Volume spike confirmation |
| `direction` | LONG/SHORT/NEUTRAL | Bias |

---

## GET /api/news

Returns today's market news headlines with sentiment.

**Response:**
```json
[
  {
    "title": "Gold prices surge on Fed rate cut speculation",
    "source": "Reuters",
    "time": "07:15 UTC",
    "sentiment": "bullish"
  },
  {
    "title": "Oil drops on demand concerns",
    "source": "Yahoo Finance",
    "time": "06:45 UTC",
    "sentiment": "bearish"
  }
]
```

---

## GET /api/calendar

Returns today's economic calendar events from Forex Factory.

**Response:**
```json
[
  {
    "time": "14:30",
    "currency": "USD",
    "event": "Core PCE Price Index (MoM)",
    "impact": "high",
    "previous": "0.3%",
    "forecast": "0.3%",
    "actual": "",
    "affected_assets": ["NQ=F", "ES=F", "YM=F", "GC=F", "CL=F"]
  }
]
```

---

## GET /api/asset/{symbol}

Returns detailed data for a specific asset.

**Parameters:**
- `symbol` — Asset symbol (e.g., `GC`, `NQ`, `ES`)

**Example:** `GET /api/asset/GC`

**Response:**
```json
{
  "symbol": "GC",
  "name": "Gold",
  "price": 2043.20,
  "atr": 18.50,
  "atr_pct_of_price": 0.905,
  "volume_ratio": 1.3,
  "nearest_level": 2045.00,
  "pivot_levels": { ... },
  "h4_levels": { ... }
}
```

---

## Rate Limits

- Yahoo Finance: ~2,000 requests/hour (throttled gracefully)
- Forex Factory: scraped once per request (cached for 5 min recommended)
- News: ~100 requests/hour

---

## Errors

All endpoints return errors as:
```json
{
  "error": "Error description",
  "generated_at": "2026-03-24T07:30:00.000Z"
}
```
