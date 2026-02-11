"""Reference — システム仕様リファレンス"""

from datetime import datetime

import dashboard_data as _dm
import streamlit as st

from components.shared import L, P, W, section_header

fresh = _dm.get_data_latest_dates()

st.title("システム仕様")
with st.container(border=True):
    st.caption("判定基準・計算式・実行ルール・障害時の見方をまとめています。")


# ============================================================
# 1. 運用スコープ
# ============================================================

section_header("運用スコープ", color=P)
with st.container(border=True):
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Phase 3 開始日", _dm.PHASE3_START)
    c2.metric("判定期限", _dm.GONOGO_DEADLINE)
    c3.metric("初期資本", f"${_dm.INITIAL_CAPITAL:,.0f}")
    c4.metric("判定KPI", "4項目")
    c5.metric("最新データ日", fresh.get("latest", "-") or "-")
    st.caption(f"画面更新時刻: {datetime.now().strftime('%Y-%m-%d %H:%M')}")


# ============================================================
# 2. Go/No-Go 判定仕様
# ============================================================

section_header("Go/No-Go 判定仕様", color="#f59e0b")
with st.container(border=True):
    st.markdown(
        f"""
| KPI | 目標値 | 計算式 | 判定の意味 |
|---|---:|---|---|
| 勝率 | **{_dm.KPI_TARGETS['win_rate']:.0f}%以上** | `wins / closed_trades * 100` | 取引の質 |
| 年率リターン | **{_dm.KPI_TARGETS['annual_return']:.0f}%以上** | `actual_return_pct * (365 / days_running)` | 収益性 |
| 最大DD | **{_dm.KPI_TARGETS['max_drawdown']:.0f}%以下** | ピーク比の最大下落率 | 下振れ耐性 |
| 稼働率 | **{_dm.KPI_TARGETS['uptime']:.0f}%以上** | `completed_runs / total_runs * 100` | 運用品質 |
"""
    )

    st.markdown(
        """
**総合判定ロジック**

- `GO`: 4/4 達成
- `CONDITIONAL_GO`: 3/4 達成
- `NO_GO`: 0-2/4 達成
"""
    )


# ============================================================
# 3. KPIの計算ルール
# ============================================================

section_header("KPIの計算ルール", color=W)
with st.container(border=True):
    st.markdown(
        """
| 項目 | 詳細ルール |
|---|---|
| 勝率 | `status='CLOSED'` の取引のみ対象 |
| 年率リターン | 累積損益を初期資本で割り、運用日数で年換算 |
| 最大DD | `portfolio_snapshots` 優先。無い場合はトレード損益から推定 |
| 稼働率 | 開始7日以内は全期間、8日目以降は直近7日ローリング |
"""
    )


# ============================================================
# 4. データソース詳細
# ============================================================

section_header("データソース詳細", color=P, subtitle="4レイヤー情報収集")
with st.container(border=True):
    st.markdown(
        """
**6つのニュースソース**（優先度順に自動巡回）
"""
    )
    st.markdown(
        """
| # | ソース | タイムアウト | 備考 |
|---|--------|----------:|------|
| 1 | Yahoo Finance | 15秒 | メインソース |
| 2 | Google News RSS | 10秒 | 広範なカバレッジ |
| 3 | NewsAPI | 10秒 | 100リクエスト/日制限 |
| 4 | FMP (Financial Modeling Prep) | 10秒 | 有料プラン |
| 5 | Finnhub | 10秒 | 3日間の履歴 |
| 6 | Reddit | 15秒 | センチメント分析 |
"""
    )

    with st.expander("ソース信頼度レベル（Tier分類）"):
        st.markdown(
            """
| Tier | 信頼スコア | ソース例 |
|------|----------:|---------|
| **Tier 1** | 100 | 企業公式開示(10-K, 10-Q)、政府統計(BLS, FRED)、SEC、NYSE |
| **Tier 2** | 80-90 | Bloomberg, Reuters, WSJ, FT, TechCrunch, Yahoo Finance |
| **Tier 3** | 40-60 | Reddit(60), Twitter/X(55), Seeking Alpha(50), StockTwits(40) |
"""
        )


# ============================================================
# 5. ニュース分析フロー
# ============================================================

