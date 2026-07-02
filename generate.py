import re
import requests
import email.utils
from datetime import datetime
import os

SOURCE_URL = "https://r.jina.ai/http://info.asep.gr/feed.xml"
OUTPUT_FILE = "docs/ASEP-RSS-Feed.xml"


# ---------------------------
# FETCH (via Jina)
# ---------------------------
def fetch_feed():
    r = requests.get(SOURCE_URL, timeout=30)
    r.raise_for_status()
    return r.text


# ---------------------------
# PARSE JINA OUTPUT
# ---------------------------
def parse_items(text):
    items = []

    matches = re.findall(
        r"### \[(.*?)\]\((https?://[^\)]+)\)(.*?)(?=### |\Z)",
        text,
        re.S
    )

    for title, link, block in matches:

        # extract date if present
        date_match = re.search(r"(\d{2}/\d{2}/\d{4} - \d{2}:\d{2})", block)

        if date_match:
            dt = datetime.strptime(date_match.group(1), "%d/%m/%Y - %H:%M")
        else:
            dt = datetime.utcnow()

        pub_date = email.utils.format_datetime(dt)

        items.append({
            "title": title.strip(),
            "link": link.strip(),
            "pubDate": pub_date
        })

    return items


# ---------------------------
# BUILD RSS (Outlook-safe HTML)
# ---------------------------
def build_rss(items):
    xml_items = []

    for it in items:

        description = f"""
<![CDATA[
<div>
    <b>{it['title']}</b><br/>
    {it['pubDate']}<br/>
    <a href="{it['link']}">Open article</a>
</div>
]]>
"""

        xml_items.append(f"""
<item>
    <title>{it['title']}</title>
    <link>{it['link']}</link>
    <guid isPermaLink="true">{it['link']}</guid>
    <pubDate>{it['pubDate']}</pubDate>
    <description>{description}</description>
</item>
""")

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>ΑΣΕΠ Ενημερωτική Πύλη</title>
    <link>https://info.asep.gr/</link>
    <description>Custom ASEP RSS Feed</description>
    <pubDate>{email.utils.format_datetime(datetime.utcnow())}</pubDate>
    {''.join(xml_items)}
  </channel>
</rss>
"""

    return rss


# ---------------------------
# SAVE FILE
# ---------------------------
def save_feed(xml):
    os.makedirs("docs", exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(xml)


# ---------------------------
# MAIN
# ---------------------------
if __name__ == "__main__":
    raw = fetch_feed()

    items = parse_items(raw)
    print("ITEM COUNT:", len(items))

    rss = build_rss(items)
    save_feed(rss)
