"""
Market news headline fetcher.
Pulls recent market news from free sources.
"""
import httpx
from bs4 import BeautifulSoup
import logging
from datetime import datetime

# News sources (all free, no API key needed)
NEWS_SOURCES = [
    {
        "name": "Reuters Markets",
        "url": "https://www.reutersagency.com/feed/?best-topics=markets&post_type=best",
        "selectors": {"title": "h2.entry-title a", "summary": ".entry-content"}
    },
    {
        "name": "Yahoo Finance",
        "url": "https://finance.yahoo.com/news/",
        "selectors": {"title": "h3", "summary": "p"}
    }
]


def fetch_headlines(url: str, selectors: dict, source: str, max_items: int = 8) -> list:
    """Fetch headlines from a news source."""
    headlines = []

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }

        with httpx.Client(timeout=10.0) as client:
            response = client.get(url, headers=headers)
            if response.status_code != 200:
                return headlines

            soup = BeautifulSoup(response.text, "html.parser")

            # Try to find news items
            for elem in soup.select(selectors["title"])[:max_items]:
                try:
                    title = elem.get_text(strip=True)
                    link = elem.get("href", "") if elem.name == "a" else elem.find_parent("a").get("href", "") if elem.find_parent("a") else ""

                    # Clean up title
                    title = title[:200]  # Truncate long titles

                    if title and len(title) > 10:
                        headlines.append({
                            "title": title,
                            "source": source,
                            "url": link if link.startswith("http") else "",
                            "time": datetime.utcnow().strftime("%H:%M UTC"),
                            "sentiment": classify_sentiment(title)
                        })
                except Exception:
                    continue

    except Exception as e:
        logging.warning(f"News fetch error from {source}: {e}")

    return headlines


def classify_sentiment(headline: str) -> str:
    """Basic keyword-based sentiment classification."""
    headline_lower = headline.lower()

    bullish = ["surge", "rally", "gain", "rise", "high", "bull", "upbeat", "growth",
               "strong", "beat", "exceed", "record", "soar", "jump", "boost"]
    bearish = ["fall", "drop", "decline", "tumble", "plunge", "low", "bear", "downbeat",
               "weak", "miss", "slump", "worries", "fear", "selloff", "cut"]

    score = sum(1 for w in bullish if w in headline_lower) - sum(1 for w in bearish if w in headline_lower)

    if score > 0:
        return "bullish"
    elif score < 0:
        return "bearish"
    else:
        return "neutral"


def get_market_news() -> list:
    """Get market news from all configured sources."""
    all_headlines = []

    for source in NEWS_SOURCES:
        headlines = fetch_headlines(
            source["url"],
            source["selectors"],
            source["name"]
        )
        all_headlines.extend(headlines)
        logging.info(f"Fetched {len(headlines)} headlines from {source['name']}")

    # Sort by sentiment (prioritise highly directional news)
    sentiment_order = {"bearish": 0, "bullish": 1, "neutral": 2}
    all_headlines.sort(key=lambda x: sentiment_order.get(x.get("sentiment", "neutral")))

    # Deduplicate by title
    seen = set()
    unique = []
    for h in all_headlines:
        if h["title"] not in seen:
            seen.add(h["title"])
            unique.append(h)

    return unique[:15]  # Top 15 headlines


if __name__ == "__main__":
    news = get_market_news()
    for item in news:
        print(f"[{item['sentiment'].upper():8}] {item['source']} | {item['title']}")
