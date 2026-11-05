#!/usr/bin/env python3
"""Devon content generator using NVIDIA step-5-preview."""
from __future__ import annotations
import argparse, json, os, re, sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
from nvidia_client import NvidiaClient

SYSTEM_SCRIPT = """你是 Devon 的資深內容編輯。產出 35–45 秒短影音腳本。
規則：
1. 只輸出合法 JSON array，不要 markdown
2. 繁體中文
3. 共 7 段，最後一段固定結尾
4. say 數字用國字，總字數 ≤ 220
5. title ≤ 10 字，sub ≤ 16 字
6. img 只能 a.jpg/b.jpg/c.jpg/null，最後一段 img 必須 null
7. 結尾必須是：{"id":7,"say":"追蹤 Devon，每天四次全球 AI 情報。","en":"Follow Devon for global AI intelligence, four times a day.","img":null,"tag":"","title":"","sub":""}
"""

SYSTEM_CAPTION = """根據 script 產出 IG caption：吸睛標題+emoji、3-4 個📌、💬互動、圖片來源、hashtag 含 #Devon #AI。純文字不要 code block。"""

def extract_json_array(text: str) -> List[Dict[str, Any]]:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text).strip()
    try:
        data = json.loads(text)
        if isinstance(data, list): return data
    except json.JSONDecodeError:
        pass
    m = re.search(r"\[.*\]", text, re.DOTALL)
    if m: return json.loads(m.group(0))
    raise ValueError("Cannot parse JSON array from model output")

def generate_script(client: NvidiaClient, slot: str, news: str, date_str: str, temperature: float = 0.6):
    user = f"時段：{slot}\n日期：{date_str}\n\n候選新聞：\n{news}\n\n請產出完整 7 段 script.json（直接輸出 JSON array）。"
    result = client.generate(system=SYSTEM_SCRIPT, user=user, temperature=temperature, max_tokens=4096)
    if result["reasoning"]:
        print("=== Reasoning (trim) ===", file=sys.stderr)
        print(result["reasoning"][:1500], file=sys.stderr)
    script = extract_json_array(result["content"])
    if script:
        script[-1] = {"id": 7, "say": "追蹤 Devon，每天四次全球 AI 情報。",
                      "en": "Follow Devon for global AI intelligence, four times a day.",
                      "img": None, "tag": "", "title": "", "sub": ""}
    for i, seg in enumerate(script, 1):
        seg["id"] = i
    return script

def generate_caption(client: NvidiaClient, script, credits):
    summary = "\n".join(f"- [{s.get('tag','')}] {s.get('title','')}: {s.get('say','')}" for s in script if s.get("img"))
    user = f"腳本摘要：\n{summary}\n圖片來源：{json.dumps(credits, ensure_ascii=False)}\n請產出 caption.txt"
    result = client.generate(system=SYSTEM_CAPTION, user=user, temperature=0.5, max_tokens=1024)
    return result["content"].strip()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--slot", required=True)
    parser.add_argument("--news", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--date", default=None)
    parser.add_argument("--bgm", default="bright_d")
    parser.add_argument("--temperature", type=float, default=0.6)
    args = parser.parse_args()
    news_path = Path(args.news)
    news = news_path.read_text(encoding="utf-8") if news_path.exists() else args.news
    date_str = args.date or datetime.now().strftime("%Y.%m.%d")
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "img").mkdir(exist_ok=True)
    client = NvidiaClient()
    print(f"[Devon] generating script for {args.slot}...", file=sys.stderr)
    script = generate_script(client, args.slot, news, date_str, args.temperature)
    credits = {"a.jpg": "圖片來源：待標註", "b.jpg": "圖片來源：待標註", "c.jpg": "圖片來源：待標註"}
    meta = {"date": date_str, "category": "AI", "credits": credits, "out": "reel.mp4", "bgm": args.bgm, "slot": args.slot}
    caption = generate_caption(client, script, credits)
    (out_dir / "script.json").write_text(json.dumps(script, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "caption.txt").write_text(caption + "\n", encoding="utf-8")
    print(f"[Devon] wrote -> {out_dir}")

if __name__ == "__main__":
    main()