section_header("ニュース分析フロー", color=P, subtitle="品質スコアリング100点")
with st.container(border=True):
    st.markdown(
        """
**5ステップの分析パイプライン**:
重複排除 → センチメント分析 → 品質スコアリング → インパクト分析 → 統合レポート
"""
    )

    with st.expander("品質スコアリング（100点満点の内訳）"):
        q1, q2, q3 = st.columns(3)
        with q1:
            st.metric("Market Impact", "40pts")
            st.markdown(
                """
- 決算: 40pts
- M&A/FDA: 35pts
- 大型契約/規制: 30pts
- 提携/技術革新: 25pts
- 製品発表: 22pts
- 格付け変更: 20pts
- 一般ニュース: 5pts
"""
            )
        with q2:
            st.metric("Time Urgency", "30pts")
            st.markdown(
                """
- ≤1時間: 30pts
- ≤3時間: 25pts
- ≤6時間: 20pts
- ≤24時間: 15pts
- ≤72時間: 10pts
- >72時間: 5pts
"""
            )
        with q3:
            st.metric("Source Reliability", "30pts")
            st.markdown(
                """
- Tier 1 ソース: 30pts
- Tier 2 ソース: 20pts
- Tier 3 ソース: 10pts
"""
            )

        st.markdown(
            """
**品質閾値**: ≥70pts → CRITICAL（即時対応） / ≥50pts → HIGH / ≥30pts → MEDIUM / <30pts → LOW
"""
        )

    with st.expander("AI分析モデルとフォールバック"):
        st.markdown(
            """
**センチメント分析**: Gemini 2.0 Flash（軽量モデル） → Deepseek（フォールバック）

**ニュースインパクト分析・テーマ統合分析**: 高精度Proモデルを使用

| 優先度 | モデル |
|--------|--------|
| 1 | gemini-3-pro |
| 2 | gemini-3-pro-preview |
| 3 | gemini-2.5-pro |
| 4 | gemini-1.5-pro |
| 5 | gemini-3-flash-preview |
| 6 | gemini-2.5-flash |
| 7 | gemini-2.0-flash-exp |
| 8 | gemini-1.5-flash |

**障害時**: Gemini全滅 → Deepseek → 両方失敗 → センチメント=0.0（中立）を返却
"""
        )


# ============================================================
# 6. シグナル生成の詳細
# ============================================================

section_header("シグナル生成の詳細", color=W, subtitle="3戦略統合")
with st.container(border=True):
    st.markdown(
        """
**3戦略（押し目買い・トレンド追従・VIX逆張り）のテクニカル指標＋AIニュース分析を統合。**
最低3カテゴリ一致＆確信度6以上で発出。
"""
    )

    with st.expander("3戦略のテクニカル条件"):
        st.markdown("**Strategy A: 押し目買い（Mean Reversion）**")
        st.markdown(
            """
| 条件 | 閾値 |
|------|------|
| Price > MA200 | 長期上昇トレンド内 |
| MA200 乖離率 | ≤ ±3%（押し目ゾーン） |
| RSI | 35-65（正常レンジ） |
| 確信度 | ≥ 6 |
"""
        )
        st.markdown("**Strategy B: トレンド追従（Breakout）**")
        st.markdown(
            """
| 条件 | 閾値 |
|------|------|
| MA20 > MA50 | 短期上昇トレンド |
| Price > 20日高値 | ブレイクアウト確認 |
| 出来高 > MA出来高 × 1.5 | モメンタム確認 |
| RSI > 50 | 健全な勢い |
"""
        )
        st.markdown("**Strategy C: VIX逆張り（Contrarian）**")
        st.markdown(
            """
| 条件 | 閾値 |
|------|------|
| VIX | > 25（高ボラティリティ環境） |
| 確信度閾値 | ≥ 9（通常より厳格） |
| ポジションサイズ | 保守的 |
"""
        )

    with st.expander("確信度（Conviction）スコアリング"):
        st.markdown(
            """
**最大15ポイント**（テクニカル指標の組み合わせ）

| 要素 | 加算ポイント |
|------|----------:|
| Price > MA200 | +2 |
| MA50 > MA200（ゴールデンクロス） | +2 |
| MA200 乖離率 0-3% | +3 |
| RSI 35-65 | +2 |
| ストキャスティクス < 20 | +2 |
| MACD > シグナルライン | +2 |
| 出来高比 > 1.2x | +1 |

**確信度 → ポジションサイズ倍率**

| 確信度 | 判定 | サイズ倍率 |
|--------|------|----------:|
| 10-15 | Strong Buy | 100% |
| 8-9 | Buy | 75% |
| 7 | Conditional | 50% |
| 4-6 | Watchlist | 0% |
| 0-3 | Skip | 0% |

**VIX連動の動的閾値**: VIX > 25 → 確信度 ≥ 9 必須 / 通常 → ≥ 7
"""
        )


# ============================================================
# 7. 注文前7段階ゲート
# ============================================================

