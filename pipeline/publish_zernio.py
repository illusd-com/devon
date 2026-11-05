#!/usr/bin/env python3
"""Devon -> Zernio -> Instagram Reels"""
from __future__ import annotations
import argparse, json, os, sys
from pathlib import Path
from typing import Any, Dict, Optional
import requests

BASE = os.environ.get("ZERNIO_BASE_URL", "https://zernio.com/api/v1").rstrip("/")

def require_env(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        raise SystemExit(f"Missing {name}. Get keys at https://zernio.com")
    return v

def headers() -> Dict[str, str]:
    return {"Authorization": f"Bearer {require_env('ZERNIO_API_KEY')}", "Content-Type": "application/json", "Accept": "application/json"}

def list_accounts() -> list:
    r = requests.get(f"{BASE}/accounts", headers=headers(), timeout=30)
    r.raise_for_status()
    data = r.json()
    return data.get("accounts") or data.get("data") or data

def create_post(*, caption: str, video_url: str, cover_url: Optional[str], account_id: str,
                publish_now: bool = False, scheduled_for: Optional[str] = None,
                timezone: str = "Asia/Taipei", share_to_feed: bool = True) -> Dict[str, Any]:
    media_items = [{"type": "video", "url": video_url}]
    if cover_url:
        media_items[0]["instagramThumbnail"] = cover_url
    body: Dict[str, Any] = {
        "content": caption[:2200],
        "mediaItems": media_items,
        "platforms": [{"platform": "instagram", "accountId": account_id,
                       "platformSpecificData": {"shareToFeed": share_to_feed}}],
    }
    if publish_now:
        body["publishNow"] = True
    else:
        if not scheduled_for:
            raise ValueError("Need scheduled_for or --publish-now")
        body["scheduledFor"] = scheduled_for
        body["timezone"] = timezone
    r = requests.post(f"{BASE}/posts", headers=headers(), json=body, timeout=60)
    if r.status_code >= 400:
        raise RuntimeError(f"Zernio {r.status_code}: {r.text[:1200]}")
    return r.json()

def load_reel_dir(reel_dir: Path) -> Dict[str, Any]:
    caption_path = reel_dir / "caption.txt"
    video_path = reel_dir / "reel.mp4"
    cover_path = reel_dir / "cover.jpg"
    if not video_path.exists():
        raise SystemExit(f"Missing {video_path}; run render.py first")
    caption = caption_path.read_text(encoding="utf-8").strip() if caption_path.exists() else ""
    return {"caption": caption, "video_path": video_path,
            "cover_path": cover_path if cover_path.exists() else None}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("reel_dir", nargs="?", default=".")
    parser.add_argument("--video-url")
    parser.add_argument("--cover-url")
    parser.add_argument("--publish-now", action="store_true")
    parser.add_argument("--schedule")
    parser.add_argument("--tz", default="Asia/Taipei")
    parser.add_argument("--list-accounts", action="store_true")
    parser.add_argument("--account-id", default=None)
    args = parser.parse_args()
    if args.list_accounts:
        print(json.dumps(list_accounts(), ensure_ascii=False, indent=2)); return
    account_id = args.account_id or require_env("ZERNIO_IG_ACCOUNT_ID")
    if not args.video_url:
        print("Need public HTTPS --video-url (upload reel.mp4 to CDN first)", file=sys.stderr)
        raise SystemExit(1)
    data = load_reel_dir(Path(args.reel_dir))
    result = create_post(caption=data["caption"], video_url=args.video_url, cover_url=args.cover_url,
                         account_id=account_id, publish_now=args.publish_now,
                         scheduled_for=args.schedule, timezone=args.tz)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    out = Path(args.reel_dir) / "zernio_result.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
