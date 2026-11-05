#!/usr/bin/env python3
"""Lightweight news collector for Devon."""
from __future__ import annotations
import argparse
import datetime as dt
import sys
from pathlib import Path

try:
    import feedparser
except ImportError:
    feedparser = None

import requests

FEEDS = [
    "https://openai.com/blog/rss.xml",
    "https://blog.google/technology/ai/rss/",
    "https://huggingface.co/blog/feed.xml",
    "https://techcrunch.com/category/artificial-intelligence/feed/",
]

def fetch_rss(limit_per_feed: int = 5) -> list[str]:
    items: list[str] = []
    if feedparser is None:
        for url in FEEDS:
            try:
                r = requests.get(url, timeout=12, headers={"User-Agent": "DevonBot/1.0"})
                if r.status_code != 200:
                    continue
                import re
                titles = re.findall(r"<title[^>]*>([^<]+)</title>", r.text, re.I)
                for t in titles[1 : 1 + limit_per_feed]:
                    t = t.strip()
                    if t and len(t) > 10:
                        items.append(f"- {t}  (source: {url})")
            except Exception as e:
                print(f"[collect] skip {url}: {e}", file=sys.stderr)
        return items
    for url in FEEDS:
        try:
            d = feedparser.parse(url)
            for e in d.entries[:limit_per_feed]:
                title = getattr(e, "title", "").strip()
                summary = getattr(e, "summary", "")[:200].strip()
                link = getattr(e, "link", "")
                if title:
                    items.append(f"- {title}\n  {summary}\n  {link}")
        except Exception as e:
            print(f"[collect] skip {url}: {e}", file=sys.stderr)
    return items

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--slot", default="11:00")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
    header = f"Devon candidates\nslot: {args.slot}\ntime: {now.isoformat()}\n---\n"
    items = fetch_rss()
    body = "\n\n".join(items) if items else "(no RSS items; paste news manually)"
    slot_hint = {
        "06:00": "Prefer major releases / industry events in last 12-18h.",
        "11:00": "Prefer new models, papers, HF activity.",
        "16:00": "Prefer GitHub trending / open source.",
        "19:00": "Prefer funding, startups, company news.",
    }.get(args.slot, "")
    text = header + f"hint: {slot_hint}\n\n" + body + "\n"
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(text, encoding="utf-8")
    print(f"[collect] wrote {args.out} ({len(items)} items)", file=sys.stderr)

if __name__ == "__main__":
    main()
