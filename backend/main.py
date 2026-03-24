"""
AJFX Trading Radar — FastAPI Backend
Serves asset rankings, news, economic calendar, and HTF levels.
"""
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import asyncio
import logging
from datetime import datetime

# Import data modules
from data.yahoo import get_assets_data
from data.calendar import get_economic_calendar
from data.news import get_market_news
from data.levels import compute_htf_levels
from scoring.engine import score_assets

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(
    title="AJFX Trading Radar",
    version="1.0.0",
    description="Which asset should I be trading today?"
)

# CORS — allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount frontend static files
if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "service": "ajfx-radar",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/scan")
async def scan_assets():
    """
    Main endpoint — returns ranked asset list with full scoring.
    Combines price data, HTF levels, news, and economic calendar.
    """
    try:
        # Run all data fetches in parallel
        price_task = asyncio.create_task(asyncio.to_thread(get_assets_data))
        calendar_task = asyncio.create_task(asyncio.to_thread(get_economic_calendar))
        news_task = asyncio.create_task(asyncio.to_thread(get_market_news))

        prices = await price_task
        calendar = await calendar_task
        news = await news_task

        # Compute HTF levels for each asset
        assets_with_levels = []
        for asset in prices:
            levels = compute_htf_levels(asset["symbol"], asset["data"])
            asset["htf_levels"] = levels
            assets_with_levels.append(asset)

        # Score all assets
        scored = score_assets(assets_with_levels, calendar, news)

        # Sort by composite score descending
        scored.sort(key=lambda x: x["composite_score"], reverse=True)

        # Add economic events
        top_pick = scored[0]["symbol"] if scored else None

        return {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "assets": scored,
            "economic_events": calendar,
            "news_headlines": news,
            "top_pick": top_pick
        }

    except Exception as e:
        logging.error(f"Scan error: {e}")
        return {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "error": str(e),
            "assets": [],
            "economic_events": [],
            "news_headlines": [],
            "top_pick": None
        }


@app.get("/api/news")
async def news():
    """Returns today's market news headlines."""
    try:
        return await asyncio.to_thread(get_market_news)
    except Exception as e:
        logging.error(f"News error: {e}")
        return []


@app.get("/api/calendar")
async def calendar():
    """Returns today's economic calendar events."""
    try:
        return await asyncio.to_thread(get_economic_calendar)
    except Exception as e:
        logging.error(f"Calendar error: {e}")
        return []


@app.get("/api/asset/{symbol}")
async def asset_detail(symbol: str):
    """Returns detailed data for a specific asset."""
    try:
        prices = await asyncio.to_thread(get_assets_data)
        asset = next((a for a in prices if a["symbol"].upper() == symbol.upper()), None)
        if not asset:
            return {"error": f"Symbol {symbol} not found"}

        levels = compute_htf_levels(symbol.upper(), asset["data"])
        asset["htf_levels"] = levels
        return asset
    except Exception as e:
        logging.error(f"Asset detail error: {e}")
        return {"error": str(e)}


@app.get("/")
async def index():
    """Serves the frontend dashboard."""
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "Frontend not built yet. POST to /api/scan for data."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8011)
