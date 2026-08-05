import json
import os
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

QUERY = 'site:x.com "ヴァン" "真斗" "メセカ"'
STATE_FILE = Path("seen.json")
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()

def fetch_bing_rss():
    params = urllib.parse.urlencode({"q": QUERY, "format": "rss"})
    url = f"https://www.bing.com/search?{params}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; KeywordMonitor/1.0)",
            "Accept": "application/rss+xml, application/xml, text/xml, */*",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
    root = ET.fromstring(data)
    items = []
    for item in root.findall(".//item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        desc = re.sub(r"<[^>]+>", "", item.findtext("description") or "").strip()
        if link and ("x.com/" in link or "twitter.com/" in link):
            items.append({"title": title, "link": link, "description": desc})
    return items

def load_seen():
    if not STATE_FILE.exists():
        return set()
    try:
        return set(json.loads(STATE_FILE.read_text(encoding="utf-8")))
    except Exception:
        return set()

def save_seen(seen):
    STATE_FILE.write_text(
        json.dumps(sorted(seen), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

def post_discord(item):
    if not WEBHOOK_URL:
        raise RuntimeError("DISCORD_WEBHOOK_URL is not set")
    text = item["description"] or item["title"]
    if len(text) > 1200:
        text = text[:1200] + "…"
    payload = {
        "content": "🚨 **「ヴァン 真斗 メセカ」新着候補**\n"
                   f"{text}\n"
                   f"<{item['link']}>"
    }
    req = urllib.request.Request(
        WEBHOOK_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "KeywordMonitor/1.0"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        r.read()

def main():
    items = fetch_bing_rss()
    seen = load_seen()

    # 初回実行は現在ある検索結果を既読扱いにして、大量通知を防ぐ
    if not seen:
        save_seen({x["link"] for x in items})
        print(f"Initialized with {len(items)} existing result(s); no notification sent.")
        return

    new_items = [x for x in items if x["link"] not in seen]

    for item in reversed(new_items):
        post_discord(item)

    seen.update(x["link"] for x in items)
    # seen.json が膨らみすぎないように上限をつける
    save_seen(set(list(seen)[-500:]))

    print(f"Checked {len(items)} result(s); notified {len(new_items)} new result(s).")

if __name__ == "__main__":
    main()
