import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import email.utils
import os

SOURCE_URL = "https://info.asep.gr/feed.xml"
OUTPUT_FILE = "docs/ASEP-RSS-Feed.xml"


def parse_date(date_str):
    """
    Converts ASEP format:
    '01/07/2026 - 14:06'
    into RFC 822 format required by RSS
    """
    try:
        dt = datetime.strptime(date_str.strip(), "%d/%m/%Y - %H:%M")
        return email.utils.format_datetime(dt)
    except Exception:
        return email.utils.format_datetime(datetime.utcnow())


def fetch_feed():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/rss+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "el-GR,el;q=0.9,en;q=0.8",
    }

    r = requests.get(SOURCE_URL, headers=headers, timeout=30)
    r.raise_for_status()
    return r.text


def build_rss(xml_data):
    root = ET.fromstring(xml_data)

    channel_title = "ΑΣΕΠ Ενημερωτική Πύλη"
    channel_link = "https://info.asep.gr/"
    channel_description = "Outlook-compatible RSS feed"

    items_xml = []

    for item in root.findall(".//item"):
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        guid = item.findtext("link", link).strip()
        pub_date_raw = item.findtext("pubDate", "").strip()
        category = item.findtext("category", "").strip()

        pub_date = parse_date(pub_date_raw)

        item_xml = f"""
        <item>
            <title>{title}</title>
            <link>{link}</link>
            <guid isPermaLink="true">{guid}</guid>
            <pubDate>{pub_date}</pubDate>
            <category>{category}</category>
        </item>
        """
        items_xml.append(item_xml)

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>{channel_title}</title>
    <link>{channel_link}</link>
    <description>{channel_description}</description>
    <pubDate>{email.utils.format_datetime(datetime.utcnow())}</pubDate>
    {''.join(items_xml)}
  </channel>
</rss>
"""

    return rss


def save_feed(content):
    os.makedirs("docs", exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    xml_data = fetch_feed()
    rss = build_rss(xml_data)
    save_feed(rss)
