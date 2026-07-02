import re
import requests
from datetime import datetime
import email.utils
import os

SOURCE_URL = "https://r.jina.ai/http://info.asep.gr/feed.xml"
OUTPUT_FILE = "docs/feed.xml"


def fetch_feed():
    r = requests.get(SOURCE_URL, timeout=30)
    r.raise_for_status()
    return r.text


def parse_items(text):
    items = []

    blocks = text.split("### [")[1:]  # each item starts here

    for b in blocks:
        try:
            title_match = re.match(r"(.+?)\]\((https?://[^\)]+)\)", b)
            if not title_match:
                continue

            title = title_match.group(1).strip()
            link = title_match.group(2).strip()

            # find date like "01/07/2026 - 14:06"
            date_match = re.search(r"(\d{2}/\d{2}/\d{4} - \d{2}:\d{2})", b)
            if date_match:
                dt = datetime.strptime(date_match.group(1), "%d/%m/%Y - %H:%M")
            else:
                dt = datetime.utcnow()

            pub_date = email.utils.format_datetime(dt)

            items.append({
                "title": title,
                "link": link,
                "pubDate": pub_date
            })

        except Exception:
            continue

    return items


def build_rss(items):
    xml_items = []

    for it in items:
        xml_items.append(f"""
    <item>
        <title>{it['title']}</title>
        <link>{it['link']}</link>
        <guid isPermaLink="true">{it['link']}</guid>
        <pubDate>{it['pubDate']}</pubDate>
    </item>
""")

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>ΑΣΕΠ Ενημερωτική Πύλη</title>
    <link>https://info.asep.gr/</link>
    <description>RSS feed</description>
    <pubDate>{email.utils.format_datetime(datetime.utcnow())}</pubDate>
    {''.join(xml_items)}
  </channel>
</rss>
"""


def save_feed(xml):
    os.makedirs("docs", exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(xml)


if __name__ == "__main__":
    raw = fetch_feed()
    items = parse_items(raw)
    rss = build_rss(items)
    save_feed(rss)
