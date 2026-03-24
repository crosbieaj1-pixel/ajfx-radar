# AJFX Trading Radar Product Specification

## Product name

**AJFX Trading Radar**

## Product tagline

**Which asset should I be trading today?**

---

## 1. What it is

AJFX Trading Radar is a focused market-selection product for discretionary traders. Its job is not to generate fully automated entries and exits. Its job is to answer a narrower, more useful question:

**Which of my core markets offers the best trade conditions right now?**

The system scans a fixed watchlist of liquid futures instruments:

- NQ
- ES
- YM
- GC
- CL
- 6E

It then evaluates each asset using a blended score built from:

- ATR proximity to actionable levels
- scheduled economic catalysts
- market news sentiment
- higher-timeframe structure
- simple momentum and activity context

The final output is a ranked shortlist that helps a trader decide where to focus attention first.

---

## 2. Problem statement

Most active traders waste time checking too many charts, too many headlines, and too many calendars before they even get to execution. Good opportunities are often missed because attention is spread too thin.

AJFX Trading Radar solves that by:

- narrowing focus to a high-value watchlist
- standardising how trade quality is judged
- surfacing the best opportunities first
- reducing the manual overhead of pre-market scanning

---

## 3. Target users

### Primary users
- Discretionary futures traders
- Intraday traders
- Swing traders using macro and technical context
- Traders who rotate between indices, commodities, and FX futures

### Secondary users
- Prop traders who want a quick morning prioritisation tool
- Trading communities or educators building a daily radar dashboard
- Developers building trader-facing dashboards on top of the API

### User profile
The ideal user already understands markets and execution. They do **not** need the app to place trades for them. They want the app to reduce noise, improve focus, and highlight the best-looking markets.

---

## 4. Product goals

### Primary goal
Help traders identify the **highest-quality market to trade today** across a fixed watchlist.

### Secondary goals
- shorten pre-market analysis time
- improve consistency in market selection
- blend macro + structure + sentiment in one view
- provide a clean API for a future web dashboard/mobile view

### Non-goals
- not a broker
- not an execution engine
- not a high-frequency analytics platform
- not a guaranteed predictive model
- not a replacement for trader discretion and risk management

---

## 5. Core features

## 5.1 Watchlist scanning
The system continuously or on-demand scans:

- NQ (Nasdaq 100 futures)
- ES (S&P 500 futures)
- YM (Dow futures)
- GC (Gold futures)
- CL (Crude Oil futures)
- 6E (Euro FX futures)

### Feature requirements
- fetch latest 1-hour price data
- compute instrument-level metrics consistently for all symbols
- produce a comparable score across the whole watchlist
- return a ranked list and a single top pick

---

## 5.2 ATR proximity analysis
A key premise of the product is that markets become more tradable when price is near a meaningful level and risk can be defined clearly.

### Inputs
- current price
- ATR value
- pivot levels
- H4 highs/lows
- nearest structural level

### Behaviour
- calculate distance from price to the nearest relevant level
- express that distance in ATR terms
- reward assets that are close to a significant level

### Outcome
Assets near strong levels receive a higher trade-quality contribution.

---

## 5.3 Economic catalyst mapping
Macro events can make a market much more interesting. The radar should identify whether the day’s calendar is likely to create volatility or directional opportunity.

### Inputs
- event time
- currency
- impact level
- event title

### Behaviour
- fetch daily calendar events
- map currencies/events to relevant assets
- score impact based on event importance
- expose catalysts in the API so the frontend can explain why a market ranked highly

### Outcome
Markets with relevant high-impact events receive a higher catalyst score.

---

## 5.4 News sentiment layer
The product should ingest recent macro/market headlines and convert them into a simple sentiment signal.

### Inputs
- headline text
- headline source
- timestamp

### Behaviour
- collect public market headlines from free sources
- classify them as bullish, bearish, or neutral using a simple rules-based model initially
- link relevant keywords to assets
- adjust each asset’s score based on matched sentiment

### Outcome
A market with supportive headlines receives a positive lift; adverse headlines can drag its ranking lower.

---

## 5.5 Higher-timeframe level context
Trade quality should not rely on momentum alone. The radar should know whether price is sitting at support, resistance, or in a messy mid-range area.

### Inputs
- resampled H1 data
- resampled H4 data
- recent range highs/lows
- swing points

### Behaviour
- compute H1 and H4 highs/lows/closes
- classify bias as bullish, bearish, or neutral
- label the current zone (support zone, resistance zone, mid-range, etc.)
- expose this structure in both detailed and ranked responses

### Outcome
The trader gets structural context immediately, without opening every chart individually.

---

## 5.6 Composite ranking engine
The scanner’s central job is to turn several noisy market inputs into a single ranked output.

### Behaviour
- compute component scores
- cap or clamp values where needed
- calculate a final composite score from 0 to 100
- sort all assets descending by final score
- return the best candidate as `top_pick`

### Outcome
The product produces one decisive answer while still exposing the component logic.

---

## 5.7 Single-page dashboard
The intended frontend is a simple dashboard designed for quick daily use.

### Required UI outcomes
- ranked table or cards for all six assets
- clear top pick presentation
- visible scan timestamp
- scoring breakdown per asset
- supporting macro/news context
- responsive layout for laptop-first usage

---

## 6. Scoring methodology

The current scoring logic in the codebase blends five components. For product clarity, the intended weighting should be described as follows.

## 6.1 Weight summary

| Component | Target weight | Purpose |
|---|---:|---|
| ATR proximity | 40% | Rewards assets close to actionable levels |
| Economic catalysts | 20% | Rewards assets with relevant macro volatility drivers |
| News sentiment | 10% | Reflects current headline tone |
| Momentum | 20% | Captures whether price is moving with intent |
| HTF / structural context | 10% | Rewards alignment with meaningful higher-timeframe positioning |

