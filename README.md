# AJFX Trading Radar

> **"Which asset should I be trading today?"**

A professional-grade trading radar that ranks futures assets (NQ, ES, YM, GC, CL, 6E) by trade quality — combining ATR proximity, economic catalysts, news sentiment, and HTF level analysis into a single composite score.

---

## 🎯 Live Dashboard
**Coming soon:** `https://ajfx-radar.onrender.com`

---

## Features

### 📊 Asset Rankings
Ranks all major futures instruments by composite trade quality score (0-100):
- **NQ=F** — Nasdaq 100
- **ES=F** — S&P 500
- **YM=F** — Dow Jones
- **GC=F** — Gold
- **CL=F** — WTI Crude Oil
- **6E=F** — Euro/USD

### 🎯 ATR Proximity Scoring (0-40 pts)
How close is price to a Higher Timeframe level? Measured in ATR units. The closer to a level, the higher the score. Clean ATR structure = high probability setup.

### 📰 Economic Catalyst Detection (0-20 pts)
Scans Forex Factory for high-impact events today. Maps currency events to affected assets. FOMC, NFP, CPI = maximum impact on USD-denominated assets.

### 📱 News Sentiment (-10 to +10 pts)
Free market headlines with basic bullish/bearish/neutral classification. Positive news for an asset = score boost.

### 📈 Momentum & Volume (0-15 pts)
Intraday % change vs average. Volume spike = institutional interest. Confirms or rejects directional bias.

### 🔧 HTF Level Analysis
- H4 (4-hour) S/R zones
- H1 level bias
- Swing high/low identification
- Zone classification (resistance zone, accumulation zone, etc.)
- Distance to nearest level in ATR units

### 🤖 AI Trade Brief
Each asset gets a plain-English trading brief explaining why it's ranked where it is. No jargon — just actionable insight.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Frontend (HTML/CSS/JS)            │
│         Dark trading dashboard, mobile-friendly       │
└────────────────────────┬────────────────────────────┘
                         │  GET /api/scan
┌────────────────────────▼────────────────────────────┐
│                FastAPI Backend                       │
│  Port 8011 | CORS enabled | Serves frontend         │
├──────────┬──────────┬──────────┬───────────────────┤
│ Yahoo    │ Forex    │ News     │ Scoring Engine    │
│ Finance  │ Factory  │ Headlines│ (composite)       │
│ Data     │ Calendar │          │                   │
└──────────┴──────────┴──────────┴───────────────────┘
         │           │           │
    yfinance      httpx+BS4   httpx
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python 3.11) |
| Data | yfinance, httpx, BeautifulSoup4 |
| Scoring | Pandas, NumPy |
| Frontend | Vanilla HTML/CSS/JS |
| Hosting | Render (Docker, free tier) |
| CI/CD | GitHub → Render Blueprint |

---

## Quick Start

### Local Development

```bash
# Clone repo
git clone https://github.com/crosbieaj1-pixel/ajfx-radar.git
cd ajfx-radar

# Install dependencies
pip install -r backend/requirements.txt

# Run
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8011 --reload
```

Open: http://localhost:8011

### Deploy to Render (Free)

1. Push code to GitHub
2. Go to [render.com](https://render.com) → Login
3. Click **"New"** → **"Blueprint"**
4. Connect your GitHub repo
5. Render reads `render.yaml` and deploys automatically
6. Get your URL: `https://your-app.onrender.com`

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Dashboard frontend |
| `GET` | `/api/scan` | Full ranked asset scan |
| `GET` | `/api/calendar` | Economic calendar today |
| `GET` | `/api/news` | Market news headlines |
| `GET` | `/api/asset/{symbol}` | Single asset detail |
| `GET` | `/api/health` | Service health check |

See `API_DOCS.md` for full documentation.

---

## Scoring Methodology

Composite Score (0-100) =

- **ATR Proximity** (0-40 pts): How close is price to HTF level? ≤0.3 ATR = 40pts
- **Economic Impact** (-20 to +20 pts): High-impact events today for this asset's currency
- **News Sentiment** (-10 to +10 pts): Bullish/bearish headlines affecting this asset
- **Momentum** (-10 to +10 pts): Intraday % move vs average
- **Volume** (-5 to +5 pts): Volume spike vs 5-day average

Direction bias: LONG/SHORT/NEUTRAL based on weighted signal count.

---

## Screenshots

*(Dashboard screenshots to be added)*

---

## Roadmap

- [ ] AI-generated trading brief per asset (GPT-powered)
- [ ] Twitter/X sentiment for macro traders
- [ ] Real-time price updates via WebSocket
- [ ] Trade journal integration
- [ ] Mobile app (React Native)
- [ ] Multi-timeframe scanner (H1, H4, D1 levels)
- [ ] Telegram alerts at score thresholds

---

## Contributing

1. Fork the repo
2. Create a feature branch
3. Make changes
4. Push to GitHub → auto-deploys

---

*Built by AJ & Bertie 🦔*

*No financial advice. For educational purposes only. Trading futures involves substantial risk of loss.*
