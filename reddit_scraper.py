import feedparser
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from pathlib import Path
import re

SUBREDDIT = "Silksong"
SORT = "hot"         # could be "top", "new", or "hot", use whatever tag you want
TOP_TIMEFRAME = "day"    # only matters for "top tag"
LIMIT = 5
ARCHIVE_FILE = Path("reddit_archive.md")

def rss_url():
    base = f"https://www.reddit.com/r/{SUBREDDIT}/{SORT}/.rss"
    if SORT == "top":
        return f"{base}?t={TOP_TIMEFRAME}"
    return base

def build_section(date_str):
    url = rss_url()
    feed = feedparser.parse(url, request_headers={"User-Agent": "silksong-archiver-bot"})
    entries = feed.entries[:LIMIT]
    
    lines = []
    lines.append(f"\n\n## {date_str}\n")
    lines.append(f"### r/{SUBREDDIT} — {SORT} ({TOP_TIMEFRAME})\n")
    for e in entries:
        title = e.get("title", "(no title)").replace("\n", " ").strip()
        link = e.get("link", "#")
        lines.append(f"- [{title}]({link})\n")
    return "".join(lines)

def ensure_header():
    if not ARCHIVE_FILE.exists():
        ARCHIVE_FILE.write_text(
            "# r/Silksong Daily Archive\n"
            "This file is updated daily by GitHub Actions using the subreddit RSS feed.\n",
            encoding="utf-8"
        )

def upsert_today_section(section_text, date_str):
    content = ARCHIVE_FILE.read_text(encoding="utf-8")
    # Remove existing section for this date
    pattern = rf"(?ms)^## {re.escape(date_str)}.*?(?=^## |\Z)"
    new_content = re.sub(pattern, "", content)
    ARCHIVE_FILE.write_text(new_content.rstrip() + section_text, encoding="utf-8")

def main():
    ensure_header()
    now_utc = datetime.now(timezone.utc)
    ist_now = now_utc.astimezone(ZoneInfo("Asia/Kolkata"))  
    date_str = ist_now.strftime("%Y-%m-%d")
    section = build_section(date_str)
    upsert_today_section(section, date_str)

if __name__ == "__main__":
    main()

