#!/usr/bin/env python3
"""Devon x NVIDIA Integrate API client — stepfun-ai/step-5-preview"""
from __future__ import annotations
import json, os, sys, time
from typing import Any, Dict, List, Optional, Union
import requests

API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
DEFAULT_MODEL = "stepfun-ai/step-5-preview"

class NvidiaClient:
    def __init__(self, api_key: Optional[str] = None, model: str = DEFAULT_MODEL, timeout: int = 180, max_retries: int = 3):
        self.api_key = api_key or os.environ.get("NVIDIA_API_KEY")
        if not self.api_key:
            raise ValueError("Missing NVIDIA_API_KEY. Get one at https://build.nvidia.com")
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries

    def _headers(self, stream: bool = False) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream" if stream else "application/json",
        }

    def chat(self, messages: List[Dict[str, Any]], *, temperature: float = 0.7, top_p: float = 0.95,
             max_tokens: int = 8192, stream: bool = False, tools=None, tool_choice=None, extra=None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "model": self.model, "messages": messages,
            "temperature": temperature, "top_p": top_p,
            "max_tokens": max_tokens, "stream": stream,
        }
        if tools: payload["tools"] = tools
        if tool_choice is not None: payload["tool_choice"] = tool_choice
        if extra: payload.update(extra)
        last_err = None
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = requests.post(API_URL, headers=self._headers(stream=stream), json=payload, timeout=self.timeout, stream=stream)
                if resp.status_code == 429:
                    time.sleep(min(2 ** attempt, 30)); continue
                if resp.status_code >= 400:
                    raise RuntimeError(f"NVIDIA API {resp.status_code}: {resp.text[:800]}")
                if stream:
                    return self._consume_stream(resp)
                return resp.json()
            except (requests.RequestException, RuntimeError) as e:
                last_err = e
                if attempt < self.max_retries:
                    time.sleep(min(2 ** attempt, 10)); continue
                raise
        raise last_err

    def _consume_stream(self, resp: requests.Response) -> Dict[str, Any]:
        content_parts, reasoning_parts, tool_calls = [], [], []
        finish_reason, model = None, self.model
        for raw in resp.iter_lines(decode_unicode=True):
            if not raw or not raw.startswith("data:"): continue
            data = raw[5:].strip()
            if data == "[DONE]": break
            try: chunk = json.loads(data)
            except json.JSONDecodeError: continue
            if "model" in chunk: model = chunk["model"]
            for choice in chunk.get("choices", []):
                delta = choice.get("delta") or {}
                if delta.get("content"): content_parts.append(delta["content"])
                if delta.get("reasoning_content"): reasoning_parts.append(delta["reasoning_content"])
                if delta.get("tool_calls"): tool_calls.extend(delta["tool_calls"])
                if choice.get("finish_reason"): finish_reason = choice["finish_reason"]
        message: Dict[str, Any] = {"role": "assistant", "content": "".join(content_parts) or None}
        if reasoning_parts: message["reasoning_content"] = "".join(reasoning_parts)
        if tool_calls: message["tool_calls"] = tool_calls
        return {"model": model, "choices": [{"index": 0, "message": message, "finish_reason": finish_reason or "stop"}]}

    def generate(self, system: str, user: str, *, temperature: float = 0.7, max_tokens: int = 8192, images=None) -> Dict[str, str]:
        if images:
            parts = [{"type": "text", "text": user}]
            for url in images[:8]:
                parts.append({"type": "image_url", "image_url": {"url": url}})
            content = parts
        else:
            content = user
        messages = [{"role": "system", "content": system}, {"role": "user", "content": content}]
        data = self.chat(messages, temperature=temperature, max_tokens=max_tokens)
        msg = data["choices"][0]["message"]
        return {"content": msg.get("content") or "", "reasoning": msg.get("reasoning_content") or "", "raw": data}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", default="用一句話介紹你自己")
    parser.add_argument("--system", default="你是有幫助的繁體中文助理。")
    parser.add_argument("--max-tokens", type=int, default=2048)
    args = parser.parse_args()
    client = NvidiaClient()
    result = client.generate(system=args.system, user=args.prompt, max_tokens=args.max_tokens)
    if result["reasoning"]:
        print("=== Reasoning ==="); print(result["reasoning"][:2000]); print()
    print("=== Content ==="); print(result["content"])
