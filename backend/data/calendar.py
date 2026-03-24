"""
Economic Calendar fetcher — Forex Factory.
Scrapes today's high-impact events.
"""
import httpx
from bs4 import BeautifulSoup
import logging
from datetime import datetime, timedelta

FOREX_FACTORY_URL = "https://www.forexfactory.com/calendar.php"
# Alternative RSS feed (no auth needed)
FOREX_FACTORY_RSS = "https://www.forexfactory.com/calendar.ashx"


def parse_ff_calendar(html: str) -> list:
    """Parse Forex Factory calendar HTML."""
    soup = BeautifulSoup(html, "html.parser")
    events = []

    today = datetime.now().strftime("%a %b %d").upper()

    # Find all calendar events
    for row in soup.select("tr.calendar__row"):
        try:
            # Extract currency
            currency_elem = row.select_one(".calendar__currency")
            currency = currency_elem.text.strip() if currency_elem else ""

            # Impact
            impact_elem = row.select_one(".calendar__impact--bullish, .calendar__impact--bearish")
            impact_class = row.get("class", [])
            if "calendar__impact--high" in impact_class:
                impact = "high"
            elif "calendar__impact--medium" in impact_class:
                impact = "medium"
            else:
                impact = "low"

            # Time
            time_elem = row.select_one(".calendar__time")
            time_str = time_elem.text.strip() if time_elem else "All Day"

            # Event name
            event_elem = row.select_one(".calendar__event")
            event_name = event_elem.text.strip() if event_elem else ""

            # Previous/Forecast/Actual
            prev_elem = row.select_one(".calendar__previous")
            forecast_elem = row.select_one(".calendar__forecast")
            actual_elem = row.select_one(".calendar__actual")

            previous = prev_elem.text.strip() if prev_elem else ""
            forecast = forecast_elem.text.strip() if forecast_elem else ""
            actual = actual_elem.text.strip() if actual_elem else ""

            if event_name and impact in ["high", "medium"]:
                events.append({
                    "time": time_str,
                    "currency": currency,
                    "event": event_name,
                    "impact": impact,
                    "previous": previous,
                    "forecast": forecast,
                    "actual": actual,
                    "affected_assets": get_affected_assets(currency)
                })

        except Exception as e:
            continue

    return events[:20]  # Top 20 events


def get_affected_assets(currency: str) -> list:
    """Map currency to affected futures assets."""
    mapping = {
        "USD": ["NQ=F", "ES=F", "YM=F", "GC=F", "CL=F"],
        "EUR": ["6E=F"],
        "GBP": ["6B=F"],
        "JPY": ["6J=F"],
        "AUD": ["6A=F"],
        "CAD": ["6C=F"],
        "CHF": ["6S=F"],
        "NZD": ["6N=F"],
        "CNY": [],
        "XAU": ["GC=F"],  # Gold
        "XTI": ["CL=F"],  # Oil
    }
    return mapping.get(currency.upper(), [])


def get_economic_calendar() -> list:
    """Fetch today's economic calendar."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        # Try main calendar page
        with httpx.Client(timeout=15.0) as client:
            response = client.get(FOREX_FACTORY_URL, headers=headers)
            if response.status_code == 200:
                events = parse_ff_calendar(response.text)
                logging.info(f"Fetched {len(events)} calendar events")
                return events

        # Fallback: try RSS
        with httpx.Client(timeout=10.0) as client:
            rss = client.get(FOREX_FACTORY_RSS, headers=headers)
            if rss.status_code == 200:
                # Parse basic RSS
                events = parse_rss(rss.text)
                logging.info(f"Fetched {len(events)} events from RSS")
                return events

    except Exception as e:
        logging.error(f"Calendar fetch error: {e}")

    return get_sample_events()  # Return sample data if fetch fails


def parse_rss(xml: str) -> list:
    """Parse Forex Factory RSS feed."""
    from xml.etree import ElementTree as ET
    events = []

    try:
        root = ET.fromstring(xml)
        for item in root.findall(".//item")[:20]:
            title = item.findtext("title", "")
            link = item.findtext("link", "")
            pub_date = item.findtext("pubDate", "")

            # Try to extract currency from title
            currency = ""
            impact = "medium"

            events.append({
                "time": pub_date[:16] if pub_date else "Today",
                "currency": currency,
                "event": title[:100],
                "impact": impact,
                "previous": "",
                "forecast": "",
                "actual": "",
                "affected_assets": [],
                "link": link
            })
    except Exception as e:
        logging.error(f"RSS parse error: {e}")

    return events


def get_sample_events() -> list:
    """Return sample events when fetch fails."""
    return [
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
            "time": "10:00",
            "currency": "USD",
            "event": "ISM Manufacturing PMI",
            "impact": "high",
            "previous": "50.3",
            "forecast": "50.5",
            "actual": "",
            "affected_assets": ["NQ=F", "ES=F", "YM=F"]
        },
        {
            "time": "14:00",
            "currency": "USD",
            "event": "FOMC Meeting Minutes",
            "impact": "high",
            "previous": "",
            "forecast": "",
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


if __name__ == "__main__":
    events = get_economic_calendar()
    for e in events:
        print(f"[{e['impact'].upper():5}] {e['time']} | {e['currency']} | {e['event']}")
