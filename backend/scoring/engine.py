"""
Asset scoring engine.
Scores each asset 0-100 based on ATR proximity, catalysts, momentum, news.
"""
import logging
from datetime import datetime

# Asset to currency/event mapping for catalyst scoring
ASSET_CATALYSTS = {
    "NQ": {"currencies": ["USD"], "keywords": ["nasdaq", "tech", "equity", "stock"]},
    "ES": {"currencies": ["USD"], "keywords": ["s&p", "sp500", "equity", "stock", "fed"]},
    "YM": {"currencies": ["USD"], "keywords": ["dow", "djia", "equity", "stock"]},
    "GC": {"currencies": ["USD", "XAU"], "keywords": ["gold", "goldman", "metals", "inflation", "safe haven"]},
    "CL": {"currencies": ["USD", "XTI"], "keywords": ["oil", "crude", "petroleum", "opec", "energy"]},
    "6E": {"currencies": ["EUR"], "keywords": ["euro", "ecb", "european"]},
}

CATALYST_IMPACT = {
    "high": 20,
    "medium": 10,
    "low": 0
}


def score_assets(assets: list, calendar: list, news: list) -> list:
    """
    Score all assets and return ranked list with explanations.
    """
    scored = []

    for asset in assets:
        try:
            symbol = asset["symbol"]
            config = ASSET_CATALYSTS.get(symbol, {"currencies": [], "keywords": []})

            # 1. ATR Proximity Score (0-40 points)
            atr_score = calc_atr_proximity_score(asset)
            atr_points = atr_score * 40

            # 2. Economic Catalyst Score (-20 to +20)
            econ_points = calc_economic_score(calendar, config["currencies"], symbol)

            # 3. News Sentiment Score (-10 to +10)
            news_points = calc_news_score(news, config["keywords"], symbol)

            # 4. Momentum Score (-10 to +10)
            momentum_points = calc_momentum_score(asset)

            # 5. Volume Score (-5 to +5)
            vol_points = calc_volume_score(asset)

            # Composite
            total = atr_points + econ_points + news_points + momentum_points + vol_points
            composite = max(0, min(100, round(total, 1)))

            # Direction bias
            direction = determine_direction(asset, econ_points, news_points, momentum_points)

            # Generate explanation
            explanation = generate_explanation(
                symbol, atr_score, econ_points, news_points, momentum_points, vol_points, direction
            )

            scored.append({
                "symbol": symbol,
                "name": asset["name"],
                "price": asset["price"],
                "daily_change_pct": asset.get("daily_change_pct", 0),
                "atr": asset["atr"],
                "composite_score": composite,
                "atr_proximity_score": round(atr_score * 100, 0),
                "economic_impact": econ_points,
                "news_sentiment": news_points,
                "momentum": momentum_points,
                "volume_score": vol_points,
                "direction": direction,
                "nearest_level": asset.get("nearest_level", 0),
                "distance_to_nearest_atr": asset.get("distance_to_nearest_atr", 999),
                "htf_bias": asset.get("htf_levels", {}).get("h4", {}).get("bias", "neutral"),
                "zone_classification": asset.get("htf_levels", {}).get("zone_classification", "unknown"),
                "catalysts": get_asset_catalysts(calendar, config["currencies"], news),
                "summary": explanation,
                "generated_at": datetime.utcnow().isoformat() + "Z"
            })

        except Exception as e:
            logging.error(f"Scoring error for {asset.get('symbol', '?')}: {e}")
            continue

    return scored


def calc_atr_proximity_score(asset: dict) -> float:
    """
    How close is price to a key level, expressed as ATR.
    0.0-0.3 ATR = score 1.0 (very close, high probability)
    0.3-0.6 ATR = score 0.7
    0.6-1.0 ATR = score 0.4
    >1.0 ATR = score 0.1
    """
    dist = asset.get("distance_to_nearest_atr", 999)
    if dist <= 0.3:
        return 1.0
    elif dist <= 0.6:
        return 0.8
    elif dist <= 1.0:
        return 0.5
    elif dist <= 1.5:
        return 0.3
    else:
        return 0.1