section_header("注文前7段階ゲート", color=L, subtitle="全通過で発注")
with st.container(border=True):
    st.markdown(
        """
シグナル発出後、実際の発注前に**7段階のリスクチェック**を全て通過する必要があります。
1つでも失敗すると発注はブロックされます。

| Gate | チェック内容 | 失敗時 |
|------|-------------|--------|
| 1. 価格検証 | yfinance価格をAlpaca価格と照合。乖離>20%で棄却 | 発注取消 |
| 2. サーキットブレーカー | 連続損失/日次損失がCB閾値を超えていないか | 全取引停止 |
| 3. 市場レジーム | VIXレベルに応じたリスク許容度を確認 | サイズ縮小 or 棄却 |
| 4. 重複チェック | 同一銘柄の保有・当日注文済みを確認 | 発注取消 |
| 5. 決算ブラックアウト | 決算発表前後7日以内でないか | 発注取消 |
| 6. マクロイベント | FOMC等の重大イベント当日でないか | 発注取消 |
| 7. 相関チェック | 既存ポジションとの相関(>0.85で棄却) | 発注取消 or サイズ縮小 |
"""
    )


# ============================================================
# 8. リスク管理ルール
# ============================================================

section_header("リスク管理ルール", color=L)
with st.container(border=True):
    st.markdown(
        """
| 項目 | ルール | 目的 |
|---|---|---|
| ハードストップロス | -8% | 単一銘柄の急落を制限 |
| 最低リスクリワード | 1.5:1以上 | 期待値の維持 |
| 1日最大買付 | 3件 | 過剰売買を抑制 |
| セクター集中制限 | 1件/セクター/日 | 集中リスク抑制 |
| 決算ブラックアウト | 前後7日 | ギャップリスク回避 |
| 最低現金保有 | $5,000 | 運用継続性の確保 |
| ポートフォリオ上限 | 90% | 全額投資を防止 |
"""
    )

    with st.expander("動的SL/TP（VIXレベル別）"):
        st.markdown(
            """
| VIX範囲 | ストップロス | テイクプロフィット | ポスチャー |
|---------|----------:|----------------:|----------|
| < 15 | -4% | +18% | アグレッシブ |
| 15-20 | -5% | +15% | スタンダード |
| 20-30 | -6% | +12% | ディフェンシブ |
| > 30 | -7% | +10% | 超防御的 |

**ATR連動**: SL = 約定価格 - 2.0 × ATR / TP = 約定価格 + 3.0 × ATR

**トレーリングストップ（3段階）**:
- +7%到達 → 10%幅で追従
- +15%到達 → 5%幅で追従
- +25%到達 → 3%幅で追従
"""
        )

    with st.expander("決済条件（4パターン）"):
        st.markdown(
            """
| 条件 | 詳細 |
|------|------|
| ストップロス | VIX/ATR連動のSLに到達 |
| テイクプロフィット | VIX/ATR連動のTPに到達 |
| テクニカル悪化 | RSI>70＋MACD下降クロス等 |
| 時間ベース | 45営業日以上保有（np.busday_count） |
"""
        )

    with st.expander("サーキットブレーカー詳細"):
        st.markdown(
            """
| トリガー | 閾値 | 冷却期間 |
|---------|------|---------|
| 連続損失 | 3回連続 | 1日 |
| 日次損失 | -2% | 当日終了まで |
| 週次損失 | -5% | 3日 |
| 外部halt | `halt(reason)` | 手動解除 |

- 信号検出は**停止しない**（execute_buy/execute_sellのみブロック）
- 状態ファイルは`os.replace()`でアトミック書き込み
- 破損時はフェイルセーフ（trading_halted=True）
"""
        )


# ============================================================
# 9. ポートフォリオ構成
# ============================================================

section_header("ポートフォリオ構成", color=P, subtitle="13テーマ 103銘柄")
with st.container(border=True):
    st.markdown("**メガトレンド投資テーマ（Tier 1/2/3）**")

    with st.expander("Tier 1（最優先）"):
        st.markdown(
            """
| テーマ | 銘柄数 | 代表銘柄 |
|--------|------:|---------|
| AI半導体 | 15 | NVDA, AMD, AVGO, TSM, MRVL |
| クラウド/AI基盤 | 9 | MSFT, GOOGL, AMZN, META |
| サイバーセキュリティ | 7 | CRWD, FTNT, ZS, PANW |
"""
        )

    with st.expander("Tier 2"):
        st.markdown(
            """
| テーマ | 銘柄数 | 代表銘柄 |
|--------|------:|---------|
| エネルギー基盤 | 8 | NEE, ENPH, FSLR |
| 防衛・宇宙 | 9 | LMT, RTX, NOC, PLTR |
| バイオ・ゲノム | 9 | ISRG, DXCM, CRSP |
| ロボティクス | 7 | FANUY, ABB, TER |
| 量子コンピューティング | 4 | IONQ, RGTI |
"""
        )

    with st.expander("Tier 3"):
        st.markdown(
            """
| テーマ | 銘柄数 | 代表銘柄 |
|--------|------:|---------|
| レアアース・素材 | 6 | MP, ALB |
| クリーンエネルギー/EV | 8 | TSLA, RIVN, LI |
| フィンテック | 8 | SQ, PYPL, COIN, SOFI |
| コンシューマーテック | 7 | AAPL, NFLX, DIS, UBER |
| エンタープライズSaaS | 7 | NOW, WDAY, TEAM, ADBE |
"""
        )

    st.caption("テーマローテーション: メガトレンド5軸スコア（100点）でライフサイクル判定。"
               "0-39=観察、40-69=積極買い、70-85=利確検討、86+=売却")


