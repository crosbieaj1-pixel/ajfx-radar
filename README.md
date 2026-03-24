# AJFX Trading Radar

> **Which asset should I be trading today?**

AJFX Trading Radar is a market scanning and ranking tool built to help traders quickly identify the best trade-quality setup across a defined watchlist of futures markets:

- **NQ** — Nasdaq 100 futures
- **ES** — S&P 500 futures
- **YM** — Dow Jones futures
- **GC** — Gold futures
- **CL** — Crude Oil futures
- **6E** — Euro FX futures

The application aggregates price structure, ATR proximity, higher-timeframe context, macro catalysts, and headline sentiment, then produces a ranked list of assets ordered by **trade quality**.

---

## What it does

Instead of manually checking six different instruments one by one, AJFX Trading Radar answers a practical daily question:

**“Which asset should I be trading today?”**

The backend fetches market data, economic events, and news headlines, calculates higher-timeframe levels, and applies a composite scoring model to rank the watchlist from most attractive to least attractive.

Typical use cases:

- Prioritising which market deserves attention first
- Quickly spotting assets near high-value levels
- Identifying when macro events may create opportunity or risk
- Getting a concise directional bias per instrument
- Feeding a lightweight single-page dashboard with fresh scan data

---

## Core features

### 1. ATR proximity scoring
Measures how close price is to a meaningful level in ATR terms. Assets sitting near key levels often provide cleaner risk/reward and more actionable setups.

### 2. Economic calendar integration
Pulls medium- and high-impact macro events and maps them to relevant assets. This helps highlight instruments likely to experience volatility from scheduled releases.

### 3. News sentiment scanning
Fetches free market headlines and applies lightweight sentiment classification. Relevant headlines can nudge an asset’s score up or down depending on whether the flow is bullish, bearish, or neutral.

### 4. Higher-timeframe levels
Calculates H1/H4 context, recent range extremes, and simple zone classification so the scan is not just momentum-chasing without structural context.

### 5. AI-style composite scoring
Combines ATR proximity, catalysts, news sentiment, momentum, and volume into a single **composite score (0–100)** so the day’s best trade candidates rise to the top.

---

## Architecture overview

AJFX Trading Radar is designed as a lightweight web app with a Python API backend and a simple single-page frontend.

### Backend
- **Framework:** FastAPI
- **Entry point:** `backend/main.py`
- **Responsibilities:**
  - fetch market data
  - fetch economic calendar data
  - fetch market news
  - compute HTF levels
  - score and rank assets
  - serve API responses

### Frontend
- Intended as a **single-page dashboard**
- Served from the backend when frontend assets exist
- Root route (`/`) returns the dashboard or a placeholder message if the frontend has not been built yet

### Deployment
- Local development via **Uvicorn**
- Container deployment via **Docker**
- Cloud deployment via **Render Blueprint / Docker web service**

### High-level flow
1. Fetch 1-hour market data for the watchlist
2. Calculate ATR, pivot levels, volume ratio, and nearest key level
3. Fetch economic calendar events
4. Fetch market headlines
5. Compute H1/H4 structural context
6. Apply scoring engine
7. Rank all assets by composite score
8. Return scan results to the frontend or API consumer

---

## API overview

Base URL examples:

- Local: `http://localhost:8011`
- Render: `https://your-render-service.onrender.com`

### Endpoints

#### `GET /api/health`
Returns service status and timestamp.

Example:

```json
{
  "status": "ok",
  "service": "ajfx-radar",
  "timestamp": "2026-03-24T07:15:42.123456"
}
```

#### `GET /api/scan`
Returns the full ranked scan across all tracked assets.

Example:

```json
{
  "generated_at": "2026-03-24T07:15:42.123456Z",
  "top_pick": "NQ",
  "assets": [
    {
      "symbol": "NQ",
      "name": "Nasdaq 100",
      "price": 20125.5,
      "daily_change_pct": 0.82,
      "atr": 185.2,
      "composite_score": 78.0,
      "atr_proximity_score": 80.0,
      "economic_impact": 20,
      "news_sentiment": 4,
      "momentum": 8,
      "volume_score": 3,
      "direction": "LONG",
      "nearest_level": 20080.0,
      "distance_to_nearest_atr": 0.24,
      "htf_bias": "bullish",
      "zone_classification": "Upper H4 Range — momentum fading",
      "catalysts": [
        "08:30 — Core PCE Price Index (MoM) (HIGH)"
      ],
      "summary": "NQ is pressing a key level — ATR proximity is excellent. Strong economic cross-currents adding volatility. Bias: LONG — bullish signals outweigh bearish.",
      "generated_at": "2026-03-24T07:15:42.123456Z"
    }
  ],
  "economic_events": [],
  "news_headlines": []
}
```

#### `GET /api/news`
Returns the latest fetched market headlines.

Example:

```json
[
  {
    "title": "Stocks rally as traders digest inflation data",
    "source": "Reuters Markets",
    "url": "https://example.com/article",
    "time": "07:12 UTC",
    "sentiment": "bullish"
  }
]
```

#### `GET /api/calendar`
Returns today’s economic calendar events.

