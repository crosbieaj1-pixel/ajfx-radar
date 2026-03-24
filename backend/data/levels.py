"""
HTF (Higher Timeframe) level calculator.
Computes H1 and H4 support/resistance zones.
"""
import pandas as pd
import logging


def identify_swing_points(df, lookback: int = 20) -> dict:
    """
    Identify swing highs and swing lows from price data.
    """
    highs = df["high"].values
    lows = df["low"].values
    closes = df["close"].values

    # Find swing high (highest point with lower highs on both sides)
    swing_high = None
    swing_high_idx = None
    for i in range(lookback, len(highs) - lookback):
        if all(highs[i] > highs[i-j] for j in range(1, lookback+1)) and \
           all(highs[i] > highs[i+j] for j in range(1, lookback+1)):
            swing_high = float(highs[i])
            swing_high_idx = i
            break

    # Find swing low (lowest point with higher lows on both sides)
    swing_low = None
    swing_low_idx = None
    for i in range(lookback, len(lows) - lookback):
        if all(lows[i] < lows[i-j] for j in range(1, lookback+1)) and \
           all(lows[i] < lows[i+j] for j in range(1, lookback+1)):
            swing_low = float(lows[i])
            swing_low_idx = i
            break

    return {
        "swing_high": swing_high,
        "swing_high_idx": swing_high_idx,
        "swing_low": swing_low,
        "swing_low_idx": swing_low_idx
    }


def compute_htf_levels(symbol: str, df: pd.DataFrame) -> dict:
    """
    Compute H1 and H4 S/R levels for a given asset.
    """
    try:
        # Resample to 1H
        df1h = df.resample("1H").agg({
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum"
        }).dropna()

        # Resample to 4H
        df4h = df.resample("4H").agg({
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum"
        }).dropna()

        # H4 levels
        h4_recent = df4h.tail(8)  # Last 32h of 4h candles
        h4_high = float(h4_recent["high"].max())
        h4_low = float(h4_recent["low"].min())
        h4_close = float(df4h["close"].iloc[-1])

        # H1 levels
        h1_recent = df1h.tail(12)  # Last 12h
        h1_high = float(h1_recent["high"].max())
        h1_low = float(h1_recent["low"].min())
        h1_close = float(df1h["close"].iloc[-1])

        # Swing points
        swings = identify_swing_points(df1h, lookback=6)

        # Determine trend bias
        if h4_close > h4_high * 0.995:
            h4_bias = "bullish"
        elif h4_close < h4_low * 1.005:
            h4_bias = "bearish"
        else:
            h4_bias = "neutral"

        if h1_close > h1_high * 0.998:
            h1_bias = "bullish"
        elif h1_close < h1_low * 1.002:
            h1_bias = "bearish"
        else:
            h1_bias = "neutral"

        # Current price position
        current_price = float(df["close"].iloc[-1])

        # Distance to H4 levels as % of ATR
        atr = float(df["high"].diff().abs().rolling(14).max().iloc[-1])
        dist_to_h4_high = (h4_high - current_price) / atr if atr else 0
        dist_to_h4_low = (current_price - h4_low) / atr if atr else 0

        return {
            "h4": {
                "high": round(h4_high, 2),
                "low": round(h4_low, 2),
                "close": round(h4_close, 2),
                "bias": h4_bias,
                "range_pct": round((h4_high - h4_low) / h4_low * 100, 2) if h4_low else 0
            },
            "h1": {
                "high": round(h1_high, 2),
                "low": round(h1_low, 2),
                "close": round(h1_close, 2),
                "bias": h1_bias,
                "range_pct": round((h1_high - h1_low) / h1_low * 100, 2) if h1_low else 0
            },
            "swings": swings,
            "atr_current": round(atr, 2),
            "dist_to_h4_high_atr": round(dist_to_h4_high, 2),
            "dist_to_h4_low_atr": round(dist_to_h4_low, 2),
            "zone_classification": classify_zone(dist_to_h4_high, dist_to_h4_low, current_price, atr)
        }

    except Exception as e:
        logging.error(f"HTF levels error for {symbol}: {e}")
        return {
            "h4": {"high": 0, "low": 0, "close": 0, "bias": "unknown"},
            "h1": {"high": 0, "low": 0, "close": 0, "bias": "unknown"},
            "swings": {},
            "atr_current": 0,
            "error": str(e)
        }


def classify_zone(h4_high: float, h4_low: float, price: float, atr: float) -> str:
    """
    Classify current price zone within H4 range.
    """
    range_size = h4_high - h4_low
    if range_size == 0:
        return "unknown"

    position = (price - h4_low) / range_size  # 0 = at bottom, 1 = at top

    if position > 0.85:
        return "H4 Resistance Zone — potential reversal"
    elif position < 0.15:
        return "H4 Support Zone — potential bounce"
    elif position > 0.65:
        return "Upper H4 Range — momentum fading"
    elif position < 0.35:
        return "Lower H4 Range — accumulation zone"
    else:
        return "Mid-range consolidation"