def calc_economic_score(calendar: list, currencies: list, symbol: str) -> int:
    """Score economic events affecting this asset."""
    if not currencies:
        return 0

    total = 0
    for event in calendar:
        if event.get("currency", "") in currencies:
            impact = event.get("impact", "low")
            total += CATALYST_IMPACT.get(impact, 0)

    # Cap at ±20
    return max(-20, min(20, total))


def calc_news_score(news: list, keywords: list, symbol: str) -> int:
    """Score news sentiment for this asset."""
    if not keywords:
        return 0

    score = 0
    for item in news:
        title = item.get("title", "").lower()
        sentiment = item.get("sentiment", "neutral")

        for kw in keywords:
            if kw in title:
                if sentiment == "bullish":
                    score += 2
                elif sentiment == "bearish":
                    score -= 2
                break

    return max(-10, min(10, score))


def calc_momentum_score(asset: dict) -> int:
    """Score based on intraday momentum and ATR% of move."""
    change = asset.get("daily_change_pct", 0)

    # Normalise: 0.5% move = 5pts, 1%+ move = 10pts
    score = min(10, int(abs(change) * 10))
    return score if change >= 0 else -score


def calc_volume_score(asset: dict) -> int:
    """Score based on volume vs average."""
    vol_ratio = asset.get("volume_ratio", 1.0)

    if vol_ratio > 1.5:
        return 5
    elif vol_ratio > 1.2:
        return 3
    elif vol_ratio < 0.7:
        return -3
    else:
        return 0


def determine_direction(asset: dict, econ: int, news: int, momentum: int) -> str:
    """Determine likely trade direction."""
    bullish_signals = 0
    bearish_signals = 0

    # Momentum
    if asset.get("daily_change_pct", 0) > 0.3:
        bullish_signals += 1
    elif asset.get("daily_change_pct", 0) < -0.3:
        bearish_signals += 1

    # Catalyst score
    if econ > 5:
        bullish_signals += 1
    elif econ < -5:
        bearish_signals += 1

    # News sentiment
    if news > 2:
        bullish_signals += 1
    elif news < -2:
        bearish_signals += 1

    # Momentum total
    if momentum > 3:
        bullish_signals += 1
    elif momentum < -3:
        bearish_signals += 1

    if bullish_signals > bearish_signals:
        return "LONG"
    elif bearish_signals > bullish_signals:
        return "SHORT"
    else:
        return "NEUTRAL"


def get_asset_catalysts(calendar: list, currencies: list, news: list) -> list:
    """Get list of active catalysts for this asset."""
    catalysts = []

    for event in calendar:
        if event.get("currency", "") in currencies and event.get("impact") in ["high", "medium"]:
            catalysts.append(f"{event.get('time', 'TBD')} — {event.get('event', 'Economic Event')} ({event.get('impact', '?').upper()})")

    return catalysts[:5]  # Top 5 catalysts


def generate_explanation(symbol: str, atr: float, econ: int, news: int, momentum: int, vol: int, direction: str) -> str:
    """Generate a human-readable trading brief for this asset."""

    parts = []

    # ATR proximity
    if atr >= 0.8:
        parts.append(f"{symbol} is pressing a key level — ATR proximity is excellent.")
    elif atr >= 0.5:
        parts.append(f"{symbol} is within ATR range of a significant level.")
    else:
        parts.append(f"{symbol} is mid-range, no compelling level setup.")

    # Economic
    if econ > 5:
        parts.append("Strong economic cross-currents adding volatility.")
    elif econ < -5:
        parts.append("Economic headwinds present.")

    # News
    if news > 3:
        parts.append("Bullish news flow supporting directional bias.")
    elif news < -3:
        parts.append("Bearish headlines weighing on price.")

    # Direction summary
    if direction == "LONG":
        parts.append("Bias: LONG — bullish signals outweigh bearish.")
    elif direction == "SHORT":
        parts.append("Bias: SHORT — bearish signals outweigh bullish.")
    else:
        parts.append("Bias: NEUTRAL — mixed signals, await clarity.")

    return " ".join(parts)
