#!/bin/bash
# GCP → Dashboard DB同期スクリプト
# 使い方: ./sync_db.sh
# GCPからDBをダウンロードし、git commit & pushまで自動実行

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
GCP_INSTANCE="ai-investor-phase3"
GCP_ZONE="us-central1-a"
GCP_PROJECT="ai-investor-phase3"
GCP_DB_PATH="/home/kouya/ai_investor/93_db/ai_investor.db"
LOCAL_DB="$SCRIPT_DIR/data/ai_investor.db"
TMP_DB="/tmp/gcp_ai_investor_sync.db"

echo "=== AI Investor Dashboard DB Sync ==="
echo "$(date '+%Y-%m-%d %H:%M:%S')"

# 1. GCPからDBダウンロード
echo "[1/4] Downloading DB from GCP..."
gcloud compute scp \
    "${GCP_INSTANCE}:${GCP_DB_PATH}" \
    "$TMP_DB" \
    --zone="$GCP_ZONE" \
    --project="$GCP_PROJECT" \
    --quiet

# 2. VACUUM（WAL/SHMを統合＋コンパクト化）
echo "[2/4] Vacuuming DB..."
sqlite3 "$TMP_DB" "VACUUM;"

# 3. 差分チェック＆コピー
if [ -f "$LOCAL_DB" ]; then
    OLD_HASH=$(md5 -q "$LOCAL_DB" 2>/dev/null || md5sum "$LOCAL_DB" | cut -d' ' -f1)
    NEW_HASH=$(md5 -q "$TMP_DB" 2>/dev/null || md5sum "$TMP_DB" | cut -d' ' -f1)
    if [ "$OLD_HASH" = "$NEW_HASH" ]; then
        echo "[3/4] DB unchanged, skipping."
        rm -f "$TMP_DB"
        exit 0
    fi
fi

echo "[3/4] Copying updated DB..."
cp "$TMP_DB" "$LOCAL_DB"
rm -f "$TMP_DB"

# 4. Git commit & push
echo "[4/4] Committing and pushing..."
cd "$SCRIPT_DIR"

# 取引サマリを取得してコミットメッセージに含める
TRADE_SUMMARY=$(sqlite3 "$LOCAL_DB" "
    SELECT
        COUNT(*) || ' trades ('
        || SUM(CASE WHEN status='CLOSED' AND profit_loss > 0 THEN 1 ELSE 0 END) || 'W/'
        || SUM(CASE WHEN status='CLOSED' AND profit_loss <= 0 THEN 1 ELSE 0 END) || 'L), PnL \$'
        || ROUND(SUM(CASE WHEN status='CLOSED' THEN profit_loss ELSE 0 END), 0)
    FROM trades
    WHERE entry_timestamp >= '2026-01-24';
" 2>/dev/null || echo "unknown")

git add data/ai_investor.db
git commit -m "data: sync GCP DB — ${TRADE_SUMMARY}" || {
    echo "Nothing to commit (DB unchanged after staging)"
    exit 0
}
git push origin main

echo "=== Sync complete ==="
echo "Summary: $TRADE_SUMMARY"