### Important implementation note
The current codebase explicitly scores:
- ATR proximity
- economic catalysts
- news sentiment
- momentum
- volume

It also exposes HTF context in the response, but HTF is not yet a fully separate weighted component in the arithmetic. Product-wise, HTF should remain a first-class scoring concept, and future iterations should tighten the scoring model so the written spec and implementation align more closely.

---

## 6.2 ATR proximity weighting

### Rationale
Price near a meaningful level is often more tradable than price drifting in the middle of nowhere.

### Proposed logic
- **0.0–0.3 ATR away** → excellent setup quality
- **0.3–0.6 ATR away** → good
- **0.6–1.0 ATR away** → moderate
- **1.0–1.5 ATR away** → weak
- **>1.5 ATR away** → poor

### Intended contribution
Up to **40 points**.

---

## 6.3 Economic catalyst weighting

### Rationale
Scheduled events can supply the volatility and narrative needed for a trade to develop.

### Proposed logic
- high-impact relevant event → strong positive contribution
- medium-impact relevant event → moderate positive contribution
- low-impact event → little or no contribution
- multiple relevant events may stack, but the score should be capped

### Intended contribution
Up to **20 points**.

---

## 6.4 News sentiment weighting

### Rationale
Headline flow can reinforce or challenge the technical picture.

### Proposed logic
- bullish relevant headlines → positive points
- bearish relevant headlines → negative points
- neutral / irrelevant headlines → no change
- cap the total to avoid headline spam skewing the ranker

### Intended contribution
Approximately **10 points** in either direction.

---

## 6.5 Momentum weighting

### Rationale
Good setups often combine location with movement. If a market is at the right place and moving with intent, it deserves more attention.

### Proposed logic
- positive daily/intraday move → positive momentum contribution
- negative move → negative contribution
- stronger moves carry larger magnitude, within a cap

### Intended contribution
Approximately **20 points**.

---

## 6.6 HTF context weighting

### Rationale
Higher-timeframe context helps distinguish between a clean level reaction and an ugly middle-of-range chase.

### Proposed logic
- bullish/bearish bias aligned with current zone → add points
- mid-range consolidation → low or neutral contribution
- price at exhaustion/resistance/support extremes without confirmation → reduce confidence

### Intended contribution
Approximately **10 points**.

### Current reality
The code currently returns HTF bias and zone classification but does not apply them as a standalone weighted score. This should be improved in a later version.

---

## 7. Functional requirements

### Backend
- expose a FastAPI app
- provide health, scan, calendar, news, and asset-detail routes
- fetch upstream data with graceful fallback behaviour
- return structured JSON payloads for dashboard consumption

### Scoring engine
- output a comparable score for every asset in the watchlist
- generate a human-readable summary for each asset
- clamp final score to a 0–100 range

### Deployment
- run locally on port `8011`
- support Docker-based hosting
- deploy cleanly to Render

### Startup scripts
- provide a Linux/macOS shell script
- provide a Windows batch script
- install dependencies when required

---

## 8. Non-functional requirements

### Performance
- target scan completion suitable for dashboard use, ideally within a few seconds under normal conditions
- avoid unnecessary repeated upstream calls where caching can be added later

### Reliability
- return partial or fallback-safe responses when external sources fail
- avoid full app crashes because one data provider is unavailable

### Usability
- output should be interpretable quickly by a trader under time pressure
- the top pick and supporting reason should be visible immediately

### Maintainability
- keep modules separated by concern: data fetchers, scoring, API
- make future provider replacement straightforward

---

## 9. Success metrics

The product is successful if it consistently helps users focus faster and better.

### Core success metrics
- **Time saved:** average pre-market scanning time reduced
- **Focus quality:** user checks fewer irrelevant markets before trading
- **Engagement:** repeated daily use of the scan/dashboard
- **Interpretability:** users understand why the top-ranked asset won
- **Reliability:** health checks pass and scan endpoint returns usable output consistently

### Suggested measurable KPIs
- daily active users / repeat daily usage
- average `/api/scan` calls per user per session
- percentage of scans returning full data vs fallback data
- median scan duration
- user-reported usefulness of `top_pick`

---

## 10. Future roadmap

## Phase 1 — solid foundation
- stabilise current API outputs
- ship clean documentation
- add a basic frontend dashboard
- improve error handling and logging

## Phase 2 — better scoring intelligence
- make HTF context a true weighted score
- introduce catalyst recency and event-time proximity weighting
- improve news relevance matching by asset
- add confidence bands or score buckets

## Phase 3 — trader workflow upgrades
- saved watchlists
- session filters (London / New York / Asia)
- alerts when a new asset becomes top pick
- richer asset-detail drilldowns
- historical scan snapshots for review

## Phase 4 — advanced data and analytics
- stronger sentiment/NLP pipeline
- additional asset classes
- custom weighting profiles per trader style
- backtesting of ranking effectiveness
- broker/charting integrations

---

## 11. Risks and constraints

- Free upstream data sources can change structure or rate-limit aggressively
- Rules-based sentiment is simple and may misclassify nuance
- Trade quality is inherently subjective; ranking should be treated as assistance, not certainty
- Free-tier hosting may introduce sleep/cold-start delays

---

## 12. Product positioning

AJFX Trading Radar should be positioned as a **decision-support radar for market selection**, not a signal-selling black box.

Its value is clarity:
- fewer charts
- faster focus
- better prioritisation
- more consistent market selection

---

## 13. Authors

**AJ & Bertie 🦔**
