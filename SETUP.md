# Devon 設定狀態

Repo: https://github.com/illusd-com/devon

## 已完成

- [x] README / Codespaces (`.devcontainer`)
- [x] GitHub Actions 每日四次排程 (`.github/workflows/devon-daily.yml`)
- [x] `pipeline/nvidia_client.py` — NVIDIA step-5-preview
- [x] `pipeline/generate_script.py` — 新聞 → script.json
- [x] `pipeline/collect_news.py` — RSS 候選
- [x] `pipeline/publish_zernio.py` — Instagram 發布
- [x] `pipeline/tts.py` — 雲哲配音
- [x] templates / example

## 你還需要補的（大檔）

這些檔案太大，請用 Codespace 或本機從原 TaiwanINFO kit 複製：

1. **字體** → `pipeline/fonts/NotoSansTC.ttf`、`NotoSerifTC.ttf`
2. **BGM** → `pipeline/bgm/*.wav`（或跑 `python3 pipeline/make_bgm.py`）
3. **render.py** → 從 TaiwanINFO_Reels_Kit 複製後，把 logo 路徑改成 `devon_logo_official.png`（若尚未推上）
4. **devon_logo_official.png**（根目錄）

## Secrets（Actions）

Settings → Secrets and variables → Actions：

| Name | 必填 |
|------|------|
| `NVIDIA_API_KEY` | ✅ |
| `ZERNIO_API_KEY` | 發 IG 時 |
| `ZERNIO_IG_ACCOUNT_ID` | 發 IG 時 |

## Codespaces 用法

1. Code → Codespaces → Create codespace
2. 終端機：

```bash
bash setup_assets.sh
export NVIDIA_API_KEY="nvapi-..."
python3 pipeline/nvidia_client.py --prompt "你好"
python3 pipeline/generate_script.py --slot 11:00 --news "測試新聞" --out-dir reels/test
```

## 每日時段（Asia/Taipei）

| Actions 觸發 (UTC) | 時段 |
|--------------------|------|
| 21:30 | 06:00 |
| 02:30 | 11:00 |
| 07:30 | 16:00 |
| 10:30 | 19:00 |
