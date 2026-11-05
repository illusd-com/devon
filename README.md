# Devon Reels Kit

全球 AI 情報短影音自動化工具包（風格繼承 Taiwan INFO）。

每天四次：06:00 / 11:00 / 16:00 / 19:00

## 快速開始（GitHub Codespaces）

1. 打開本 Repo → **Code** → **Codespaces** → **Create codespace**
2. 終端機執行：

```bash
bash setup_assets.sh   # 檢查字體 / BGM / 安裝依賴
export NVIDIA_API_KEY="nvapi-你的金鑰"

# 生成一支腳本
python3 pipeline/generate_script.py \
  --slot 11:00 \
  --news "貼新聞文字或檔案路徑" \
  --out-dir reels/test_1100
```

有圖片後：

```bash
python3 pipeline/tts.py reels/test_1100
cd pipeline && python3 render.py ../reels/test_1100
```

## GitHub Actions

已設定每日四次自動生成腳本。到 **Settings → Secrets** 新增：

- `NVIDIA_API_KEY`（必填）
- `ZERNIO_API_KEY` / `ZERNIO_IG_ACCOUNT_ID`（要發 IG 時）

詳見 [`.github/SECRETS.example.md`](.github/SECRETS.example.md)。

## 目錄

```
pipeline/          # tts / render / NVIDIA / Zernio
templates/         # 空白範本
example/           # 範例腳本
.devcontainer/     # Codespaces 設定
.github/workflows/ # 每日排程
```

完整規劃見 [`AUTOMATION_PLAN.md`](AUTOMATION_PLAN.md)。