# ============================================================
# 10. パイプライン仕様
# ============================================================

section_header("パイプライン仕様", color=P)
with st.container(border=True):
    st.markdown(
        """
| Step | 入力 | 出力 | ユーザー視点の確認ポイント |
|---|---|---|---|
| 1. 情報収集 | ニュースAPI/RSS | `news` | ニュース件数が0でないか |
| 2. AI分析 | ニュース・銘柄群 | `ai_analysis` | 方向性(強気/弱気)が偏っていないか |
| 3. 売買判断 | テクニカル+AI分析 | `signals` | シグナルの確信度が低すぎないか |
| 4. 注文執行 | シグナル+リスク制約 | `trades` | シグナルに対し実行漏れがないか |
| 5. 資産記録 | 約定・ポジション | `portfolio_snapshots` | 損益・DD表示が更新されているか |
"""
    )


# ============================================================
# 11. 実行モードとスケジュール
# ============================================================

section_header("実行モードとスケジュール", color=W)
with st.container(border=True):
    st.markdown(
        """
| モード | 意味 | 最低限更新されるべきデータ |
|---|---|---|
| フル実行 | 収集〜執行まで一括 | `news`, `ai_analysis`, `signals`, `trades`, `system_runs` |
| 中間実行 | 日中の再評価 | `signals`, `system_runs` |
| 軽量実行 | 最小再チェック | `system_runs` |
| ニュース収集 | 収集のみ | `news`, `system_runs` |
| 分析のみ | 分析更新 | `ai_analysis`, `system_runs` |
"""
    )

    with st.expander("日次スケジュール（平日/週末）"):
        st.markdown("**平日スケジュール（ET）**")
        st.markdown(
            """
| 時刻 (ET) | モード | 備考 |
|-----------|--------|------|
| 07:00 | フル実行 | 情報収集→分析→シグナル→執行 |
| 12:00 | 軽量実行 | SL/TP再チェック |
| 01:00 (翌日) | 中間実行 | 日中シグナル再評価 |
"""
        )
        st.markdown("**週末スケジュール（ET）**")
        st.markdown(
            """
| 時刻 (ET) | モード | 備考 |
|-----------|--------|------|
| 09:00 (土) | フル分析 | 執行なし、シグナルをpendingで保存 |
| 13:00 (土) | シグナル | 再評価 |
| 17:00 (土) | シグナル | 再評価 |
| 16:30 (日) | デイリーサマリー | Discord通知 |

**月曜自動執行**: 週末pendingシグナルを自動処理。
価格乖離>10% → 取消 / 2営業日超経過 → 期限切れ
"""
        )


# ============================================================
# 12. データ更新・鮮度
# ============================================================

section_header("データ更新・鮮度", color=P)
with st.container(border=True):
    d1, d2, d3, d4, d5 = st.columns(5)
    d1.metric("news", fresh.get("news", "-") or "-")
    d2.metric("analysis", fresh.get("analysis", "-") or "-")
    d3.metric("signals", fresh.get("signals", "-") or "-")
    d4.metric("runs", fresh.get("runs", "-") or "-")
    d5.metric("trades", fresh.get("trades", "-") or "-")

    st.markdown(
        """
| 項目 | キャッシュTTL | 備考 |
|---|---:|---|
| Alpacaポートフォリオ/ポジション | 120秒 | 失敗時はトレード履歴推定にフォールバック |
| パイプライン状態 | 120秒 | 当日状況を短周期更新 |
| 日次資産推移/SPY比較 | 600秒 | 中長期表示のため長め |
| 品質集計・タイムライン | 600秒 | 直近7日平均を使用 |
"""
    )


# ============================================================
# 13. 画面ごとの使い分け
# ============================================================

section_header("画面ごとの使い分け", color=W)
with st.container(border=True):
    st.markdown(
        """
| 画面 | 見るべき指標 | 主な判断 |
|---|---|---|
| ポートフォリオ | KPI達成率、累積損益、DD | 実取引移行可否 |
| パイプライン | 当日ステップ完了状況、異常件数 | 運用停止ポイントの把握 |
| 日付詳細 | 実行ログ、Tickerフロー、売買実行有無 | 日次原因分析 |
| システム仕様（本画面） | KPI定義、リスクルール、パイプライン仕様 | ルール確認・判定根拠 |
"""
    )
