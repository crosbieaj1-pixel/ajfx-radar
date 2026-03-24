"""
Yahoo Finance data fetcher for futures assets.
Gets price, ATR, volume, and H1/H4 levels.
"""
import yfinance as yf
import pandas as pd
import logging
from datetime import datetime, timedelta

# Asset config: ticker, name, description
ASSETS = [
    {"symbol": "NQ=F", "name": "Nasdaq 100", "description": "Nasdaq futures"},
    {"symbol": "ES=F", "name": "S&P 500", "description": "S&P futures"},
    {"symbol": "YM=F", "name": "Dow Jones", "description": "Dow Jones futures"},
    {"symbol": "GC=F", "name": "Gold", "description": "Gold futures"},
    {"symbol": "CL=F", "name": "Crude Oil", "description": "WTI Crude oil futures"},
    {"symbol": "6E=F", "name": "Euro", "description": "EUR/USD futures"},
]

PERIOD = "5d"  # 5 days of data for H1 levels
ATR_PERIOD = 14


def compute_atr(high, low, close, period=14):
    """Compute ATR(14)."""
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs()
    ], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return float(atr.iloc[-1])


def compute_pivot_levels(high, low, close):
    """Standard daily pivot point levels."""
    pivot = (high + low + close) / 3
    r1 = 2 * pivot - low
    s1 = 2 * pivot - high
    r2 = pivot + (high - low)
    s2 = pivot - (high - low)
    return {
        "pivot": float(pivot),
        "r1": float(r1),
        "s1": float(s1),
        "r2": float(r2),
        "s2": float(s2)
    }


def compute_h4_levels(df):
    """Compute H4 (4-hour) S/R levels from 4h candles."""
    df4h = df.resample("4H").agg({"high": "max", "low": "min", "close": "last"})
    recent_4h = df4h.iloc[-6:]  # Last 24h of 4h candles

    highs = recent_4h["high"].values
    lows = recent_4h["low"].values
    closes = recent_4h["close"].values

    # Key H4 levels
    h4_high = float(recent_4h["high"].max())
    h4_low = float(recent_4h["low"].min())
    h4_close = float(recent_4h["close"].iloc[-1])

    # Recent swing high/low
    swing_high = float(recent_4h["high"].idxmax())
    swing_low = float(recent_4h["low"].idxmin())

    return {
        "h4_high": h4_high,
        "h4_low": h4_low,
        "h4_close": h4_close,
        "swing_high_date": str(swing_high) if swing_high else None,
        "swing_low_date": str(swing_low) if swing_low else None,
    }


def get_assets_data():
    """Fetch price data for all configured assets."""
    results = []

    for asset in ASSETS:
        try:
            ticker = yf.Ticker(asset["symbol"])
            df = ticker.history(period=PERIOD, interval="1h")

            if df.empty or len(df) < 20:
                logging.warning(f"No sufficient data for {asset['symbol']}")
                continue

            current_price = float(df["close"].iloc[-1])
            prev_close = float(df["close"].iloc[-2]) if len(df) > 1 else current_price
            daily_change = ((current_price - prev_close) / prev_close) * 100

            # ATR
            atr = compute_atr(df["high"], df["low"], df["close"], ATR_PERIOD)

            # Daily pivot levels
            daily_high = float(df["high"].iloc[-1])
            daily_low = float(df["low"].iloc[-1])
            daily_close = current_price
            pivots = compute_pivot_levels(daily_high, daily_low, daily_close)

            # H4 levels
            h4 = compute_h4_levels(df)

            # Average volume
            avg_vol_5d = float(df["volume"].tail(5).mean())
            current_vol = float(df["volume"].iloc[-1])
            vol_ratio = current_vol / avg_vol_5d if avg_vol_5d > 0 else 1.0

            # Distance to nearest level
            levels = [h4["h4_high"], h4["h4_low"], pivots["r1"], pivots["s1"]]
            distances = [abs(current_price - l) for l in levels]
            nearest_distance = min(distances) / atr if atr > 0 else 999
            nearest_level = levels[distances.index(min(distances))]

            results.append({
                "symbol": asset["symbol"].replace("=F", ""),
                "name": asset["name"],
                "description": asset["description"],
                "price": round(current_price, 2),
                "daily_change_pct": round(daily_change, 2),
                "atr": round(atr, 2),
                "atr_distance": round(nearest_distance, 2),
                "atr_pct_of_price": round((atr / current_price) * 100, 3) if current_price else 0,
                "volume_ratio": round(vol_ratio, 2),
                "nearest_level": round(nearest_level, 2),
                "distance_to_nearest_atr": round(nearest_distance, 2),
                "pivot_levels": pivots,
                "h4_levels": h4,
                "data": df,
                "generated_at": datetime.utcnow().isoformat() + "Z"
            })

            logging.info(f"Fetched {asset['symbol']}: ${current_price:.2f}, ATR ${atr:.2f}")

        except Exception as e:
            logging.error(f"Error fetching {asset['symbol']}: {e}")
            continue

    return results


if __name__ == "__main__":
    data = get_assets_data()
    for asset in data:
        print(f"{asset['symbol']}: ${asset['price']} | ATR ${asset['atr']} | "
              f"Dist {asset['distance_to_nearest_atr']:.2f}x ATR")