Example:

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
  }
]
```

#### `GET /api/asset/{symbol}`
Returns detailed data for a single asset, including raw pricing-derived metrics and HTF level output.

Example:

```json
{
  "symbol": "GC",
  "name": "Gold",
  "description": "Gold futures",
  "price": 2188.4,
  "daily_change_pct": -0.21,
  "atr": 24.7,
  "atr_distance": 0.61,
  "atr_pct_of_price": 1.129,
  "volume_ratio": 1.31,
  "nearest_level": 2195.0,
  "distance_to_nearest_atr": 0.61,
  "pivot_levels": {
    "pivot": 2186.8,
    "r1": 2193.3,
    "s1": 2178.6,
    "r2": 2201.5,
    "s2": 2172.1
  },
  "h4_levels": {
    "h4_high": 2204.5,
    "h4_low": 2169.8,
    "h4_close": 2188.4,
    "swing_high_date": "2026-03-24 00:00:00",
    "swing_low_date": "2026-03-23 08:00:00"
  },
  "htf_levels": {
    "h4": {
      "high": 2204.5,
      "low": 2169.8,
      "close": 2188.4,
      "bias": "neutral",
      "range_pct": 1.6
    },
    "h1": {
      "high": 2192.2,
      "low": 2179.1,
      "close": 2188.4,
      "bias": "neutral",
      "range_pct": 0.6
    },
    "swings": {
      "swing_high": 2201.3,
      "swing_high_idx": 15,
      "swing_low": 2171.4,
      "swing_low_idx": 6
    },
    "atr_current": 18.5,
    "dist_to_h4_high_atr": 0.87,
    "dist_to_h4_low_atr": 1.01,
    "zone_classification": "Mid-range consolidation"
  },
  "generated_at": "2026-03-24T07:15:42.123456Z"
}
```

#### `GET /`
Serves the frontend if `backend/frontend/index.html` exists. Otherwise returns a placeholder JSON message.

---

## Full API docs

For a cleaner endpoint-by-endpoint reference, see:

- [`API_DOCS.md`](./API_DOCS.md)

---

## Project structure

```text
ajfx-radar-test/
├─ backend/
│  ├─ main.py
│  ├─ requirements.txt
│  ├─ Dockerfile
│  ├─ data/
│  │  ├─ yahoo.py
│  │  ├─ calendar.py
│  │  ├─ news.py
│  │  └─ levels.py
│  └─ scoring/
│     └─ engine.py
├─ README.md
├─ API_DOCS.md
├─ SPEC.md
├─ start.sh
├─ start.bat
├─ render.yaml
└─ requirements.txt
```

---

## Local development

### Option 1: Bash

```bash
chmod +x start.sh
./start.sh
```

### Option 2: Windows CMD

```bat
start.bat
```

### Option 3: Manual

```bash
pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8011 --reload
```

Then open:

- API health: `http://localhost:8011/api/health`
- Full scan: `http://localhost:8011/api/scan`

---

## Deploying to Render

This project already includes a `render.yaml` blueprint and a backend Dockerfile.

### Step-by-step

1. **Push the repository to GitHub**
   - Make sure the repo contains the latest `backend/`, `render.yaml`, and docs files.

2. **Sign in to Render**
   - Go to [https://render.com](https://render.com)

3. **Create a new Blueprint or Web Service**
   - If using blueprint deploys, connect the GitHub repo and let Render detect `render.yaml`
   - If creating manually, choose **Web Service** and point it at the repo

4. **Use Docker as the environment**
   - Render should use `backend/Dockerfile`
   - The included blueprint already sets:
     - service type: `web`
     - environment: `docker`
     - port: `8011`

5. **Confirm service settings**
   - Name: `ajfx-radar-backend`
   - Plan: `free` (or upgrade if you want better cold-start/performance)
   - Auto deploy: enabled

6. **Set environment variables if needed**
   - Current code works without secrets for basic operation
   - If future providers require API keys, add them in Render’s environment settings

7. **Deploy**
   - Trigger the first deploy
   - Wait for the build to install dependencies and start Uvicorn

8. **Verify the deployment**
   - Visit `/api/health`
   - Then test `/api/scan`
   - If a frontend is later added, test `/`

### Render notes

- Free tier services may sleep when idle
- Cold starts can make the first request slower
- External data sources can intermittently fail; the app is already written to return fallback-safe responses where possible

---

## Screenshots

This repo does not yet include final screenshots. When adding them, create a section like this:

### Suggested screenshots to capture

1. **Dashboard overview**
   - Show all six assets ranked by score
   - Include the top pick card and summary panel

2. **Asset detail panel**
   - Show one asset’s ATR distance, HTF zone, catalysts, and bias

3. **Economic calendar section**
   - Show the day’s high-impact releases and which markets they affect

4. **News sentiment section**
   - Show recent headlines with bullish/bearish/neutral tags

### Recommended image guidance

- Use a dark theme if the product is trader-facing
- Keep the scan timestamp visible
- Highlight the `top_pick` and `composite_score`
- Prefer 16:9 captures for README compatibility
- Save images under something like `docs/screenshots/`

Example placeholder markdown:

```md
![Dashboard overview](docs/screenshots/dashboard-overview.png)
![Asset detail](docs/screenshots/asset-detail.png)
![Economic calendar](docs/screenshots/economic-calendar.png)
```

---

## Tech stack

### Backend
- Python 3.11
- FastAPI
- Uvicorn
- Pandas
- NumPy
- yfinance
- httpx
- BeautifulSoup4

### Frontend
- Single-page frontend (planned / lightweight static app)
- Served by FastAPI when built

### Infrastructure
- Docker
- Render
- GitHub

---

## Design notes

AJFX Trading Radar is intentionally opinionated:

- It focuses on a **small, high-liquidity watchlist** rather than trying to scan everything
- It values **tradeability**, not just volatility
- It combines **structure + catalysts + sentiment** instead of relying on one signal class
- It is built to support a trader’s morning routine rather than replace discretionary decision-making

---

## Limitations

- News sentiment is currently lightweight and keyword-based
- Economic calendar scraping depends on third-party site structure
- The scoring engine is heuristic, not predictive ML
- Frontend assets are optional right now and may not yet exist in the repo
- Some endpoints may return partial/fallback data if external sources are unavailable

---

## Authors

**AJ & Bertie 🦔**
