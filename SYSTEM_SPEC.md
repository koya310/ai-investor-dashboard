# AI Investor Dashboard 詳細仕様

## 1. 目的
- 本ダッシュボードは **Phase 3 紙運用（Paper Trading）** の監視・分析を行う運用画面。
- 主目的:
  - Go/No-Go 判定のための KPI 可視化
  - 当日運用の異常検知
  - 日付単位での「ニュース -> 分析 -> シグナル -> 売買」追跡

## 2. 運用期間・前提
- Phase 3 開始日: `2026-01-24`
- Go/No-Go 判定期限: `2026-02-28`
- 初期資本: `$100,000`
- 対象データベース: `ai_investor.db`

## 3. ページ構成

| ページ | 役割 | 主な確認内容 |
|---|---|---|
| `pages/home.py` | KPI/損益サマリ | Go/No-Go判定、累積損益、主要KPI |
| `pages/pipeline.py` | 実行品質監視 | 当日パイプライン進捗、7日品質、実行カレンダー |
| `pages/date_detail.py` | 日付深掘り | 銘柄別フロー、実行ログ、非売買日の原因確認 |
| `pages/reference.py` | 仕様参照 | KPI式、ルール、運用定義 |

## 4. Go/No-Go 判定仕様

### 4.1 KPI定義
| KPI | 目標値 | 計算式 | データソース |
|---|---:|---|---|
| 勝率 | `>= 55%` | `wins / closed_trades * 100` | `trades` |
| 年率リターン | `>= 12%` | `actual_return_pct * (365 / days_running)` | `trades` |
| 最大ドローダウン | `<= 15%` | 資産ピーク比の最大下落率 | `portfolio_snapshots`（不足時はトレード推定） |
| 稼働率 | `>= 99%` | `completed_runs / total_runs * 100` | `system_runs` |

### 4.2 総合判定ロジック
| 判定 | 条件 |
|---|---|
| `GO` | 4/4 KPI達成 |
| `CONDITIONAL_GO` | 3/4 KPI達成 |
| `NO_GO` | 0-2/4 KPI達成 |

補足:
- 失敗KPIごとに改善推奨メッセージを生成。
- 稼働率は、開始7日以内は全期間、8日目以降は直近7日ローリングを使用。

## 5. パイプライン仕様（全体）

| Step | 入力 | 出力テーブル | 異常時の影響 |
|---|---|---|---|
| 1. ニュース収集 | RSS/API | `news` | 分析対象減少 |
| 2. AI分析 | ニュース + 銘柄群 | `ai_analysis` | シグナル品質低下 |
| 3. シグナル生成 | テクニカル + AI分析 | `signals` | 取引機会喪失 |
| 4. 注文執行 | シグナル + リスク制約 | `trades` | 売買記録欠落 |
| 5. スナップショット | 約定 + ポジション | `portfolio_snapshots` | KPI/DD精度低下 |

## 6. `date_detail` ページ仕様

### 6.1 目的
- 日付単位で、運用結果と原因を追跡可能にする。
- 「売買がなかった日」の妥当性確認を行う。

### 6.2 URL/パラメータ
- クエリパラメータ: `?date=YYYY-MM-DD`
- 対象日が範囲外の場合:
  - 最小日より前 -> 最小日へ丸める
  - 最大日より後 -> 最大日へ丸める

### 6.3 画面ブロック
| ブロック | 内容 | 主なデータ |
|---|---|---|
| 日付ナビゲーション | 前日/翌日/最新、日付ピッカー | `get_available_log_dates` |
| 日次サマリ | 件数メトリクス + 状態メッセージ | `get_log_day_summary` |
| 実行ログ | run_mode別の完了/失敗/エラー | `get_log_system_runs` |
| Ticker別フロー | 銘柄ごとの最終状態 | `get_date_ticker_flow` |
| 詳細データタブ | ニュース/分析/シグナル/取引一覧 | 各 `get_log_*` |
| 詳細仕様 | Markdown全文展開 | 本ファイル or 運用ドキュメント |

### 6.4 Ticker最終状態判定
`date_detail` の表示ラベルは次の優先順で決定:
1. `trade` が存在 -> `売買実行`
2. `signal` が存在し `trade` なし -> `シグナルのみ`
3. `analysis_count > 0` のみ -> `分析まで`
4. `news_count > 0` のみ -> `ニュースのみ`
5. いずれも無い -> `データなし`

### 6.5 「購入しなかった」読み取り方
- 「シグナルのみ」は、当該日にシグナルは検出されたが売買レコードが無い状態。
- 原因切り分けは以下を併読:
  - `signals.status`（`pending/cancelled/expired/executed`）
  - `system_runs.errors_count` と `error_message`
  - 当日の `run_mode` と完了率

## 7. リスク管理ルール（売買制約）

| 制約 | ルール |
|---|---|
| ハードストップロス | `-8%` |
| 最低リスクリワード | `1.5:1` 以上 |
| 1日最大新規買付 | `3件` |
| セクター集中制限 | `1セクター1件/日` |
| 決算ブラックアウト | 決算日前後7日 |
| 最低現金維持 | `$5,000` |

## 8. 実行モード仕様

| run_mode | 意味 | 想定更新対象 |
|---|---|---|
| `full` | 収集〜執行の一括実行 | `news`, `ai_analysis`, `signals`, `trades`, `system_runs` |
| `signal` / `medium` | 日中再評価 | `signals`, `system_runs` |
| `light` | 最小再チェック | `system_runs` |
| `news_only` / `news_collect` | 収集のみ | `news`, `system_runs` |
| `analysis_only` | 分析のみ | `ai_analysis`, `system_runs` |
| `daily_summary` | 日次要約通知 | 通知ログ + `system_runs` |

## 9. キャッシュと鮮度

| データ | TTL |
|---|---:|
| Alpaca portfolio / positions | 120秒 |
| パイプライン状態 | 120秒 |
| 日次資産推移 / SPY比較 | 600秒 |
| 実行品質集計 / タイムライン | 600秒 |

表示優先:
1. Alpacaリアルタイム値
2. 取得不可時はトレード履歴推定

## 10. Discord通知方針（運用可視化）

最低限通知すべきイベント:
1. 実行失敗（`run_main.sh` 非0終了、例: `exit=124`）
2. シグナル発生（BUY/SELL、銘柄、確信度、理由）
3. 売買実行（銘柄、株数、価格、理由）
4. 非売買（シグナル無し or リスク制約で見送りの理由）
5. 日次サマリ成功/失敗

`date_detail` は上記通知内容の事後検証画面として利用する。

## 11. 日次運用チェックリスト（推奨）

1. `pipeline` で当日ステップ完了とエラー件数を確認
2. `date_detail` で対象日の実行ログを確認
3. `Ticker別フロー` で「シグナルのみ」の銘柄を抽出
4. `signals.status` と `system_runs.error_message` を突合
5. Discord通知（シグナル/売買/非売買理由）とDB実績が一致するか確認

## 12. 既知制約
- `date_detail` は当日/指定日のログ確認UIであり、売買意思決定そのものは行わない。
- 非売買理由は1フィールドで確定表示する仕様ではなく、複数ログ（signals/runs/trades）の総合読解が必要。
